from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import datetime
import schemas, utils
from models import *
from database import get_db

router = APIRouter(
    tags=['Profile'],
    prefix="/profile"
)

# API
@router.get('/profile/about/api/table_data/{nik}')
def get_employee_table(nik: str, db: Session = Depends(get_db)):
    e = db.query(Employee).filter(
        Employee.staff_id == nik
    ).first()

    if not e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Employee of NIK ({nik}) was not found!")

    res = []

    as_of_now       = datetime.date.today().strftime("%m/%d/%Y")
    age             = utils.get_year_diff_to_now(e.date_of_birth)
    gen             = utils.get_gen(e.date_of_birth)
    auditUOBYears   = utils.get_year_diff_to_now(e.date_first_uob)

    # Process Certs
    certs = [
        "SMR", "CISA", "CEH", "ISO", "CHFI", 
        "IDEA", "QualifiedIA", "CBIA", "CIA", "CPA", "CA", "Others"]

    cert_res = []

    for c in certs:
        cert_res.append({
            'title': c,
            'value': 0
        })

    for c in e.emp_certifications:
        # SMR (Levels)
        smr_level = utils.extract_SMR_level(c.cert_name)
        
        if smr_level: # SMR
            cert_res[0]['value'] = smr_level
        elif c.cert_name in certs:
            index = utils.find_index(cert_res, 'title', c.cert_name)
            cert_res[index]['value'] = 1
        else:
            cert_res[-1]["value"] += 1

    smr_lvl = cert_res[0]['value']
    smr_str = f"Level {smr_lvl}" if smr_lvl else "-"

    res.append({
        "id"                          : e.id,
        "staffNIK"                    : e.staff_id,
        "staffName"                   : e.name,
        "email"                       : e.email,
        "role"                        : e.role.name,
        "divison"                     : e.part_of_div.name,
        "stream"                      : e.div_stream,
        "corporateTitle"              : e.corporate_title,
        "corporateGrade"              : e.corporate_grade,
        "dateOfBirth"                 : e.date_of_birth.strftime("%m/%d/%Y"),
        "dateStartFirstEmployment"    : e.date_first_employment.strftime("%m/%d/%Y"),
        "dateJoinUOB"                 : e.date_first_uob.strftime("%m/%d/%Y"),
        "dateJoinIAFunction"          : e.date_first_ia.strftime("%m/%d/%Y"),
        "asOfNow"                     : as_of_now,
        "age"                         : age,
        "gen"                         : gen,
        "gender"                      : e.gender,
        "auditUOBExp"                 : auditUOBYears,
        "auditNonUOBExp"              : e.year_audit_non_uob,
        "totalAuditExp"               : e.year_audit_non_uob + auditUOBYears,
        "educationLevel"              : e.edu_level,
        "educationMajor"              : e.edu_major,
        "educationCategory"           : e.edu_category,
        "RMGCertification"            : smr_str,
        "CISA"                        : cert_res[1]['value'],
        "CEH"                         : cert_res[2]['value'],
        "ISO"                         : cert_res[3]['value'],
        "CHFI"                        : cert_res[4]['value'],
        "IDEA"                        : cert_res[5]['value'],
        "QualifiedIA"                 : cert_res[6]['value'],
        "CBIA"                        : cert_res[7]['value'],
        "CIA"                         : cert_res[8]['value'],
        "CPA"                         : cert_res[9]['value'],
        "CA"                          : cert_res[10]['value'],
        "IABackgground"               : e.ia_background,
        "EABackground"                : e.ea_background,
        "active"                      : e.active
    })

    return res

@router.patch('/profile/about/api/table_data/{nik}')
def patch_employee_table_entry(nik: str, req: schemas.EmployeeInHiCoupling, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(
        Employee.staff_id == nik
    )

    if not emp.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ID not found')
    
    stored_data = jsonable_encoder(emp.first())
    stored_model = schemas.EmployeeIn(**stored_data)

    dataIn = schemas.Employee(
        name    = req.staffName,
        email   = req.email,
        pw      = emp.first().pw,

        staff_id                = req.staffNIK,
        div_stream              = req.stream,
        corporate_title         = req.corporateTitle,
        corporate_grade         = req.corporateGrade,
        date_of_birth           = utils.str_to_datetime(req.dateOfBirth),
        date_first_employment   = utils.str_to_datetime(req.dateStartFirstEmployment),
        date_first_uob          = utils.str_to_datetime(req.dateJoinUOB),
        date_first_ia           = utils.str_to_datetime(req.dateJoinIAFunction),
        gender                  = req.gender,
        year_audit_non_uob      = req.auditNonUOBExp,
        edu_level               = req.educationLevel,
        edu_major               = req.educationMajor,
        edu_category            = req.educationCategory,
        ia_background           = req.IABackgground,
        ea_background           = req.EABackground,
        active                  = req.active,

        div_id = utils.div_str_to_divID(req.divison),
        role_id = utils.role_str_to_id(req.role)
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    emp.update(stored_data)
    db.commit()
    return updated

@router.get('/api/header_training/{nik}/{year}')
def get_header_training(nik: int, year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    # Get Emp_id
    emp = db.query(Employee).filter(
        Employee.staff_id == str(nik)
    ).one()

    # Get Training Target
    trgt = db.query(TrainingTarget).filter(
        TrainingTarget.emp_id == emp.id,
        TrainingTarget.year == year
    ).one()

    # Get Sum of Training Days
    trainings = db.query(Training).filter(
        Training.emp_id == emp.id,
        Training.date >= startDate,
        Training.date <= endDate        
    ).all()

    sum_t_hours = 0

    for t in trainings:
        sum_t_hours += t.duration_hours
    
    sum_t_hours = utils.remove_exponent(sum_t_hours/8)
    trgt_hour   = utils.remove_exponent(trgt.target_hours/8)
    
    return [{
        'training_done' : f"{sum_t_hours}/{trgt_hour} days"
    }]

@router.get('/api/data_chart_trainings/{nik}/{year}')
def get_header_training(nik: int, year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    # Get Emp_id
    emp = db.query(Employee).filter(
        Employee.staff_id == str(nik)
    ).one()

    # Get Training Target
    trgt = db.query(TrainingTarget).filter(
        TrainingTarget.emp_id == emp.id,
        TrainingTarget.year == year
    ).one()

    # Get Sum of Training Days
    trainings = db.query(Training).filter(
        Training.emp_id == emp.id,
        Training.date >= startDate,
        Training.date <= endDate        
    ).all()

    sum_t_hours = 0

    for t in trainings:
        sum_t_hours += t.duration_hours
    
    t_pctg = round((sum_t_hours/trgt.target_hours)*100)

    return [{"title":"done","total_training":t_pctg},
            {"title":"remaining","total_training":100 - t_pctg}]
