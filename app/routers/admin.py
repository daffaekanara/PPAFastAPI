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

@router.patch('/attrition_data/api/table_data', status_code=status.HTTP_202_ACCEPTED)
def patch_attr_entry(req: schemas.YearlyAttritionInHiCoupling, db: Session = Depends(get_db)):
    attr = db.query(YearlyAttrition).filter(
        YearlyAttrition.id == int(req.id)
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

@router.delete('/attrition_data/api/table_data', status_code=status.HTTP_202_ACCEPTED)
def delete_attr_entry(req: schemas.YearlyAttritionInHiCoupling, db: Session = Depends(get_db)):
    attr = db.query(YearlyAttrition).filter(
        YearlyAttrition.id == int(req.id)
    )

    if not attr.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    attr.delete()
    db.commit()

    return {'details': 'Deleted'}
