from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import schemas, oauth2
from models import *
from database import get_db

router = APIRouter(
    tags=['Training Target'],
    prefix="/trainingtarget"
)

@router.get('/')
def get_all(db: Session = Depends(get_db)):
    trainingTrgts = db.query(TrainingTarget).all()
    return trainingTrgts

@router.get('/{id}')
def get_single(id: int, db: Session = Depends(get_db)):
    query = db.query(TrainingTarget).filter(TrainingTarget.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Training Target of ID ({id}) was not found!")

    return query

@router.post('/', status_code=status.HTTP_201_CREATED)
def create(req: schemas.TrainingTarget, db: Session = Depends(get_db)):
    newTrainTrgt = TrainingTarget(
        year        = req.year,
        target_days = req.target_days,
        emp_id      = req.emp_id
    )

    db.add(newTrainTrgt)
    db.commit()
    db.refresh(newTrainTrgt)

    return newTrainTrgt

@router.patch('/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update(id: int, req: schemas.TrainingTargetIn, db: Session = Depends(get_db)):
    query_res = db.query(TrainingTarget).filter(TrainingTarget.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.TrainingTargetIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete(id: int, db: Session = Depends(get_db)):
    query_res = db.query(TrainingTarget).filter(TrainingTarget.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}
