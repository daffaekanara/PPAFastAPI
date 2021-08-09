from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import schemas, oauth2
import utils
from models import *
from database import get_db

router = APIRouter(
    tags=['CSF'],
    prefix="/csf"
)

# API
@router.get('/api/client_survey/{year}')
def get_csf_bar_chart_data(year: int, db: Session = Depends(get_db)):
    divs    = ["WBGM", "RBA", "BRDS", "TAD"]
    
    # Get All CSF where Project's year is {year}
    csfs = db.query(CSF).filter(
        CSF.prj.has(year=year)
    ).all()

    # Init result dict
    res = []
    for d in divs:
        res.append({
            "division"      : d, 
            "by_division"   : 0, 
            "by_project"    : 0
        })

    # Calc byProject Score
    for d in divs:
        prj_ids = []
        list_of_prj_scores = []

        # Find Unique Project IDs of a div
        for c in csfs:
            if c.prj.div.name == d:
                if c.prj_id not in prj_ids:
                    prj_ids.append(c.prj_id)

        # Calc each project overall score
        for prj_id in prj_ids:
            list_of_csf_scores = []
            
            # Get project's feedback scores
            for c in csfs:
                if c.prj_id == prj_id:
                    score = utils.calc_single_csf_score(c)
                    list_of_csf_scores.append(score)
            
            # Project Overall Score
            if list_of_csf_scores:
                score = sum(list_of_csf_scores) / len(list_of_csf_scores)
                list_of_prj_scores.append(round(score,2))

        if list_of_prj_scores:
            score = sum(list_of_prj_scores) / len(list_of_prj_scores)

            index = utils.find_index(res, "division", d)
            res[index]["by_project"] = round(score, 2)
  
    # Calc byInvDiv Score
    for d in divs:
        prj_ids = []
        list_of_prj_scores = []

        # Find Unique Project IDs of a div
        for c in csfs:
            if c.by_invdiv_div.name == d:
                if c.prj_id not in prj_ids:
                    prj_ids.append(c.prj_id)

        # Calc each project overall score
        for prj_id in prj_ids:
            list_of_csf_scores = []
            
            # Get project's feedback scores
            for c in csfs:
                if c.prj_id == prj_id and c.by_invdiv_div.name == d:
                    score = utils.calc_single_csf_score(c)
                    list_of_csf_scores.append(score)
            
            # Project Overall Score
            if list_of_csf_scores:
                score = sum(list_of_csf_scores) / len(list_of_csf_scores)
                list_of_prj_scores.append(round(score,2))

        if list_of_prj_scores:
            score = sum(list_of_prj_scores) / len(list_of_prj_scores)

            index = utils.find_index(res, "division", d)
            res[index]["by_division"] = round(score, 2)

    return res

@router.get('/api/overall_csf/{year}')
def get_csf_donut_data(year: int, db: Session = Depends(get_db)):
    divs    = ["WBGM", "RBA", "BRDS", "TAD"]
    
    # Get All CSF where Project's year is {year}
    csfs = db.query(CSF).filter(
        CSF.prj.has(year=year)
    ).all()

    scores = []

    # Calc byInvDiv Score
    for d in divs:
        prj_ids = []
        list_of_prj_scores = []

        # Find Unique Project IDs of a div
        for c in csfs:
            if c.by_invdiv_div.name == d:
                if c.prj_id not in prj_ids:
                    prj_ids.append(c.prj_id)

        # Calc each project overall score
        for prj_id in prj_ids:
            list_of_csf_scores = []
            
            # Get project's feedback scores
            for c in csfs:
                if c.prj_id == prj_id and c.by_invdiv_div.name == d:
                    score = utils.calc_single_csf_score(c)
                    list_of_csf_scores.append(score)
            
            # Project Overall Score
            if list_of_csf_scores:
                score = sum(list_of_csf_scores) / len(list_of_csf_scores)
                list_of_prj_scores.append(round(score,2))

        if list_of_prj_scores:
            score = sum(list_of_prj_scores) / len(list_of_prj_scores)
            scores.append(round(score, 2))
        else:
            scores.append(0)
  
    avg = sum(scores) / len(scores)

    res = [
        {
            "title" : "score",
	        "rate"  : round(avg, 2)
        },
        {
            "title" : "",
	        "rate"  : round(4-avg, 2)
        }
    ]

    return res
# CSF
@router.get('/')
def get_all(db: Session = Depends(get_db)):
    csf = db.query(CSF).all()
    return csf

@router.get('/{id}')
def get_single(id: int, db: Session = Depends(get_db)):
    query = db.query(CSF).filter(CSF.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"CSF of ID ({id}) was not found!")

    return query

@router.post('/', status_code=status.HTTP_201_CREATED)
def create(req: schemas.CSF, db: Session = Depends(get_db)):
    newType = CSF(
        client_name         = req.client_name,
        client_unit         = req.client_unit,
        csf_date            = req.csf_date,
        atp_1               = req.atp_1,
        atp_2               = req.atp_2,
        atp_3               = req.atp_3,
        atp_4               = req.atp_4,
        atp_5               = req.atp_5,
        atp_6               = req.atp_6,
        ac_1                = req.ac_1,
        ac_2                = req.ac_2,
        ac_3                = req.ac_3,
        ac_4                = req.ac_4,
        ac_5                = req.ac_5,
        ac_6                = req.ac_6,
        paw_1               = req.paw_1,
        paw_2               = req.paw_2,
        paw_3               = req.paw_3,

        prj_id              = req.prj_id,
        tl_id               = req.tl_id,
        by_invdiv_div_id    = req.by_invdiv_div_id
    )

    db.add(newType)
    db.commit()
    db.refresh(newType)

    return newType

@router.patch('/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update(id: int, req: schemas.CSFIn, db: Session = Depends(get_db)):
    query_res = db.query(CSF).filter(CSF.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.CSFIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete(id: int, db: Session = Depends(get_db)):
    query_res = db.query(CSF).filter(CSF.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}
