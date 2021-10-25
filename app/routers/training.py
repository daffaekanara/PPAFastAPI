from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.exc import MultipleResultsFound, NoResultFound 
import datetime
import schemas, oauth2, utils
from models import *
from database import get_db

router = APIRouter(
    tags=['Training'],
    prefix="/training"
)
# Training Announcement
@router.get('/announcement')
def get_all(db: Session = Depends(get_db)):
    annoucements = db.query(Annoucement).filter(
        Annoucement.type_name == "Training"
    ).all()
    return annoucements

@router.get('/announcement/{id}')
def get_single(id: int, db: Session = Depends(get_db)):
    query = db.query(Annoucement).filter(
        Annoucement.id == id
    ).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Annoucement of ID ({id}) was not found!")

    return query

@router.post('/announcement', status_code=status.HTTP_201_CREATED)
def create(req: schemas.AnnouncementCreate, db: Session = Depends(get_db)):
    newAnnoucement = Annoucement(
        type_name   = "Training",
        body        = req.body
    )

    db.add(newAnnoucement)
    db.commit()
    db.refresh(newAnnoucement)

    return newAnnoucement

@router.put('/announcement/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update(id: int, req: schemas.AnnouncementCreate, db: Session = Depends(get_db)):
    query_res = db.query(Annoucement).filter(
        Annoucement.id == id
    )

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.AnnouncementCreate(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/announcement/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete(id: int, db: Session = Depends(get_db)):
    query_res = db.query(Annoucement).filter(
        Annoucement.id == id
    )

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}


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

@router.put('/target/{id}',  status_code=status.HTTP_202_ACCEPTED)
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

@router.put('/budget/{id}',  status_code=status.HTTP_202_ACCEPTED)
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

@router.put('/{id}',  status_code=status.HTTP_202_ACCEPTED)
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
