# LangGraph Cheat Sheet

## Basic StateGraph

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    query: str
    plan: str
    research: str
    final_output: str

def planner_node(state: AgentState) -> AgentState:
    # call LLM
    return {"plan": "Step 1: research, Step 2: execute"}

def researcher_node(state: AgentState) -> AgentState:
    return {"research": f"Findings for: {state['plan']}"}

graph = StateGraph(AgentState)
graph.add_node("planner", planner_node)
graph.add_node("researcher", researcher_node)
graph.set_entry_point("planner")
graph.add_edge("planner", "researcher")
graph.add_edge("researcher", END)

app = graph.compile()
result = app.invoke({"query": "Build agent marketplace"})
```

## Conditional Routing

```python
def should_revise(state: AgentState) -> str:
    if "NEEDS_REVISION" in state.get("critique", ""):
        return "researcher"
    return "executor"

graph.add_conditional_edges("critic", should_revise, {
    "researcher": "researcher",
    "executor": "executor",
})
```

## Human-in-the-Loop

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = graph.compile(checkpointer=memory, interrupt_before=["executor"])
```

## Multi-Agent with Messages

```python
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(llm, tools=[check_balance])
result = agent.invoke({"messages": [("user", "Check balance for 0x...")]})
```

## This Kit's Upgrade Path

See `agents/workflow.py` → `build_langgraph_workflow()` for the skeleton.

Steps to upgrade:
1. Define `AgentState` TypedDict
2. Convert each agent's `run()` to a graph node
3. Add conditional edge from critic
4. Compile and call from `/agent/workflow`

## Debug

```python
from langgraph.graph import StateGraph
# Visualize (if supported)
print(app.get_graph().draw_ascii())
```
