from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, oauth2
from database import get_db

router = APIRouter(
    tags=['Training'],
    prefix="/training"
)

@router.get('/{training_id}', response_model=schemas.ShowTraining)
def get_single(training_id: int, db: Session = Depends(get_db)):
    training = db.query(models.Training).filter(models.Training.id == training_id).first()

    if not training:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Training of ID ({id}) was not found!")

    return training

@router.post('/', status_code=status.HTTP_201_CREATED)
def create(req: schemas.Training, db: Session = Depends(get_db)):
    new_train = models.Training(name=req.name, 
                                date=req.date, 
                                duration_days=req.duration_days, 
                                proof=req.proof, 
                                emp_id=req.emp_id
                                )
    db.add(new_train)
    db.commit()
    db.refresh(new_train)
    return new_train