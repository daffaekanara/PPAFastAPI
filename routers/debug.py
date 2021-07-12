from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import schemas, oauth2
from models import *
from database import get_db

router = APIRouter(
    tags=["Debug"],
    prefix="/debug"
)

@router.get('/parent')
def get(db: Session = Depends(get_db)):
    parents = db.query(DebugParent).all()
    return parents

@router.post('/parent')
def create(req: schemas.DebugParent, db: Session = Depends(get_db)):
    newParent = DebugParent(
        first_name=req.first_name, 
        last_name=req.last_name
    )

    db.add(newParent)
    db.commit()
    db.refresh(newParent)

    return newParent

@router.patch('parent/{id}', status_code=status.HTTP_202_ACCEPTED)
def patch(id: int, req: schemas.DebugParentIn, db: Session = Depends(get_db)):
    query_res = db.query(DebugParent).filter(DebugParent.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.DebugParentIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated