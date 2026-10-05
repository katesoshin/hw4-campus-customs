"""Tools the Campus Customs agent can call, plus the model builder.

Every tool reads the local SQLite database (via db.py) so the agent's claims about price,
colors, and stock are always grounded in real data — never invented.
"""
from __future__ import annotations

from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

import db
from config import CHAT_MODEL, PORTKEY_BASE_URL, portkey_api_key
from models import Product, ProductInfo, SizeAvailability, StockResult


def build_model() -> OpenAIResponsesModel:
    """OpenAI (via Portkey) model used by the agent. Model id comes from config."""
    key = portkey_api_key()
    client = AsyncOpenAI(
        api_key=key,
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-api-key": key},
        timeout=60,
        max_retries=2,
    )
    return OpenAIResponsesModel(CHAT_MODEL, provider=OpenAIProvider(openai_client=client))


def _availability(p: Product) -> list[SizeAvailability]:
    return [SizeAvailability(size=s.size, quantity=s.quantity, in_stock=s.quantity > 0) for s in p.sizes]


def _to_info(p: Product) -> ProductInfo:
    """Build the agent-facing product view from a catalogue + inventory record."""
    return ProductInfo(
        product_id=p.product_id,
        name=p.name,
        garment_type=p.garment_type,
        description=p.description,
        price_usd=p.price,
        colors=p.colors,
        sizes=_availability(p),
    )


# ---- Agent tools (registered in agent.py). All read campus_customs.db — never invented. ----
def search_catalogue(query: str) -> list[ProductInfo]:
    """Search the Campus Customs catalogue by keywords (garment type, color, team, design,
    occasion, etc.). Returns matching products with description, exact price, colors, and
    per-size stock. Use this to find products a shopper is describing."""
    return [_to_info(p) for p in db.search_catalogue(query, limit=8)]


def filter_products(
    garment_type: str | None = None,
    color: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
) -> list[ProductInfo]:
    """Filter the catalogue precisely by garment type, color, price range, and stock. Use this
    for questions with constraints — e.g. "hoodies under $70", "navy quarter-zips in stock".
    All criteria are optional and combine (AND). Prices are in US dollars."""
    out: list[ProductInfo] = []
    for p in db.list_products():
        if garment_type and garment_type.lower() not in p.garment_type.lower():
            continue
        if color and not any(color.lower() in c.lower() for c in p.colors):
            continue
        if min_price is not None and p.price < min_price:
            continue
        if max_price is not None and p.price > max_price:
            continue
        if in_stock_only and not any(s.quantity > 0 for s in p.sizes):
            continue
        out.append(_to_info(p))
    return out[:12]


def get_product_details(product_id: str) -> ProductInfo | None:
    """Get full details for one product by its product_id: description, exact price, colors,
    and per-size stock. Returns None if no such product exists."""
    p = db.get_product(product_id)
    return _to_info(p) if p else None


def check_stock(product_id: str, size: str | None = None) -> StockResult:
    """Check live inventory for a product. If a size is given, report just that size;
    otherwise report every size. Always call this before telling a shopper whether something
    is in stock — quantity 0 means that size is sold out."""
    p = db.get_product(product_id)
    if not p:
        return StockResult(product_id=product_id, name="(unknown)", price_usd=0.0, sizes=[],
                           note=f"No product with id '{product_id}'.")
    all_sizes = _availability(p)
    if size is None:
        return StockResult(product_id=p.product_id, name=p.name, price_usd=p.price, sizes=all_sizes)
    matched = [s for s in all_sizes if s.size.upper() == size.upper()]
    if not matched:
        offered = ", ".join(s.size for s in all_sizes)
        return StockResult(product_id=p.product_id, name=p.name, price_usd=p.price, sizes=[],
                           note=f"Size '{size}' is not offered for this product. Offered sizes: {offered}.")
    return StockResult(product_id=p.product_id, name=p.name, price_usd=p.price, sizes=matched)
