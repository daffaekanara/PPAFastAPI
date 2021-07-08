from typing import List, Optional
from pydantic import BaseModel
import datetime

class Division(BaseModel):
    name:str

class ShowDivision(BaseModel):
    name:str

    class Config():
        orm_mode = True

class Employee(BaseModel):
    name:str
    email:str
    pw:str
    div_id:int

class ShowEmployee(BaseModel):
    name:str
    email:str
    part_of_div:ShowDivision

    class Config():
        orm_mode = True

class Login(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Trainings
class Training(BaseModel):
    name:str
    duration_days:float
    date:datetime.date
    proof:bool
    emp_id:int

class ShowTraining(BaseModel):
    name:str
    duration_days:float
    date:datetime.date
    proof:bool
    trainee: ShowEmployee

    class Config():
        orm_mode = True

# class TrainingTarget(BaseModel):
#     year:int
#     target_days:float
#     emp_id:int