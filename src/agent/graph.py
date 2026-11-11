from src.agent.state import AgentState
from src.agent.nodes import recipe_node, route_decision, router_node, select_node, step_node
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

# Инициализация графа
graph = StateGraph(AgentState)

# Добавление узлов
graph.add_node("router", router_node)
graph.add_node("recipe", recipe_node)
graph.add_node("select", select_node)
graph.add_node("step", step_node)

# Добавление ребер
graph.add_edge(START, "router")
graph.add_conditional_edges(
    "router",
    route_decision,
    {
        "recipe_node": "recipe",
        "select_node": "select",
        "step_node": "step",
        "end_node": END,
    },
)
graph.add_edge("recipe", END)
graph.add_edge("select", END)
graph.add_edge("step", END)

# Компиляция графа с памятью диалога между вызовами
app = graph.compile(checkpointer=MemorySaver())
