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

# QAIP Type
@router.get('/types')
def get_all_qa_types(db: Session = Depends(get_db)):
    qTypes = db.query(QAType).all()
    return qTypes

@router.get('/types/{id}')
def get_single_qa_type(id: int, db: Session = Depends(get_db)):
    query = db.query(QAType).filter(QAType.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"QAType of ID ({id}) was not found!")

    return query

@router.post('/types', status_code=status.HTTP_201_CREATED)
def create_qa_type(req: schemas.QAType, db: Session = Depends(get_db)):
    newType = QAType(
        name = req.name
    )

    db.add(newType)
    db.commit()
    db.refresh(newType)

    return newType

@router.put('/types/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_qa_type(id: int, req: schemas.QATypeIn, db: Session = Depends(get_db)):
    query_res = db.query(QAType).filter(QAType.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.QATypeIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/types/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_qa_type(id: int, db: Session = Depends(get_db)):
    query_res = db.query(QAType).filter(QAType.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}

# QAIP Type
@router.get('/gradingresult')
def get_all_qa_grading_results(db: Session = Depends(get_db)):
    qGradRes = db.query(QAGradingResult).all()
    return qGradRes

@router.get('/gradingresult/{id}')
def get_single_qa_grading_result(id: int, db: Session = Depends(get_db)):
    query = db.query(QAGradingResult).filter(
        QAGradingResult.id == id
    ).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"QAGradingResult of ID ({id}) was not found!")

    return query

@router.post('/gradingresult', status_code=status.HTTP_201_CREATED)
def create_qa_grading_result(req: schemas.QAGradingResult, db: Session = Depends(get_db)):
    newType = QAGradingResult(
        name = req.name
    )

    db.add(newType)
    db.commit()
    db.refresh(newType)

    return newType

@router.put('/gradingresult/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_qa_grading_result(id: int, req: schemas.QATypeIn, db: Session = Depends(get_db)):
    query_res = db.query(QAGradingResult).filter(
        QAGradingResult.id == id
    )

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.QAGradingResultIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/gradingresult/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_qa_grading_result(id: int, db: Session = Depends(get_db)):
    query_res = db.query(QAGradingResult).filter(
        QAGradingResult.id == id
    )

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
    newQA = QAIP(
        prj_id                      = req.prj_id,
        qa_type_id                  = req.qa_type_id,
        qa_grading_result_id        = req.qa_grading_result_id,

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
        qa_sample                   = req.qa_sample
    )

    db.add(newQA)
    db.commit()
    db.refresh(newQA)

    return newQA

@router.put('/{id}',  status_code=status.HTTP_202_ACCEPTED)
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
