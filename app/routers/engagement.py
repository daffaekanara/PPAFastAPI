from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import datetime
import schemas, oauth2
from models import *
from database import get_db

router = APIRouter(
    tags=['BU/SU Engagement'],
    prefix="/engagement"
)

# API
@router.get('/api/total_by_division/{year}')
def get_total_by_division_by_year(year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    query = db.query(BUSUEngagement).filter(BUSUEngagement.date >= startDate, BUSUEngagement.date <= endDate).all()
    
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    res = []

    # Init result dict
    for div in divs:
        res.append({"quarterly_meeting":0, "workshop":0, "divisions":div})

    for q in query:
        eng_by_div = next((index for (index, d) in enumerate(res) if d["divisions"] == q.div.name), None)

        if q.eng_type_id == 1:
            res[eng_by_div]["quarterly_meeting"] += 1
        if q.eng_type_id == 2:
            res[eng_by_div]["workshop"] += 1

    return res

# Engagement Type
@router.get('/type')
def get_all_engagement_type(db: Session = Depends(get_db)):
    eType = db.query(EngagementType).all()
    return eType

@router.get('/type/{id}')
def get_single_engagement_type(id: int, db: Session = Depends(get_db)):
    query = db.query(EngagementType).filter(EngagementType.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Engagement Type of ID ({id}) was not found!")

    return query

@router.post('/type', status_code=status.HTTP_201_CREATED)
def create_engagement_type(req: schemas.EngagementType, db: Session = Depends(get_db)):
    newType = EngagementType(
        name    =req.name
    )

    db.add(newType)
    db.commit()
    db.refresh(newType)

    return newType

@router.patch('/type/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_engagement_type(id: int, req: schemas.EngagementTypeIn, db: Session = Depends(get_db)):
    query_res = db.query(EngagementType).filter(EngagementType.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.EngagementTypeIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/type/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_engagement_type(id: int, db: Session = Depends(get_db)):
    query_res = db.query(EngagementType).filter(EngagementType.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}

# Engagement 
@router.get('/')
def get_all_engagement(db: Session = Depends(get_db)):
    engs = db.query(BUSUEngagement).all()
    return engs

@router.get('/{id}')
def get_single_engagement(id: int, db: Session = Depends(get_db)):
    query = db.query(BUSUEngagement).filter(BUSUEngagement.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"BUSU Engagement of ID ({id}) was not found!")

    return query

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_engagement(req: schemas.BUSUEngagement, db: Session = Depends(get_db)):
    newEng = BUSUEngagement(
        activity_name   = req.activity_name,
        date            = req.date,
        proof           = req.proof,

        eng_type_id     = req.eng_type_id,

        div_id          = req.div_id
    )

    db.add(newEng)
    db.commit()
    db.refresh(newEng)

    return newEng

@router.patch('/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_engagement(id: int, req: schemas.BUSUEngagementIn, db: Session = Depends(get_db)):
    query_res = db.query(BUSUEngagement).filter(BUSUEngagement.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.BUSUEngagementIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_engagement(id: int, db: Session = Depends(get_db)):
    query_res = db.query(BUSUEngagement).filter(BUSUEngagement.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}

