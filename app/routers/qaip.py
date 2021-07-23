from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import schemas, oauth2
from models import *
from database import get_db

router = APIRouter(
    tags=['QAIP'],
    prefix="/qaip"
)

# QAIP Head Divs
@router.get('/headdivs')
def get_all_qaipheaddiv(db: Session = Depends(get_db)):
    qHeadDivs = db.query(QAIPHeadDiv).all()
    return qHeadDivs

@router.get('/headdivs/{id}')
def get_single_qaipheaddiv(id: int, db: Session = Depends(get_db)):
    query = db.query(QAIPHeadDiv).filter(QAIPHeadDiv.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"QAIPHeadDiv of ID ({id}) was not found!")

    return query

@router.post('/headdivs', status_code=status.HTTP_201_CREATED)
def create_qaipheaddiv(req: schemas.QAIPHeadDiv, db: Session = Depends(get_db)):
    newType = QAIPHeadDiv(
        div_head    = req.div_head,
        qaip_id     = req.qaip_id
    )

    db.add(newType)
    db.commit()
    db.refresh(newType)

    return newType

@router.patch('/headdivs/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_qaipheaddiv(id: int, req: schemas.QAIPHeadDivIn, db: Session = Depends(get_db)):
    query_res = db.query(QAIPHeadDiv).filter(QAIPHeadDiv.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.QAIPHeadDivIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/headdivs/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_qaipheaddiv(id: int, db: Session = Depends(get_db)):
    query_res = db.query(QAIPHeadDiv).filter(QAIPHeadDiv.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}

# QAIP
@router.get('/')
def get_all_qaip(db: Session = Depends(get_db)):
    qaip = db.query(QAIP).all()
    return qaip

@router.get('/{id}')
def get_single_qaip(id: int, db: Session = Depends(get_db)):
    query = db.query(QAIP).filter(QAIP.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"QAIP of ID ({id}) was not found!")

    return query

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_qaip(req: schemas.QAIP, db: Session = Depends(get_db)):
    newType = QAIP(
        qaip_type                   = req.qaip_type,
        project_name                = req.project_name,
        qa_result                   = req.qa_result,

        qaf_category_clarity        = req.qaf_category_clarity,
        qaf_category_completeness   = req.qaf_category_completeness,
        qaf_category_consistency    = req.qaf_category_consistency,
        qaf_category_others         = req.qaf_category_others,
        qaf_stage_planning          = req.qaf_stage_planning,
        qaf_stage_fieldwork         = req.qaf_stage_fieldwork,
        qaf_stage_reporting         = req.qaf_stage_reporting,
        qaf_stage_post_audit_act    = req.qaf_stage_post_audit_act,
        qaf_deliverables_1a         = req.qaf_deliverables_1a,
        qaf_deliverables_1b         = req.qaf_deliverables_1b,
        qaf_deliverables_1c         = req.qaf_deliverables_1c,
        qaf_deliverables_1d         = req.qaf_deliverables_1d,
        qaf_deliverables_1e         = req.qaf_deliverables_1e,
        qaf_deliverables_1f         = req.qaf_deliverables_1f,
        qaf_deliverables_1g         = req.qaf_deliverables_1g,
        qaf_deliverables_1h         = req.qaf_deliverables_1h,
        qaf_deliverables_1i         = req.qaf_deliverables_1i,
        qaf_deliverables_1j         = req.qaf_deliverables_1j,
        qaf_deliverables_1k         = req.qaf_deliverables_1k,
        qaf_deliverables_2          = req.qaf_deliverables_2,
        qaf_deliverables_3          = req.qaf_deliverables_3,
        qaf_deliverables_4          = req.qaf_deliverables_4,
        qaf_deliverables_5          = req.qaf_deliverables_5,
        qaf_deliverables_6          = req.qaf_deliverables_6,
        qaf_deliverables_7          = req.qaf_deliverables_7,
        issue_count                 = req.issue_count,
        qa_sample                   = req.qa_sample,

        tl_id                       = req.tl_id
    )

    db.add(newType)
    db.commit()
    db.refresh(newType)

    return newType

@router.patch('/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_qaip(id: int, req: schemas.QAIPIn, db: Session = Depends(get_db)):
    query_res = db.query(QAIP).filter(QAIP.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.QAIPIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_qaip(id: int, db: Session = Depends(get_db)):
    query_res = db.query(QAIP).filter(QAIP.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}
