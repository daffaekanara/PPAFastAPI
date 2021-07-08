from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, hashing
from database import get_db

router = APIRouter(
    tags=['Employee'],
    prefix="/employee"
)


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_employee(req: schemas.Employee, db: Session = Depends(get_db)):
    # new_emp = models.Employee(req)
    hashed = hashing.bcrypt(req.pw)

    new_emp = models.Employee(name=req.name, email=req.email, pw=hashed, div_id=req.div_id)

    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp

@router.get('/')
def get_all_employees(db: Session = Depends(get_db)):
    emps = db.query(models.Employee).all()
    return emps

@router.get('/{id}',response_model=schemas.ShowEmployee)
def get_single_employee(id: int, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == id).first()

    if not emp:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Employee of ID ({id}) was not found!")

    return emp

@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update_employee(id: int, req: schemas.Employee, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == id)

    if not emp.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Division of ID ({id}) was not found!")

    emp.update(req)

    pass

@router.delete('/{id}')
def delete_employee(id: int, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == id)

    if not emp:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Employee of ID ({id} was not found)")

    emp.delete(synchronize_session=False)
    db.commit()