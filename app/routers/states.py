from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import schemas, oauth2
from models import *
from database import get_db

router = APIRouter(
    tags=['Server State'],
    prefix="/state"
)

@router.get('/')
def get_all_states(db: Session = Depends(get_db)):
    state = db.query(ServerState).all()
    return state

@router.get('/{id}')
def get_single_state(id: int, db: Session = Depends(get_db)):
    query = db.query(ServerState).filter(
        ServerState.id == id
    ).first()

    if not query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Server State of ID ({id}) was not found!")

    return query

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_state(req: schemas.ServerState, db: Session = Depends(get_db)):
    newState = ServerState(
        name    = req.name,
        value   = req.value
    )

    db.add(newState)
    db.commit()
    db.refresh(newState)

    return newState

@router.patch('/{id}',  status_code=status.HTTP_202_ACCEPTED)
def update_state(id: int, req: schemas.ServerStateIn, db: Session = Depends(get_db)):
    query_res = db.query(ServerState).filter(
        ServerState.id == id
    )

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.ServerStateIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_state(id: int, db: Session = Depends(get_db)):
    query_res = db.query(ServerState).filter(
        ServerState.id == id
    )

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}
