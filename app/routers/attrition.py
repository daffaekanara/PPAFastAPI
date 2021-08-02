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

# API
@router.get('/api/staff_attrition/{year}')
def get_total_by_division_by_year(year: int, db: Session = Depends(get_db)):

    query = db.query(YearlyAttrition).filter(YearlyAttrition.year == year).all()

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

    for q in query:
        q_div_index = utils.find_index(res, "division", q.div.name)

        res[q_div_index]["headcounts"]  = q.start_headcount
        res[q_div_index]["join"]        = q.joined_count
        res[q_div_index]["resign"]      = q.resigned_count
        res[q_div_index]["transfer"]    = q.transfer_count

    return res

@router.get('/api/rate/{div_name}/{year}')
def get_rate_by_division_by_yearmonth(div_name: str, year: int, db: Session = Depends(get_db)):

    query = db.query(YearlyAttrition).filter(
        YearlyAttrition.div.has(name=div_name),
        YearlyAttrition.year == year
    ).one()

    attr_sum = query.resigned_count + query.transfer_count
    attr_rate = attr_sum / query.start_headcount

    return [
        {"title":"Attrition Rate","rate":attr_rate},
        {"title":"","rate":1-attr_rate}
    ]

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
