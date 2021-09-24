from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import datetime
import schemas, oauth2, utils
from models import *
from database import get_db

router = APIRouter(
    tags=['Historic'],
    prefix="/historic"
)


@router.get('/training')
def get_training_historic(db: Session = Depends(get_db)):
    query = db.query(TrainingHistory).all()
    return query

@router.get('/busu')
def get_busu_historic(db: Session = Depends(get_db)):
    query = db.query(BUSUHistory).all()
    return query

@router.get('/socialContrib')
def get_socContrib_historic(db: Session = Depends(get_db)):
    query = db.query(SocialContribHistory).all()
    return query

@router.get('/csf')
def get_csf_historic(db: Session = Depends(get_db)):
    query = db.query(CSFHistory).all()
    return query