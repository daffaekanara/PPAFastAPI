from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from routers import division, employee, auth, training, debug, qaip
from routers import socialContrib, attrition, engagement, project, budget
from database import engine

models.Base.metadata.create_all(engine)

app = FastAPI()

origins = [
    # "https://111.95.148.87"
    "*"
]

app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# app.include_router(debug.router)
app.include_router(qaip.router)
app.include_router(budget.router)
app.include_router(project.router)
app.include_router(engagement.router)
app.include_router(attrition.router)
app.include_router(socialContrib.router)
app.include_router(training.router)
app.include_router(division.router)
app.include_router(employee.router)
app.include_router(auth.router)


@app.get('/')
def index():
    return {"Msg": "Go to site/docs for the API docs"}

