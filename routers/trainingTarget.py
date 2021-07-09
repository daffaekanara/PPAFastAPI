from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
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

@router.post('/', status_code=status.HTTP_201_CREATED)
def create(req: schemas.TrainingTarget, db: Session = Depends(get_db)):
    newTrainTrgt = TrainingTarget(
        year        =req.year,
        target_days =req.target_days,
        emp_id      =req.emp_id
    )

    db.add(newTrainTrgt)
    db.commit()
    db.refresh(newTrainTrgt)

    return newTrainTrgt