from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import schemas, datetime
from models import *
from database import get_db

router = APIRouter(
    tags=['Profile'],
    prefix="/profile"
)

# API

@router.get('/api/header_training/{nik}/{year}')
def get_header_training(nik: int, year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    # Get Emp_id
    emp = db.query(Employee).filter(
        Employee.staff_id == str(nik)
    ).one()

    # Get Training Target
    trgt = db.query(TrainingTarget).filter(
        TrainingTarget.emp_id == emp.id,
        TrainingTarget.year == year
    ).one()

    # Get Sum of Training Days
    trainings = db.query(Training).filter(
        Training.emp_id == emp.id,
        Training.date >= startDate,
        Training.date <= endDate        
    ).all()

    sum_t_days = 0

    for t in trainings:
        sum_t_days += t.duration_days
    
    return {
        'training_done' : sum_t_days,
        'training_all'  : trgt.target_days
    }

@router.get('/api/data_chart_trainings/{nik}/{year}')
def get_header_training(nik: int, year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    # Get Emp_id
    emp = db.query(Employee).filter(
        Employee.staff_id == str(nik)
    ).one()

    # Get Training Target
    trgt = db.query(TrainingTarget).filter(
        TrainingTarget.emp_id == emp.id,
        TrainingTarget.year == year
    ).one()

    # Get Sum of Training Days
    trainings = db.query(Training).filter(
        Training.emp_id == emp.id,
        Training.date >= startDate,
        Training.date <= endDate        
    ).all()

    sum_t_days = 0

    for t in trainings:
        sum_t_days += t.duration_days
    
    return {
        'complete_title' : sum_t_days,
        'complete_data'  : trgt.target_days
    }