# Multi-Agent Network

## Problem

Complex tasks require multiple specialized agents coordinating — but most demos show single chatbots.

## Solution

A visible multi-agent network where:
- Planner decomposes goals
- Researcher gathers context via RAG
- Critic validates before execution
- Executor delivers final output
- All steps visible in DemoPanel with timing

## Architecture

```
User Query
  → planner_agent
  → researcher_agent (+ RAG)
  → critic_agent
  → executor_agent
  → Final Output

Optional: LangGraph StateGraph (agents/workflow.py TODO)
```

## Tech Stack

- agents/workflow.py (ready to run)
- POST /agent/workflow endpoint
- DemoPanel with step animation
- LangGraph for production upgrade

## Demo Plan

1. Open /demo page
2. Enter: "Design a token-gated agent marketplace on Monad"
3. Click Run Workflow
4. Watch 4 steps complete with timing
5. Present final_output to judges

## Judge Pitch

> "This isn't one chatbot — it's a network of specialized agents. Planner, Researcher, Critic, Executor — each with a role. Watch the pipeline run live. Swap in LangGraph for production."
