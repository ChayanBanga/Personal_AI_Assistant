from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)

def chat(message: str) -> str:
    response = llm.invoke(message)
    return response.content