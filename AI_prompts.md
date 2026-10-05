# HW4 — AI Prompt Log

A by-problem record of what I asked Claude to do while building the Campus Customs customer
website (React + Vite + TypeScript front end, FastAPI + PydanticAI backend). One section per
problem; each is filled in when we actually work that problem.

---

## Problem 2 — Analyze the database

### Prompt in my own words
Explore `data/campus_customs.db` and map out its tables — especially catalogue, inventory,
and users. Begin an `output/harness.md` that lists each table, its fields, and a one-line
note on why each field matters to the shop or the chatbot. This harness will keep growing in
later problems (models, tools, safety, specs).

---

## Problem 3 — Build the Campus Customs website

### Prompt in my own words
Scaffold a React + Vite + TypeScript front end for Campus Customs with a top nav bar linking
the main pages: Home, Products, About Us, Log In, and Create account. Take the look and feel
from yalebulldogblue.com for Home and About Us, but write those pages in our own voice (don't
copy the original text). On the Products page, show product images from the catalogue (using
the image paths in the database) with basic info — name, price, short description — and make
each card open a single-item page (large image on one side; full description, price, and
sizes/stock on the other). Add a floating chat panel in the bottom-right; it doesn't need a
real agent yet — a stub that will later call the backend is fine. Also stand up a small
FastAPI app in `backend/main.py` to serve products and images from the database, which we'll
grow into the agent backend in Problem 5.

---

## Problem 4 — Create account and login

### Prompt in my own words
Build a normal create-account / login flow. Create account collects first name, last name,
email, password, and confirm password; log in takes email and password. New accounts go into
the `users` table, and passwords must be stored securely so they can't be stolen. Use the
seeded test user (`test@campuscustoms.yale.edu` / `password`) while building — confirm I can
log in as that user and that a brand-new account also works. Then update `output/harness.md`
with how auth works: what we store for a user and how passwords are protected.

### Follow-up prompt
The seeded hashes don't record their iteration count, so the test user wouldn't log in and I
was blocked from searching for the count. Asked how to handle it; chose to re-hash the test
user's password into our secure self-describing format so it logs in through the normal flow.

---

## Problem 5 — PydanticAI agent backend

### Prompt in my own words
Build the shop chatbot as a PydanticAI agent behind FastAPI, plugged into the front-end chat
widget. Keep the API in `backend/main.py` (the file run with Uvicorn) and the agent in four
files beside it, like HW3: `prompts/prompt.md` (system prompt, grown later), `agent.py`
(agent wiring), `tools.py` (the agent's tools), and `models.py` (Pydantic / structured
types). In `main.py`, expose a chat route so a message from the website returns a reply from
the agent, alongside the product/auth routes. Put the Campus Customs voice and safety basics
into `prompts/prompt.md`, and add/update chat-reply and product-card types in `models.py`.
Document in `output/harness.md` how the front end talks to FastAPI and how the agent is loaded
(prompt file + model). The backend must run from `backend/` with `uvicorn main:app --reload
--port 8000`.

---

## Problem 6 — Tools: product info and stock

### Prompt in my own words
Give the agent tools that look up real info from `campus_customs.db` — product description,
price, and how many are in stock (by size when the customer asks). The agent must use the
database and must not invent prices or quantities, and when a size is out of stock it should
say so clearly. Expand `prompts/prompt.md` so the agent knows to call these tools for price
and stock questions, and add/update the return types in `models.py`. In `output/harness.md`,
list each tool and explain which model fields we chose for lookup results and why.

---

## Problem 7 — Chat search that updates the page

### Prompt in my own words
Add a feature where asking about a type of item ("what hoodies do you have?") makes the agent
search the catalogue and the website dynamically shows those matching items as product cards
(image, name, price, short info). Treat it as an API contract: the agent returns structured
product matches and the front end renders them on the page. After the dynamic cards load, keep
the Problem 3 single-item behavior — every card, including the ones chat just added, should
still open the detail view when clicked. Update `prompts/prompt.md` and `output/harness.md` so
it's clear how search results reach the page.

---

## Problem 8 — Customer memory

### Prompt in my own words
When a shopper is logged in, save their chat history in an appropriate database table and
reload it when they return. The agent should know who is chatting (name and email) — put that
in the agent deps (or an equivalent clear pattern) and/or tools. Also pass enough page context
that if someone is on a product page and asks "do you have this in pink?" the agent knows which
item they mean. Guests can still chat, but history only needs to persist for logged-in users.
Document in `output/harness.md` how chat history is stored, what customer fields the agent
sees, and how page context is passed.

---

## Problem 9 — Usability improvements

### Prompt in my own words
Now that the core shop works, improve it: implement two front-end usability improvements
(things that make the site look better and easier to use) and two agent/backend usability
improvements (things that make the agent's output better, more accurate, or safer — new tools,
or faster/cheaper runs). Write `output/usability.md` as we build, and for each improvement say
what was added and why it helps a Campus Customs shopper or the business. Make sure all four
improvements actually show up in the running app.

---

## Problem 10 — Style the website

### Prompt in my own words
Add creative design so the site feels like a real Campus Customs storefront (fonts, color,
hierarchy, motion, product presentation, chat feel). Specifically: put a good photo of Yale's
campus in fall (e.g. Sterling Library) in the big blue hero square on the homepage, ideally
with a gradient; make the chat agent's logo Handsome Dan (photo provided); and use Times New
Roman throughout. Write `output/design.md` — what changed and why it should help customers
stick around and buy — concrete and short.

### Follow-up prompt
Provided a Yale fall campus photo and asked to crop the black area and use it in the hero.

---

## Problem 11 — Site testing (app check)

### Prompt in my own words
Test the live site and document it in `output/app_check.html` — a page we can double-click to
open — with clear screenshots and short captions for three checks: (1) the chat checking an
item's inventory level (honest stock/price from the DB), (2) the dynamic search-result cards
appearing after a category question (e.g. hoodies), and (3) one of the usability features we
added in Problem 9. Make it easy to grade: a heading per check, the screenshot, and one or two
sentences on what it proves. Put the screenshot image files in `output/app_check_images/` and
link them from the HTML with relative paths (e.g. `app_check_images/inventory.png`).

---

## Problem 12 — Audit trail, safety, finish harness

### Prompt in my own words
Keep an append-only `output/audit_trail.json` of agent-loop activity (time, tool name, short
args/result, stop reason) that is not wiped between runs. Come up with safety rules for the
agent and put them in `prompts/prompt.md`. Finish `output/harness.md` so it's clear how the
system works: the model fields in `models.py` and why we chose them, the tools and abilities,
the safety rules, and the specs (loop limits, result caps, models, and how to run the front end
and backend).

### Follow-up (fix found while testing)
A message that tripped the model provider's content filter was raising a 500; added a graceful
fallback so the chat route returns a friendly message (still recorded in the audit trail).

---

## Problem 13 — Push to GitHub and submit the URL

### Prompt in my own words
Put the code in a folder named `hw4` and push it to a public GitHub repository, then submit the
repo URL on Canvas (a link graders can open and clone). Don't put the real `.env`,
`campus_customs.db`, or product images in the repo — use `.gitignore` — and include a
`.env.example` with placeholders only. Match the expected file layout.

### What I did
Restructured to the expected tree (requirements.txt at root, added `.env.example` + `README.md`,
hardened `.gitignore` to exclude `.env`, `data/`, `data.zip`, `*.db`, product images, `.node/`,
`.claude/`, `node_modules/`), made the backend read `.env` from `hw4/` so the repo is
self-contained, removed dead code, and committed. Verified no secrets/DB/images are tracked.
