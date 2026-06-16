from tools.chat import llm

def summarize(text: str) -> str:
    prompt = f"""Summarize the following text in a clear and concise way:

{text}

Provide a brief summary with key points."""
    
    response = llm.invoke(prompt)
    return response.content