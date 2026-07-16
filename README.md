# 🚀 ProjectMentor AI

> Transform any project idea into a complete technical blueprint using AI-powered multi-agent systems.

ProjectMentor AI is an intelligent project planning platform that helps students, developers, startup founders, and hackathon participants convert a simple project idea into a detailed implementation blueprint. The platform leverages a multi-agent AI architecture to generate requirements, documentation, architecture recommendations, technology stack suggestions, API designs, database structures, and development roadmaps.

---

## ✨ Features

### 🤖 AI-Powered Blueprint Generation

Generate a complete project plan from a single project idea.

### 📋 Requirements Analysis

Automatically identifies:

* Problem statement
* Objectives
* Scope
* Functional requirements
* Non-functional requirements

### 🏗️ System Architecture Design

Provides:

* High-level architecture
* Component breakdown
* Deployment suggestions
* Scalability considerations

### 💻 Technology Stack Recommendations

Suggests:

* Frontend frameworks
* Backend technologies
* Databases
* Cloud services
* Third-party integrations

### 🗄️ Database Design Suggestions

Generates:

* Database recommendations
* Schema considerations
* Data relationships

### 🔌 API Planning

Creates:

* API endpoint suggestions
* Request/response structures
* Integration recommendations

### 🛣️ Development Roadmap

Provides a step-by-step implementation plan including milestones and future enhancements.

---

## 🏛️ Multi-Agent Workflow

```text
Project Idea
      │
      ▼
Requirements Agent
      │
      ▼
Documentation Agent
      │
      ▼
Architecture Agent
      │
      ▼
Tech Stack Agent
      │
      ▼
Blueprint Aggregator
      │
      ▼
Final Project Blueprint
```

Each AI agent focuses on a specific responsibility, ensuring higher quality and more structured outputs.

---

## 🖥️ Tech Stack

### Frontend

* React.js
* Vite
* JavaScript
* CSS

### Backend

* FastAPI
* Python
* Pydantic

### AI & LLM Integration

* DeepSeek
* OpenRouter
* Multi-Agent AI Architecture

---

## 📂 Project Structure

```text
ProjectMentor-AI/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── models/
│   │   ├── prompts/
│   │   ├── routes/
│   │   └── services/
│   │
│   ├── requirements.txt
│   └── README.md
│
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/projectmentor-ai.git

cd projectmentor-ai
```

---

## 🚀 Backend Setup

### Create Virtual Environment

```bash
cd backend

python -m venv venv
```

### Activate Environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
LLM_PROVIDER=deepseek

# OR
LLM_PROVIDER=openrouter

API_KEY=your_api_key
```

### Run Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at:

```text
http://localhost:8000
```

---

## 🎨 Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend will run at:

```text
http://localhost:5173
```

---

## 📡 API Endpoint

### Generate Project Blueprint

**POST**

```http
/api/generate-blueprint
```

### Request

```json
{
  "project_idea": "Build an AI Interview Preparation Platform"
}
```

### Response

```json
{
  "problem_statement": "...",
  "objectives": "...",
  "features": [...],
  "tech_stack": [...],
  "architecture": "...",
  "database": "...",
  "apis": [...],
  "roadmap": "..."
}
```

---

## 🎯 Use Cases

* Hackathon Project Planning
* Final Year Projects
* Startup MVP Planning
* Software Architecture Exploration
* AI-Assisted Project Documentation
* Product Discovery & Ideation

---

## 🔮 Future Enhancements

* PDF Blueprint Export
* ER Diagram Generation
* UML Diagram Generation
* Team Role Recommendations
* Cost Estimation Module
* AI-Powered Risk Analysis
* Project Timeline Visualization
* Cloud Deployment Suggestions

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a new feature branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License.

---

## 👨‍💻 Authors

Developed with ❤️ to simplify project planning and accelerate innovation through AI.

If you find this project useful, consider giving it a ⭐ on GitHub.
