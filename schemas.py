from typing import List, Optional
from pydantic import BaseModel
import datetime

class Division(BaseModel):
    name:str

class DivisionIn(BaseModel):
    name:Optional[str]

class ShowDivision(BaseModel):
    name:str

    class Config():
        orm_mode = True

class Employee(BaseModel):
    name:str
    email:str
    pw:str
    div_id:int

class EmployeeIn(BaseModel):
    name:Optional[str]
    email:Optional[str]
    pw:Optional[str]
    div_id:Optional[int]

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

class TrainingTargetIn(BaseModel):
    year:Optional[int]
    target_days:Optional[float]
    emp_id:Optional[int]

class DebugParent(BaseModel):
    first_name:str
    last_name:str

class DebugParentIn(BaseModel):
    first_name:Optional[str]
    last_name:Optional[str]

# Social Contributions
class SocialType(BaseModel):
    name        :str

class SocialTypeIn(BaseModel):
    name        :Optional[str]

class ShowSocialType(BaseModel):
    name        :str

    class Config():
        orm_mode = True

class SocialContrib(BaseModel):
    date        :datetime.date
    topic_name  :str
    div_id      :int
    social_type_id:int

class SocialContribIn(BaseModel):
    date        :Optional[datetime.date]
    topic_name  :Optional[str]
    div_id      :Optional[int]
    social_type_id:Optional[int]

class ShowSocialContrib(BaseModel):
    date        :str
    topic_name  :str
    div         :ShowDivision
    social_type :ShowSocialType

    class Config():
        orm_mode = True