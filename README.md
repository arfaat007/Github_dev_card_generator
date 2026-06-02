# GitHub Dev Card Generator

A web-based AI-powered application that generates a personalized developer profile card using any public GitHub username.

The app fetches GitHub profile data, analyzes the developer’s repositories and skills using Gemini AI, and generates a clean shareable developer card.

---
## 🌐 Live Demo

Check out the live project here:

🔗 [GitHub Dev Card Generator](https://github-card-generator-153768643879.europe-west1.run.app)

---
## 🚀 Features

- Search any public GitHub username
- Fetch GitHub profile details using GitHub API
- Analyze developer profile using Gemini AI
- Generate a personalized developer card
- Display top repositories, skills, followers, and developer summary
- Share generated card URL
- Docker support for deployment
- FastAPI backend with a simple HTML frontend

---

## 🛠️ Tech Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- FastAPI
- Uvicorn
- Pydantic
- HTTPX

### AI / Agent Tools
- Google Gemini API
- Google ADK
- MCP Server

### Deployment
- Docker
- Docker Compose
- Google Cloud Run ready

---

## 📂 Project Structure

```bash
Github_dev_card_generator/
│
├── backend/
│   ├── main.py
│   ├── agent.py
│   ├── mcp_server.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── static/
│       └── cards/
│
├── frontend/
│   ├── index.html
│   └── Dockerfile
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
