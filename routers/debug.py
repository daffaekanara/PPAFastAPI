from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import schemas, oauth2
from models import *
from database import get_db

router = APIRouter(
    tags=["Debug"],
    prefix="/debug"
)

@router.get('/parent')
def get(db: Session = Depends(get_db)):
    parents = db.query(DebugParent).all()
    return parents

@router.post('/parent')
def create(req: schemas.DebugParent, db: Session = Depends(get_db)):
    newParent = DebugParent(
        first_name=req.first_name, 
        last_name=req.last_name
    )

    db.add(newParent)
    db.commit()
    db.refresh(newParent)

    return newParent

@router.put('/parent/{id}')
def update(id: int, req: schemas.DebugParentIn, db: Session = Depends(get_db)):
    parent = db.query(DebugParent).filter(DebugParent.id == id)

    ## TODO Fix partial data update (Update one column of a row)
    # Right now .update() will take json as info to update the database
    # but req (pydantic schemas) will assign NoneType to any unassigned field in the request


    parent.update(req.dict())
    db.commit()



# @router.get('/child')
# def get_children(db: Session = Depends(get_db)):
#     children = db.query(DebugChild).all()
#     return children

# @router.post('/child')
# def create_child(req: schemas.DebugChild, db: Session = Depends(get_db)):
#     newChild = DebugChild(
#         first_name=req.first_name, 
#         last_name=req.last_name, 
#         parent_id=req.parent_id
#     )

#     db.add(newChild)
#     db.commit()
#     db.refresh(newChild)

#     return newChild