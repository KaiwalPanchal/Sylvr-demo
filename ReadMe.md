# Chatbot Application

This is a WebSocket-based chatbot application.  

## 🟣 Installation

1. **Clone the repository:**

```bash
git clone <your-repo-url>
cd <your-repo-name>

pip install -r requirements.txt

cd chatbot

uvicorn main:app --reload

open postman or any tool you like and use this 

ws://localhost:8000/chat

add the following url to .env on your system for it to work properly:
MONGODB_URI="mongodb+srv://fakeslakke:B8PYEtEguzChJCsr@cluster0.ghuc7qq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
GOOGLE_API_KEY="your api key"