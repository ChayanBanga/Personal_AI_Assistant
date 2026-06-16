import os
import warnings
warnings.filterwarnings('ignore')

from dotenv import load_dotenv
load_dotenv()

import gradio as gr
from agent import agent

conversation_history = []

def chat(user_input, history):
    global conversation_history
    
    context = ""
    if conversation_history:
        context = "Previous conversation:\n"
        for msg in conversation_history[-4:]:
            context += f"{msg}\n"
        context += "\n"
    
    full_input = context + f"User: {user_input}"
    
    result = agent.invoke({
        "user_input": full_input,
        "tool_used": "",
        "result": ""
    })
    
    response = result['result']
    
    conversation_history.append(f"User: {user_input}")
    conversation_history.append(f"Assistant: {response}")
    
    return response

ui = gr.ChatInterface(
    fn=chat,
    title="🤖 Personal AI Assistant",
    description="Ask me anything — I can search the web, chat, generate code, and summarize text.",
    theme=gr.themes.Ocean(),
    
)

if __name__ == "__main__":
    ui.launch()