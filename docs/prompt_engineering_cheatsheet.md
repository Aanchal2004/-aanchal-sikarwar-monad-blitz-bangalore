# Prompt Engineering Cheat Sheet

## System Prompt Structure

```
Role → Constraints → Output Format → Examples (optional)
```

## Good System Prompt (from this kit)

See `prompts/planner.txt`:
- Clear role definition
- Numbered responsibilities
- Structured output format
- Hackathon-specific constraints ("ship in 6-8 hours")

## Techniques

| Technique | When to Use | Example |
|-----------|-------------|---------|
| Role prompting | Every agent | "You are a Critic Agent..." |
| Few-shot | Format-sensitive tasks | Include 1-2 input/output examples |
| Chain-of-thought | Complex reasoning | "Think step by step" |
| Output schema | Structured data | "Return JSON: {steps: []}" |
| Constraints | Safety/scope | "Never expose private keys" |

## Agent-Specific Tips

**Planner**: Ask for numbered steps with complexity estimates
**Researcher**: Require sources, distinguish facts vs assumptions
**Critic**: Force APPROVED/NEEDS_REVISION verdict
**Executor**: Include demo script in output
**Wallet**: Never output private keys; always show safety notes

## Prompt Variables

```python
system = load_prompt("planner")
user = f"Goal: {query}\nContext: {context}"
```

## Reduce Hallucination

- "Answer using ONLY the provided context"
- "If unsure, say I don't know"
- Pass retrieved RAG chunks explicitly

## Hackathon Speed

1. Start with prompts in `prompts/` — they're pre-written
2. Tune ONE prompt that matters most for your demo
3. Don't over-optimize — working demo > perfect prompts

## Test Quickly

```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "planner", "input": "Build agent marketplace"}'
```
