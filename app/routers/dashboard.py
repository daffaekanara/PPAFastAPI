from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import datetime
import schemas, utils
from models import *
from database import get_db

router = APIRouter(
    tags=['Dashboard'],
    prefix="/dashboard"
)

gen_x_youngest = datetime.date(1980,12,31)
gen_y_youngest = datetime.date(1996,12,31)


# API
@router.get('/api/age_group/')
def get_header_training(db: Session = Depends(get_db)):
    # Get All Emps
    emps = db.query(Employee).all()

    gens = ["Gen-X", "Gen-Y", "Gen-Z"]
    res = []

    # Init result dict
    for gen in gens:
        res.append({
            "male_sum"  : 0,
            "female_sum": 0,
            "gen_name"  : gen
        })
    
    for e in emps:
        if e.date_of_birth <= gen_x_youngest: # Gen X
            if e.gender == 'M':
                res[0]['male_sum'] += 1
            elif e.gender == 'F':
                res[0]['female_sum'] += 1
        elif e.date_of_birth <= gen_y_youngest: # Gen Y
            if e.gender == 'M':
                res[1]['male_sum'] += 1
            elif e.gender == 'F':
                res[1]['female_sum'] += 1
        else:
            if e.gender == 'M':
                res[2]['male_sum'] += 1
            elif e.gender == 'F':
                res[2]['female_sum'] += 1

    return res