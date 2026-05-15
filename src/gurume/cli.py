"""Command-line interface."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from enum import StrEnum
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .area_mapping import get_area_slug
from .genre_mapping import get_all_genres
from .genre_mapping import get_genre_code
from .restaurant import PriceRange
from .restaurant import SortType
from .search import SearchRequest

app = typer.Typer(
    name="gurume",
    help="Gurume 餐廳搜尋工具 - 搜尋 Tabelog 上的日本餐廳",
    add_completion=False,
)

console = Console()
err_console = Console(stderr=True)


class OutputFormat(StrEnum):
    """Output format."""

    TABLE = "table"
    JSON = "json"
    SIMPLE = "simple"


class SortOption(StrEnum):
    """Sort option."""

    RANKING = "ranking"
    REVIEW_COUNT = "review-count"
    NEW_OPEN = "new-open"
    STANDARD = "standard"
    # Client-side ascending sort by parsed budget. Tabelog has no native price sort,
    # so this re-orders the page after it is fetched.
    PRICE = "price"


SORT_TYPE_MAP = {
    SortOption.RANKING: SortType.RANKING,
    SortOption.REVIEW_COUNT: SortType.REVIEW_COUNT,
    SortOption.NEW_OPEN: SortType.NEW_OPEN,
    SortOption.STANDARD: SortType.STANDARD,
    # PRICE delegates to STANDARD on the network; client re-sorts the result list.
    SortOption.PRICE: SortType.STANDARD,
}


# Match both half-width ¥ (search list pages) and full-width ￥ (detail pages).
_PRICE_LOWER_BOUND_RE = re.compile(r"[¥￥](\d[\d,]*)")


def _price_lower_bound(price_text: str | None) -> int | None:
    """Return the lower yen bound of a Tabelog budget string, or None.

    Tabelog renders budgets as e.g. "ランチ ¥1,000～¥1,999" or "ディナー ¥4,000～¥4,999".
    The first ¥-prefixed number is the lower bound.
    """
    if not price_text:
        return None
    match = _PRICE_LOWER_BOUND_RE.search(price_text)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def _enrich_with_detail_prices(restaurants: Sequence, *, concurrency: int = 5) -> list:
    """Fill in ``lunch_price``/``dinner_price`` by fetching each restaurant's detail page.

    Tabelog's search list pages omit budgets for many restaurants, so ``--sort price``
    alone often can't rank them. This helper hits each detail page in parallel using
    the existing ``RestaurantDetailRequest`` parser (which already extracts the budget
    block), and returns a NEW list of Restaurant objects with their price fields
    populated when the detail page provides them. Restaurants whose detail fetch
    fails are returned unchanged.
    """
    import asyncio
    from dataclasses import replace

    from .detail import RestaurantDetailRequest

    async def _one(sem: asyncio.Semaphore, r):
        async with sem:
            try:
                detail = await RestaurantDetailRequest(
                    restaurant_url=r.url,
                    fetch_reviews=False,
                    fetch_menu=False,
                    fetch_courses=False,
                ).fetch()
            except Exception:  # noqa: BLE001 — best-effort enrichment, keep the row
                return r
            lunch = r.lunch_price or detail.restaurant.lunch_price
            dinner = r.dinner_price or detail.restaurant.dinner_price
            if lunch == r.lunch_price and dinner == r.dinner_price:
                return r
            return replace(r, lunch_price=lunch, dinner_price=dinner)

    async def _all():
        sem = asyncio.Semaphore(concurrency)
        return await asyncio.gather(*[_one(sem, r) for r in restaurants])

    return asyncio.run(_all())


def _restaurant_min_price(r) -> int:
    """Sort key: minimum of parsed lunch/dinner lower bounds, or +inf if neither parses."""
    candidates = [
        v for v in (_price_lower_bound(r.lunch_price), _price_lower_bound(r.dinner_price)) if v is not None
    ]
    return min(candidates) if candidates else 10**9


def _resolve_genre_code(
    cuisine: str | None,
    keyword: str | None,
    status_console: Console = console,
) -> tuple[str | None, str | None]:
    genre_code = None
    if cuisine:
        genre_code = get_genre_code(cuisine)
        if genre_code:
            status_console.print(f"[cyan]使用料理類別過濾：{cuisine} ({genre_code})[/cyan]")
            return genre_code, keyword

        status_console.print(f"[yellow]警告：未知的料理類別「{cuisine}」，將作為關鍵字搜尋[/yellow]")
        return None, cuisine

    if keyword:
        detected_genre_code = get_genre_code(keyword)
        if detected_genre_code:
            status_console.print(f"[cyan]自動偵測料理類別：{keyword} ({detected_genre_code})[/cyan]")
            return detected_genre_code, None

    return None, keyword


def _build_json_data(restaurants: Sequence) -> list[dict[str, object]]:
    return [
        {
            "name": r.name,
            "rating": r.rating,
            "review_count": r.review_count,
            "area": r.area,
            "genres": r.genres,
            "url": r.url,
            "lunch_price": r.lunch_price,
            "dinner_price": r.dinner_price,
        }
        for r in restaurants
    ]


@app.command()
def search(
    area: Annotated[str | None, typer.Option("--area", "-a", help="搜尋地區（例如：東京、大阪）")] = None,
    keyword: Annotated[str | None, typer.Option("--keyword", "-k", help="關鍵字（例如：寿司、ラーメン）")] = None,
    cuisine: Annotated[str | None, typer.Option("--cuisine", "-c", help="料理類別（例如：すき焼き、寿司）")] = None,
    sort: Annotated[SortOption, typer.Option("--sort", "-s", help="排序方式")] = SortOption.RANKING,
    price_range: Annotated[
        str | None,
        typer.Option(
            "--price-range",
            "-p",
            help="預算範圍 Tabelog 代碼，例如 B001 (午餐 ¥999 以下)、C002 (晚餐 ¥1,000-1,999)",
        ),
    ] = None,
    enrich: Annotated[
        bool,
        typer.Option(
            "--enrich-from-detail/--no-enrich",
            "-E",
            help=(
                "搜尋結果再抓取每家餐廳的詳細頁，填入準確的午餐／晚餐預算。"
                " --sort price 在 list-page 沒有預算時非常有用，但會多送 N 個 HTTP 請求。"
            ),
        ),
    ] = False,
    enrich_concurrency: Annotated[
        int,
        typer.Option("--enrich-concurrency", min=1, max=20, help="並發抓取詳細頁的最大連線數"),
    ] = 5,
    limit: Annotated[int, typer.Option("--limit", "-n", min=1, help="顯示結果數量")] = 20,
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="輸出格式")] = OutputFormat.TABLE,
) -> None:
    """Search restaurants.

    Examples:
      gurume search --area 東京 --keyword 寿司
      gurume search -a 三重 -c すき焼き --sort ranking
      gurume search --area 大阪 --cuisine ラーメン -o json
    """
    status_console = err_console if output == OutputFormat.JSON else console

    if not area and not keyword and not cuisine:
        status_console.print("[red]錯誤：至少需要提供地區、關鍵字或料理類別之一[/red]")
        raise typer.Exit(1)

    genre_code, keyword = _resolve_genre_code(cuisine, keyword, status_console)
    if area and genre_code and get_area_slug(area) is None:
        status_console.print(f"[yellow]警告：無法精準映射地區「{area}」，搜尋結果可能包含其他地區[/yellow]")
    sort_type = SORT_TYPE_MAP[sort]

    price_range_enum: PriceRange | None = None
    if price_range is not None:
        try:
            price_range_enum = PriceRange(price_range)
        except ValueError:
            valid = ", ".join(p.value for p in PriceRange)
            status_console.print(f"[red]錯誤：無效的預算代碼「{price_range}」。可用代碼：{valid}[/red]")
            raise typer.Exit(1) from None

    # Execute search.
    status_console.print("[green]搜尋中...[/green]")
    request = SearchRequest(
        area=area,
        keyword=keyword,
        genre_code=genre_code,
        sort_type=sort_type,
        price_range=price_range_enum,
        max_pages=1,
    )

    response = request.search_sync()

    if response.status.value == "error":
        status_console.print(f"[red]搜尋錯誤：{response.error_message}[/red]")
        raise typer.Exit(1)

    if not response.restaurants:
        status_console.print("[yellow]沒有找到餐廳[/yellow]")
        raise typer.Exit(0)

    # Optionally enrich each row with prices fetched from the detail page.
    # Useful because Tabelog list pages don't expose budgets for many results,
    # which makes --sort price a no-op without enrichment.
    fetched = response.restaurants
    if enrich:
        status_console.print(
            f"[green]從詳細頁抓取預算 ({len(fetched)} 家，並發 {enrich_concurrency})...[/green]"
        )
        fetched = _enrich_with_detail_prices(fetched, concurrency=enrich_concurrency)

    if sort == SortOption.PRICE:
        fetched = sorted(fetched, key=_restaurant_min_price)
    restaurants = fetched[:limit]

    # Output results.
    if output == OutputFormat.JSON:
        _output_json(restaurants)
    elif output == OutputFormat.SIMPLE:
        _output_simple(restaurants)
    else:
        _output_table(restaurants)

    # Show summary stats.
    status_console.print(f"\n[cyan]共找到 {len(response.restaurants)} 家餐廳，顯示前 {len(restaurants)} 家[/cyan]")


def _output_table(restaurants: list) -> None:
    """Output restaurants as a table."""
    table = Table(title="搜尋結果")
    table.add_column("餐廳名稱", style="cyan", no_wrap=False)
    table.add_column("評分", justify="right", style="yellow")
    table.add_column("評論數", justify="right", style="green")
    table.add_column("地區", style="blue")
    table.add_column("類型", style="magenta")

    for r in restaurants:
        table.add_row(
            r.name,
            f"{r.rating:.2f}" if r.rating else "N/A",
            str(r.review_count) if r.review_count else "N/A",
            r.area or "N/A",
            ", ".join(r.genres[:2]) if r.genres else "N/A",
        )

    console.print(table)


def _output_json(restaurants: list) -> None:
    """Output restaurants as JSON."""
    console.print(json.dumps(_build_json_data(restaurants), ensure_ascii=False, indent=2))


def _output_simple(restaurants: list) -> None:
    """Output restaurants in a simple text format."""
    for i, r in enumerate(restaurants, 1):
        rating_str = f"{r.rating:.2f}" if r.rating else "N/A"
        review_str = str(r.review_count) if r.review_count else "N/A"
        console.print(f"{i}. {r.name} - ⭐{rating_str} ({review_str} 評論)")
        if r.area:
            console.print(f"   地區: {r.area}")
        if r.genres:
            console.print(f"   類型: {', '.join(r.genres[:3])}")
        console.print(f"   URL: {r.url}")
        console.print()


@app.command()
def list_cuisines() -> None:
    """List all supported cuisines."""
    cuisines = get_all_genres()

    table = Table(title=f"支援的料理類別（共 {len(cuisines)} 種）")
    table.add_column("料理名稱", style="cyan")
    table.add_column("代碼", style="yellow")

    for cuisine in cuisines:
        code = get_genre_code(cuisine)
        table.add_row(cuisine, code or "")

    console.print(table)


@app.command()
def tui() -> None:
    """Launch the interactive TUI."""
    from .tui import main as tui_main

    tui_main()


class McpTransport(StrEnum):
    STDIO = "stdio"
    SSE = "sse"
    STREAMABLE_HTTP = "streamable-http"


@app.command()
def mcp(
    transport: Annotated[
        McpTransport,
        typer.Option(
            "--transport",
            "-t",
            help="MCP transport. Use 'streamable-http' for HTTP clients.",
        ),
    ] = McpTransport.STDIO,
    host: Annotated[
        str,
        typer.Option("--host", help="Bind host for HTTP transports."),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option("--port", "-p", help="Bind port for HTTP transports."),
    ] = 8000,
    path: Annotated[
        str,
        typer.Option(
            "--path",
            help="HTTP mount path (streamable-http or sse).",
        ),
    ] = "/mcp",
) -> None:
    """Start the MCP (Model Context Protocol) server."""
    from .server import run

    run(transport=transport.value, host=host, port=port, path=path)


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
