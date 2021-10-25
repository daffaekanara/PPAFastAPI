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

@router.put('/type/{id}',  status_code=status.HTTP_202_ACCEPTED)
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

        creator_id      = req.creator_id
    )

    db.add(newEng)
    db.commit()
    db.refresh(newEng)

    return newEng

@router.put('/{id}',  status_code=status.HTTP_202_ACCEPTED)
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

