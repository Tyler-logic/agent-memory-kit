# agent-memory-kit

Four small, dependency-free memory and safety patterns for LLM agents — no vector
database, no framework lock-in. Companion library to the AgentCraft articles
["Why Your AI Agent Forgets Things Mid-Task"](https://agentcraft-logicpond.netlify.app/articles/01-why-agents-forget-things/)
and ["How to Stop an Autonomous Agent From Doing Something Destructive"](https://agentcraft-logicpond.netlify.app/articles/08-permission-boundary-pattern/).

```bash
pip install agent-memory-kit
```

## Pattern 1 — Scratchpad state

Facts that must never age out of a truncated context window, re-injected into
every prompt.

```python
from agent_memory_kit import ScratchpadState

state = ScratchpadState()
state.set_pref("timezone", "America/Edmonton")
state.record_decision("using SQLite, not Postgres — no ops overhead needed")

system_prompt = f"You are a coding assistant.\n\n{state.render()}"
```

## Pattern 2 — Fuzzy recall

For facts too numerous to keep resident. Starts crude (difflib over a flat
JSONL file, zero infra) on purpose — swap in real embeddings later by passing
a custom `scorer`, without changing call sites.

```python
from agent_memory_kit import FuzzyRecall

memory = FuzzyRecall(path="memory.jsonl")
memory.remember("the deploy target changed to Cloudflare Pages")
memory.recall("what is the deploy target?", top_k=3)
```

## Pattern 3 — Pre-compaction checkpointing

If your framework auto-summarizes old turns, don't let it decide unsupervised
what survives — extract load-bearing facts into Pattern 1's state first.

```python
from agent_memory_kit import ScratchpadState, CompactionCheckpoint

state = ScratchpadState()

def extract(history):
    # a cheap, targeted LLM call — not shown here
    return {"decisions": ["switched to SQLite"]}

checkpoint = CompactionCheckpoint(state, extractor=extract)
checkpoint.before_compaction(conversation_history=history)
# now safe to let the framework summarize/drop the raw turns
```

## Pattern 4 — Permission boundaries

Classifies actions by reversibility and enforces it in code the model can't
talk its way around — not a prompt instruction it can forget.

```python
from agent_memory_kit import ActionTier, PermissionBoundary

boundary = PermissionBoundary()
boundary.register("read_file", ActionTier.AUTONOMOUS, read_file_impl)
boundary.register("send_email", ActionTier.CONFIRM, send_email_impl)
boundary.register("transfer_funds", ActionTier.BLOCKED, transfer_funds_impl)

boundary.execute("send_email", {"to": "a@b.com", "body": "hi"}, get_human_approval=ask_user)
# unknown/unregistered actions default to CONFIRM, never AUTONOMOUS
```

## Which one do you need?

- A handful of durable facts in a single-session assistant → **Pattern 1** alone.
- A large, persistent corpus (a whole codebase, months of history) → **Pattern 2**,
  starting crude.
- A framework that auto-summarizes and you keep losing specifics → **Pattern 3**,
  layered on top of whichever of the first two you're already using.

Most production agents end up running most or all four at once — the first three
for memory reliability, Pattern 4 for safety once the agent can act autonomously.

## Status

Published to PyPI as `agent-memory-kit` (v0.2.0):
https://pypi.org/project/agent-memory-kit/

```bash
pip install agent-memory-kit
```

Source: https://github.com/Tyler-logic/agent-memory-kit

## License

MIT
