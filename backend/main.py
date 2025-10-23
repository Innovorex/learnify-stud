from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import auth, teacher, student, teacher_results, syllabus_routes
from app.db import Base, engine

# Create DB tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Assessment Backend - Phase 5")

# Configure CORS - Allow specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3004",
        "http://127.0.0.1:3004",
        "https://learnifystudent.innovorex.co.in",
        "http://learnifystudent.innovorex.co.in",  # HTTP version
        "http://104.251.217.92:3004",  # IP-based access if needed
        "http://104.251.217.119:3004",  # Server IP
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(teacher.router, prefix="/teacher", tags=["Teacher"])
app.include_router(student.router, prefix="/student", tags=["Student"])
app.include_router(teacher_results.router, prefix="/teacher", tags=["Results"])
app.include_router(syllabus_routes.router, tags=["Syllabus"])

@app.get("/")
def home():
    return {"message": "AI Assessment Backend - Phase 1 running "}
