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

# Attrition JoinResignTransfer
@router.get('/jrt')
def get_all_jrt_attrition(db: Session = Depends(get_db)):
    attr = db.query(AttritionJoinResignTransfer).all()
    return attr

@router.post('/jrt', status_code=status.HTTP_201_CREATED)
def create_jrt_attrition(req: schemas.AttritionJoinResignTransfer, db: Session = Depends(get_db)):
    newJtr = AttritionJoinResignTransfer(
        type_id     = req.type_id,

        staff_name  = req.staff_name,
        date        = req.date,
        div_id      = req.div_id
    )

    db.add(newJtr)
    db.commit()
    db.refresh(newJtr)

    return newJtr

@router.patch('/jrt/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_jrt_attrition(id: int, req: schemas.AttritionJoinResignTransferIn, db: Session = Depends(get_db)):
    query_res = db.query(AttritionJoinResignTransfer).filter(
        AttritionJoinResignTransfer.id == id
    )

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.AttritionJoinResignTransfer(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/jrt/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_jrt_attrition(id: int, db: Session = Depends(get_db)):
    query_res = db.query(AttritionJoinResignTransfer).filter(
        AttritionJoinResignTransfer.id == id
    )

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}

# Attrition Rotation
@router.get('/rotation')
def get_all_rotation_attrition(db: Session = Depends(get_db)):
    attr = db.query(AttritionRotation).all()
    return attr

@router.post('/rotation', status_code=status.HTTP_201_CREATED)
def create_rotation_attrition(req: schemas.AttritionRotation, db: Session = Depends(get_db)):
    newAttr = AttritionRotation(
        staff_name  = req.staff_name,
        date        = req.date,
        from_div_id = req.from_div_id,
        to_div_id   = req.to_div_id
    )

    db.add(newAttr)
    db.commit()
    db.refresh(newAttr)

    return newAttr

@router.patch('/rotation/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_rotation_attrition(id: int, req: schemas.AttritionRotationIn, db: Session = Depends(get_db)):
    query_res = db.query(AttritionRotation).filter(
        AttritionRotation.id == id
    )

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.AttritionRotation(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/rotation/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_rotation_attrition(id: int, db: Session = Depends(get_db)):
    query_res = db.query(AttritionRotation).filter(
        AttritionRotation.id == id
    )

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
