import os
import warnings
warnings.filterwarnings('ignore')

from dotenv import load_dotenv
load_dotenv()

from agent import agent

conversation_history = []
pending_action = ""
needs_confirmation = False

def chat(user_input, history):
    global conversation_history, pending_action, needs_confirmation


    result = agent.invoke({
        "user_input": user_input,  # ✅ clean, just the current message
        "conversation_history": conversation_history[-4:],  # ✅ separate field
        "thought": "",
        "plan": [],
        "actions_taken": [],
        "observations": [],
        "final_answer": "",
        "needs_confirmation": needs_confirmation,
        "pending_action": pending_action,
        "loop_count": 0
    })
    pending_action = result.get('pending_action', '')
    needs_confirmation = result.get('needs_confirmation', False)

    response = result['final_answer']
    conversation_history.append(f"User: {user_input}")
    conversation_history.append(f"Assistant: {response}")

    return response

import gradio as gr

ui = gr.ChatInterface(
    fn=chat,
    title="🤖 Personal AI Assistant",
    description="Ask me anything — I can search the web, chat, generate code, read emails, and more.",
    theme=gr.themes.Ocean(),
)

if __name__ == "__main__":
    ui.launch()
