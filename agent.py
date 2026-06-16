from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from tools.search import search_web
from tools.summary import summarize
from tools.chat import chat, llm

class AgentState(TypedDict):
    user_input: str
    tool_used: str
    result: str

def router(state: AgentState):
    prompt = f"""You are an intelligent router. Based on the user input, decide which tool to use.
    
User input: {state['user_input']}

Reply with ONLY one word:
- "search" → if user wants to find/research something from the web
- "summarize" → if user wants to summarize a text
- "chat" → if user wants to chat, ask questions, or generate code

Your response (one word only):"""
    
    response = llm.invoke(prompt)
    tool = response.content.strip().lower()
    
    if tool not in ["search", "summarize", "chat"]:
        tool = "chat"
    
    print(f"🧠 Routing to: {tool}")
    return {"tool_used": tool}

def search_node(state: AgentState):
    print("🔍 Searching the web...")
    raw_results = search_web(state['user_input'])
    
    # pass through LLM to give proper answer
    prompt = f"""Based on these search results, answer the user's question properly.

User question: {state['user_input']}

Search Results:
{raw_results}

Give a clear, direct answer."""
    
    response = llm.invoke(prompt)
    return {"result": response.content}

def summarize_node(state: AgentState):
    print("📝 Summarizing...")
    result = summarize(state['user_input'])
    return {"result": result}

def chat_node(state: AgentState):
    print("💬 Chatting...")
    result = chat(state['user_input'])
    return {"result": result}

def route_decision(state: AgentState):
    return state['tool_used']

# Build graph
graph = StateGraph(AgentState)
graph.add_node("router", router)
graph.add_node("search", search_node)
graph.add_node("summarize", summarize_node)
graph.add_node("chat", chat_node)

graph.set_entry_point("router")
graph.add_conditional_edges("router", route_decision, {
    "search": "search",
    "summarize": "summarize",
    "chat": "chat"
})
graph.add_edge("search", END)
graph.add_edge("summarize", END)
graph.add_edge("chat", END)

agent = graph.compile()