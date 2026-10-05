"""Campus Customs backend — FastAPI.

Problem 3 scope: serve the product catalogue and product images from the local database so
the React front end has something real to render. We grow this into the full agent backend
(auth in P4, the PydanticAI chat agent in P5) in later problems.
"""
from __future__ import annotations

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import json

import auth
import db
import tools
from agent import build_history, run_chat
from config import PRODUCTS_DIR
from models import (
    AuthResponse,
    ChatHistoryItem,
    ChatRequest,
    ChatResponse,
    LoginRequest,
    Product,
    PublicUser,
    RegisterRequest,
)

app = FastAPI(title="Campus Customs API")

# Allow the Vite dev server to call us during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/products", response_model=list[Product])
def list_products():
    """All products with price, colors, and per-size stock."""
    return db.list_products()


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    """A single product for the item detail page."""
    product = db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# ---- Auth (Problem 4) ----
def _public_user(row) -> PublicUser:
    return PublicUser(id=row["id"], name=row["name"], email=row["email"], first_name=row["first_name"])


def current_user(authorization: str | None = Header(default=None)):
    """Resolve the signed-in user from a Bearer token, or raise 401."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    uid = auth.verify_token(authorization.split(" ", 1)[1])
    if uid is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    row = db.get_user_by_id(uid)
    if not row:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return row


@app.post("/api/auth/register", response_model=AuthResponse)
def register(req: RegisterRequest):
    if db.get_user_by_email(req.email):
        raise HTTPException(status_code=409, detail="An account with that email already exists")
    first = req.first_name.strip()
    last = req.last_name.strip()
    uid = db.create_user(
        name=f"{first} {last}".strip(),
        email=req.email,
        password_hash=auth.hash_password(req.password),  # securely hashed; plain text never stored
        first_name=first,
        last_name=last,
    )
    row = db.get_user_by_id(uid)
    return AuthResponse(token=auth.create_token(uid), user=_public_user(row))


@app.post("/api/auth/login", response_model=AuthResponse)
def login(req: LoginRequest):
    row = db.get_user_by_email(req.email)
    if not row or not auth.verify_password(req.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return AuthResponse(token=auth.create_token(row["id"]), user=_public_user(row))


@app.get("/api/auth/me", response_model=PublicUser)
def me(user=Depends(current_user)):
    return _public_user(user)


def optional_user(authorization: str | None = Header(default=None)):
    """Like current_user, but returns None instead of raising for guests."""
    try:
        return current_user(authorization)
    except HTTPException:
        return None


# ---- Chat (Problems 5 + 7 + 8) ----
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, user=Depends(optional_user)):
    """A shopper message in → the agent's reply out, with any matching product cards.

    Logged-in shoppers get persistent memory (history saved/reloaded) and are known to the
    agent by name + email. Page context (the product being viewed) resolves "this"/"it".
    """
    user_name = (user["first_name"] or user["name"]) if user else None
    user_email = user["email"] if user else None

    # Memory: for signed-in shoppers, feed recent history into the agent.
    history = build_history(db.recent_messages(user["id"])) if user else []

    # Page context: the product the shopper is viewing, so references like "this" resolve.
    viewing = tools.get_product_details(req.product_id) if req.product_id else None

    try:
        reply = await run_chat(
            req.message, user_name=user_name, user_email=user_email, viewing=viewing, history=history
        )
    except Exception:
        # The run (and its cause) is already recorded in the audit trail. Degrade gracefully
        # instead of 500-ing — e.g. when a message trips the model provider's content filter.
        return ChatResponse(
            message="Sorry, I can't help with that one. I'm here to help you shop Campus Customs — "
            "ask me about Yale hoodies, tees, sizes, prices, or what's in stock!",
            products=[],
        )
    products = db.get_products(reply.product_ids)

    # Persist this turn for signed-in shoppers (store product_ids to rehydrate later).
    if user:
        db.save_message(user["id"], "user", req.message)
        products_json = json.dumps(reply.product_ids) if reply.product_ids else None
        db.save_message(user["id"], "assistant", reply.message, products_json)

    return ChatResponse(message=reply.message, products=products)


@app.get("/api/chat/history", response_model=list[ChatHistoryItem])
def chat_history(user=Depends(current_user)):
    """Reload a signed-in shopper's saved conversation (oldest first)."""
    items: list[ChatHistoryItem] = []
    for row in db.recent_messages(user["id"], limit=50):
        product_ids = json.loads(row["products_json"]) if row["products_json"] else []
        # Older seed rows may store full product dicts; keep only ids we can rehydrate.
        if product_ids and isinstance(product_ids[0], dict):
            product_ids = [p.get("product_id") for p in product_ids if p.get("product_id")]
        items.append(
            ChatHistoryItem(role=row["role"], message=row["content"], products=db.get_products(product_ids))
        )
    return items


@app.get("/images/{product_id}")
def product_image(product_id: str):
    """Serve a product's photo from data/products/ (never committed to git)."""
    rel = db.image_path(product_id)
    if not rel:
        raise HTTPException(status_code=404, detail="Unknown product")
    # image_file_path looks like "products/<file>.jpg"; serve the file safely from PRODUCTS_DIR.
    name = rel.split("/")[-1]
    path = (PRODUCTS_DIR / name).resolve()
    if PRODUCTS_DIR.resolve() not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)
