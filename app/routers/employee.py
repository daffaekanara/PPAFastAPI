from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import schemas, hashing
from models import *
from database import get_db
from fileio import fileio_module as fio

router = APIRouter(
    tags=['Employee'],
    prefix="/employee"
)

# Roles
@router.get('/role')
def get_all_role(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return roles

@router.get('/role/{id}')
def get_single_role(id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(
        Role.id == id
    ).first()

    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Role of ID ({id}) was not found!")

    return role

@router.post('/role', status_code=status.HTTP_201_CREATED)
def create_role(req: schemas.Role, db: Session = Depends(get_db)):
    newRole = Role(
        name = req.name
    )

    db.add(newRole)
    db.commit()
    db.refresh(newRole)

    return newRole

@router.put('/role/{id}', status_code=status.HTTP_202_ACCEPTED)
def update_role(id: int, req: schemas.RoleIn, db: Session = Depends(get_db)):
    query_res = db.query(Role).filter(Role.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.RoleIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/role/{id}')
def delete_role(id: int, db: Session = Depends(get_db)):
    query_res = db.query(Role).filter(Role.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}

# Certification
@router.get('/cert')
def get_all_cert(db: Session = Depends(get_db)):
    certs = db.query(Certification).all()
    return certs

@router.get('/cert/{id}') #response_model=schemas.ShowEmployee
def get_single_cert(id: int, db: Session = Depends(get_db)):
    cert = db.query(Certification).filter(Certification.id == id).first()

    if not cert:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Certification of ID ({id}) was not found!")

    return cert

@router.post('/cert', status_code=status.HTTP_201_CREATED)
def create_cert(req: schemas.Certification, db: Session = Depends(get_db)):
    newCert = Certification(
        cert_name   = req.cert_name,
        cert_proof  = req.cert_proof,
        emp_id      = req.emp_id
    )

    db.add(newCert)
    db.commit()
    db.refresh(newCert)

    return newCert

@router.put('/cert/{id}', status_code=status.HTTP_202_ACCEPTED)
def update_cert(id: int, req: schemas.CertificationIn, db: Session = Depends(get_db)):
    query_res = db.query(Certification).filter(Certification.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.CertificationIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/cert/cert_proof')
def delete_cert_proof(db: Session = Depends(get_db)):
    certs = db.query(Certification).all()

    for c in certs:
        query = db.query(Certification).filter(
            Certification.id == c.id
        )
        stored_data = jsonable_encoder(query.first())
        stored_model = schemas.CertificationIn(**stored_data)
        new_data = {"cert_proof": ""}
        updated = stored_model.copy(update=new_data)
        stored_data.update(updated)
        query.update(stored_data)
        db.commit()
    
    fio.delete_cert_files_dir()

    return {'details': 'All cert_proof deleted'}

@router.delete('/cert/{id}')
def delete_cert(id: int, db: Session = Depends(get_db)):
    query_res = db.query(Certification).filter(Certification.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}

# Employee
@router.get('/')
def get_all(db: Session = Depends(get_db)):
    emps = db.query(Employee).all()
    return emps

@router.get('/{id}') #response_model=schemas.ShowEmployee
def get_single(id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == id).first()

    if not emp:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Employee of ID ({id}) was not found!")

    return emp

@router.post('/', status_code=status.HTTP_201_CREATED)
def create(req: schemas.Employee, db: Session = Depends(get_db)):
    hashed = hashing.bcrypt(req.pw)

    newEmp = Employee(
        name                    = req.name, 
        email                   = req.email, 
        pw                      = hashed,
        staff_id                = req.staff_id,
        div_stream              = req.div_stream,
        corporate_title         = req.corporate_title,
        corporate_grade         = req.corporate_grade,
        date_of_birth           = req.date_of_birth,
        date_first_employment   = req.date_first_employment,
        date_first_uob          = req.date_first_uob,
        date_first_ia           = req.date_first_ia,
        gender                  = req.gender,
        year_audit_non_uob      = req.year_audit_non_uob,
        edu_level               = req.edu_level,
        edu_major               = req.edu_major,
        edu_category            = req.edu_category,
        ia_background           = req.ia_background,
        ea_background           = req.ea_background,
        active                  = req.active,
        div_id                  = req.div_id,
        role_id                 = req.role_id
    )

    db.add(newEmp)
    db.commit()
    db.refresh(newEmp)

    return newEmp

@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id: int, req: schemas.EmployeeIn, db: Session = Depends(get_db)):
    query_res = db.query(Employee).filter(Employee.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    stored_data = jsonable_encoder(query_res.first())
    stored_model = schemas.EmployeeIn(**stored_data)

    new_data = req.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    query_res.update(stored_data)
    db.commit()
    return updated

@router.delete('/{id}')
def delete_employee(id: int, db: Session = Depends(get_db)):
    query_res = db.query(Employee).filter(Employee.id == id)

    if not query_res.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')

    query_res.delete()
    db.commit()

    return {'details': 'Deleted'}
