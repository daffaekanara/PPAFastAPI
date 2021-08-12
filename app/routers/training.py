from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import datetime
import schemas, oauth2, utils
from models import *
from database import get_db

router = APIRouter(
    tags=['Training'],
    prefix="/training"
)

# API
@router.get('/api/budget_percentange/{year}')
def get_training_budget_percentage(year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    yearlyBudgets = db.query(TrainingBudget).filter(
        TrainingBudget.year == year
    ).all()

    mandatories = db.query(Training).filter(
        Training.date >= startDate,
        Training.date <= endDate,
        Training.emp_id == 0
    ).all()

    trainings = db.query(Training).filter(
        Training.date >= startDate,
        Training.date <= endDate
    ).all()

    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA", "Mandatory/Inhouse"]

    # Init values dict
    values = []
    for d in divs:
        values.append({
            "div"       : d,
            "budget"    : 0,
            "realized"  : 0,
            "charged"   : 0
        })

    # Get Divisions Yearly Training Budget
    for y in yearlyBudgets:
        if 0 < y.div_id < 6:
            i = utils.find_index(values, "div", y.div.name)
            values[i]["budget"] = y.budget
    
    # Get Each Training's Charged and Realized
    for t in trainings:
        if t.emp_id == 0: # Mandatory (Not specific to a employee)
            values[5]["budget"]     += t.budget
            values[5]["realized"]   += t.realization
            values[5]["charged"]    += t.charged_by_fin
        else:
            if 1 <= t.employee.div_id <= 5: # Not Including IAH
                i = utils.find_index(values, "div", t.employee.part_of_div.name)
                values[i]["realized"]   += t.realization
                values[i]["charged"]    += t.charged_by_fin

    # Translate to Percentage
    res = []
    for d in divs:
        res.append({
            "budget"            : 0,
            "cost_realization"  : 0,
            "charged_by_finance": 0,
            "divisions_and_mandatory": d
        })
    
    for i, r in enumerate(res):
        cost_realized   = values[i]["realized"] / values[i]["budget"] * 100 if values[i]["budget"] != 0 else 0
        charged         = values[i]["charged"] / values[i]["budget"] * 100 if values[i]["budget"] != 0 else 0
        
        res[i]["budget"]             = 100.0
        res[i]["cost_realization"]   = round(cost_realized, 2)
        res[i]["charged_by_finance"] = round(charged, 2)
        
    return res

@router.get('/api/progress_percentange/{year}')
def get_training_progress_percentage(year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    targets = db.query(TrainingTarget).filter(
        TrainingTarget.year == year
    ).all()

    trainings = db.query(Training).filter(
        Training.date >= startDate,
        Training.date <= endDate,
        Training.emp_id > 0
    ).all()

    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA", "IAH"]

    # Init values dict
    values = []
    for d in divs:
        values.append({
            "div"           : d,
            "target_hours"   : 0,
            "curr_hours"     : 0
        })
    
    # Get Targets
    for t in targets:
        i = utils.find_index(values, "div", t.trainee.part_of_div.name)
        values[i]["target_hours"] += t.target_hours

    # Get Currs
    for t in trainings:
        i = utils.find_index(values, "div", t.employee.part_of_div.name)
        values[i]["curr_hours"] += t.duration_hours
    
    # Translate to Percentage
    res = []
    for d in divs:
        res.append({
            "percentage" : 0,
            "divisions": d
        })
    
    for i, r in enumerate(res):
        if values[i]["target_hours"] == 0:
            res[i]["percentage"]   = 0.0
        else:
            pctg = values[i]["curr_hours"] / values[i]["target_hours"] * 100
            res[i]["percentage"]   = round(pctg, 2)
        

    return res

@router.post('/api/form', status_code=status.HTTP_201_CREATED)
def create_training_from_form(req: schemas.TrainingInHiCouplingForm, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(
        Employee.staff_id == req.nik
    )

    if not emp.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Employee of NIK ({req.nik}) was not found!")

    emp_id = emp.first().id
    
    newTrain = Training(
        name            = req.name, 
        date            = utils.str_to_datetime(req.date), 
        duration_hours  = req.duration_hours, 
        proof           = req.proof,
        budget          = 0,
        realization     = 0,
        charged_by_fin  = 0,
        remark          = req.remarks,
        mandatory_from  = "",
        emp_id          = emp_id
    )
    
    db.add(newTrain)
    db.commit()
    db.refresh(newTrain)
    return newTrain

# Training Target
@router.get('/target')
def get_all(db: Session = Depends(get_db)):
    trainingTrgts = db.query(TrainingTarget).all()
    return trainingTrgts

@router.get('/target/{id}')
def get_single(id: int, db: Session = Depends(get_db)):
    query = db.query(TrainingTarget).filter(TrainingTarget.id == id).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Training Target of ID ({id}) was not found!")

    return query

@router.post('/target', status_code=status.HTTP_201_CREATED)
def create(req: schemas.TrainingTarget, db: Session = Depends(get_db)):
    newTrainTrgt = TrainingTarget(
        year        = req.year,
        target_hours= req.target_hours,
        emp_id      = req.emp_id
    )

    db.add(newTrainTrgt)
    db.commit()
    db.refresh(newTrainTrgt)

    return newTrainTrgt

@router.patch('/target/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update(id: int, req: schemas.TrainingTargetIn, db: Session = Depends(get_db)):
    query_res = db.query(TrainingTarget).filter(TrainingTarget.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.TrainingTargetIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/target/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete(id: int, db: Session = Depends(get_db)):
    query_res = db.query(TrainingTarget).filter(TrainingTarget.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}

# Training Budget
@router.get('/budget')
def get_all(db: Session = Depends(get_db)):
    budgets = db.query(TrainingBudget).all()
    return budgets

@router.get('/budget/{budget_id}', response_model=schemas.ShowTraining)
def get_single(budget_id: int, db: Session = Depends(get_db)):
    budget = db.query(TrainingBudget).filter(TrainingBudget.id == budget_id).first()

    if not budget:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"TrainingBudget of ID ({id}) was not found!")

    return budget

@router.post('/budget', status_code=status.HTTP_201_CREATED)
def create(req: schemas.TrainingBudget, db: Session = Depends(get_db)):
    newTrainBdgt = TrainingBudget(
        year    = req.year,
        budget  = req.budget,
        div_id  = req.div_id
    )
    
    db.add(newTrainBdgt)
    db.commit()
    db.refresh(newTrainBdgt)
    return newTrainBdgt

@router.patch('/budget/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_training_budget(id: int, req: schemas.TrainingBudgetIn, db: Session = Depends(get_db)):
    query_res = db.query(TrainingBudget).filter(TrainingBudget.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.TrainingBudgetIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/budget/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_training_budget(id: int, db: Session = Depends(get_db)):
    query_res = db.query(TrainingBudget).filter(TrainingBudget.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}

#### Endpoints #####
@router.get('/by_div/{div_id}', response_model=List[schemas.ShowTraining])
def get_trainings_by_division(div_id: int, db: Session = Depends(get_db)):
    emps = db.query(Employee).filter(Employee.div_id == div_id).all()

    emps_ids = [x.id for x in emps]

    # trainings = db.query(Training).filter

    query = db.query(Training)
    query = query.filter(Training.emp_id.in_(emps_ids))
    res = query.all()

    return res

# Training
@router.get('/')
def get_all(db: Session = Depends(get_db)):
    trainings = db.query(Training).all()
    return trainings

@router.get('/{training_id}', response_model=schemas.ShowTraining)
def get_single(training_id: int, db: Session = Depends(get_db)):
    training = db.query(Training).filter(Training.id == training_id).first()

    if not training:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Training of ID ({id}) was not found!")

    return training

@router.post('/', status_code=status.HTTP_201_CREATED)
def create(req: schemas.Training, db: Session = Depends(get_db)):
    newTrain = Training(
        name            = req.name, 
        date            = req.date, 
        duration_hours  = req.duration_hours, 
        proof           = req.proof,
        budget          = req.budget,
        realization     = req.realization,
        charged_by_fin  = req.charged_by_fin,
        remark          = req.remark,
        mandatory_from  = req.mandatory_from,
        emp_id=req.emp_id
    )
    
    db.add(newTrain)
    db.commit()
    db.refresh(newTrain)
    return newTrain

@router.patch('/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_training(id: int, req: schemas.TrainingIn, db: Session = Depends(get_db)):
    query_res = db.query(Training).filter(Training.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.TrainingIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_training(id: int, db: Session = Depends(get_db)):
    query_res = db.query(Training).filter(Training.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}
