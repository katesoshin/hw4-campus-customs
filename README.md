# Campus Customs — Yale Bulldog Blue

A customer website for **Campus Customs**, a store selling officially licensed Yale University
merchandise. Shoppers can browse products, create an account and log in, and chat with an AI
store assistant (**Handsome Dan**) that answers honestly about price and stock from a local
database and surfaces matching products on the page.

- **Front end:** React + Vite + TypeScript (`frontend/`)
- **Back end:** Python FastAPI whose brain is a **PydanticAI** agent (`backend/`), using the
  OpenAI API via Portkey.

## Project structure

```
hw4/
├── AI_prompts.md            # log of the prompts used to build this
├── requirements.txt         # Python (backend) dependencies
├── .env.example             # copy to .env and add your key
├── .gitignore
├── README.md
├── frontend/                # Vite React TypeScript app
├── backend/                 # the AGENT is four files: prompts/prompt.md, agent.py,
│   ├── main.py              #   tools.py, models.py. main.py is the FastAPI app
│   ├── agent.py             #   (run: uvicorn main:app) and config/db/auth/audit are
│   ├── tools.py             #   supporting infrastructure.
│   ├── models.py
│   ├── config.py  db.py  auth.py  audit.py
│   └── prompts/prompt.md    # system prompt (voice + safety rules)
└── output/                  # harness, design/usability notes, app check, audit trail
```

**The agent** is the four files under `backend/`: `prompts/prompt.md` (system prompt),
`agent.py` (wiring + audited run loop), `tools.py` (catalogue/stock lookups), and `models.py`
(structured types).

## Step 1 — Place the local data pack (not in git)

The database and product images are **not committed** (per the assignment). Before running,
place the provided data pack so the tree looks exactly like this:

```
hw4/data/
├── campus_customs.db
└── products/            # images referenced by the catalogue
```

If you have `data.zip`, unzip it inside `hw4/` and it will create `hw4/data/` for you.

## Step 2 — Run the backend (from `hw4/`)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env and set PORTKEY_API_KEY
cd backend
uvicorn main:app --reload --port 8000
```

The backend serves the catalogue, product images, auth, and the chat agent on
**http://localhost:8000**. (It reads `campus_customs.db` and `products/` from `hw4/data/`, so
Step 1 must be done first.)

## Step 3 — Run the front end (from `hw4/frontend/`, in a second terminal)

```bash
npm install
npm run dev                     # Vite dev server on http://localhost:5173
```

Open **http://localhost:5173**. The Vite dev server proxies `/api` and `/images` to the
backend on port 8000, so keep the backend running.

### Try it
- Browse the **Shop**, open a product for the detail page.
- **Create account** / **Log In** (signed-in shoppers get a remembered chat).
- Open the chat (bottom-right) and ask things like *"What hoodies do you have under $70?"* or
  *"Is the Baseball Left Chest Crewneck in XS?"* — matching products appear on the page.

## Notes
- The chat agent uses OpenAI via Portkey; set `PORTKEY_API_KEY` in `.env`. The key is read at
  runtime and never logged or committed.
- Passwords are stored as salted PBKDF2-SHA256 hashes; plain-text passwords are never stored.
- `output/harness.md` documents the full system (models, tools, safety rules, specs).
