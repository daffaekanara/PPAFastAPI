from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import schemas, database, models, hashing, JWTtoken

router = APIRouter(
    tags=["Authentication"]
)

@router.post('/login')
# def login(req: schemas.Login, db: Session = Depends(database.get_db)):
def login(req: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.Employee).filter(models.Employee.email == req.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Email not found!")

    if not hashing.verify_bcrypt(user.pw, req.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incorrect password")

    # Generate JWT Token
    access_token = JWTtoken.create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token-type": "bearer"}

@router.post('/auth')
def temp_login(req: schemas.TempLoginForm, db: Session = Depends(database.get_db)):
    user = db.query(models.Employee).filter(
        models.Employee.email == req.email
    ).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Email not found!")

    if not hashing.verify_bcrypt(user.pw, req.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incorrect password")

    return {
        'token': user.role.name
    }