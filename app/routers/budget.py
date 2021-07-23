from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import schemas, oauth2
from models import *
from database import get_db

router = APIRouter(
    tags=['Budgets'],
    prefix="/budget"
)

# Monthly Actual Budget
@router.get('/monthlyactual')
def get_all_monthly_actual_budget(db: Session = Depends(get_db)):
    eType = db.query(MonthlyActualBudget).all()
    return eType

@router.get('/monthlyactual/{id}')
def get_single_monthly_actual_budget(id: int, db: Session = Depends(get_db)):
    query = db.query(MonthlyActualBudget).filter(MonthlyActualBudget.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"MonthlyActualBudget of ID ({id}) was not found!")

    return query

@router.post('/monthlyactual', status_code=status.HTTP_201_CREATED)
def create_monthly_actual_budget(req: schemas.MonthlyActualBudget, db: Session = Depends(get_db)):
    newMonthActualBudget = MonthlyActualBudget(
        year                        = req.year,
        month                       = req.month,
        staff_salaries              = req.staff_salaries,
        staff_training_reg_meeting  = req.staff_training_reg_meeting,
        revenue_related             = req.revenue_related,
        it_related                  = req.it_related,
        occupancy_related           = req.occupancy_related,
        other_transport_travel      = req.other_transport_travel,
        other_other                 = req.other_other,
        indirect_expense            = req.indirect_expense
    )

    db.add(newMonthActualBudget)
    db.commit()
    db.refresh(newMonthActualBudget)

    return newMonthActualBudget

@router.patch('/monthlyactual/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_monthly_actual_budget(id: int, req: schemas.MonthlyActualBudgetIn, db: Session = Depends(get_db)):
    query_res = db.query(MonthlyActualBudget).filter(MonthlyActualBudget.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.MonthlyActualBudgetIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/monthlyactual/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_monthly_actual_budget(id: int, db: Session = Depends(get_db)):
    query_res = db.query(MonthlyActualBudget).filter(MonthlyActualBudget.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}

# Monthly Budget
@router.get('/monthly')
def get_all_monthly_budget(db: Session = Depends(get_db)):
    eType = db.query(MonthlyBudget).all()
    return eType

@router.get('/monthly/{id}')
def get_single_monthly_budget(id: int, db: Session = Depends(get_db)):
    query = db.query(MonthlyBudget).filter(MonthlyBudget.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"MonthlyBudget of ID ({id}) was not found!")

    return query

@router.post('/monthly', status_code=status.HTTP_201_CREATED)
def create_monthly_budget(req: schemas.MonthlyBudget, db: Session = Depends(get_db)):
    newMonthBudget = MonthlyBudget(
        year                        = req.year,
        month                       = req.month,
        staff_salaries              = req.staff_salaries,
        staff_training_reg_meeting  = req.staff_training_reg_meeting,
        revenue_related             = req.revenue_related,
        it_related                  = req.it_related,
        occupancy_related           = req.occupancy_related,
        other_transport_travel      = req.other_transport_travel,
        other_other                 = req.other_other,
        indirect_expense            = req.indirect_expense
    )

    db.add(newMonthBudget)
    db.commit()
    db.refresh(newMonthBudget)

    return newMonthBudget

@router.patch('/monthly/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_monthly_budget(id: int, req: schemas.MonthlyBudgetIn, db: Session = Depends(get_db)):
    query_res = db.query(MonthlyBudget).filter(MonthlyBudget.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.MonthlyBudgetIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/monthly/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_monthly_budget(id: int, db: Session = Depends(get_db)):
    query_res = db.query(MonthlyBudget).filter(MonthlyBudget.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}
