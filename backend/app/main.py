from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProjectRequest(BaseModel):
    project_idea: str


@app.get("/")
def home():
    return {"message": "Backend running"}


@app.post("/generate-blueprint")
def generate_blueprint(request: ProjectRequest):
    return {
        "problem_statement": f"This project solves the problem related to: {request.project_idea}",

        "objectives": [
            "Understand the user requirement",
            "Design a scalable project architecture",
            "Suggest a suitable technology stack",
            "Create a clear development roadmap",
        ],

        "tech_stack": [
            "React",
            "FastAPI",
            "Gemini",
            "MongoDB",
        ],

        "roadmap": [
            "Phase 1 - Requirement Analysis",
            "Phase 2 - UI/UX Design",
            "Phase 3 - Backend API Development",
            "Phase 4 - AI Integration",
            "Phase 5 - Testing and Deployment",
        ],

        "team_roles": [
            "Frontend Developer",
            "Backend Developer",
            "AI/ML Engineer",
            "Database Engineer",
            "UI/UX Designer",
        ],

        "risks": [
            "API cost may increase with heavy usage",
            "AI response accuracy may vary",
            "Data privacy needs proper handling",
            "Deployment errors may occur",
        ],

        "project_score": {
            "innovation": 8,
            "complexity": 7,
            "scalability": 9,
            "overall": 8,
        },

        "ai_suggestions": [
            "Add user authentication",
            "Add PDF export feature",
            "Store generated blueprints in database",
            "Add project comparison feature",
        ],
    }