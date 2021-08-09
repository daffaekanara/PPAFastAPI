from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import schemas, oauth2
from models import *
from database import get_db

router = APIRouter(
    tags=['Division'],
    prefix="/division"
)

@router.get('/get_emps')
def get_employees_by_div(db: Session = Depends(get_db)):
    divs = db.query(Division).all()

    ds    = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]

    res = []
    for d in ds:
        res.append({
            'division': d,
            'employees': []
        })

    for d in divs:
        for e in d.employees_of_div:
            res[d.id - 1]['employees'].append(e.name)

    return res

@router.get('/')
def get_all(db: Session = Depends(get_db)):
    divs = db.query(Division).all()
    return divs

@router.get('/{id}', status_code=status.HTTP_200_OK)
def get_single(id: int, db: Session = Depends(get_db)):
    div = db.query(Division).filter(Division.id == id).first()

    if not div:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Division of ID ({id}) was not found!")

    return div

@router.post('/', status_code=status.HTTP_201_CREATED)
def create(req: schemas.Division, db: Session = Depends(get_db)):
    new_div = Division(
        name=req.name
    )

    db.add(new_div)
    db.commit()
    db.refresh(new_div)

    return new_div

@router.patch('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id: int, req: schemas.DivisionIn , db: Session = Depends(get_db)):
    query_res = db.query(Division).filter(Division.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.DivisionIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_division(id: int, db: Session = Depends(get_db)): #, currUser = Depends(oauth2.get_current_user)
    query_res = db.query(Division).filter(Division.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return
