"""Campus Customs shopping assistant — PydanticAI agent wiring.

Loads the system prompt from prompts/prompt.md, builds the model, registers the tools from
tools.py, and returns a structured ChatReply (a message plus product_ids to display).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.usage import UsageLimits

import tools
from audit import append_audit
from models import ChatReply, ProductInfo

# Cap model/tool round-trips per message: keeps replies snappy and costs predictable, and
# guards against a runaway or adversarial prompt driving an expensive loop. A normal turn
# needs 1–2 model requests (one to call tools, one to answer); this leaves headroom.
RUN_LIMITS = UsageLimits(request_limit=6)

PROMPT_FILE = Path(__file__).resolve().parent / "prompts" / "prompt.md"
SYSTEM_PROMPT = PROMPT_FILE.read_text(encoding="utf-8")


@dataclass
class ChatDeps:
    """Per-request context available to the dynamic prompt (and tools, if needed)."""
    user_name: str | None = None
    user_email: str | None = None
    viewing: ProductInfo | None = None  # the product the shopper is currently looking at


agent = Agent(
    tools.build_model(),
    deps_type=ChatDeps,
    output_type=ChatReply,
    system_prompt=SYSTEM_PROMPT,
    tools=[tools.search_catalogue, tools.filter_products, tools.get_product_details, tools.check_stock],
    retries=2,
)


@agent.system_prompt
def _who_is_shopping(ctx: RunContext[ChatDeps]) -> str:
    if ctx.deps.user_name:
        who = f"The signed-in shopper is {ctx.deps.user_name}"
        if ctx.deps.user_email:
            who += f" (email: {ctx.deps.user_email})"
        return who + ". Greet them by name when natural. You may recall earlier messages in this conversation."
    return "The shopper is browsing as a guest (no saved history)."


@agent.system_prompt
def _page_context(ctx: RunContext[ChatDeps]) -> str:
    """Tell the agent which product the shopper is looking at, so 'this'/'it' resolves."""
    p = ctx.deps.viewing
    if not p:
        return ""
    return (
        f"The shopper is currently viewing this product page: {p.name} "
        f"(product_id: {p.product_id}, ${p.price_usd:.2f}, colors: {', '.join(p.colors)}). "
        "If they say 'this', 'it', or 'this one' without naming a product, they mean THIS item. "
        "Use its product_id with your tools to answer about its price, colors, or stock."
    )


def build_history(rows) -> list[ModelMessage]:
    """Turn stored chat rows into PydanticAI message history (used for memory in Problem 8)."""
    history: list[ModelMessage] = []
    for row in rows:
        if row["role"] == "user":
            history.append(ModelRequest(parts=[UserPromptPart(content=row["content"])]))
        elif row["role"] == "assistant":
            history.append(ModelResponse(parts=[TextPart(content=row["content"])]))
    return history


async def run_chat(
    message: str,
    user_name: str | None = None,
    user_email: str | None = None,
    viewing: ProductInfo | None = None,
    history: list[ModelMessage] | None = None,
) -> ChatReply:
    """Run one turn of the shop assistant, auditing every step of the agent loop.

    We step through the agent graph with agent.iter() so each loop event (model request,
    tool call, tool result, final answer) is appended to the audit trail.
    """
    deps = ChatDeps(user_name=user_name, user_email=user_email, viewing=viewing)
    run_id = uuid4().hex[:12]
    append_audit(run_id, "run_start", args=message)
    try:
        async with agent.iter(
            message, deps=deps, message_history=history or [], usage_limits=RUN_LIMITS
        ) as run:
            async for node in run:
                if Agent.is_model_request_node(node):
                    # Log any tool results coming back into the model on this request.
                    for part in node.request.parts:
                        if isinstance(part, ToolReturnPart):
                            append_audit(run_id, "tool_result", tool_name=part.tool_name, result=part.content)
                elif Agent.is_call_tools_node(node):
                    resp = node.model_response
                    stop = getattr(resp, "finish_reason", None)
                    calls = [p for p in resp.parts if isinstance(p, ToolCallPart)]
                    if calls:
                        for call in calls:
                            append_audit(run_id, "tool_call", tool_name=call.tool_name,
                                         args=call.args, stop_reason=stop)
                    else:
                        append_audit(run_id, "model_response", stop_reason=stop)
                elif Agent.is_end_node(node):
                    out = node.data.output
                    append_audit(run_id, "run_end",
                                 result=f"message chars={len(out.message)}, product_ids={out.product_ids}",
                                 stop_reason="final_result")
        return run.result.output
    except Exception as error:
        append_audit(run_id, "error", result=f"{type(error).__name__}: {error}", stop_reason="error")
        raise
