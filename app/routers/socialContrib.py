from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import datetime
import schemas, oauth2
from models import *
from database import get_db

router = APIRouter(
    tags=['Social Contrib'],
    prefix="/socialcontrib"
)

# SocialType
@router.get('/type')
def get_all_social_type(db: Session = Depends(get_db)):
    contribs = db.query(SocialType).all()
    return contribs

@router.get('/type/{id}')
def get_single_social_type(id: int, db: Session = Depends(get_db)):
    query = db.query(SocialType).filter(SocialType.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Social Contrib Type of ID ({id}) was not found!")

    return query

@router.post('/type', status_code=status.HTTP_201_CREATED)
def create_social_type(req: schemas.SocialType, db: Session = Depends(get_db)):
    newType = SocialType(
        name    = req.name
    )

    db.add(newType)
    db.commit()
    db.refresh(newType)

    return newType

@router.put('/type/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_social_type(id: int, req: schemas.SocialTypeIn, db: Session = Depends(get_db)):
    query_res = db.query(SocialType).filter(SocialType.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.SocialTypeIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/type/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_social_type(id: int, db: Session = Depends(get_db)):
    query_res = db.query(SocialType).filter(SocialType.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}

# SocialContrib
@router.get('/')
def get_all_contrib(db: Session = Depends(get_db)):
    contribs = db.query(SocialContrib).all()
    return contribs

@router.get('/{id}')
def get_single_contrib(id: int, db: Session = Depends(get_db)):
    query = db.query(SocialContrib).filter(SocialContrib.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Social Contribution of ID ({id}) was not found!")

    return query

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_contrib(req: schemas.SocialContrib, db: Session = Depends(get_db)):
    newContrib = SocialContrib(
        date            = req.date,
        topic_name      = req.topic_name,
        creator_id      = req.creator_id,
        social_type_id  = req.social_type_id
    )

    db.add(newContrib)
    db.commit()
    db.refresh(newContrib)

    return newContrib

@router.put('/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_contrib(id: int, req: schemas.SocialContribIn, db: Session = Depends(get_db)):
    query_res = db.query(SocialContrib).filter(SocialContrib.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.SocialContribIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_contrib(id: int, db: Session = Depends(get_db)):
    query_res = db.query(SocialContrib).filter(SocialContrib.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}
