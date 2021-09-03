from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import datetime
import schemas, oauth2, utils
from models import *
from database import get_db

router = APIRouter(
    tags=['Attrition'],
    prefix="/attrition"
)

# AttrType
@router.get('/type')
def get_all_attr_type(db: Session = Depends(get_db)):
    attr_types = db.query(AttrType).all()
    return attr_types

@router.post('/type', status_code=status.HTTP_201_CREATED)
def create_attr_type(req: schemas.AttrType, db: Session = Depends(get_db)):
    newAttrTyoe = AttrType(
        name = req.name
    )

    db.add(newAttrTyoe)
    db.commit()
    db.refresh(newAttrTyoe)

    return newAttrTyoe

@router.patch('/type/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_attr_type(id: int, req: schemas.AttrType, db: Session = Depends(get_db)):
    query_res = db.query(AttrType).filter(AttrType.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.AttrType(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/type/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_attr_type(id: int, db: Session = Depends(get_db)):
    query_res = db.query(AttrType).filter(AttrType.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}

# Yearly Attrition
@router.get('/yearly')
def get_all_yearly_attr(db: Session = Depends(get_db)):
    yAttr = db.query(YearlyAttrition).all()
    return yAttr

@router.get('/yearly/{id}')
def get_single_yearly_attr(id: int, db: Session = Depends(get_db)):
    query = db.query(YearlyAttrition).filter(YearlyAttrition.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Yearly Attr of ID ({id}) was not found!")

    return query

@router.post('/yearly', status_code=status.HTTP_201_CREATED)
def create_yearly_attr(req: schemas.YearlyAttrition, db: Session = Depends(get_db)):
    newYAttr = YearlyAttrition(
        year                = req.year,
        start_headcount     = req.start_headcount,
        budget_headcount    = req.budget_headcount,
        joined_count        = req.joined_count,
        resigned_count      = req.resigned_count,
        transfer_count      = req.transfer_count,
        div_id              = req.div_id
    )

    db.add(newYAttr)
    db.commit()
    db.refresh(newYAttr)

    return newYAttr

@router.patch('/yearly/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_yearly_attr(id: int, req: schemas.YearlyAttritionIn, db: Session = Depends(get_db)):
    query_res = db.query(YearlyAttrition).filter(YearlyAttrition.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.YearlyAttritionConstIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/yearly/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_yearly_attr(id: int, db: Session = Depends(get_db)):
    query_res = db.query(YearlyAttrition).filter(YearlyAttrition.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}


# Attrition
@router.get('/')
def get_all_attrition(db: Session = Depends(get_db)):
    attr = db.query(Attrition).all()
    return attr

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_attrition(req: schemas.Attrition, db: Session = Depends(get_db)):
    newAttr = Attrition(
        type_id     = req.type_id,
        staff_name  = req.staff_name,
        staff_nik   = req.staff_nik,
        date        = req.date,
        from_div_id = req.from_div_id,
        to_div_id   = req.to_div_id
    )

    db.add(newAttr)
    db.commit()
    db.refresh(newAttr)

    return newAttr

@router.patch('/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_attrition(id: int, req: schemas.AttritionIn, db: Session = Depends(get_db)):
    query_res = db.query(Attrition).filter(Attrition.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.Attrition(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_attrition(id: int, db: Session = Depends(get_db)):
    query_res = db.query(Attrition).filter(Attrition.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}
