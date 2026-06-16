import os
import warnings
warnings.filterwarnings('ignore')

from dotenv import load_dotenv
load_dotenv()

from agent import agent

def run():
    print("🤖 Personal AI Assistant Ready! (type 'exit' to quit)\n")
    
    conversation_history = []
    
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        if user_input.lower() == 'exit':
            print("Bye!")
            break
        
        # add history to input
        context = ""
        if conversation_history:
            context = "Previous conversation:\n"
            for msg in conversation_history[-4:]:  # last 4 exchanges
                context += f"{msg}\n"
            context += "\n"
        
        full_input = context + f"User: {user_input}"
        
        result = agent.invoke({
            "user_input": full_input,
            "tool_used": "",
            "result": ""
        })
        
        # save to history
        conversation_history.append(f"User: {user_input}")
        conversation_history.append(f"Assistant: {result['result']}")
        
        print(f"\n🤖 Agent: {result['result']}\n")
        print("-" * 50)

if __name__ == "__main__":
    run()