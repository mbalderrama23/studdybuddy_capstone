# StudyBuddy Backend (FastAPI + AgentPro)

StudyBuddy is an AI-powered backend that helps students learn from their own uploaded study materials.  
It uses **FastAPI**, **AgentPro's ReAct architecture**, and multiple custom tools to generate:

- 📄 *Cheat sheets*  
- 🧠 *Grounded question answering*  
- 📝 *Quizzes*  
- 📅 *Study plans*  

---

## 🚀 Features

- Upload PDFs, DOCX, PPTX, and text files  
- Extract and store document text  
- Chat with an intelligent ReAct-based agent  
- Tools for summarizing, quizzing, planning, and searching  
- Clean FastAPI endpoints for easy frontend integration  

---

## 📁 Project Structure

```
studybuddy/
├── main.py
├── agent/
├── tools/
├── services/
├── storage/
└── models/
```

---

## 🔗 Key Endpoints

| Method | Route | Purpose |
|--------|--------|----------|
| POST | `/upload/file` | Upload a document |
| POST | `/upload/text` | Upload raw text |
| GET | `/materials` | List stored materials |
| POST | `/chat` | Interact with the StudyBuddy agent |

---

## ▶️ Running the App

```
pip install -r requirements.txt
uvicorn main:app --reload
```

Swagger docs at:  
**http://localhost:8000/docs**

---

## 🛠️ Requirements

- Python 3.10+
- FastAPI 0.109.0  
- OpenAI API key in `.env`

---

## 👤 Author

**Arunava Singh**  
Backend powered by FastAPI + AgentPro + OpenAI.
