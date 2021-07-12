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

class ShowEmployeeOnly(BaseModel):
    name:str
    email:str

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

class TrainingIn(BaseModel):
    name: Optional[str]
    duration_days: Optional[float]
    date: Optional[datetime.date]
    proof: Optional[bool]
    emp_id: Optional[int]

class ShowTraining(BaseModel):
    name:str
    duration_days:float
    date:datetime.date
    proof:bool
    emp_id:int
    employee: ShowEmployeeOnly
    
    class Config():
        orm_mode = True

class TrainingTarget(BaseModel):
    year:int
    target_days:float
    emp_id:int

class DebugParent(BaseModel):
    first_name:str
    last_name:str

class DebugParentIn(BaseModel):
    first_name:Optional[str]
    last_name:Optional[str]

class DebugChild(BaseModel):
    first_name:str
    last_name:str
    parent_id:int