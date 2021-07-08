from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, oauth2
from database import get_db

router = APIRouter(
    tags=['Training Target'],
    prefix="/trainingtarget"
)

@router.get('/')
def get_single(trainTrgt_id: int, db: Session = Depends(get_db)):
    trainingTrgts = db.query(models.TrainingTarget).all()
    return trainingTrgts