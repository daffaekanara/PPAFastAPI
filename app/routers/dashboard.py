from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import datetime
from dateutil.relativedelta import relativedelta
import schemas, utils
from models import *
from database import get_db

router = APIRouter(
    tags=['Dashboard'],
    prefix="/dashboard"
)

gen_x_youngest = datetime.date(1975,12,31)
gen_y_youngest = datetime.date(1989,12,31)


# API
@router.get('/api/smr_certification')
def get_smr_certs(db: Session = Depends(get_db)):
    # Get Emps
    emps = db.query(Employee).all()

    # Init res
    levels = [
        "SMR Level 1",
        "SMR Level 2",
        "SMR Level 3",
        "SMR Level 4",
        "SMR Level 5",
        "SMR In Progress",
    ]
    res = []
    for lvl in levels:
        res.append({
            "smr_level"     : lvl,
            "sum_per_level" : 0
        })

    for e in emps:
        for cert in e.emp_certifications:
            index = utils.find_index(res,"smr_level", cert.cert_name)
    
            if index:
                res[index]["sum_per_level"] += 1 
    
    return res

@router.get('/api/pro_certification')
def get_pro_certs(db: Session = Depends(get_db)):
    # Get Emps
    emps = db.query(Employee).all()

    # Init res
    types = [
        "CISA",
        "CEH",
        "ISO27001",
        "CHFI",
        "QIA",
        "CIA",
        "CA",
        "CBIA",
        "CPA"
    ]
    res = []
    for t in types:
        res.append({
            "certification_name": t,
            "sum_per_name"     : 0
        })

    for e in emps:
        for cert in e.emp_certifications:
            index = utils.find_index(res,"certification_name", cert.cert_name)
    
            if index:
                res[index]["sum_per_name"] += 1 
    
    return res

@router.get('/api/age_group/')
def get_age_group(db: Session = Depends(get_db)):
    # Get All Emps
    emps = db.query(Employee).all()

    gens = ["Gen-X", "Gen-Y", "Gen-Z"]
    res = []

    # Init result dict
    for gen in gens:
        res.append({
            "male_sum"  : 0,
            "female_sum": 0,
            "gen_name"  : gen
        })
    
    for e in emps:
        if e.date_of_birth <= gen_x_youngest: # Gen X
            if e.gender == 'M':
                res[0]['male_sum'] += 1
            elif e.gender == 'F':
                res[0]['female_sum'] += 1
        elif e.date_of_birth <= gen_y_youngest: # Gen Y
            if e.gender == 'M':
                res[1]['male_sum'] += 1
            elif e.gender == 'F':
                res[1]['female_sum'] += 1
        else:
            if e.gender == 'M':
                res[2]['male_sum'] += 1
            elif e.gender == 'F':
                res[2]['female_sum'] += 1

    return res

@router.get('/api/education_level/')
def get_edu_level(db: Session = Depends(get_db)):
    # Get All Emps
    emps = db.query(Employee).all()

    titles = ["Management/Economy", "Information Technology", "Others"]
    res = []

    # Init result dict
    for title in titles:
        res.append({
            "bachelor_sum"  : 0,
            "master_sum"    : 0,
            "major_title"   : title
        })
    
    for e in emps:
        if e.edu_category == "Information Technology":
            if e.edu_level == "Bachelor":
                res[1]['bachelor_sum'] += 1
            elif e.edu_level == "Master":
                res[1]['master_sum'] += 1
        elif e.edu_category == "Management/Economy":
            if e.edu_level == "Bachelor":
                res[0]['bachelor_sum'] += 1
            elif e.edu_level == "Master":
                res[0]['master_sum'] += 1
        elif e.edu_category == "Others":
            if e.edu_level == "Bachelor":
                res[2]['bachelor_sum'] += 1
            elif e.edu_level == "Master":
                res[2]['master_sum'] += 1

    return res

@router.get('/api/audit_exp/')
def get_total_audit_exp(db: Session = Depends(get_db)):
    # Get All Emps
    emps = db.query(Employee).all()

    # in_uob, outside_uob, total_exp, year
    year_cats = [
        "Less than 3", 
        "3-6", 
        "7-9",
        "10-12",
        "13-15",
        "More Than 15"
    ]
    res = []

    # Init result dict
    for y in year_cats:
        res.append({
            "in_uob"        : 0,
            "outside_uob"   : 0,
            "total_exp"     : 0,
            "year"          : y
        })

    for e in emps:
        years   = [0,0,0] #in UOB, outside UOB, total
        keys    = ["in_uob", "outside_uob", "total_exp"]

        years[0]    = relativedelta(datetime.date.today(), e.date_first_uob).years
        years[1]    = e.year_audit_non_uob
        years[2]    = years[0] + years[1]

        for index, year in enumerate(years):
            if year < 3:
                res[utils.find_index(res,"year","Less than 3")][keys[index]] += 1
            elif year < 7:
                res[utils.find_index(res,"year","3-6")][keys[index]] += 1
            elif year < 10:
                res[utils.find_index(res,"year","7-9")][keys[index]] += 1
            elif year < 13:
                res[utils.find_index(res,"year","10-12")][keys[index]] += 1
            elif year < 16:
                res[utils.find_index(res,"year","13-15")][keys[index]] += 1
            else:
                res[utils.find_index(res,"year","More than 15")][keys[index]] += 1

    return res