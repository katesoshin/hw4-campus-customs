# Campus Customs — Usability Improvements (Problem 9)

Two front-end improvements (look + ease of use) and two agent/backend improvements (better,
more accurate, safer, cheaper). Each says what we added and why it helps a shopper or the
business.

## Front-end

### 1. Markdown formatting in chat replies
**What:** The chat bubbles now render the assistant's Markdown — **bold**, line breaks, and
bullet lists — instead of showing raw `**asterisks**` and run-together text. A small, safe
renderer (no raw HTML injected) handles bold, newlines, and `-`/`*` bullets.
**Why it helps:** The agent naturally replies with bolded product names and bulleted lists.
Rendering them makes answers scannable and professional, so shoppers can compare options at a
glance instead of reading a wall of text with stray symbols.

### 2. Sort and "in stock only" controls on the Shop page
**What:** The Products page gets a sort dropdown (Featured / Price: low→high / Price:
high→low / Name A–Z) and an "In stock only" toggle, working alongside the existing search.
**Why it helps:** Shoppers browse by budget and hide sold-out items, which is how people
actually shop for apparel. Finding something in their size and price faster means fewer
dead ends and more completed purchases.

## Agent / backend

### 3. `filter_products` tool for precise constraint queries
**What:** A new agent tool that filters the catalogue by garment type, color, price range
(min/max), and in-stock-only — all read from the database. The prompt directs the agent to
use it for questions with constraints ("hoodies under $70", "quarter-zips in navy that are in
stock").
**Why it helps:** Keyword search alone was loose on numeric/boolean constraints, so "under
$70" could slip in a $72 item. Exact filtering means accurate, trustworthy answers — the
agent recommends only items that truly match, which protects the shopper's trust and the
store's credibility.

### 4. Agent run limits (`UsageLimits`)
**What:** The agent run is bounded with PydanticAI `UsageLimits` (a cap on model
requests/tool-call rounds per message). If a turn would exceed the cap it stops cleanly
instead of looping.
**Why it helps:** It keeps responses snappy and costs predictable (fewer wasted model/tool
round-trips per message) and adds a safety rail against a runaway or adversarial prompt
driving an expensive loop — better for the shopper (speed) and the business (cost + safety).
