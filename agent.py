from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from tools.search import search_web
from tools.chat import chat, llm
from tools.summary import summarize
from tools.gmail_tool import (
    get_latest_emails,
    search_emails,
    read_email,
    send_email,
    reply_to_email
)
from datetime import datetime

class AgentState(TypedDict):
    user_input: str
    thought: str
    plan: List[str]
    actions_taken: List[str]
    observations: List[str]
    final_answer: str
    needs_confirmation: bool
    pending_action: str
    loop_count: int

# ─── STEP 1: THINK ───────────────────────────────────────
def think(state: AgentState):
    today = datetime.now().strftime("%A, %d %B %Y, %I:%M %p")
    print("\n🧠 Thinking...")

    prompt = f"""You are a smart AI assistant. Today is {today}.

Analyze this user request carefully and break it down.

User request: {state['user_input']}

Previous observations: {state.get('observations', [])}

Think step by step:
1. What is the user ACTUALLY asking for?
2. Is this a simple task or complex?
3. Does it need tools or just reasoning?
4. Are there any risks? (irreversible actions like sending emails, deleting)
5. What sub-tasks are needed?

Write your thought process clearly:"""

    response = llm.invoke(prompt)
    thought = response.content
    print(f"   💭 {thought[:200]}...")
    return {"thought": thought, "loop_count": state.get("loop_count", 0) + 1}

# ─── STEP 2: PLAN ────────────────────────────────────────
def plan(state: AgentState):
    print("📋 Planning...")

    prompt = f"""Based on this thought, create an action plan.

User request: {state['user_input']}
Thought: {state['thought']}
Today: {datetime.now().strftime("%A, %d %B %Y")}

Available tools:
- "chat" → answer questions, generate text, write emails/code (NO external data needed)
- "search" → search the web for current info, news, dates, events
- "get_latest_emails" → fetch latest emails from inbox
- "search_emails" → search emails by keyword/sender
- "read_email" → read a specific email by ID
- "send_email" → send a new email (REQUIRES confirmation first)
- "reply_email" → reply to an email (REQUIRES confirmation first)
- "summarize" → summarize long text
- "no_tool" → if request can be answered directly from reasoning

RULES:
- If user says "generate/write/draft email" → use "chat" only, NOT send
- If user says "send/reply" → plan "chat" first to compose, then flag for confirmation
- If question involves current date/time → today is already injected, use "chat"
- If question needs live web data → use "search"
- Never plan "send_email" without confirmation step

Return ONLY a Python list of actions in order:
["action1", "action2", ...]
Example: ["chat"] or ["search", "chat"] or ["get_latest_emails"]"""

    response = llm.invoke(prompt)
    
    try:
        plan_list = eval(response.content.strip())
        if not isinstance(plan_list, list):
            plan_list = ["chat"]
    except:
        plan_list = ["chat"]

    print(f"   📌 Plan: {plan_list}")
    return {"plan": plan_list}

# ─── STEP 3: ACT ─────────────────────────────────────────
def act(state: AgentState):
    print("⚡ Acting...")
    
    plan_list = state['plan']
    observations = state.get('observations', [])
    actions_taken = state.get('actions_taken', [])
    needs_confirmation = False
    pending_action = ""

    for action in plan_list:
        print(f"   🔧 Executing: {action}")

        if action == "chat":
            today = datetime.now().strftime("%A, %d %B %Y, %I:%M %p")
            prompt = f"""Today is {today}.
User request: {state['user_input']}
Previous context: {observations}
Respond helpfully:"""
            result = llm.invoke(prompt).content
            observations.append(f"chat result: {result}")
            actions_taken.append("chat")

        elif action == "search":
            query_prompt = f"""Extract the best and most specific search query for this request.
            Request: {state['user_input']}
            Today: {datetime.now().strftime("%d %B %Y")}
            Include today's date in the query if it's about current events.
            Return ONLY the search query, nothing else:"""
            query = llm.invoke(query_prompt).content.strip()
            result = search_web(query, max_results=8)  # increase results
            observations.append(f"search result for '{query}': {result}")
            actions_taken.append(f"search: {query}")

        elif action == "get_latest_emails":
            result = get_latest_emails(max_results=5)
            observations.append(f"latest emails: {result}")
            actions_taken.append("get_latest_emails")

        elif action == "search_emails":
            query_prompt = f"""Extract email search query from this request.
            Request: {state['user_input']}
            Return ONLY the search query:"""
            query = llm.invoke(query_prompt).content.strip()
            result = search_emails(query)
            observations.append(f"email search result: {result}")
            actions_taken.append(f"search_emails: {query}")

        elif action == "read_email":
            id_prompt = f"""Extract the email ID from this request.
            Request: {state['user_input']}
            Observations so far: {observations}
            Return ONLY the email ID:"""
            email_id = llm.invoke(id_prompt).content.strip()
            result = read_email(email_id)
            observations.append(f"email content: {result}")
            actions_taken.append(f"read_email: {email_id}")

        elif action == "summarize":
            result = summarize(state['user_input'])
            observations.append(f"summary: {result}")
            actions_taken.append("summarize")

        elif action == "send_email":
            needs_confirmation = True
            details_prompt = f"""Extract email details from this request.
            Request: {state['user_input']}
            Context: {observations}
            Return ONLY a Python dict, no markdown, no backticks, no explanation:
            {{"to": "email@example.com", "subject": "subject", "body": "body"}}"""
    
            raw = llm.invoke(details_prompt).content.strip()
            # clean markdown if LLM adds it
            raw = raw.replace("```python", "").replace("```json", "").replace("```", "").strip()
            details = eval(raw)
            pending_action = f"send_email:{details['to']}:{details['subject']}:{details['body']}"
            observations.append(f"composed email: {details}")
            actions_taken.append("composed email - awaiting confirmation")

        elif action == "reply_email":
            needs_confirmation = True
            reply_prompt = f"""Extract reply details from this request.
            Request: {state['user_input']}
            Context: {observations}
            Return ONLY a Python dict, no markdown, no backticks, no explanation:
            {{"email_id": "id", "body": "reply body"}}"""
            
            raw = llm.invoke(reply_prompt).content.strip()
            raw = raw.replace("```python", "").replace("```json", "").replace("```", "").strip()
            details = eval(raw)
            pending_action = f"reply_email:{details['email_id']}:{details['body']}"
            observations.append(f"composed reply - awaiting confirmation")
            actions_taken.append("composed reply - awaiting confirmation")

    return {
        "observations": observations,
        "actions_taken": actions_taken,
        "needs_confirmation": needs_confirmation,
        "pending_action": pending_action
    }

# ─── STEP 4: OBSERVE + ANSWER ────────────────────────────
def answer(state: AgentState):
    print("✅ Generating answer...")

    # if confirmation needed
    if state.get('needs_confirmation') and state.get('pending_action'):
        parts = state['pending_action'].split(':')
        action_type = parts[0]

        if action_type == "send_email":
            return {"final_answer": f"""✋ **Confirmation Required**

            I've composed this email:
            **To:** {parts[1]}
            **Subject:** {parts[2]}
            **Body:** {parts[3]}

            Reply **"yes send it"** to send or **"cancel"** to discard."""}

        elif action_type == "reply_email":
            return {"final_answer": f"""✋ **Confirmation Required**

I've composed this reply:
**Email ID:** {parts[1]}
**Reply:** {parts[2]}

Reply **"yes send it"** to send or **"cancel"** to discard."""}

    # normal answer
    prompt = f"""Based on all observations, give a final clean answer.

User request: {state['user_input']}
Thought: {state['thought']}
Actions taken: {state['actions_taken']}
Observations: {state['observations']}

STRICT RULES:
- Extract ACTUAL information from observations, don't just give links
- If search results contain match details, state them directly
- If genuinely no data found, say so clearly in ONE line
- Never say "check these websites" — extract the info yourself
- Be direct and confident

Give a clear, helpful, well-formatted final answer:"""

    response = llm.invoke(prompt)
    return {"final_answer": response.content}

# ─── CONFIRMATION HANDLER ─────────────────────────────────
def handle_confirmation(state: AgentState):
    user_input = state['user_input'].lower().strip()
    pending = state.get('pending_action', '')

    # STRICT confirmation only
    if ('yes send it' in user_input or 'yes, send it' in user_input) and pending:
        parts = pending.split(':')
        action_type = parts[0]

        if action_type == "send_email":
            result = send_email(parts[1], parts[2], parts[3])
            return {"final_answer": f"✅ {result}", "pending_action": "", "needs_confirmation": False}

        elif action_type == "reply_email":
            result = reply_to_email(parts[1], parts[2])
            return {"final_answer": f"✅ {result}", "pending_action": "", "needs_confirmation": False}

    elif 'cancel' in user_input:
        return {"final_answer": "❌ Action cancelled.", "pending_action": "", "needs_confirmation": False}

    # anything else — don't send, go back to answer
    return {"final_answer": "Email not sent. Reply **'yes send it'** to confirm or **'cancel'** to discard.", "pending_action": pending, "needs_confirmation": True}

# ─── ROUTING LOGIC ───────────────────────────────────────
def should_confirm(state: AgentState):
    user_input = state['user_input'].lower().strip()
    if state.get('needs_confirmation') and state.get('pending_action'):
        # STRICT check — only exact confirmation phrases
        if 'yes send it' in user_input or 'yes, send it' in user_input:
            return "confirm"
    return "answer"

# ─── BUILD GRAPH ─────────────────────────────────────────
graph = StateGraph(AgentState)
graph.add_node("think", think)
graph.add_node("plan", plan)
graph.add_node("act", act)
graph.add_node("answer", answer)
graph.add_node("confirm", handle_confirmation)

graph.set_entry_point("think")
graph.add_edge("think", "plan")
graph.add_edge("plan", "act")
graph.add_conditional_edges("act", should_confirm, {
    "confirm": "confirm",
    "answer": "answer"
})
graph.add_edge("answer", END)
graph.add_edge("confirm", END)

agent = graph.compile()