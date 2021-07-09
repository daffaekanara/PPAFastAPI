from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, oauth2
from database import get_db

router = APIRouter(
    tags=['Division'],
    prefix="/division"
)

@router.get('/')
def get_all_divisions(db: Session = Depends(get_db)):
    divs = db.query(models.Division).all()
    return divs

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_division(req: schemas.Division, db: Session = Depends(get_db)):
    new_div = models.Division(name=req.name)
    db.add(new_div)
    db.commit()
    db.refresh(new_div)
    return new_div

@router.get('/{id}', status_code=status.HTTP_200_OK)
def get_single_division(id: int, db: Session = Depends(get_db)):

    div = db.query(models.Division).filter(models.Division.id == id).first()
    # div = db.query(models.Division).filter_by(id= id).first()

    if not div:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Division of ID ({id}) was not found!")

    return div

# TODO 
# [ ] Delete will return 200 even when ID is not found
@router.delete('/{id}')
def delete_division(id: int, db: Session = Depends(get_db), currUser = Depends(oauth2.get_current_user)):
    div = db.query(models.Division).filter(models.Division.id == id)

    if not div:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Division of ID ({id}) was not found!")
    
    div.delete(synchronize_session=False)
    db.commit()

@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update_division_name(id: int, req: schemas.Division , db: Session = Depends(get_db)):

    div = db.query(models.Division).filter(models.Division.id == id).first()

    if not div:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Division of ID ({id}) was not found!")

    # div.update({'name': req.name})
    div.name = req.name

    db.commit()
