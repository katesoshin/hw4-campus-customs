"""Pydantic models shared across the API and the agent."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class SizeStock(BaseModel):
    size: str
    quantity: int

    @property
    def in_stock(self) -> bool:
        return self.quantity > 0


class Product(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    search_tags: list[str]
    image_url: str
    price: float
    sizes: list[SizeStock] = Field(default_factory=list)

    @property
    def in_stock(self) -> bool:
        return any(s.quantity > 0 for s in self.sizes)


# ---- Auth ----
class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PublicUser(BaseModel):
    id: int
    name: str
    email: str
    first_name: str | None = None


class AuthResponse(BaseModel):
    token: str
    user: PublicUser


# ---- Agent tool return types (Problem 6) ----
class SizeAvailability(BaseModel):
    """Stock for one size of a product."""
    size: str
    quantity: int = Field(description="Units on hand for this size; 0 means sold out.")
    in_stock: bool = Field(description="True when quantity > 0.")


class ProductInfo(BaseModel):
    """What the agent gets back when it looks up a product (search or details).

    Only fields the agent needs to answer a shopper honestly — identity, what it is,
    exact price, colors, and per-size stock.
    """
    product_id: str = Field(description="Stable id used to display the product on the site.")
    name: str
    garment_type: str
    description: str
    price_usd: float = Field(description="Exact price in US dollars — state as given, never rounded or guessed.")
    colors: list[str]
    sizes: list[SizeAvailability]


class StockResult(BaseModel):
    """Result of a stock check — overall or for one requested size."""
    product_id: str
    name: str
    price_usd: float
    sizes: list[SizeAvailability] = Field(description="The size(s) checked, each with quantity and in_stock.")
    note: str | None = Field(default=None, description="Set when something needs flagging, e.g. a size we don't offer.")


# ---- Chat ----
class ChatRequest(BaseModel):
    message: str
    product_id: str | None = Field(
        default=None,
        description="Page context: the product_id the shopper is currently viewing, if any, "
        "so references like 'this' resolve to it.",
    )


class ChatReply(BaseModel):
    """Structured result the agent returns for a customer message."""
    message: str = Field(description="The assistant's reply to show the shopper.")
    product_ids: list[str] = Field(
        default_factory=list,
        description="product_id values of catalogue items to display alongside the reply.",
    )


class ChatResponse(BaseModel):
    message: str
    products: list[Product] = Field(default_factory=list)


class ChatHistoryItem(BaseModel):
    """One stored message, rehydrated for the front end to re-render on return."""
    role: str
    message: str
    products: list[Product] = Field(default_factory=list)
