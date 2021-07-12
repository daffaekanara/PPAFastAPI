from fastapi import FastAPI
import models
from routers import division, employee, auth, training, trainingTarget, debug
from database import engine

models.Base.metadata.create_all(engine)

app = FastAPI()
# app.include_router(debug.router)
app.include_router(trainingTarget.router)
app.include_router(training.router)
app.include_router(division.router)
app.include_router(employee.router)
app.include_router(auth.router)


@app.get('/')
def index():
    return {"Msg": "Go to site/docs for the API docs"}

