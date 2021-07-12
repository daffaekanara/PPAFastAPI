from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import schemas, hashing
from models import *
from database import get_db

router = APIRouter(
    tags=['Employee'],
    prefix="/employee"
)

@router.get('/')
def get_all(db: Session = Depends(get_db)):
    emps = db.query(Employee).all()
    return emps

@router.get('/{id}') #response_model=schemas.ShowEmployee
def get_single(id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == id).first()

    if not emp:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Employee of ID ({id}) was not found!")

    return emp

@router.post('/', status_code=status.HTTP_201_CREATED)
def create(req: schemas.Employee, db: Session = Depends(get_db)):
    hashed = hashing.bcrypt(req.pw)

    newEmp = Employee(
        name    = req.name, 
        email   = req.email, 
        pw      = hashed, 
        div_id  = req.div_id
    )

    db.add(newEmp)
    db.commit()
    db.refresh(newEmp)

    return newEmp

@router.patch('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id: int, req: schemas.EmployeeIn, db: Session = Depends(get_db)):
    query_res = db.query(Employee).filter(Employee.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.EmployeeIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/{id}')
def delete_employee(id: int, db: Session = Depends(get_db)):
    query_res = db.query(Employee).filter(Employee.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}