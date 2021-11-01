from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import schemas, oauth2, utils
from models import *
from database import get_db

router = APIRouter(
    tags=['Projects'],
    prefix="/projects"
)

# Project Status
@router.get('/status')
def get_all_status(db: Session = Depends(get_db)):
    pStat = db.query(ProjectStatus).all()
    return pStat

@router.post('/status', status_code=status.HTTP_201_CREATED)
def create_status(req: schemas.ProjectStatus, db: Session = Depends(get_db)):
    newType = ProjectStatus(
        name    =req.name
    )

    db.add(newType)
    db.commit()
    db.refresh(newType)

    return newType

@router.put('/status/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_status(id: int, req: schemas.ProjectStatusIn, db: Session = Depends(get_db)):
    query_res = db.query(ProjectStatus).filter(ProjectStatus.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.ProjectStatusIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/status/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_status(id: int, db: Session = Depends(get_db)):
    query_res = db.query(ProjectStatus).filter(ProjectStatus.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}

# Project
@router.get('/')
def get_all_project(db: Session = Depends(get_db)):
    prjs = db.query(Project).all()
    return prjs

@router.get('/{id}')
def get_single_project(id: int, db: Session = Depends(get_db)):
    query = db.query(Project).filter(Project.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Project of ID ({id}) was not found!")

    return query

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_project(req: schemas.Project, db: Session = Depends(get_db)):
    newPrj = Project(
        name            = req.name,
        used_DA         = req.used_DA,
        completion_PA   = req.completion_PA,
        is_carried_over = req.is_carried_over,
        timely_report   = req.timely_report,
        year            = req.year,
        status_id       = req.status_id,
        div_id          = req.div_id,
        tl_id           = req.tl_id
    )

    db.add(newPrj)
    db.commit()
    db.refresh(newPrj)

    return newPrj

@router.put('/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_project(id: int, req: schemas.ProjectIn, db: Session = Depends(get_db)):
    query_res = db.query(Project).filter(Project.id == id).first()

    if not query_res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.name = req.name
    query_res.used_DA = req.used_DA
    query_res.completion_PA = req.completion_PA
    query_res.is_carried_over = req.is_carried_over
    query_res.timely_report = req.timely_report
    query_res.year = req.year
    query_res.status_id = req.status_id
    query_res.div_id = req.div_id
    

    db.commit()
    return query_res

@router.delete('/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_project(id: int, db: Session = Depends(get_db)):
    query_res = db.query(Project).filter(Project.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}
