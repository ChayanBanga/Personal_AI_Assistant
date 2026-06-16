# 🤖 Personal AI Assistant

[![GitHub stars](https://img.shields.io/github/stars/ChayanBanga/Personal_AI_Assistant?style=social)](https://github.com/ChayanBanga/Personal_AI_Assistant/stargazers)

⭐ Star this repo if you find it helpful!

A multi-tool AI assistant built with LangGraph + Groq (Llama 3.3 70B) that intelligently routes your queries to the right tool automatically.

## ✨ Features

- 🧠 **Smart Routing** — automatically decides whether to search, chat, or summarize
- 🔍 **Web Search** — searches the web and gives clean answers
- 💬 **Chat & Code** — answers questions, generates code, explains concepts
- 📝 **Summarization** — condenses long text into key points
- 🧵 **Memory** — remembers previous messages in the conversation

## 🏗️ Architecture

User Input

↓

Router (Llama 3.3 70B decides)

↓

┌───────────┬──────────────┬─────────────┐

│  Search   │     Chat     │  Summarize  │

│  (Web)    │ (Code/Q&A)   │   (Text)    │

└───────────┴──────────────┴─────────────┘

↓

Final Answer

## Project Structure:
research-agent/
├── main.py          # entry point
├── agent.py         # langgraph graph
├── tools/
│   ├── search.py    # web search tool
│   ├── summary.py   # summarizer
│   └── chat.py      # regular chat
├── requirements.txt
└── README.md


## 🛠️ Tech Stack

- **LangGraph** — agent loop and routing
- **Groq** — ultra-fast inference (Llama 3.3 70B)
- **DuckDuckGo Search** — free web search, no API key needed
- **Python** — backend

## 🚀 Setup

1. Clone the repo
```bash
git clone https://github.com/ChayanBanga/Personal_AI_Assistant
cd Personal_AI_Assistant
```

2. Install dependencies
```bash
pip install -r Requirement.txt
```

3. Create `.env` file