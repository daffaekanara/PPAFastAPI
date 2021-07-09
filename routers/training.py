from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import schemas, oauth2
from models import *
from database import get_db

router = APIRouter(
    tags=['Training'],
    prefix="/training"
)

@router.get('/')
def get_all(db: Session = Depends(get_db)):
    trainings = db.query(Training).all()
    return trainings

@router.get('/{training_id}', response_model=schemas.ShowTraining)
def get_single(training_id: int, db: Session = Depends(get_db)):
    training = db.query(Training).filter(Training.id == training_id).first()

    if not training:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Training of ID ({id}) was not found!")

    return training

@router.post('/', status_code=status.HTTP_201_CREATED)
def create(req: schemas.Training, db: Session = Depends(get_db)):
    new_train = Training(
        name=req.name, 
        date=req.date, 
        duration_days=req.duration_days, 
        proof=req.proof, 
        emp_id=req.emp_id
    )
    
    db.add(new_train)
    db.commit()
    db.refresh(new_train)
    return new_train

@router.get('/by_div/{div_id}', response_model=List[schemas.ShowTraining])
def get_trainings_by_division(div_id: int, db: Session = Depends(get_db)):
    emps = db.query(Employee).filter(Employee.div_id == div_id).all()

    emps_ids = [x.id for x in emps]

    # trainings = db.query(Training).filter

    query = db.query(Training)
    query = query.filter(Training.emp_id.in_(emps_ids))
    res = query.all()

    return res

@router.patch('/{training_id}',  status_code=status.HTTP_202_ACCEPTED)
def update_training(training_id: int, req: schemas.Training, db: Session = Depends(get_db)):
    training_item = db.query(Training).filter(Training.id == training_id)

    if not training_item.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Not Found')

    training_item.update(req.dict())
    db.commit()
    return "Updated"

