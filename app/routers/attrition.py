from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import datetime
import schemas, oauth2, utils
from models import *
from database import get_db

router = APIRouter(
    tags=['Attrition'],
    prefix="/attrition"
)

# Yearly Attrition
@router.get('/yearly')
def get_all_yearly_attr(db: Session = Depends(get_db)):
    yAttr = db.query(YearlyAttrition).all()
    return yAttr

@router.get('/yearly/{id}')
def get_single_yearly_attr(id: int, db: Session = Depends(get_db)):
    query = db.query(YearlyAttrition).filter(YearlyAttrition.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Yearly Attr of ID ({id}) was not found!")

    return query

@router.post('/yearly', status_code=status.HTTP_201_CREATED)
def create_yearly_attr(req: schemas.YearlyAttrition, db: Session = Depends(get_db)):
    newYAttr = YearlyAttrition(
        year                = req.year,
        start_headcount     = req.start_headcount,
        budget_headcount    = req.budget_headcount,
        joined_count        = req.joined_count,
        resigned_count      = req.resigned_count,
        transfer_count      = req.transfer_count,
        div_id              = req.div_id
    )

    db.add(newYAttr)
    db.commit()
    db.refresh(newYAttr)

    return newYAttr

@router.patch('/yearly/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_yearly_attr(id: int, req: schemas.YearlyAttritionIn, db: Session = Depends(get_db)):
    query_res = db.query(YearlyAttrition).filter(YearlyAttrition.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.YearlyAttritionConstIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/yearly/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_yearly_attr(id: int, db: Session = Depends(get_db)):
    query_res = db.query(YearlyAttrition).filter(YearlyAttrition.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}
