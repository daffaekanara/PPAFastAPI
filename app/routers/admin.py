from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import schemas, datetime, utils
from models import *
from database import get_db

# API
router = APIRouter(
    tags=['Admin'],
    prefix="/admin"
)

# Social Contribution
@router.get('/audit_contribution_data/api/table_data/{year}')
def get_contrib_table(year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    contribs = db.query(SocialContrib).filter(
        SocialContrib.date >= startDate,
        SocialContrib.date <= endDate
    ).all()

    res = []

    for c in contribs:
        res.append({
            "id"        : str(c.id),
            "division"  : c.div.name,
            "category"  : c.social_type.name,
            "title"     : c.topic_name,
            "date"      : c.date.strftime("%m/%d/%Y")
        })

    return res

@router.post('/audit_contribution_data/api/table_data')
def create_contrib_table_entry(req: schemas.SocialContribHiCouplingIn, db: Session = Depends(get_db)):
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    types = ["Audit News", "MyUOB", "Audit Bulletin"]

    div_id = divs.index(req.division)+1

    new_con = SocialContrib(
        date            = datetime.datetime.strptime(req.date, "%m/%d/%Y"),
        topic_name      = req.title,
        div_id          = divs.index(req.division) + 1,
        social_type_id  = types.index(req.category) + 1
    )

    db.add(new_con)
    db.commit()
    db.refresh(new_con)

    return new_con

@router.patch('/audit_contribution_data/api/table_data/{id}')
def patch_contrib_table_entry(id: int,req: schemas.SocialContribHiCouplingIn, db: Session = Depends(get_db)):
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    types = ["Audit News", "MyUOB", "Audit Bulletin"]

    contrib = db.query(SocialContrib).filter(
        SocialContrib.id == id
    )

    if not contrib.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')
    
    stored_data = jsonable_encoder(contrib.first())
    stored_model = schemas.SocialContribIn(**stored_data)
    
    div_id = divs.index(req.division)+1
    social_type_id  =types.index(req.category)+1

    dataIn = schemas.SocialContribIn(
        date            = datetime.datetime.strptime(req.date, "%m/%d/%Y"),
        topic_name      = req.title,
        div_id          = div_id,
        social_type_id  = social_type_id
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    contrib.update(stored_data)
    db.commit()
    return updated

@router.delete('/audit_contribution_data/api/table_data/{id}')
def delete_contrib_table_entry(id: int, db: Session = Depends(get_db)):
    contrib = db.query(SocialContrib).filter(
        SocialContrib.id == id
    )

    if not contrib.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')
    
    contrib.delete()
    db.commit()

    return {'details': 'Deleted'}

# BUSU Engagement Table
@router.get('/busu_data/api/table_data/{year}')
def get_busu_table(year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    engs = db.query(BUSUEngagement).filter(
        BUSUEngagement.date >= startDate,
        BUSUEngagement.date <= endDate
    ).all()

    res = []
    
    for e in engs:
        res.append({
            "id"        : str(e.id),
            "division"  : e.div.name,
            "WorRM"     : e.eng_type.name,
            "activity"  : e.activity_name,
            "date"      : e.date.strftime("%m/%d/%Y")
        })
    
    return res

@router.post('/busu_data/api/table_data/')
def create_busu_table_entry(req: schemas.BUSUEngagementInHiCoupling, db: Session = Depends(get_db)):
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    eng_types = ["Regular Meeting", "Workshop"]

    div_id = divs.index(req.division)+1

    new_eng = BUSUEngagement(
        activity_name   = req.activity,
        date            = datetime.datetime.strptime(req.date, "%m/%d/%Y"),
        proof           = False,
        
        eng_type_id     = eng_types.index(req.WorRM) + 1,

        div_id          = divs.index(req.division) + 1 
    )

    db.add(new_eng)
    db.commit()
    db.refresh(new_eng)

    return new_eng

@router.patch('/busu_data/api/table_data/{id}')
def patch_busu_table_entry(id:int, req: schemas.BUSUEngagementInHiCoupling, db: Session = Depends(get_db)):
    eng = db.query(BUSUEngagement).filter(
        BUSUEngagement.id == id
    ) 

    if not eng.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(eng.first())
    stored_model = schemas.BUSUEngagementIn(**stored_data)

    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    eng_types = ["Regular Meeting", "Workshop"]
    div_id =  divs.index(req.division) + 1

    dataIn = schemas.BUSUEngagementIn(
        activity_name   = req.activity,
        date            = datetime.datetime.strptime(req.date, "%m/%d/%Y"),
        proof           = False,

        eng_type_id     = eng_types.index(req.WorRM) + 1,

        div_id          = divs.index(req.division) + 1
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    eng.update(stored_data)
    db.commit()
    return updated

@router.delete('/busu_data/api/table_data/{id}')
def delete_busu_table_entry(id:int, db: Session = Depends(get_db)):
    eng = db.query(BUSUEngagement).filter(
        BUSUEngagement.id == id
    )

    if not eng.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    eng.delete()
    db.commit()

    return {'details': 'Deleted'}

# Attrition Table
@router.get('/attrition_data/api/table_data/{year}')
def get_attr_table(year: int, db: Session = Depends(get_db)):
    attrs = db.query(YearlyAttrition).filter(
        YearlyAttrition.year == year
    )

    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    res = []

    # Init result dict
    for div in divs:
        res.append({
            "id"              : "",
            "division"        : div,
            "totalBudgetHC"   : 0,
            "totalHCNewYear"  : 0,
            "join"            : 0,
            "resign"          : 0,
            "transfer"        : 0,
            "attritionRate"   : "",
            "CurrentHC"       : 0,
        })

    for a in attrs:
        index = utils.find_index(res, "division", a.div.name)

        attr_rate = (a.resigned_count + a.transfer_count) / a.start_headcount
        attr_rate_str = str(round(attr_rate*100, 2)) + '%'

        curr_hc = a.start_headcount + a.joined_count - (a.resigned_count + a.transfer_count)

        res[index]['id']             = str(a.id)
        res[index]['totalBudgetHC']  = a.budget_headcount
        res[index]['totalHCNewYear'] = a.start_headcount
        res[index]['join']           = a.joined_count
        res[index]['resign']         = a.resigned_count
        res[index]['transfer']       = a.transfer_count
        res[index]['attritionRate']  = attr_rate_str
        res[index]['CurrentHC']      = curr_hc

    return res

@router.post('/attrition_data/api/table_data/{year}')
def create_attr_table_entry(year: int, req: schemas.YearlyAttritionInHiCoupling, db: Session = Depends(get_db)):
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]

    div_id = divs.index(req.division)+1

    new_attr = YearlyAttrition(
        year                = year,
        start_headcount     = req.totalHCNewYear,
        budget_headcount    = req.totalBudgetHC,
        joined_count        = req.join,
        resigned_count      = req.resign,
        transfer_count      = req.transfer,
        div_id              = div_id
    )

    db.add(new_attr)
    db.commit()
    db.refresh(new_attr)

    return new_attr

@router.patch('/attrition_data/api/table_data/{id}', status_code=status.HTTP_202_ACCEPTED)
def patch_attr_entry(id:int, req: schemas.YearlyAttritionInHiCoupling, db: Session = Depends(get_db)):
    attr = db.query(YearlyAttrition).filter(
        YearlyAttrition.id == id
    )

    if not attr.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(attr.first())
    stored_model = schemas.YearlyAttritionIn(**stored_data)

    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    div_id =  divs.index(req.division) + 1

    dataIn = schemas.YearlyAttritionIn(
        start_headcount = req.totalHCNewYear,
        budget_headcount= req.totalBudgetHC,
        joined_count    = req.join,
        resigned_count  = req.resign,
        transfer_count  = req.transfer,
        div_id          = div_id
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    attr.update(stored_data)
    db.commit()
    return updated

@router.delete('/attrition_data/api/table_data/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_attr_entry(id:int, db: Session = Depends(get_db)):
    attr = db.query(YearlyAttrition).filter(
        YearlyAttrition.id == id
    )

    if not attr.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    attr.delete()
    db.commit()

    return {'details': 'Deleted'}
