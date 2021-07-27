from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import datetime
import schemas, oauth2
from models import *
from database import get_db

router = APIRouter(
    tags=['Attrition'],
    prefix="/attrition"
)

# API
@router.get('/api/staff_attrition/{year}/{month}')
def get_total_by_division_by_year(year: int, month: int, db: Session = Depends(get_db)):

    query = db.query(MonthlyAttrition).filter(MonthlyAttrition.year == year, MonthlyAttrition.month == month).all()
    yearlyQuery = db.query(YearlyAttritionConst).filter(YearlyAttritionConst.year == year).all()

    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    res = []

    # Init result dict
    for div in divs:
        res.append({
            "headcounts":0,
            "join":0,
            "resign":0,
            "transfer":0, 
            "division":div
        })

    for q in yearlyQuery:
        q_div_index = next((index for (index, d) in enumerate(res) if d["division"] == q.div.name), None)
        res[q_div_index]["headcounts"]        = q.start_headcount

    for q in query:
        q_div_index = next((index for (index, d) in enumerate(res) if d["division"] == q.div.name), None)

        res[q_div_index]["join"]        = q.joined_count
        res[q_div_index]["resign"]      = q.resigned_count
        res[q_div_index]["transfer"]    = q.transfer_count
    return res

# Yearly Attrition
@router.get('/yearly')
def get_all_yearly_attr(db: Session = Depends(get_db)):
    yAttr = db.query(YearlyAttritionConst).all()
    return yAttr

@router.get('/yearly/{id}')
def get_single_yearly_attr(id: int, db: Session = Depends(get_db)):
    query = db.query(YearlyAttritionConst).filter(YearlyAttritionConst.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Yearly Attr of ID ({id}) was not found!")

    return query

@router.post('/yearly', status_code=status.HTTP_201_CREATED)
def create_yearly_attr(req: schemas.YearlyAttritionConst, db: Session = Depends(get_db)):
    newYAttr = YearlyAttritionConst(
        year                = req.year,
        start_headcount     = req.start_headcount,
        budget_headcount    = req.budget_headcount,
        div_id              = req.div_id
    )

    db.add(newYAttr)
    db.commit()
    db.refresh(newYAttr)

    return newYAttr

@router.patch('/yearly/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_yearly_attr(id: int, req: schemas.YearlyAttritionConstIn, db: Session = Depends(get_db)):
    query_res = db.query(YearlyAttritionConst).filter(YearlyAttritionConst.id == id)

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
    query_res = db.query(YearlyAttritionConst).filter(YearlyAttritionConst.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}

# Monthly Attrition
@router.get('/monthly')
def get_all_monthy_attr(db: Session = Depends(get_db)):
    mAttr = db.query(MonthlyAttrition).all()
    return mAttr

@router.get('/monthly/{id}')
def get_single_monthly_attr(id: int, db: Session = Depends(get_db)):
    query = db.query(MonthlyAttrition).filter(MonthlyAttrition.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Monthly Attr of ID ({id}) was not found!")

    return query

@router.post('/monthly', status_code=status.HTTP_201_CREATED)
def create_monthly_attr(req: schemas.MonthlyAttrition, db: Session = Depends(get_db)):
    newMAttr = MonthlyAttrition(
        joined_count    = req.joined_count,
        resigned_count  = req.resigned_count,
        transfer_count  = req.transfer_count,
        month           = req.month,
        year            = req.year,
        div_id          = req.div_id
    )

    db.add(newMAttr)
    db.commit()
    db.refresh(newMAttr)

    return newMAttr

@router.patch('/monthly/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_monthly_attr(id: int, req: schemas.MonthlyAttritionIn, db: Session = Depends(get_db)):
    query_res = db.query(MonthlyAttrition).filter(MonthlyAttrition.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.MonthlyAttritionIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/monthly/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_monthly_attr(id: int, db: Session = Depends(get_db)):
    query_res = db.query(MonthlyAttrition).filter(MonthlyAttrition.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}
