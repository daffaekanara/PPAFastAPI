from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.datastructures import UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import File
from sqlalchemy.orm import Session
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
import datetime
import calendar
from operator import itemgetter
from dateutil.relativedelta import relativedelta
from sqlalchemy.sql.expression import or_
from fastapi.responses import FileResponse
from sqlalchemy.sql.schema import ColumnCollectionConstraint
from fileio import fileio_module as fio
import schemas, datetime, utils, hashing
from models import *
from database import get_db
from MrptParser import parser_module as pm

gen_x_youngest = datetime.date(1975,12,31)
gen_y_youngest = datetime.date(1989,12,31)

# API
router = APIRouter(
    tags=['API'],
    prefix="/api"
)

### File ###
@router.get('/admin/audit_project_data/download/pa/id/{id}')
def get_prj_paproof_proof(id: int, db: Session = Depends(get_db)):
    prj = get_prj_by_id(id, db)

    if prj.completion_PA == "":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No uploaded proof for PA Completion of Project ({prj.name})")
    elif fio.is_file_exist(prj.completion_PA):
        return FileResponse(prj.completion_PA)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Cannot find file on filepath ({prj.completion_PA})")

@router.get('/admin/training_data/download/proof/id/{id}')
def get_training_proof(id: int, db: Session = Depends(get_db)):
    train = get_training_by_id(id, db)

    if train.proof == "":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No uploaded proof for Training ({train.name})")
    elif fio.is_file_exist(train.proof):
        return FileResponse(train.proof)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Cannot find file on filepath ({train.proof})")

@router.get('/admin/busu_data/download/proof/id/{id}')
def get_busu_proof(id: int, db: Session = Depends(get_db)):
    busu = get_busu_by_id(id, db)

    if busu.proof == "":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No uploaded proof for BUSU Engagement ({busu.activity_name})")
    elif fio.is_file_exist(busu.proof):
        return FileResponse(busu.proof)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Cannot find file on filepath ({busu.proof})")

@router.get('/profile/get_cert_proof/id/{id}')
def get_cert_proof(id: int, db: Session = Depends(get_db)):
    cert = get_cert_by_id(id, db)

    if cert.cert_proof == "":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No uploaded proof for Cert ({cert.cert_name})")
    elif fio.is_file_exist(cert.cert_proof):
        return FileResponse(cert.cert_proof)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Cannot find file on filepath ({cert.cert_proof})")

@router.get('/admin/employee/download/cert/cname/{cert_name}/nik/{nik}')
def get_cert_proof(cert_name: str, nik: str, db: Session = Depends(get_db)):
    # Check if cert_name is SMR_x
    if "SMR_" in cert_name:
        smr_lvl = cert_name[-1]
        cert_name = f"SMR Level {smr_lvl}"
    
    try:
        cert = get_cert_by_empnik_certname(nik, cert_name, db)
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No Cert of name ({cert_name}) and Owner NIK of ({nik}) was found!")
    except MultipleResultsFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Found multiple Certs of name ({cert_name}) and Owner NIK of ({nik}) was found!")
    

    if cert.cert_proof == "":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Employee of NIK ({nik}) hasn't uploaded any files for {cert.cert_name} cert!")
    elif not fio.is_file_exist(cert.cert_proof):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Cert of name ({cert_name}) and Employee of NIK ({nik}) was found (id:{cert.id}, but file ({cert.cert_proof}) doesn't exist in server!")
        
    return FileResponse(cert.cert_proof)

@router.post('/project/submit_pa_form/{year}')
def post_pa_completion_form(
    year            : int,
    projectTitle    : str= Form(...),
    attachment_proof: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    data = attachment_proof.file.read()

    # Check Project Name
    prj_query = db.query(Project).filter(
        Project.year == year,
        Project.name == projectTitle
    )

    try:
        prj = prj_query.one()
    except MultipleResultsFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Multiple Project of Name ({projectTitle}) and of year ({year}) was found!")
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No Projects of Name ({projectTitle}) and of year ({year}) was found!")

    # Process Proof
    filepath = fio.write_pa_completion_proof(prj.id, data, attachment_proof.filename)

    stored_data = jsonable_encoder(prj)
    stored_model = schemas.ProjectIn(**stored_data)
    new_data = {"completion_PA": filepath}
    updated = stored_model.copy(update=new_data)
    stored_data.update(updated)
    prj_query.update(stored_data)
    db.commit()

    return {"Details": "Success"}

@router.post('/engagement/input_form')
def post_engagement_input_form(
    id              : str= Form(...),
    WorM            : str= Form(...),
    activity        : str= Form(...),
    date            : str= Form(...),
    proof           : UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    eng_types = ["Regular Meeting", "Workshop"]

    data = proof.file.read()
    # Check NIK
    emp = get_emp_by_nik(id, db)
    emp_id = emp.id

    # Create BUSU Engagement
    new_eng = BUSUEngagement(
        activity_name   = activity,
        date            = utils.formstr_to_datetime(date),
        proof           = "",
        
        eng_type_id     = eng_types.index(WorM) + 1,

        creator_id      = emp_id
    )

    db.add(new_eng)
    db.commit()
    db.refresh(new_eng)

    # Process Proof
    filepath = fio.write_busu_proof(new_eng.id, emp_id, data, proof.filename)

    eng_query = db.query(BUSUEngagement).filter(BUSUEngagement.id == new_eng.id)

    stored_data = jsonable_encoder(new_eng)
    stored_model = schemas.BUSUEngagementIn(**stored_data)
    new_data = {"proof": filepath}
    updated = stored_model.copy(update=new_data)
    stored_data.update(updated)
    eng_query.update(stored_data)
    db.commit()

    return {"Details": "Success"}

@router.post('/training/form-file')
def post_training_proof_file(
    name            : str= Form(...),
    date            : str= Form(...),
    duration_hours  : int= Form(...),
    id              : str= Form(...),
    remarks         : str= Form(...),
    proof           : UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    data = proof.file.read()
    # Check NIK
    emp = get_emp_by_nik(id, db)
    emp_id = emp.id

    # Create Training
    newTrain = Training(
        name            = name, 
        date            = utils.formstr_to_datetime(date), 
        duration_hours  = duration_hours, 
        proof           = "",
        budget          = 0,
        realization     = 0,
        charged_by_fin  = 0,
        remark          = remarks,
        mandatory_from  = "",
        emp_id          = emp_id
    )

    db.add(newTrain)
    db.commit()
    db.refresh(newTrain)

    # Process Proof
    filepath = fio.write_training_proof(newTrain.id, emp_id, data, proof.filename)

    train_query = db.query(Training).filter(Training.id == newTrain.id)

    stored_data = jsonable_encoder(newTrain)
    stored_model = schemas.TrainingIn(**stored_data)
    new_data = {"proof": filepath}
    updated = stored_model.copy(update=new_data)
    stored_data.update(updated)
    train_query.update(stored_data)
    db.commit()

    return {"Details": "Success"}

@router.post('/training/proof/{nik}/{training_id}')
def post_training_proof_file(nik: str, training_id: int, attachment_proof: UploadFile = File(...), db: Session = Depends(get_db)):
    data = attachment_proof.file.read()

    # Check NIK
    emp = get_emp_by_nik(id,db)
    emp_id = emp.id

    # Check training_id
    train_query = db.query(Training).filter(
        Training.id == training_id
    )

    try:
        train = train_query.one()
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Training of ID ({training_id}) was not found!")

    if not train.emp_id == emp_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Training of ID ({training_id}) belongs to emp of id ({train.emp_id}), not ({emp_id})!")


    filepath = fio.write_training_proof(training_id, emp_id, data, attachment_proof.filename)

    # Update DB
    stored_data = jsonable_encoder(train)
    stored_model = schemas.TrainingIn(**stored_data)
    new_data = {"proof": filepath}
    updated = stored_model.copy(update=new_data)
    stored_data.update(updated)
    train_query.update(stored_data)
    db.commit()

    return {"filename": filepath}

@router.post('/admin/budget_data/mrpt_file')
def post_mrpt_file(mrpt: UploadFile = File(...), db: Session = Depends(get_db)):
    # Check if .xlsx
    if not ".xlsx" in mrpt.filename:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Sent file ({mrpt.filename}) isnt of '.xlsx' format!")

    # Parse Excel
    data = mrpt.file.read()
    filepath = fio.write_mrpt(data, mrpt.filename)
    actuals, mBudgets, yBudget = pm.parse_excel_to_budgets(filepath)
    fio.delete_file(filepath)

    # Process Monthly Actuals
    for a in actuals:
        # print(f"mActuals: {a['year']}/{a['month']}")
        create_or_update_mActual(a, db)
    
    # Process Monthly Budget
    for m in mBudgets:
        # print(f"mBudgets: {m['year']}/{m['month']}")
        create_or_update_mBudget(m, db)
    
    # Process Yearly Budget
    # print(f"yBudget: {yBudget['year']}")
    create_or_update_yBudget(yBudget, db)
    
    return {'details': 'All budgets updated!'}

@router.post('/admin/employee_data/cert/others')
def post_others_cert_form(
    certification_name  : str= Form(...),
    nik                 : str= Form(...),
    proof               : UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    data = proof.file.read()

    # Check NIK
    emp = get_emp_by_nik(nik, db)

    # Write CertFile
    filepath = fio.write_cert(certification_name, emp.id, data, proof.filename)

    # Update DB
    existing_cert = None
    for c in emp.emp_certifications:
        if c.cert_name == certification_name:
            existing_cert = c
            break

    if existing_cert: # Update cert_proof
        query = db.query(Certification).filter(
            Certification.id == existing_cert.id
        )
        stored_data = jsonable_encoder(existing_cert)
        stored_model = schemas.CertificationIn(**stored_data)
        new_data = {"cert_proof": filepath}
        updated = stored_model.copy(update=new_data)
        stored_data.update(updated)
        query.update(stored_data)
        db.commit()
    else: # Create New Cert
        newCert = Certification(
            cert_name   = certification_name,
            cert_proof  = filepath,
            emp_id      = emp.id
        )

        db.add(newCert)
        db.commit()
        db.refresh(newCert)

    return {"filename": filepath}

@router.post('/admin/employee_data/cert/{cert_name}/{nik}')
def post_file(cert_name: str, nik: str, cert_file: UploadFile = File(...), db: Session = Depends(get_db)):
    data = cert_file.file.read()

    # Check NIK
    emp = get_emp_by_nik(nik, db)
    emp_id = emp.id

    filepath = fio.write_cert(cert_name, emp_id, data, cert_file.filename)

    # Check if cert_name is SMR_x
    if "SMR_" in cert_name:
        smr_lvl = cert_name[-1]
        cert_db_name = f"SMR Level {smr_lvl}"
    else:
        cert_db_name = cert_name

    # Update DB
    existing_cert = None
    for c in emp.emp_certifications:
        if c.cert_name == cert_db_name:
            existing_cert = c
            break
    
    if existing_cert: # Update cert_proof
        query = db.query(Certification).filter(
            Certification.id == existing_cert.id
        )
        stored_data = jsonable_encoder(existing_cert)
        stored_model = schemas.CertificationIn(**stored_data)
        new_data = {"cert_proof": filepath}
        updated = stored_model.copy(update=new_data)
        stored_data.update(updated)
        query.update(stored_data)
        db.commit()
    else: # Create New Cert
        newCert = Certification(
            cert_name   = cert_db_name,
            cert_proof  = filepath,
            emp_id      = emp_id
        )

        db.add(newCert)
        db.commit()
        db.refresh(newCert)

    return {"filename": filepath}

@router.post('/file')
def post_file(attachment_proof: UploadFile = File(...)):
    data = attachment_proof.file.read()

    f = open(f'data/{attachment_proof.filename}', 'wb')
    f.write(data)
    f.close()

    return {"filename": attachment_proof.filename}

@router.post('/admin/budget_data/excel_parse')
def post_excel_file_budget(file: UploadFile = File(...)):
    data = file.file.read()

    # TODO Make sure dir exists

    f = open(f'data/files/budget/{file.filename}', 'wb')
    f.write(data)
    f.close()

    return

### Dashboard ###

@router.get('/dashboard/smr_certification')
def get_smr_certs(db: Session = Depends(get_db)):
    # Get Emps
    emps = get_all_active_emps(db)

    # Init res
    levels = [
        "SMR In Progress",
        "SMR Level 1",
        "SMR Level 2",
        "SMR Level 3",
        "SMR Level 4",
        "SMR Level 5",
    ]
    res = []
    for lvl in levels:
        res.append({
            "smr_level"     : lvl,
            "sum_per_level" : 0
        })

    for e in emps:
        # Check Smr of Emp
        max_lvl, max_id = extract_highest_smr_level(e.emp_certifications)

        if max_lvl >= 0:
            res[max_lvl]["sum_per_level"] += 1
    
    return res

@router.get('/dashboard/pro_certification')
def get_pro_certs(db: Session = Depends(get_db)):
    # Get Emps
    emps = get_all_active_emps(db)

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

    other_certs = 0

    for e in emps:
        for cert in e.emp_certifications:
            index = utils.find_index(res,"certification_name", cert.cert_name)
    
            if cert.cert_proof:
                if index is not None:
                    res[index]["sum_per_name"] += 1
                else:
                    other_certs += 1
    
    res.append({
        "certification_name": "Others",
        "sum_per_name"      : other_certs
    })

    return res

@router.get('/dashboard/age_group')
def get_age_group(db: Session = Depends(get_db)):
    # Get All Emps
    emps = get_all_active_emps(db)

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

@router.get('/dashboard/education_level')
def get_edu_level(db: Session = Depends(get_db)):
    # Get All Emps
    emps = get_all_active_emps(db)

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

@router.get('/dashboard/audit_exp')
def get_total_audit_exp(db: Session = Depends(get_db)):
    # Get All Emps
    emps = get_all_active_emps(db)

    # in_uob, outside_uob, total_exp, year
    year_cats = [
        "Less than 3", 
        "3-6", 
        "7-9",
        "10-12",
        "13-15",
        "More than 15"
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

### ClickTable ###
@router.get('/clicktable/emp/audit_exp')
def get_emp_audit_exp(db: Session = Depends(get_db)):
    # Get Emps
    emps = get_all_active_emps(db)

    res = []

    for e in emps:
        auditUOBYears   = utils.get_year_diff_to_now(e.date_first_uob)

        res.append({
            'id'            : e.id,
            'name'          : e.name,
            'total_year'    : e.year_audit_non_uob + auditUOBYears,
            'inside_uob'    : auditUOBYears,
            'outside_uob'   : e.year_audit_non_uob
        })

    return sorted(res, key=itemgetter('total_year'), reverse=True)

@router.get('/clicktable/emp/edu_lvl')
def get_emp_edulvl(db: Session = Depends(get_db)):
    # Get Emps
    emps = get_all_active_emps(db)

    res = []

    for e in emps:
        res.append({
            'id'        : e.id,
            'BorM'      : e.edu_level,
            'major'     : e.edu_major,
            'name'      : e.name
        })

    return sorted(res, key=itemgetter('BorM'), reverse=True)

@router.get('/clicktable/emp/generation')
def get_emp_gen(db: Session = Depends(get_db)):
    # Get Emps
    emps = get_all_active_emps(db)

    res = []

    for e in emps:
        res.append({
            'id'            : e.id,
            'generation'    : utils.get_gen(e.date_of_birth),
            'gender'        : e.gender,
            'name'          : e.name
        })

    return sorted(res, key=itemgetter('generation'), reverse=True)

@router.get('/clicktable/cert/smr')
def get_click_cert_smr(db: Session = Depends(get_db)):
    # Get Emps
    emps = get_all_active_emps(db)

    # Init res
    res = []
    for e in emps:
        # Check Smr of Emp
        max_lvl, max_id = extract_highest_smr_level(e.emp_certifications)
        
        if max_lvl > -1:
            res.append({
                'id'        : max_id,
                'smr_level' : "SMR In Progress" if max_lvl == 0 else f"SMR Level {max_lvl}",
                'name'      : e.name
            })
    
    return sorted(res, key=itemgetter('smr_level'), reverse=True)

@router.get('/clicktable/cert/pro')
def get_click_cert_pro(db: Session = Depends(get_db)):
    # Get Emps
    emps = get_all_active_emps(db)

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

    # Init res
    res = []
    for e in emps:
        for c in e.emp_certifications:
            if not is_cert_smr_related(c) and c.cert_proof:
            # if c.cert_proof or not is_cert_smr_related(c):
                res.append({
                    'id'            : c.id,
                    'certification' : c.cert_name,
                    'name'          : e.name
                })
    
    return sorted(res, key=itemgetter('certification'), reverse=False)

### Profile ###

@router.get('/profile/about/table_data/{nik}')
def get_employee_table(nik: str, db: Session = Depends(get_db)):
    e = get_emp_by_nik(nik, db)

    res = []

    as_of_now       = datetime.date.today().strftime("%m/%d/%Y")
    age             = utils.get_year_diff_to_now(e.date_of_birth)
    gen             = utils.get_gen(e.date_of_birth)
    auditUOBYears   = utils.get_year_diff_to_now(e.date_first_uob)

    # Process Certs
    certs = [
        "SMR", "CISA", "CEH", "ISO27001", "CHFI", 
        "IDEA", "QualifiedIA", "CBIA", "CIA", "CPA", "CA"]

    cert_res = []

    for c in certs:
        cert_res.append({
            'title': c,
            'value': 0
        })

    otherCerts = []
    max_smr = 0

    for c in e.emp_certifications:
        # SMR (Levels)
        smr_level = utils.extract_SMR_level(c.cert_name)
        
        if smr_level: # SMR
            if c.cert_proof:
                if smr_level > max_smr:
                    cert_res[0]['value'] = smr_level
                    max_smr = smr_level
        elif c.cert_name == "SMR In Progress":
            cert_res[0]['value'] = "In Progress"
        elif c.cert_name in certs and c.cert_proof: # Pro Certs
            index = utils.find_index(cert_res, 'title', c.cert_name)
            cert_res[index]['value'] = 1
        elif c.cert_proof:                          # Other Certs
            otherCerts.append(c.cert_name)

    smr_lvl = cert_res[0]['value']

    if smr_lvl == "In Progress":
        smr_str = smr_lvl
    elif smr_lvl:
        smr_str = f"Level {smr_lvl}"
    else:
        smr_str = "-"

    res.append({
        "id"                          : e.id,
        "staffNIK"                    : e.staff_id,
        "staffName"                   : e.name,
        "email"                       : e.email,
        "role"                        : e.role.name,
        "divison"                     : e.part_of_div.short_name,
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
        "ISO27001"                    : cert_res[3]['value'],
        "CHFI"                        : cert_res[4]['value'],
        "IDEA"                        : cert_res[5]['value'],
        "QualifiedIA"                 : cert_res[6]['value'],
        "CBIA"                        : cert_res[7]['value'],
        "CIA"                         : cert_res[8]['value'],
        "CPA"                         : cert_res[9]['value'],
        "CA"                          : cert_res[10]['value'],
        "other_cert"                  : ", ".join(otherCerts),
        "IABackgground"               : e.ia_background,
        "EABackground"                : e.ea_background,
        "active"                      : e.active
    })

    return res

@router.patch('/profile/about/table_data/{nik}')
def patch_employee_table_entry(nik: str, req: schemas.EmployeeInHiCoupling, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(
        Employee.staff_id == nik
    )

    if not emp.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
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

@router.get('/profile/header_training/{nik}/{year}')
def get_header_training(nik: str, year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    # Get Emp_id
    emp = get_emp_by_nik(nik, db)

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

@router.get('/profile/data_chart_trainings/{nik}/{year}')
def get_header_training(nik: str, year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    # Get Emp_id
    emp = get_emp_by_nik(nik, db)

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

@router.post('/profile/change_password/{id}')
def change_password(id: int, req: schemas.PasswordChangeIn, db: Session = Depends(get_db)):
    # Check old_pw
    emp_query = db.query(Employee).filter(
        Employee.id == id,
        Employee.active == True
    )

    if not emp_query.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Emp ID not found')

    emp = emp_query.first()

    if not hashing.verify_bcrypt(emp.pw, req.old_pw):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Old Password do not match')

    # Update new_pw
    stored_data = jsonable_encoder(emp)
    stored_model = schemas.EmployeeIn(**stored_data)

    new_data = {'pw': hashing.bcrypt(req.new_pw)}
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    emp_query.update(stored_data)
    db.commit()

    return {'detail':'Password Change Success!'}

### Budgets ###

@router.get('/budget/budgetdata/{year}/{month}')
def get_total_by_division_by_year(year: int, month: int, db: Session = Depends(get_db)):

    yearlyQuery = db.query(MonthlyBudget).filter(
        MonthlyBudget.year == year
    ).all() # 12 data

    query = db.query(MonthlyActualBudget).filter(
        MonthlyActualBudget.year == year, 
        MonthlyActualBudget.month == month
    ).first()

    # Init result dict
    cats = [
        "Staff Expense", 
        "Revenue Related", 
        "IT Related", 
        "Occupancy Related", 
        "Other Related",
        "Direct Expense",
        "Indirect Expense",
        "Total"
    ]
    res = []
    yearlyBudget = {}
    actualMonthBudget = {}

    for cat in cats:
        res.append({
            "yearly":0,
            "month_to_year":0,
            "expense_category":cat
        })

        yearlyBudget[cat] = 0
        actualMonthBudget[cat] = 0

    # Process YearlyBudget
    for y in yearlyQuery:
        yearlyBudget['Staff Expense']               += y.staff_salaries
        yearlyBudget['Staff Expense']               += y.staff_training_reg_meeting
        yearlyBudget['Revenue Related']             += y.revenue_related
        yearlyBudget['IT Related']                  += y.it_related
        yearlyBudget['Occupancy Related']           += y.occupancy_related
        yearlyBudget['Other Related']               += y.other_transport_travel
        yearlyBudget['Other Related']               += y.other_other
        yearlyBudget['Direct Expense']              += y.staff_salaries + y.revenue_related + y.it_related + y.occupancy_related + y.other_transport_travel + y.other_other   
        yearlyBudget['Indirect Expense']            += y.indirect_expense 
        yearlyBudget['Total']                       += yearlyBudget['Direct Expense'] + yearlyBudget['Indirect Expense']
        
    # process MonthlyActualBudget
    actualMonthBudget['Staff Expense']               = query.staff_salaries if query else 0
    actualMonthBudget['Staff Expense']               = query.staff_training_reg_meeting  if query else 0
    actualMonthBudget['Revenue Related']             = query.revenue_related  if query else 0
    actualMonthBudget['IT Related']                  = query.it_related  if query else 0
    actualMonthBudget['Occupancy Related']           = query.occupancy_related  if query else 0
    actualMonthBudget['Other Related']               = query.other_transport_travel  if query else 0
    actualMonthBudget['Other Related']               = query.other_other  if query else 0
    actualMonthBudget['Direct Expense']              = query.staff_salaries + query.revenue_related + query.it_related + query.occupancy_related + query.other_transport_travel + query.other_other if query else 0  
    actualMonthBudget['Indirect Expense']            = query.indirect_expense if query else 0
    actualMonthBudget['Total']                       = actualMonthBudget['Direct Expense'] + actualMonthBudget['Indirect Expense']


    for cat in cats:
        i = utils.find_index(res, 'expense_category', cat)
        res[i]["yearly"]        = yearlyBudget[cat]
        res[i]["month_to_year"] = actualMonthBudget[cat]

    return res

### Audit Project ###

# EditStatusProject Table
@router.get('/projects/edit_project_table/{nik}/{year}')
def get_project_table(nik: str, year: int, db: Session = Depends(get_db)):
    # Check NIK
    emp = get_emp_by_nik(nik, db)

    projects = db.query(Project).filter(
        Project.year == year,
        Project.tl.has(id=emp.id)
    ).all()

    res = []

    for p in projects:
        res.append({
            "id"        : str(p.id),
            "auditPlan" : p.name,
            "division"  : p.div.short_name,
            "status"    : p.status.name,
            "useOfDA"   : p.used_DA,
            "year"      : p.year,

            "is_carried_over" : p.is_carried_over,
            "timely_report"   : p.timely_report,
            "completion_PA"   : len(p.completion_PA) > 0
        })

    return res

@router.patch('/projects/edit_project_table/{id}')
def patch_project_table_entry(id: int,req: schemas.ProjectInHiCoupling, db: Session = Depends(get_db)):
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]

    prj = db.query(Project).filter(
        Project.id == id
    )

    if not prj.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    stored_data = jsonable_encoder(prj.first())
    stored_model = schemas.ProjectIn(**stored_data)
    
    div_id      = divs.index(req.division)+1
    status_id   = get_project_status_id(req.status)

    dataIn = schemas.ProjectIn(
        name            = req.auditPlan,
        used_DA         = req.useOfDA,
        is_carried_over = req.is_carried_over,
        timely_report   = req.timely_report,
        year            = req.year,

        status_id       = status_id,
        div_id          = div_id
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    prj.update(stored_data)
    db.commit()
    return updated

# Chart
@router.get('/projects/total_by_division/v2/{year}')
def get_total_by_division_by_year_v2(year: int, db: Session = Depends(get_db)):
    projects = db.query(Project).filter(Project.year == year).all()
    
    status = [
        "Total Projects",
        "Completed",
        "Sign-off",
        "Reporting",
        "Fieldwork",
        "Planning",
        "Timely Report",
        "DA",
        "PA"
    ]

    # Init result dict
    res = {
        'labels': status,
        'datasets': []
    }

    divs_name = get_divs_name_exclude_IAH(db)
    colors = [
        "#F44336", "#9C27B0", "#FFEB3B", "#4CAF50", "#2196F3", 
        "#3F51B5", "#FF5722", "#795548", "#9E9E9E", "#000000",
        "#F44336", "#9C27B0", "#FFEB3B", "#4CAF50", "#2196F3", 
        "#3F51B5", "#FF5722", "#795548", "#9E9E9E", "#000000"
    ]

    datasets = []
    for idx, d in enumerate(divs_name):
        datasets.append({
            "label"             : d,
            "data"              : [0,0,0,0,0,0,0,0,0],
            "backgroundColor"   : colors[idx]
        })

    for p in projects:
        # Cek Divisi
        div_name = p.div.short_name
        div_index = utils.find_index(datasets, "label", div_name)
        # Process Each Prj Status
        # res[utils.find_index(res, 'project_status', status[0])]

        datasets[div_index]["data"][0] += 1
        datasets[div_index]["data"][1] += 1 and p.status.name == status[1]
        datasets[div_index]["data"][2] += 1 and p.status.name == status[2]
        datasets[div_index]["data"][3] += 1 and p.status.name == status[3]
        datasets[div_index]["data"][4] += 1 and p.status.name == status[4]
        datasets[div_index]["data"][5] += 1 and p.status.name == status[5]
        datasets[div_index]["data"][6] += 1 and p.timely_report
        datasets[div_index]["data"][7] += 1 and p.used_DA
        datasets[div_index]["data"][8] += 1 and len(p.completion_PA) > 0        
    
    res["datasets"] = datasets

    return res

@router.get('/projects/total_by_division/{year}')
def get_total_by_division_by_year(year: int, db: Session = Depends(get_db)):
    query = db.query(Project).filter(Project.year == year).all()
    
    status = [
        "Total Projects",
        "Completed",
        "Sign-off",
        "Reporting",
        "Fieldwork",
        "Planning",
        "Timely Report",
        "DA",
        "PA"
    ]

    # Init result dict
    res = []
    for s in status:
        res.append({
            "project_status":s,
            "WBGM":0, 
            "RBA":0, 
            "BRDS":0,
            "TAD":0
        })

    for q in query:
        # Cek Divisi
        div_name = q.div.short_name

        # Process Each Prj Status
        # res[utils.find_index(res, 'project_status', status[0])]
        res[0][div_name] += 1
        res[1][div_name] += 1 and q.status.name == status[1]
        res[2][div_name] += 1 and q.status.name == status[2]
        res[3][div_name] += 1 and q.status.name == status[3]
        res[4][div_name] += 1 and q.status.name == status[4]
        res[5][div_name] += 1 and q.status.name == status[5]
        res[6][div_name] += 1 and q.timely_report
        res[7][div_name] += 1 and q.used_DA
        res[8][div_name] += 1 and len(q.completion_PA) > 0        
        

    return res

### Social Contrib ###
@router.get('/auditcontrib/audit_contribution_data/table_data/{year}/{nik}')
def get_contrib_table_by_div(year: int, nik: str, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    # Check NIK
    creator = get_emp_by_nik(nik, db)

    contribs = db.query(SocialContrib).filter(
        SocialContrib.date >= startDate,
        SocialContrib.date <= endDate,
        SocialContrib.creator_id == creator.id
    ).all()

    res = []

    for c in contribs:
        res.append({
            "id"        : str(c.id),
            "category"  : c.social_type.name,
            "title"     : c.topic_name,
            "date"      : c.date.strftime("%m/%d/%Y")
        })

    return res

@router.post('/auditcontrib/audit_contribution_data/table_data/{nik}')
def create_contrib_table_entry(nik: str, req: schemas.SocialContribHiCouplingUserPageIn, db: Session = Depends(get_db)):
    types = ["Audit News", "MyUOB", "Audit Bulletin"]

    # Check NIK
    creator = get_emp_by_nik(nik, db)

    new_con = SocialContrib(
        date            = utils.tablestr_to_datetime(req.date),
        topic_name      = req.title,
        creator_id      = creator.id,
        social_type_id  = types.index(req.category) + 1
    )

    db.add(new_con)
    db.commit()
    db.refresh(new_con)

    return new_con

@router.patch('/auditcontrib/audit_contribution_data/table_data/{id}')
def patch_contrib_table_entry(id: int,req: schemas.SocialContribHiCouplingUserPageIn, db: Session = Depends(get_db)):
    types = ["Audit News", "MyUOB", "Audit Bulletin"]

    contrib = db.query(SocialContrib).filter(
        SocialContrib.id == id
    )

    if not contrib.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    stored_data = jsonable_encoder(contrib.first())
    stored_model = schemas.SocialContribIn(**stored_data)
    
    social_type_id  =types.index(req.category)+1

    dataIn = schemas.SocialContribIn(
        date            = utils.tablestr_to_datetime(req.date),
        topic_name      = req.title,
        social_type_id  = social_type_id
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    contrib.update(stored_data)
    db.commit()
    return updated

@router.delete('/auditcontrib/audit_contribution_data/table_data/{id}')
def delete_contrib_table_entry(id: int, db: Session = Depends(get_db)):
    contrib = db.query(SocialContrib).filter(
        SocialContrib.id == id
    )

    if not contrib.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    contrib.delete()
    db.commit()

    return {'details': 'Deleted'}

@router.get('/socialcontrib/total_by_division/{year}')
def get_total_by_division_by_year(year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    query = db.query(SocialContrib).filter(
        SocialContrib.date >= startDate, 
        SocialContrib.date <= endDate,
        SocialContrib.creator.has(active=True)
    ).all()
    
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    res = []

    # Init result dict
    for div in divs:
        res.append({"contribute_sum":0, "division":div})

    for q in query:
        contrib_by_div = next((index for (index, d) in enumerate(res) if d["division"] == q.creator.part_of_div.short_name), None)
        res[contrib_by_div]["contribute_sum"] += 1

    return res

@router.get('/socialcontrib/total_by_division_type_categorized/{year}')
def get_total_by_division_by_year_type_categorized(year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    query = db.query(SocialContrib).filter(SocialContrib.date >= startDate, SocialContrib.date <= endDate).all()
    
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    res = {}

    # Init result dict
    for div in divs:
        res[div] = {"news":0, "myUob":0, "buletin":0}

    for q in query:
        if q.social_type_id == 1:
            res[q.div.short_name]["news"] += 1
        if q.social_type_id == 2:
            res[q.div.short_name]["myUob"] += 1
        if q.social_type_id == 3:
            res[q.div.short_name]["buletin"] += 1

    return res

### Training ###
@router.get('/training/announcement')
def get_training_annoucement(db: Session = Depends(get_db)):
    ann_query = db.query(Annoucement).filter(
        Annoucement.type_name == "Training"
    )

    try:
        ann = ann_query.one_or_none()
    except MultipleResultsFound:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Multiple Announcements of type 'Training' was found!)")

    if not ann:
        return None
    else:
        return {'body': ann.body}

@router.get('/training/budget_percentange/{year}')
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
            i = utils.find_index(values, "div", y.div.short_name)
            values[i]["budget"] = y.budget
    
    # Get Each Training's Charged and Realized
    for t in trainings:
        if t.emp_id == 0: # Mandatory (Not specific to a employee)
            values[5]["budget"]     += t.budget
            values[5]["realized"]   += t.realization
            values[5]["charged"]    += t.charged_by_fin
        elif t.employee.active:
            if 1 <= t.employee.div_id <= 5: # Not Including IAH
                i = utils.find_index(values, "div", t.employee.part_of_div.short_name)
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

@router.get('/training/progress_percentange/{year}')
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
        i = utils.find_index(values, "div", t.trainee.part_of_div.short_name)
        values[i]["target_hours"] += t.target_hours

    # Get Currs
    for t in trainings:
        if t.employee.active:
            i = utils.find_index(values, "div", t.employee.part_of_div.short_name)
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

@router.post('/training/form', status_code=status.HTTP_201_CREATED)
def create_training_from_form(req: schemas.TrainingInHiCouplingForm, db: Session = Depends(get_db)):
    emp = get_emp_by_nik(req.nik, db)
    
    newTrain = Training(
        name            = req.name, 
        date            = utils.str_to_datetime(req.date), 
        duration_hours  = req.duration_hours, 
        proof           = "",
        budget          = 0,
        realization     = 0,
        charged_by_fin  = 0,
        remark          = req.remarks,
        mandatory_from  = "",
        emp_id          = emp.id
    )
    
    db.add(newTrain)
    db.commit()
    db.refresh(newTrain)
    return newTrain

# Table
@router.get('/training/table/{nik}/{year}')
def get_training_table(nik: str, year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)
    
    # Check NIK
    emp = get_emp_by_nik(nik, db)

    training = db.query(Training).filter(
        Training.date >= startDate,
        Training.date <= endDate,
        Training.emp_id == emp.id
    ).all()

    res = []

    for t in training:
        if not t.employee.active:
            continue

        divison = t.employee.part_of_div.short_name if t.employee else ""
        emp_name= t.employee.name if t.employee else ""
        emp_nik = t.employee.staff_id if t.employee else ""

        res.append({
            "id"                : str(t.id),
            "division"          : divison,
            "name"              : emp_name,
            "nik"               : emp_nik,
            "trainingTitle"     : t.name,
            "date"              : t.date.strftime("%m/%d/%Y"),
            "numberOfHours"     : t.duration_hours,
            "budget"            : t.budget,
            "costRealization"   : t.realization,
            "chargedByFinance"  : t.charged_by_fin,
            "mandatoryFrom"     : t.mandatory_from,
            "remark"            : t.remark
        })

    return res

@router.patch('/training/table/{id}')
def update_training_table_entry(id: int, req: schemas.TrainingInHiCouplingUserPage, db: Session = Depends(get_db)):
    train_q = db.query(Training).filter(
        Training.id == id
    )

    try:
        train = train_q.one()
    except MultipleResultsFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Multiple Training of ID ({id}) was found!")
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Training of ID ({id}) was not found!")

    stored_data = jsonable_encoder(train)
    stored_model = schemas.TrainingIn(**stored_data)

    dataIn = schemas.TrainingIn(
        name            = req.trainingTitle,
        date            = utils.tablestr_to_datetime(req.date),
        duration_hours  = req.numberOfHours
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)
    stored_data.update(updated)

    train_q.update(stored_data)
    db.commit()
    return updated

@router.delete('/training/table/{id}')
def delete_training_table_entry(id: int, db: Session = Depends(get_db)):
    t = db.query(Training).filter(
        Training.id == id
    )

    if not t.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    t.delete()
    db.commit()

    return {'details': 'Deleted'}

### CSF ###

@router.get('/csf/client_survey/{year}')
def get_csf_bar_chart_data(year: int, db: Session = Depends(get_db)):
    divs    = ["WBGM", "RBA", "BRDS", "TAD"]
    
    # Get All CSF where Project's year is {year}
    csfs = db.query(CSF).filter(
        CSF.prj.has(year=year)
    ).all()

    # Init result dict
    res = []
    for d in divs:
        res.append({
            "division"      : d, 
            "by_division"   : 0, 
            "by_project"    : 0
        })

    # Calc byProject Score
    for d in divs:
        prj_ids = []
        list_of_prj_scores = []

        # Find Unique Project IDs of a div
        for c in csfs:
            if c.prj.div.short_name == d:
                if c.prj_id not in prj_ids:
                    prj_ids.append(c.prj_id)

        # Calc each project overall score
        for prj_id in prj_ids:
            list_of_csf_scores = []
            
            # Get project's feedback scores
            for c in csfs:
                if c.prj_id == prj_id:
                    score = utils.calc_single_csf_score(c)
                    list_of_csf_scores.append(score)
            
            # Project Overall Score
            if list_of_csf_scores:
                score = sum(list_of_csf_scores) / len(list_of_csf_scores)
                list_of_prj_scores.append(round(score,2))

        if list_of_prj_scores:
            score = sum(list_of_prj_scores) / len(list_of_prj_scores)

            index = utils.find_index(res, "division", d)
            res[index]["by_project"] = round(score, 2)
  
    # Calc byInvDiv Score
    for d in divs:
        prj_ids = []
        list_of_prj_scores = []

        # Find Unique Project IDs of a div
        for c in csfs:
            if c.by_invdiv_div.short_name == d:
                if c.prj_id not in prj_ids:
                    prj_ids.append(c.prj_id)

        # Calc each project overall score
        for prj_id in prj_ids:
            list_of_csf_scores = []
            
            # Get project's feedback scores
            for c in csfs:
                if c.prj_id == prj_id and c.by_invdiv_div.short_name == d:
                    score = utils.calc_single_csf_score(c)
                    list_of_csf_scores.append(score)
            
            # Project Overall Score
            if list_of_csf_scores:
                score = sum(list_of_csf_scores) / len(list_of_csf_scores)
                list_of_prj_scores.append(round(score,2))

        if list_of_prj_scores:
            score = sum(list_of_prj_scores) / len(list_of_prj_scores)

            index = utils.find_index(res, "division", d)
            res[index]["by_division"] = round(score, 2)

    return res

@router.get('/csf/overall_csf/{year}')
def get_csf_donut_data(year: int, db: Session = Depends(get_db)):
    divs    = ["WBGM", "RBA", "BRDS", "TAD"]
    
    # Get All CSF where Project's year is {year}
    csfs = db.query(CSF).filter(
        CSF.prj.has(year=year)
    ).all()

    scores = []

    # Calc byInvDiv Score
    for d in divs:
        prj_ids = []
        list_of_prj_scores = []

        # Find Unique Project IDs of a div
        for c in csfs:
            if c.by_invdiv_div.short_name == d:
                if c.prj_id not in prj_ids:
                    prj_ids.append(c.prj_id)

        # Calc each project overall score
        for prj_id in prj_ids:
            list_of_csf_scores = []
            
            # Get project's feedback scores
            for c in csfs:
                if c.prj_id == prj_id and c.by_invdiv_div.short_name == d:
                    score = utils.calc_single_csf_score(c)
                    list_of_csf_scores.append(score)
            
            # Project Overall Score
            if list_of_csf_scores:
                score = sum(list_of_csf_scores) / len(list_of_csf_scores)
                list_of_prj_scores.append(round(score,2))

        if list_of_prj_scores:
            score = sum(list_of_prj_scores) / len(list_of_prj_scores)
            scores.append(round(score, 2))
        else:
            scores.append(0)
  
    avg = sum(scores) / len(scores)

    res = [
        {
            "title" : "score",
	        "rate"  : round(avg, 2)
        },
        {
            "title" : "",
	        "rate"  : round(4-avg, 2)
        }
    ]

    return res

### BUSU Engagement ###

# Input Table
@router.get('/engagement/input_table/{nik}/{year}')
def get_busu_input_table(nik: str, year: int, db: Session = Depends(get_db)):
    # Check NIK
    emp = get_emp_by_nik(nik, db)

    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    engs = db.query(BUSUEngagement).filter(
        BUSUEngagement.date >= startDate,
        BUSUEngagement.date <= endDate,
        BUSUEngagement.creator_id == emp.id
    ).all()

    res = []
    
    for e in engs:
        res.append({
            "id"        : str(e.id),
            "division"  : e.creator.part_of_div.short_name,
            "WorRM"     : e.eng_type.name,
            "activity"  : e.activity_name,
            "date"      : e.date.strftime("%m/%d/%Y")
        })
    
    return res

@router.post('/engagement/input_table/{nik}')
def create_busu_input_table_entry(nik: str, req: schemas.BUSUEngagementInHiCoupling, db: Session = Depends(get_db)):
    eng_types = ["Regular Meeting", "Workshop"]

    # Check NIK
    emp = get_emp_by_nik(nik, db)

    new_eng = BUSUEngagement(
        activity_name   = req.activity,
        date            = utils.tablestr_to_datetime(req.date),
        proof           = "",
        
        eng_type_id     = eng_types.index(req.WorRM) + 1,

        creator_id      = emp.id
    )

    db.add(new_eng)
    db.commit()
    db.refresh(new_eng)

    return new_eng

@router.patch('/engagement/input_table/{id}')
def patch_busu_input_table_entry(id:int, req: schemas.BUSUEngagementInHiCoupling, db: Session = Depends(get_db)):
    eng = db.query(BUSUEngagement).filter(
        BUSUEngagement.id == id
    ) 

    if not eng.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')


    stored_data = jsonable_encoder(eng.first())
    stored_model = schemas.BUSUEngagementIn(**stored_data)

    eng_types = ["Regular Meeting", "Workshop"]

    dataIn = schemas.BUSUEngagementIn(
        activity_name   = req.activity,
        date            = utils.tablestr_to_datetime(req.date),
        proof           = "",

        eng_type_id     = eng_types.index(req.WorRM) + 1
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    eng.update(stored_data)
    db.commit()
    return updated

@router.delete('/engagement/input_table/{id}')
def delete_busu_input_table_entry(id:int, db: Session = Depends(get_db)):
    eng = db.query(BUSUEngagement).filter(
        BUSUEngagement.id == id
    )

    if not eng.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')

    eng.delete()
    db.commit()

    return {'details': 'Deleted'}

# View Table
@router.get('/engagement/user_div_table/{nik}/{year}')
def get_view_busu_table(nik: str, year: int, db: Session = Depends(get_db)):
    # Check NIK
    emp = get_emp_by_nik(nik, db)

    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    engs = db.query(BUSUEngagement).filter(
        BUSUEngagement.date >= startDate,
        BUSUEngagement.date <= endDate,
        BUSUEngagement.creator.has(div_id= emp.div_id)
    ).all()

    res = []

    for e in engs:
        res.append({
            "id"        : str(e.id),
            "division"  : e.creator.part_of_div.short_name,
            "WorRM"     : e.eng_type.name,
            "activity"  : e.activity_name,
            "date"      : e.date.strftime("%m/%d/%Y")
        })
    
    return res

@router.get('/engagement/total_by_division/{year}')
def get_total_by_division_by_year(year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    query = db.query(BUSUEngagement).filter(
        BUSUEngagement.date >= startDate,
        BUSUEngagement.date <= endDate
    ).all()
    
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    res = []

    # Init result dict
    for div in divs:
        res.append({"quarterly_meeting":0, "workshop":0, "division":div})

    for q in query:
        eng_by_div = next((index for (index, d) in enumerate(res) if d["division"] == q.creator.part_of_div.short_name), None)

        if q.eng_type_id == 1:
            res[eng_by_div]["quarterly_meeting"] += 1
        if q.eng_type_id == 2:
            res[eng_by_div]["workshop"] += 1

    return res

### Attrition ###
def get_attr_summary_details_by_div_shortname(year: int, div: str, db: Session):
    """Returns a tuple of ints (join, resign, transfer_in, transfer_out, resign_in, resign_out, start_hc, curr_hc) given a div shortname and year"""
    
    yAttr = get_yAttr_by_div_shortname(year, div, db)
    div_id = yAttr.div_id

    join = resign = t_in = t_out = r_in = r_out = curr_hc = 0
    
    # Join, Resign, Transfer (jrt)
    attr_jrts = get_jrtAttrs(year, db, div_id=div_id)
    for a in attr_jrts:
        jrt_type = a.type.name

        join += 1   and jrt_type == "Join"
        resign += 1 and jrt_type == "Resign"
        t_in += 1   and jrt_type == "Transfer In"
        t_out += 1  and jrt_type == "Transfer Out"

    # Rotation (rot)
    attr_rots = get_rotAttrs(year, db, div_id=div_id)
    for b in attr_rots:
        r_in += 1   and b.to_div_id == div_id
        r_out += 1  and b.from_div_id == div_id

    # CurrentHC
    start_count = yAttr.start_headcount
    plus_count  = join + t_in + r_in
    minus_count = resign + t_out + r_out
    curr_hc = start_count + plus_count - minus_count

    return (join, resign, t_in, t_out, r_in, r_out, start_count, curr_hc)


@router.get('/attrition/staff_attrition/{year}')
def get_total_by_division_by_year(year: int, db: Session = Depends(get_db)):
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    res = []

    for div in divs:
        (join, resign, t_in, t_out, r_in, r_out, start_hc, curr_hc) = get_attr_summary_details_by_div_shortname(year, div, db)

        res.append({
            "headcounts"    :curr_hc,
            "join"          :join,
            "resign"        :resign,
            "transfer_in"   :t_in, 
            "transfer_out"  :t_out,
            "rotation_in"   :r_in, 
            "rotation_out"  :r_out, 
            "division"      :div
        })
    
    return res

@router.get('/attrition/rate_wbgm_testing/year/{year}')
def get_dynamic_attr_rate_byYear(year: int, db: Session = Depends(get_db)):
    """Temp EP for Daffa Testing WBGM Attr Rate Donut Chart"""
    divs    = ["WBGM"]

    res = []


    for index,div in enumerate(divs):
        (join, resign, t_in, t_out, r_in, r_out, start_hc, curr_hc) = get_attr_summary_details_by_div_shortname(year, div, db)

        attr_sum = resign + t_out + r_out
        attr_rate = (attr_sum / start_hc) * 100

        res = [{
            'id'        : index+1,
            'division'  : div,
            'rate'      : round(attr_rate, 2),
            'else_rate' : round(100-attr_rate,2),
            'title_rate': f'{div} Attrition Rate',
            'title_else': '',
            'text'      : f'Attrition Rate: {round(attr_rate, 2)}%'
        }]

    return res

@router.get('/attrition/rate_v4/year/{year}')
def get_dynamic_attr_rate_byYear(year: int, db: Session = Depends(get_db)):
    """Returns List of List of Dict"""
    divs    = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]

    res = []


    for index,div in enumerate(divs):
        (join, resign, t_in, t_out, r_in, r_out, start_hc, curr_hc) = get_attr_summary_details_by_div_shortname(year, div, db)

        attr_sum = resign + t_out + r_out
        attr_rate = (attr_sum / start_hc) * 100

        x = [{
            'id'        : index+1,
            'division'  : div,
            'rate'      : round(attr_rate, 2),
            'else_rate' : round(100-attr_rate,2),
            'title_rate': f'{div} Attrition Rate',
            'title_else': '',
            'text'      : f'Attrition Rate: {round(attr_rate, 2)}%'
        }]
        res.append(x)

    return res

@router.get('/attrition/rate_v3/year/{year}')
def get_dynamic_attr_rate_byYear(year: int, db: Session = Depends(get_db)):
    """Returns List of Dict"""

    divs    = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]

    res = []


    for index,div in enumerate(divs):
        (join, resign, t_in, t_out, r_in, r_out, start_hc, curr_hc) = get_attr_summary_details_by_div_shortname(year, div, db)

        attr_sum = resign + t_out + r_out
        attr_rate = (attr_sum / start_hc) * 100

        res.append({
            'id'        : index+1,
            'division'  : div,
            'rate'      : round(attr_rate, 2),
            'else_rate' : round(100-attr_rate,2),
            'title_rate': f'{div} Attrition Rate',
            'title_else': '',
            'text'      : f'Attrition Rate: {round(attr_rate, 2)}%'
        })

    return res

@router.get('/attrition/rate_v2/div/{div_name}/year/{year}')
def get_rate_by_division_by_yearmonth(div_name: str, year: int, db: Session = Depends(get_db)):
    (join, resign, t_in, t_out, r_in, r_out, start_hc, curr_hc) = get_attr_summary_details_by_div_shortname(year, div_name, db)


    attr_sum = resign + t_out + r_out
    attr_rate = (attr_sum / start_hc) * 100 

    return [
        {"title":"Attrition Rate","rate":f"{round(attr_rate, 2)}%"},
        {"title":"","rate":f"{round(100-attr_rate,2)}%"}
    ]

@router.get('/attrition/rate/{div_name}/{year}')
def get_rate_by_division_by_yearmonth(div_name: str, year: int, db: Session = Depends(get_db)):
    (join, resign, t_in, t_out, r_in, r_out, start_hc, curr_hc) = get_attr_summary_details_by_div_shortname(year, div_name, db)


    attr_sum = resign + t_out + r_out
    attr_rate = (attr_sum / start_hc) * 100 

    return [
        {"title":"Attrition Rate","rate":round(attr_rate, 2)},
        {"title":"","rate":round(100-attr_rate,2)}
    ]

### Admin ###

# Maintenance
@router.get('/admin/maintenance')
def get_maintenance_status(db: Session = Depends(get_db)):
    state_name = "Maintenance"
    mState_query = db.query(ServerState).filter(
        ServerState.name == state_name
    )

    try:
        mState = mState_query.one_or_none()
    except MultipleResultsFound:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Found multiple state with name ({state_name})")

    if mState:
        return {'is_maintenance_mode': mState.value}
    else:
        newState = ServerState(
            name    = state_name,
            value   = False
        )

        db.add(newState)
        db.commit()
        db.refresh(newState)

        return {'is_maintenance_mode': newState.value}

@router.post('/admin/maintenance')
def toggle_maintenance_status(db: Session = Depends(get_db)):
    state_name = "Maintenance"

    mState_query = db.query(ServerState).filter(
        ServerState.name == state_name
    )

    try:
        mState = mState_query.one_or_none()
    except MultipleResultsFound:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Found multiple state with name ({state_name})")
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Found no states with name ({state_name})")

    stored_data = jsonable_encoder(mState)
    stored_model = schemas.ServerStateIn(**stored_data)

    new_data = {'value': not mState.value}
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    mState_query.update(stored_data)
    db.commit()

    return {'is_maintenance_mode': new_data['value']}

# QA Result
@router.get('/admin/qaip_data/table_data/{year}')
def get_qaip_table(year: int, db: Session = Depends(get_db)):
    qaips = db.query(QAIP).filter(
        QAIP.prj.has(year=year)
    ).all()

    res = []

    for q in qaips:
        cats    = utils.qa_to_category_str(q)
        stages  = utils.qa_to_stage_str(q)
        delivs  = utils.qa_to_delivs_str(q)

        # Get DH Name
        dh = get_emp(q.prj.div.dh_id, db)

        res.append({
            "id"            : str(q.id),
            "QAType"        : q.qa_type.name,
            "auditProject"  : q.prj.name,
            "TL"            : q.prj.tl.name,
            "divisionHead"  : dh.name,
            "result"        : q.qa_grading_result.name,
            "category"      : ", ".join(cats),
            "stage"         : ", ".join(stages),
            "deliverable"   : ", ".join(delivs),
            "noOfIssues"    : len(delivs),
            "QASample"      : q.qa_sample
        })
    
    return res

@router.patch('/admin/qaip_data/form')
def patch_qaip_entry(req: schemas.QAIPFormInHiCoupling, db: Session = Depends(get_db)):
    qaip = db.query(QAIP).filter(
        QAIP.prj.has(name=req.projectTitle),
        QAIP.prj.has(year=req.year)
    )

    if not qaip.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Project with name ({req.projectTitle}) and year ({req.year}) was not found!')

    qaip = db.query(QAIP).filter(
        QAIP.id == qaip.first().id
    )

    qaip_model = qaip.first()

    stored_data = jsonable_encoder(qaip_model)
    stored_model = schemas.QAIPIn(**stored_data)

    # Data Validation
    type_id     = utils.qa_type_str_to_id(req.QAType)
    gradRes_id  = utils.qa_gradingres_str_to_id(req.QAResults)

    if not type_id or not gradRes_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong QAType or QAResults')

    # Patch Entry
    dataIn = schemas.QAIP(
        prj_id                      = qaip_model.prj_id,

        qa_type_id                  = type_id,
        qa_grading_result_id        = gradRes_id,

        qaf_category_clarity        = req.qaf_category_clarity,
        qaf_category_completeness   = req.qaf_category_completeness,
        qaf_category_consistency    = req.qaf_category_consistency,
        qaf_category_others         = req.qaf_category_others,
        qaf_stage_planning          = req.qaf_stage_planning,
        qaf_stage_fieldwork         = req.qaf_stage_fieldwork,
        qaf_stage_reporting         = req.qaf_stage_reporting,
        qaf_stage_post_audit_act    = req.qaf_stage_post_audit_act,
        qaf_deliverables_1a         = req.qaf_deliverables_1a,
        qaf_deliverables_1b         = req.qaf_deliverables_1b,
        qaf_deliverables_1c         = req.qaf_deliverables_1c,
        qaf_deliverables_1d         = req.qaf_deliverables_1d,
        qaf_deliverables_1e         = req.qaf_deliverables_1e,
        qaf_deliverables_1f         = req.qaf_deliverables_1f,
        qaf_deliverables_1g         = req.qaf_deliverables_1g,
        qaf_deliverables_1h         = req.qaf_deliverables_1h,
        qaf_deliverables_1i         = req.qaf_deliverables_1i,
        qaf_deliverables_1j         = req.qaf_deliverables_1j,
        qaf_deliverables_1k         = req.qaf_deliverables_1k,
        qaf_deliverables_2          = req.qaf_deliverables_2,
        qaf_deliverables_3          = req.qaf_deliverables_3,
        qaf_deliverables_4          = req.qaf_deliverables_4,
        qaf_deliverables_5          = req.qaf_deliverables_5,
        qaf_deliverables_6          = req.qaf_deliverables_6,
        qaf_deliverables_7          = req.qaf_deliverables_7,
        qa_sample                   = req.qa_sample
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    qaip.update(stored_data)
    db.commit()
    return updated

# Budget
@router.get('/admin/budget_data/table_data/{year}/{month}')
def get_budget_table(year: int, month: int, db: Session = Depends(get_db)):
    cats = [
        "Staff Expense",
        "Staff Expense (Salaries)",
        "Staff Training & Regional Meeting",
        "Revenue Related (Communications)",
        "IT Related (Softwares)",
        "Occupancy Related (Premises)",
        "Other Related",
        "Transport & Travel",
        "Others",
        "Direct Expense",
        "Indirect Expense"
    ]

    i = 1
    res = []
    for c in cats:
        res.append({
            "id"                : str(i),
            "expenses"          : c,
            "budgetYear"        : 0,
            "budgetMonth"       : 0,
            "budgetMonthTD"     : 0,
            "actualMonth"       : 0,
            "actualMonthTD"     : 0,
            "MTD"               : '-',
            "YTD"               : '-',
            "STDProRate"        : '-',
            "overUnderBudget"   : '-',
            "variance"          : ''
        })
        i += 1

    # Get Actual Budget
    actualBudget = db.query(MonthlyActualBudget).filter(
        MonthlyActualBudget.year == year,
        MonthlyActualBudget.month == month
    ).first()

    if actualBudget:
        res[0]["actualMonth"]   = actualBudget.staff_salaries + actualBudget.staff_training_reg_meeting
        res[1]["actualMonth"]   = actualBudget.staff_salaries
        res[2]["actualMonth"]   = actualBudget.staff_training_reg_meeting
        res[3]["actualMonth"]   = actualBudget.revenue_related
        res[4]["actualMonth"]   = actualBudget.it_related
        res[5]["actualMonth"]   = actualBudget.occupancy_related
        res[6]["actualMonth"]   = actualBudget.other_transport_travel + actualBudget.other_other
        res[7]["actualMonth"]   = actualBudget.other_transport_travel
        res[8]["actualMonth"]   = actualBudget.other_other
        res[9]["actualMonth"]   = res[0]["actualMonth"] + res[3]["actualMonth"] + res[4]["actualMonth"] + res[5]["actualMonth"] + res[6]["actualMonth"]
        res[10]["actualMonth"]  = actualBudget.indirect_expense

    actualBudgets = db.query(MonthlyActualBudget).filter(
        MonthlyActualBudget.year == year,
        MonthlyActualBudget.month <= month
    ).all()

    for a in actualBudgets:
        res[0]["actualMonthTD"]   += a.staff_salaries + a.staff_training_reg_meeting
        res[1]["actualMonthTD"]   += a.staff_salaries
        res[2]["actualMonthTD"]   += a.staff_training_reg_meeting

        res[3]["actualMonthTD"]   += a.revenue_related
        res[4]["actualMonthTD"]   += a.it_related
        res[5]["actualMonthTD"]   += a.occupancy_related

        res[6]["actualMonthTD"]   += a.other_transport_travel + a.other_other
        res[7]["actualMonthTD"]   += a.other_transport_travel
        res[8]["actualMonthTD"]   += a.other_other

        res[9]["actualMonthTD"]   += res[0]["actualMonthTD"] + res[3]["actualMonthTD"] + res[4]["actualMonthTD"] + res[5]["actualMonthTD"] + res[6]["actualMonthTD"]
        res[10]["actualMonthTD"]  += a.indirect_expense

    # Get Yearly Budget
    y = db.query(YearlyBudget).filter(
        YearlyBudget.year == year
    ).first()

    if y:
        res[0]["budgetYear"]   += y.staff_salaries + y.staff_training_reg_meeting
        res[1]["budgetYear"]   += y.staff_salaries
        res[2]["budgetYear"]   += y.staff_training_reg_meeting

        res[3]["budgetYear"]   += y.revenue_related
        res[4]["budgetYear"]   += y.it_related
        res[5]["budgetYear"]   += y.occupancy_related

        res[6]["budgetYear"]   += y.other_transport_travel + y.other_other
        res[7]["budgetYear"]   += y.other_transport_travel
        res[8]["budgetYear"]   += y.other_other

        res[9]["budgetYear"]   += res[0]["budgetYear"] + res[3]["budgetYear"] + res[4]["budgetYear"] + res[5]["budgetYear"] + res[6]["budgetYear"]
        res[10]["budgetYear"]  += y.indirect_expense

    # Get Monthly Budgets
    monthlyBudget = db.query(MonthlyBudget).filter(
        MonthlyBudget.year == year,
        MonthlyBudget.month == month
    ).first()

    if monthlyBudget:
        res[0]["budgetMonth"]   += monthlyBudget.staff_salaries + monthlyBudget.staff_training_reg_meeting
        res[1]["budgetMonth"]   += monthlyBudget.staff_salaries
        res[2]["budgetMonth"]   += monthlyBudget.staff_training_reg_meeting
        res[3]["budgetMonth"]   += monthlyBudget.revenue_related
        res[4]["budgetMonth"]   += monthlyBudget.it_related
        res[5]["budgetMonth"]   += monthlyBudget.occupancy_related
        res[6]["budgetMonth"]   += monthlyBudget.other_transport_travel + monthlyBudget.other_other
        res[7]["budgetMonth"]   += monthlyBudget.other_transport_travel
        res[8]["budgetMonth"]   += monthlyBudget.other_other
        res[9]["budgetMonth"]   += res[0]["budgetMonth"] + res[3]["budgetMonth"] + res[4]["budgetMonth"] + res[5]["budgetMonth"] + res[6]["budgetMonth"]
        res[10]["budgetMonth"]  += monthlyBudget.indirect_expense
    
    monthlyBudgets = db.query(MonthlyBudget).filter(
        MonthlyBudget.year == year,
        MonthlyBudget.month <= month
    ).all()

    for m in monthlyBudgets:
        res[0]["budgetMonthTD"]   += m.staff_salaries + m.staff_training_reg_meeting
        res[1]["budgetMonthTD"]   += m.staff_salaries
        res[2]["budgetMonthTD"]   += m.staff_training_reg_meeting
        res[3]["budgetMonthTD"]   += m.revenue_related
        res[4]["budgetMonthTD"]   += m.it_related
        res[5]["budgetMonthTD"]   += m.occupancy_related
        res[6]["budgetMonthTD"]   += m.other_transport_travel + m.other_other
        res[7]["budgetMonthTD"]   += m.other_transport_travel
        res[8]["budgetMonthTD"]   += m.other_other
        res[9]["budgetMonthTD"]   += res[0]["budgetMonthTD"] + res[3]["budgetMonthTD"] + res[4]["budgetMonthTD"] + res[5]["budgetMonthTD"] + res[6]["budgetMonthTD"]
        res[10]["budgetMonthTD"]  += m.indirect_expense

    # Process Statistics
    for r in res:
        mtd_rate = r["actualMonthTD"] / r["budgetMonthTD"] if r["budgetMonthTD"] != 0 else None
        ytd_rate = r["actualMonthTD"] / r["budgetYear"] if r["budgetYear"] != 0 else None
        std_rate = month / 12

        r["MTD"]               = "-%" if mtd_rate == None else f"{round(mtd_rate * 100)}%"
        r["YTD"]               = "-%" if ytd_rate == None else f"{round(ytd_rate * 100)}%"
        r["STDProRate"]        = f"{round(std_rate * 100)}%"
        r["overUnderBudget"]   = "-%" if ytd_rate == None else f"{round((ytd_rate - std_rate) * 100)}%"

    # Format Numbering
    res = utils.format_budget_numbering(res)

    return res

@router.patch('/admin/budget_data/table_data/{year}/{month}', status_code=status.HTTP_202_ACCEPTED)
def patch_budget_table_entry(year: int, month: int, req: schemas.BudgetTableInHiCoupling, db: Session = Depends(get_db)):
    cats = [
        "Staff Expense",
        "Staff Expense (Salaries)",
        "Staff Training & Regional Meeting",
        "Revenue Related (Communications)",
        "IT Related (Softwares)",
        "Occupancy Related (Premises)",
        "Other Related",
        "Transport & Travel",
        "Others",
        "Direct Expense",
        "Indirect Expense"
    ]

    formulated_cats = [0, 6, 9]

    # Check Expense Type
    cat_index = -1
    if not req.expenses in cats:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Given Expense field ({req.expenses}) is not allowed")
    elif cats.index(req.expenses) in formulated_cats:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Given Expense field ({req.expenses}) is formulated value (Cannot be modified)")
    else:
        cat_index = cats.index(req.expenses)

    # Set Budget Year
    yearBudget = db.query(YearlyBudget).filter(
        YearlyBudget.year == year
    )

    try:
        yearBudget_model = yearBudget.one_or_none()
    except MultipleResultsFound:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Multiple YearlyBudget entries for given year ({year}) were found!")

    if not yearBudget_model: # No YearlyBudget was found
        # Create a new Yearly Budget
        payload = {}

        for c in cats:
            payload[c] = 0

        payload[req.expenses] = req.budgetYear

        newYearBudget = YearlyBudget(
            year                        = year,
            staff_salaries              = payload["Staff Expense (Salaries)"],
            staff_training_reg_meeting  = payload["Staff Training & Regional Meeting"],
            revenue_related             = payload["Revenue Related (Communications)"],
            it_related                  = payload["IT Related (Softwares)"],
            occupancy_related           = payload["Occupancy Related (Premises)"],
            other_transport_travel      = payload["Transport & Travel"],
            other_other                 = payload["Others"],
            indirect_expense            = payload["Indirect Expense"]
        )

        db.add(newYearBudget)
        db.commit()
        db.refresh(newYearBudget)
    else: # Existing YearlyBudget was found 
        stored_data = jsonable_encoder(yearBudget_model)
        stored_model = schemas.YearlyBudgetIn(**stored_data)

        payload = schemas.YearlyBudgetIn()

        if req.expenses == cats[1]:
            payload.staff_salaries = req.budgetYear
        elif req.expenses == cats[2]:
            payload.staff_training_reg_meeting = req.budgetYear
        elif req.expenses == cats[3]:
            payload.revenue_related = req.budgetYear
        elif req.expenses == cats[4]:
            payload.it_related = req.budgetYear
        elif req.expenses == cats[5]:
            payload.occupancy_related = req.budgetYear
        elif req.expenses == cats[7]:
            payload.other_transport_travel = req.budgetYear
        elif req.expenses == cats[8]:
            payload.other_other = req.budgetYear
        elif req.expenses == cats[10]:
            payload.indirect_expense = req.budgetYear

        new_data = payload.dict(exclude_unset=True)
        updated = stored_model.copy(update=new_data)

        stored_data.update(updated)

        yearBudget.update(stored_data)
        db.commit()

    # Set Budget Month
    monthBudget = db.query(MonthlyBudget).filter(
        MonthlyBudget.year == year,
        MonthlyBudget.month == month
    )

    try:
        monthBudget_model = monthBudget.one_or_none()
    except MultipleResultsFound:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Multiple MonthBudget entries for given year/month ({year}/{month}) were found!")

    if not monthBudget_model: # No MonthlyBudget was found
        # Create a new Yearly Budget
        payload = {}

        for c in cats:
            payload[c] = 0

        payload[req.expenses] = req.budgetMonth

        newMonthBudget = MonthlyBudget(
            year                        = year,
            month                       = month,
            staff_salaries              = payload["Staff Expense (Salaries)"],
            staff_training_reg_meeting  = payload["Staff Training & Regional Meeting"],
            revenue_related             = payload["Revenue Related (Communications)"],
            it_related                  = payload["IT Related (Softwares)"],
            occupancy_related           = payload["Occupancy Related (Premises)"],
            other_transport_travel      = payload["Transport & Travel"],
            other_other                 = payload["Others"],
            indirect_expense            = payload["Indirect Expense"]
        )

        db.add(newMonthBudget)
        db.commit()
        db.refresh(newMonthBudget)
    else: # Existing MonthlyBudget was found 
        stored_data = jsonable_encoder(monthBudget_model)
        stored_model = schemas.MonthlyBudgetIn(**stored_data)

        payload = schemas.MonthlyBudgetIn()

        if req.expenses == cats[1]:
            payload.staff_salaries = req.budgetYear
        elif req.expenses == cats[2]:
            payload.staff_training_reg_meeting = req.budgetYear
        elif req.expenses == cats[3]:
            payload.revenue_related = req.budgetYear
        elif req.expenses == cats[4]:
            payload.it_related = req.budgetYear
        elif req.expenses == cats[5]:
            payload.occupancy_related = req.budgetYear
        elif req.expenses == cats[7]:
            payload.other_transport_travel = req.budgetYear
        elif req.expenses == cats[8]:
            payload.other_other = req.budgetYear
        elif req.expenses == cats[10]:
            payload.indirect_expense = req.budgetYear

        new_data = payload.dict(exclude_unset=True)
        updated = stored_model.copy(update=new_data)

        stored_data.update(updated)

        monthBudget.update(stored_data)
        db.commit()

    
    # Set Actual Month
    actualMonthBudget = db.query(MonthlyActualBudget).filter(
        MonthlyActualBudget.year == year,
        MonthlyActualBudget.month == month
    )

    try:
        actualMonthBudget_model = actualMonthBudget.one_or_none()
    except MultipleResultsFound:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Multiple ActualMonthBudget entries for given year/month ({year}/{month}) were found!")

    if not actualMonthBudget_model: # No ActualMonthlyBudget was found
        # Create a new Actual Monthly Budget
        payload = {}

        for c in cats:
            payload[c] = 0

        payload[req.expenses] = req.actualMonth

        newActualMonthBudget = MonthlyActualBudget(
            year                        = year,
            month                       = month,
            staff_salaries              = payload["Staff Expense (Salaries)"],
            staff_training_reg_meeting  = payload["Staff Training & Regional Meeting"],
            revenue_related             = payload["Revenue Related (Communications)"],
            it_related                  = payload["IT Related (Softwares)"],
            occupancy_related           = payload["Occupancy Related (Premises)"],
            other_transport_travel      = payload["Transport & Travel"],
            other_other                 = payload["Others"],
            indirect_expense            = payload["Indirect Expense"],
            remark                      = ""
        )

        db.add(newActualMonthBudget)
        db.commit()
        db.refresh(newActualMonthBudget)
    else: # Existing ActualMonthlyBudget was found 
        stored_data = jsonable_encoder(actualMonthBudget_model)
        stored_model = schemas.MonthlyActualBudgetIn(**stored_data)

        payload = schemas.MonthlyActualBudgetIn()

        if req.expenses == cats[1]:
            payload.staff_salaries = req.budgetYear
        elif req.expenses == cats[2]:
            payload.staff_training_reg_meeting = req.budgetYear
        elif req.expenses == cats[3]:
            payload.revenue_related = req.budgetYear
        elif req.expenses == cats[4]:
            payload.it_related = req.budgetYear
        elif req.expenses == cats[5]:
            payload.occupancy_related = req.budgetYear
        elif req.expenses == cats[7]:
            payload.other_transport_travel = req.budgetYear
        elif req.expenses == cats[8]:
            payload.other_other = req.budgetYear
        elif req.expenses == cats[10]:
            payload.indirect_expense = req.budgetYear

        new_data = payload.dict(exclude_unset=True)
        updated = stored_model.copy(update=new_data)

        stored_data.update(updated)

        actualMonthBudget.update(stored_data)
        db.commit()

# CSF
@router.get('/admin/csf_data/table_data/{year}')
def get_csf_table(year: int, db: Session = Depends(get_db)):
    prjs = db.query(Project).filter(
        Project.year == year
    ).all()

    prj_ids = [p.id for p in prjs]

    csfs = db.query(CSF).filter(
        CSF.prj_id.in_(prj_ids)
    ).all()

    res = []

    for c in csfs:
        sum_atp = c.atp_1 + c.atp_2 + c.atp_3 + c.atp_4 + c.atp_5 + c.atp_6
        avg_atp = round(sum_atp / 6, 2)

        sum_ac = c.ac_1 + c.ac_2 + c.ac_3 + c.ac_4 + c.ac_5 + c.ac_6
        avg_ac = round(sum_ac / 6, 2)

        sum_paw = c.paw_1 + c.paw_2 + c.paw_3
        avg_paw = round(sum_paw / 3, 2)       

        avg = round((avg_ac + avg_atp + avg_paw)/3, 2)

        res.append({
            'id'                : str(c.id),
            'division_project'  : c.prj.div.short_name,
            'auditProject'      : str(c.prj_id),
            'clientName'        : c.client_name,
            'unitJabatan'       : c.client_unit,
            'TL'                : c.prj.tl.name,
            'CSFDate'           : utils.date_to_str(c.csf_date),
            'atp1'              : c.atp_1,
            'atp2'              : c.atp_2,
            'atp3'              : c.atp_3,
            'atp4'              : c.atp_4,
            'atp5'              : c.atp_5,
            'atp6'              : c.atp_6,
            'atpOverall'        : avg_atp,
            'ac1'               : c.ac_1,
            'ac2'               : c.ac_2,
            'ac3'               : c.ac_3,
            'ac4'               : c.ac_4,
            'ac5'               : c.ac_5,
            'ac6'               : c.ac_6,
            'acOverall'         : avg_ac,
            'paw1'              : c.paw_1,
            'paw2'              : c.paw_2,
            'paw3'              : c.paw_3,
            'pawOverall'        : avg_paw,
            'overall'           : avg,
            'division_by_inv'   : c.by_invdiv_div.short_name
        })

    return res

@router.post('/admin/csf_data/table_data', status_code=status.HTTP_201_CREATED)
def create_csf_table_entry(req: schemas.CSFInHiCoupling, db: Session = Depends(get_db)):
    invdiv_id = utils.div_str_to_divID(req.division_by_inv)
    
    if not invdiv_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Div Name not found')

    prj_id = utils.str_to_int_or_None(req.auditProject)
    if not prj_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Audit Project must be an ID')
    
    prj = db.query(Project).filter(Project.id == prj_id)
    if not prj.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Audit Project must be an ID of an existing project')
    
    new_csf = CSF(
        client_name         = req.clientName,
        client_unit         = req.unitJabatan,
        csf_date            = utils.tablestr_to_datetime(req.CSFdate),
        atp_1               = req.atp1,
        atp_2               = req.atp2,
        atp_3               = req.atp3,
        atp_4               = req.atp4,
        atp_5               = req.atp5,
        atp_6               = req.atp6,
        ac_1                = req.ac1,
        ac_2                = req.ac2,
        ac_3                = req.ac3,
        ac_4                = req.ac4,
        ac_5                = req.ac5,
        ac_6                = req.ac6,
        paw_1               = req.paw1,
        paw_2               = req.paw2,
        paw_3               = req.paw3,

        prj_id              = prj_id,
        by_invdiv_div_id    = invdiv_id
    )

    db.add(new_csf)
    db.commit()
    db.refresh(new_csf)

    return new_csf

@router.patch('/admin/csf_data/table_data/{id}', status_code=status.HTTP_202_ACCEPTED)
def patch_csf_table_entry(id: int, req: schemas.CSFInHiCoupling, db: Session = Depends(get_db)):
    csf = db.query(CSF).filter(
        CSF.id == id
    )

    if not csf.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    stored_data = jsonable_encoder(csf.first())
    stored_model = schemas.CSFIn(**stored_data)

    # Data Validation
    invdiv_id = utils.div_str_to_divID(req.division_by_inv)
    
    if not invdiv_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Div Name not found')

    prj_id = utils.str_to_int_or_None(req.auditProject)
    if not prj_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Audit Project must be an ID')
    
    prj = db.query(Project).filter(Project.id == prj_id)
    if not prj.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Audit Project must be an ID of an existing project')
    
    dataIn = schemas.CSF(
        client_name         = req.clientName,
        client_unit         = req.unitJabatan,
        csf_date            = utils.tablestr_to_datetime(req.CSFDate),
        atp_1               = req.atp1,
        atp_2               = req.atp2,
        atp_3               = req.atp3,
        atp_4               = req.atp4,
        atp_5               = req.atp5,
        atp_6               = req.atp6,
        ac_1                = req.ac1,
        ac_2                = req.ac2,
        ac_3                = req.ac3,
        ac_4                = req.ac4,
        ac_5                = req.ac5,
        ac_6                = req.ac6,
        paw_1               = req.paw1,
        paw_2               = req.paw2,
        paw_3               = req.paw3,

        prj_id              = prj_id,
        by_invdiv_div_id    = invdiv_id
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    csf.update(stored_data)
    db.commit()
    return updated

@router.delete('/admin/csf_data/table_data/{id}')
def delete_csf_table_entry(id: int, db: Session = Depends(get_db)):
    c = db.query(CSF).filter(
        CSF.id == id
    )

    if not c.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    c.delete()
    db.commit()

    return {'details': 'Deleted'}

# Division
@router.get('/admin/division_table_data')
def get_division_table(db: Session = Depends(get_db)):
    divs = db.query(Division).all()

    res = []

    for d in divs:
        dh = get_emp(d.dh_id, db)

        res.append({
            "id"            : d.id,
            "short_name"    : d.short_name,
            "long_name"     : d.long_name,
            "dh_id"         : dh.staff_id if dh else "",
            "dh_name"       : dh.name if dh else ""
        })

    return res

@router.post('/admin/division_table_data')
def create_division_table_entry(req: schemas.DivisionInHiCoupling, db: Session = Depends(get_db)):
    # Check NIK
    dh = get_emp_by_nik(req.dh_id, db)
    
    new_div = Division(
        short_name  = req.short_name,
        long_name   = req.long_name,
        dh_id       = dh.id if dh else None
    )

    db.add(new_div)
    db.commit()
    db.refresh(new_div)

    return new_div

@router.patch('/admin/division_table_data/{id}')
def patch_division_table_entry(id: int, req: schemas.DivisionInHiCoupling, db: Session = Depends(get_db)):
    div = db.query(Division).filter(
        Division.id == id
    )

    if not div.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    stored_data = jsonable_encoder(div.first())
    stored_model = schemas.DivisionIn(**stored_data)

    dh = get_emp_by_nik(req.dh_id, db)

    dataIn = schemas.DivisionIn(
        short_name  = req.short_name,
        long_name   = req.long_name,
        dh_id       = dh.id if dh else None
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    div.update(stored_data)
    db.commit()

    return updated

@router.delete('/admin/division_table_data/{id}')
def delete_division_table_entry(id: int, db: Session = Depends(get_db)):
    d = db.query(Division).filter(
        Division.id == id
    )

    if not d.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    d.delete()
    db.commit()

    return {'details': 'Deleted'}

# Employee
@router.post('/admin/change_password')
def change_password_admin(req: schemas.PasswordChangeAdminIn, db: Session = Depends(get_db)):
    # Check NIK
    emp_query = db.query(Employee).filter(
        Employee.staff_id == req.nik,
        Employee.active == True
    )

    if not emp_query.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Employee of NIK ({req.nik}) was not found')

    emp = emp_query.first()

    # Update new_pw
    stored_data = jsonable_encoder(emp)
    stored_model = schemas.EmployeeIn(**stored_data)

    new_data = {'pw': hashing.bcrypt(req.new_pw)}
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    emp_query.update(stored_data)
    db.commit()

    return {'detail':'Password Change Success!'}

@router.get('/admin/employee/tables/cert/nik/{nik}')
def get_employee_cert_table(nik: str, db: Session = Depends(get_db)):
    emp = get_emp_by_nik(nik, db)

    res = []

    for c in emp.emp_certifications:
        if not c.owner.active:
            continue

        res.append({
            "id"              : c.id,
            "employee_name"   : emp.name,
            "certifcate_name" : c.cert_name
        })
    
    return res

@router.delete('/admin/employee/tables/cert/id/{id}')
def delete_employee_cert_table_entry(id: int, db: Session = Depends(get_db)):
    c = get_cert_by_id(id, db)

    c_q = db.query(Certification).filter(
        Certification.id == c.id
    )

    c_q.delete()
    db.commit()

    return {'details': 'Deleted'}

@router.get('/admin/employee_data/table_data')
def get_employee_table(db: Session = Depends(get_db)):
    emps = get_all_active_emps(db)

    res = []

    for e in emps:
        as_of_now       = datetime.date.today().strftime("%m/%d/%Y")
        age             = utils.get_year_diff_to_now(e.date_of_birth)
        gen             = utils.get_gen(e.date_of_birth)
        auditUOBYears   = utils.get_year_diff_to_now(e.date_first_uob)

        # Process Certs
        certs = [
            "SMR", "CISA", "CEH", "ISO27001", "CHFI", 
            "IDEA", "QualifiedIA", "CBIA", "CIA", "CPA", "CA"]

        cert_res = []

        for c in certs:
            cert_res.append({
                'title': c,
                'value': 0
            })

        otherCerts = []
        max_smr = 0

        for c in e.emp_certifications:
            # SMR (Levels)
            smr_level = utils.extract_SMR_level(c.cert_name)
            
            if smr_level: # SMR
                if c.cert_proof:
                    if smr_level > max_smr:
                        cert_res[0]['value'] = smr_level
                        max_smr = smr_level
            elif c.cert_name == "SMR In Progress":
                cert_res[0]['value'] = "In Progress"
            elif c.cert_name in certs and c.cert_proof: # Pro Certs
                index = utils.find_index(cert_res, 'title', c.cert_name)
                cert_res[index]['value'] = 1
            elif c.cert_proof:                          # Other Certs
                otherCerts.append(c.cert_name)

        smr_lvl = cert_res[0]['value']

        if smr_lvl == "In Progress":
            smr_str = smr_lvl
        elif smr_lvl:
            smr_str = f"Level {smr_lvl}"
        else:
            smr_str = "-"

        res.append({
            "id"                          : e.id,
            "staffNIK"                    : e.staff_id,
            "staffName"                   : e.name,
            "email"                       : e.email,
            "role"                        : e.role.name,
            "divison"                     : e.part_of_div.id,
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
            "ISO27001"                    : cert_res[3]['value'],
            "CHFI"                        : cert_res[4]['value'],
            "IDEA"                        : cert_res[5]['value'],
            "QualifiedIA"                 : cert_res[6]['value'],
            "CBIA"                        : cert_res[7]['value'],
            "CIA"                         : cert_res[8]['value'],
            "CPA"                         : cert_res[9]['value'],
            "CA"                          : cert_res[10]['value'],
            "other_cert"                  : ", ".join(otherCerts),
            "IABackgground"               : e.ia_background,
            "EABackground"                : e.ea_background,
            "active"                      : e.active
        })

    return res

@router.post('/admin/employee_data/table_data')
def create_employee_table_entry(req: schemas.EmployeeInHiCoupling, db: Session = Depends(get_db)):
    # Create Employee Data
    emp = _create_employee_from_table(req, db)
    return emp

@router.patch('/admin/employee_data/table_data/{id}')
def patch_employee_table_entry(id: int, req: schemas.EmployeeInHiCoupling, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(
        Employee.id == id,
        Employee.active == True
    )

    if not emp.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    stored_data = jsonable_encoder(emp.first())
    stored_model = schemas.EmployeeIn(**stored_data)

    # Check Division ID
    div_q = db.query(Division).filter(
        Division.id == req.divison
    )

    try:
        div = div_q.one()
    except MultipleResultsFound:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Multiple Division of ID ({req.divison}) was found!')
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'No Division of ID ({req.divison}) was found!')

    dataIn = schemas.Employee(
        name    = req.staffName,
        email   = req.email,
        pw      = emp.first().pw,

        staff_id                = req.staffNIK,
        div_stream              = req.stream,
        corporate_title         = req.corporateTitle,
        corporate_grade         = req.corporateGrade,
        date_of_birth           = utils.tablestr_to_datetime(req.dateOfBirth),
        date_first_employment   = utils.tablestr_to_datetime(req.dateStartFirstEmployment),
        date_first_uob          = utils.tablestr_to_datetime(req.dateJoinUOB),
        date_first_ia           = utils.tablestr_to_datetime(req.dateJoinIAFunction),
        gender                  = req.gender,
        year_audit_non_uob      = req.auditNonUOBExp,
        edu_level               = req.educationLevel,
        edu_major               = req.educationMajor,
        edu_category            = req.educationCategory,
        ia_background           = req.IABackgground,
        ea_background           = req.EABackground,
        active                  = req.active,

        div_id = div.id,
        role_id = utils.role_str_to_id(req.role)
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    emp.update(stored_data)
    db.commit()

    # Handle SMR In Progress Edits
    # 1. "-"
    # 2. "In Progress"
    emp = db.query(Employee).filter(
        Employee.id == id
    ).first()

    if req.RMGCertification == "In Progress":
        # Check level SMR si Emp
        max_smr_level   = 0
        has_progress    = False

        for c in emp.emp_certifications:
            smr_level = utils.extract_SMR_level(c.cert_name)
            if smr_level:
                if smr_level > max_smr_level:
                    max_smr_level = smr_level
            elif c.cert_name == "SMR In Progress":
                has_progress = True

        # Need to create SMR In Progress?
        if not has_progress and max_smr_level == 0:
            # Create SMR In Progress
            new_cert = Certification(
                cert_name   = "SMR In Progress",
                cert_proof  = "",
                emp_id      = emp.id
            )

            db.add(new_cert)
            db.commit()
            db.refresh(new_cert)

    return updated

@router.delete('/admin/employee_data/table_data/{id}')
def delete_employee_table_entry(id: int, db: Session = Depends(get_db)):
    e = db.query(Employee).filter(
        Employee.id == id
    )

    if not e.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    e.delete()
    db.commit()

    return {'details': 'Deleted'}

# Training
@router.post('/admin/training_announcement_form')
def post_training_annoucement(req: schemas.AnnouncementCreate, db: Session = Depends(get_db)):
    #Check Existing
    ann_query = db.query(Annoucement).filter(
        Annoucement.type_name == "Training"
    )

    try:
        ann = ann_query.one_or_none()
    except MultipleResultsFound:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Multiple Training Announcement was found')

    if not ann:
        newAnnoucement = Annoucement(
            type_name   = "Training",
            body        = req.body
        )

        db.add(newAnnoucement)
        db.commit()
        db.refresh(newAnnoucement)

        return newAnnoucement
    else:
        stored_data = jsonable_encoder(ann)
        stored_model = schemas.AnnouncementCreate(**stored_data)

        new_data = req.dict(exclude_unset=True)
        updated = stored_model.copy(update=new_data)

        stored_data.update(updated)

        ann_query.update(stored_data)
        db.commit()
        return updated
        
@router.get('/admin/training_data/table_data/{year}')
def get_training_table(year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)
    
    training = db.query(Training).filter(
        Training.date >= startDate,
        Training.date <= endDate
    ).all()

    res = []

    for t in training:
        if not t.employee.active:
            continue

        divison = t.employee.part_of_div.short_name if t.employee else ""
        emp_name= t.employee.name if t.employee else ""
        emp_nik = t.employee.staff_id if t.employee else ""

        res.append({
            "id"                : str(t.id),
            "division"          : divison,
            "name"              : emp_name,
            "nik"               : emp_nik,
            "trainingTitle"     : t.name,
            "date"              : t.date.strftime("%m/%d/%Y"),
            "numberOfHours"     : t.duration_hours,
            "budget"            : t.budget,
            "costRealization"   : t.realization,
            "chargedByFinance"  : t.charged_by_fin,
            "mandatoryFrom"     : t.mandatory_from,
            "remark"            : t.remark
        })

    return res

@router.post('/admin/training_data/table_data/')
def create_training_table_entry(req: schemas.TrainingInHiCoupling, db: Session = Depends(get_db)):    
    emp = get_emp_by_nik(req.nik, db)

    new_train = Training(
        name            = req.trainingTitle,
        date            = utils.tablestr_to_datetime(req.date),
        duration_hours  = req.numberOfHours,
        proof           = "",
        budget          = req.budget,
        realization     = req.costRealization,
        charged_by_fin  = req.chargedByFinance,
        remark          = req.remark,
        mandatory_from  = req.mandatoryFrom,

        emp_id          = emp.id
    )

    db.add(new_train)
    db.commit()
    db.refresh(new_train)

    return new_train

@router.patch('/admin/training_data/table_data/{id}')
def patch_training_table_entry(id: int, req: schemas.TrainingInHiCoupling, db: Session = Depends(get_db)):    
    training = db.query(Training).filter(
        Training.id == id
    )

    if not training.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    stored_data = jsonable_encoder(training.first())
    stored_model = schemas.TrainingIn(**stored_data)
    
    # Get emp_id from NIK
    emp = db.query(Employee).filter(
        Employee.staff_id == req.nik,
        Employee.active == True
    )

    emp_id = 0

    try:
        emp_id = emp.one().id
    except MultipleResultsFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Multiple Employee of NIK ({req.nik}) was found!")
    except NoResultFound:
        pass

    dataIn = schemas.Training(
        name            = req.trainingTitle,
        date            = utils.tablestr_to_datetime(req.date),
        duration_hours  = req.numberOfHours,
        proof           = stored_data["proof"],

        budget          = req.budget,
        realization     = req.costRealization,
        charged_by_fin  = req.chargedByFinance,
        remark          = req.remark,
        mandatory_from  = req.mandatoryFrom,

        emp_id          = emp_id
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    training.update(stored_data)
    db.commit()
    return updated

@router.delete('/admin/training_data/table_data/{id}')
def delete_training_table_entry(id: int, db: Session = Depends(get_db)):
    t = db.query(Training).filter(
        Training.id == id
    )

    if not t.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    t.delete()
    db.commit()

    return {'details': 'Deleted'}

# Audit Project
@router.get('/admin/audit_project_data/table_data/{year}')
def get_project_table(year: int, db: Session = Depends(get_db)):
    projects = db.query(Project).filter(
        Project.year == year
    ).all()

    res = []

    for p in projects:
        res.append({
            "id"        : str(p.id),
            "auditPlan" : p.name,
            "division"  : p.div.short_name,
            "tl_name"   : p.tl.name,
            "tl_nik"    : p.tl.staff_id,
            "status"    : p.status.name,
            "useOfDA"   : p.used_DA,
            "year"      : p.year,

            "is_carried_over" : p.is_carried_over,
            "timely_report"   : p.timely_report,
            "completion_PA"   : len(p.completion_PA) > 0
        })

    return res

@router.post('/admin/audit_project_data/table_data')
def create_project_table_entry(req: schemas.ProjectInHiCoupling, db: Session = Depends(get_db)):
    divs    = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]

    div_id = divs.index(req.division)+1
    status_id = get_project_status_id(req.status)

    # Check NIK
    emp = get_emp_by_nik(req.tl_nik, db)

    # Create Project
    new_prj = Project(
        name            = req.auditPlan,
        used_DA         = req.useOfDA,
        completion_PA   = "",
        is_carried_over = req.is_carried_over,
        timely_report   = req.timely_report,
        year            = req.year,

        status_id       = status_id,
        div_id          = div_id,
        tl_id           = emp.id
    )

    db.add(new_prj)
    db.commit()
    db.refresh(new_prj)

    # Create Empty QA Result Data
    newQA = QAIP(
        prj_id                      = new_prj.id,
        TL                          = "-",
        DH                          = "-",
        qa_type_id                  = 5,
        qa_grading_result_id        = 4,

        qaf_category_clarity        = False,
        qaf_category_completeness   = False,
        qaf_category_consistency    = False,
        qaf_category_others         = False,
        qaf_stage_planning          = False,
        qaf_stage_fieldwork         = False,
        qaf_stage_reporting         = False,
        qaf_stage_post_audit_act    = False,
        qaf_deliverables_1a         = False,
        qaf_deliverables_1b         = False,
        qaf_deliverables_1c         = False,
        qaf_deliverables_1d         = False,
        qaf_deliverables_1e         = False,
        qaf_deliverables_1f         = False,
        qaf_deliverables_1g         = False,
        qaf_deliverables_1h         = False,
        qaf_deliverables_1i         = False,
        qaf_deliverables_1j         = False,
        qaf_deliverables_1k         = False,
        qaf_deliverables_2          = False,
        qaf_deliverables_3          = False,
        qaf_deliverables_4          = False,
        qaf_deliverables_5          = False,
        qaf_deliverables_6          = False,
        qaf_deliverables_7          = False,
        qa_sample                   = False
    )

    db.add(newQA)
    db.commit()
    db.refresh(newQA)

    return new_prj

@router.patch('/admin/audit_project_data/table_data/{id}')
def patch_project_table_entry(id: int,req: schemas.ProjectInHiCoupling, db: Session = Depends(get_db)):
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]

    prj = db.query(Project).filter(
        Project.id == id
    )

    if not prj.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    stored_data = jsonable_encoder(prj.first())
    stored_model = schemas.ProjectIn(**stored_data)
    
    div_id      = divs.index(req.division)+1
    status_id   = get_project_status_id(req.status)
    # Check NIK
    emp = get_emp_by_nik(req.tl_nik, db)

    dataIn = schemas.ProjectIn(
        name            = req.auditPlan,
        used_DA         = req.useOfDA,
        is_carried_over = req.is_carried_over,
        timely_report   = req.timely_report,
        year            = req.year,

        status_id       = status_id,
        div_id          = div_id,
        tl_id           = emp.id 
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    prj.update(stored_data)
    db.commit()
    return updated

@router.delete('/admin/audit_project_data/table_data/{id}')
def delete_project_table_entry(id: int, db: Session = Depends(get_db)):
    prj = db.query(Project).filter(
        Project.id == id
    )

    if not prj.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')

    if len(prj.first().qaips) != 1:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='More than one QA Result entry associated with this project is found.')

    
    db.delete(prj.first().qaips[0])

    prj.delete()
    db.commit()

    return {'details': 'Deleted'}

# Social Contribution
@router.get('/admin/audit_contribution_data/table_data/{year}')
def get_contrib_table(year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    contribs = db.query(SocialContrib).filter(
        SocialContrib.date >= startDate,
        SocialContrib.date <= endDate
    ).all()

    res = []

    for c in contribs:
        res.append({
            "id"        : str(c.id),
            "creator_name"  : c.creator.name,
            "creator_nik"   : c.creator.staff_id,
            "division"  : c.creator.part_of_div.short_name,
            "category"  : c.social_type.name,
            "title"     : c.topic_name,
            "date"      : c.date.strftime("%m/%d/%Y")
        })

    return res

@router.post('/admin/audit_contribution_data/table_data')
def create_contrib_table_entry(req: schemas.SocialContribHiCouplingIn, db: Session = Depends(get_db)):
    types = ["Audit News", "MyUOB", "Audit Bulletin"]

    # Check NIK
    creator = get_emp_by_nik(req.creator_nik, db)

    new_con = SocialContrib(
        date            = utils.tablestr_to_datetime(req.date),
        topic_name      = req.title,
        creator_id      = creator.id,
        social_type_id  = types.index(req.category) + 1
    )

    db.add(new_con)
    db.commit()
    db.refresh(new_con)

    return new_con

@router.patch('/admin/audit_contribution_data/table_data/{id}')
def patch_contrib_table_entry(id: int,req: schemas.SocialContribHiCouplingIn, db: Session = Depends(get_db)):
    types = ["Audit News", "MyUOB", "Audit Bulletin"]

    contrib = db.query(SocialContrib).filter(
        SocialContrib.id == id
    )

    if not contrib.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    stored_data = jsonable_encoder(contrib.first())
    stored_model = schemas.SocialContribIn(**stored_data)
    
    # Check NIK
    creator = get_emp_by_nik(req.creator_nik, db)
    social_type_id  =types.index(req.category)+1

    dataIn = schemas.SocialContribIn(
        date            = utils.tablestr_to_datetime(req.date),
        topic_name      = req.title,
        creator_id      = creator.id,
        social_type_id  = social_type_id
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    contrib.update(stored_data)
    db.commit()
    return updated

@router.delete('/admin/audit_contribution_data/table_data/{id}')
def delete_contrib_table_entry(id: int, db: Session = Depends(get_db)):
    contrib = db.query(SocialContrib).filter(
        SocialContrib.id == id
    )

    if not contrib.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')
    
    contrib.delete()
    db.commit()

    return {'details': 'Deleted'}

# BUSU Engagement Table
@router.get('/admin/busu_data/table_data/{year}')
def get_busu_table(year: int, db: Session = Depends(get_db)):
    startDate   = datetime.date(year,1,1)
    endDate     = datetime.date(year,12,31)

    engs = db.query(BUSUEngagement).filter(
        BUSUEngagement.date >= startDate,
        BUSUEngagement.date <= endDate
    ).all()

    res = []
    
    for e in engs:
        res.append({
            "id"        : str(e.id),
            "nik"       : e.creator.staff_id,
            "division"  : e.creator.part_of_div.short_name,
            "WorRM"     : e.eng_type.name,
            "activity"  : e.activity_name,
            "date"      : e.date.strftime("%m/%d/%Y")
        })
    
    return res

@router.post('/admin/busu_data/table_data/')
def create_busu_table_entry(req: schemas.BUSUEngagementInHiCoupling, db: Session = Depends(get_db)):
    eng_types = ["Regular Meeting", "Workshop"]

    # Check NIK
    emp = get_emp_by_nik(req.nik, db)
    new_eng = BUSUEngagement(
        activity_name   = req.activity,
        date            = utils.tablestr_to_datetime(req.date),
        proof           = "",
        
        eng_type_id     = eng_types.index(req.WorRM) + 1,

        creator_id      = emp.id
    )

    db.add(new_eng)
    db.commit()
    db.refresh(new_eng)

    return new_eng

@router.patch('/admin/busu_data/table_data/{id}')
def patch_busu_table_entry(id:int, req: schemas.BUSUEngagementInHiCoupling, db: Session = Depends(get_db)):
    eng = db.query(BUSUEngagement).filter(
        BUSUEngagement.id == id
    ) 

    if not eng.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')

    # Check NIK
    emp = get_emp_by_nik(req.nik,db)

    stored_data = jsonable_encoder(eng.first())
    stored_model = schemas.BUSUEngagementIn(**stored_data)

    eng_types = ["Regular Meeting", "Workshop"]

    dataIn = schemas.BUSUEngagementIn(
        activity_name   = req.activity,
        date            = utils.tablestr_to_datetime(req.date),
        proof           = "",

        eng_type_id     = eng_types.index(req.WorRM) + 1,

        creator_id      = emp.id
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    eng.update(stored_data)
    db.commit()
    return updated

@router.delete('/admin/busu_data/table_data/{id}')
def delete_busu_table_entry(id:int, db: Session = Depends(get_db)):
    eng = db.query(BUSUEngagement).filter(
        BUSUEngagement.id == id
    )

    if not eng.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ID not found')

    eng.delete()
    db.commit()

    return {'details': 'Deleted'}

# Attrition MainTable
@router.get('/admin/attrition/summary_table/year/{year}')
def get_summary_attr_table(year: int, db: Session = Depends(get_db)):
    divs = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    res = []

    # Result Dict
    for div in divs:
        # HCBudget and NewYear
        yAttr = get_yAttr_by_div_shortname(year, div, db)
        div_id = yAttr.div_id

        join = resign = t_in = t_out = r_in = r_out = curr_hc = 0

        # Join, Resign, Transfer (jrt)
        attr_jrts = get_jrtAttrs(year, db, div_id=div_id)
        for a in attr_jrts:
            jrt_type = a.type.name

            join += 1   and jrt_type == "Join"
            resign += 1 and jrt_type == "Resign"
            t_in += 1   and jrt_type == "Transfer In"
            t_out += 1  and jrt_type == "Transfer Out"

        # Rotation (rot)
        attr_rots = get_rotAttrs(year, db, div_id=div_id)
        for b in attr_rots:
            r_in += 1   and b.to_div_id == div_id
            r_out += 1  and b.from_div_id == div_id

        # CurrentHC
        start_count = yAttr.start_headcount
        plus_count  = join + t_in + r_in
        minus_count = resign + t_out + r_out
        curr_hc = start_count + plus_count - minus_count

        # Attr Rate
        attr_rate = minus_count / yAttr.start_headcount
        attr_rate_str = str(round(attr_rate*100, 2)) + '%'

        res.append({
            "id"                : yAttr.id,
            "division"          : div,
            "totalBudgetHC"     : yAttr.budget_headcount,
            "totalHCNewYear"    : start_count,
            "join"              : join,
            "resign"            : resign,
            "rotation_in"       : r_in,
            "rotation_out"      : r_out,
            "transfer_in"       : t_in,
            "transfer_out"      : t_out,
            "attritionRate"     : attr_rate_str,
            "CurrentHC"         : curr_hc
        })

    return res

@router.patch('/admin/attrition/summary_table/year/{year}/id/{id}')
def get_summary_attr_table(year: int, id: int, req: schemas.YearlyAttritionInHiCoupling, db: Session = Depends(get_db)):
    yAttr_q = db.query(YearlyAttrition).filter(
        YearlyAttrition.id == id
    )

    try:
        yAttr = yAttr_q.one()
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f'yAttr of ID ({id}) was not found')
    
    if yAttr.year != year:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Found yAttr's year ({yAttr.year}) is different to endpoint's year ({year})")

    stored_data = jsonable_encoder(yAttr)
    stored_model = schemas.YearlyAttritionIn(**stored_data)

    dataIn = schemas.YearlyAttritionIn(
        start_headcount = req.totalHCNewYear,
        budget_headcount= req.totalBudgetHC
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    yAttr_q.update(stored_data)
    db.commit()
    return updated

# Attrition JRT Table
@router.get('/admin/attrition/jrt_table/year/{year}/month/{month}')
def get_jrt_attr_table(year: int, month: int, db: Session = Depends(get_db)):
    jrts = get_jrtAttrs(year, db, month=month)

    # Res
    res = []
    for j in jrts:
        # div_name = get_div_by_id(j.div_id, db).short_name

        res.append({
            "id"                : j.id,
            "employee_name"     : j.staff_name,
            "employee_nik"      : j.staff_nik,
            "category"          : j.type.name,
            "date"              : j.date.strftime("%m/%d/%Y"),
            "division"          : j.div_id
        })

    return res

@router.post('/admin/attrition/jrt_table')
def create_jrt_attr_table_entry(req: schemas.AttritionJoinResignTransferInHiCoupling, db: Session = Depends(get_db)):
    jrtTypes = ["Join", "Resign", "Transfer In", "Transfer Out"]
    
    # type_id, NIK, Div
    try:
        type_id = jrtTypes.index(req.category) + 1
        emp = get_emp_by_nik(req.employee_nik, db)
        # div = get_div_by_shortname(req.division, db)
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Invalid Type ({req.category})!')

    newJrtAttr = AttritionJoinResignTransfer(
        type_id     = type_id,
        staff_nik   = emp.staff_id,
        staff_name  = emp.name,
        date        = utils.tablestr_to_datetime(req.date),
        div_id      = int(req.division)
    )

    db.add(newJrtAttr)
    db.commit()
    db.refresh(newJrtAttr)

    return newJrtAttr

@router.patch('/admin/attrition/jrt_table/id/{id}')
def patch_jrt_attr_table_entry(id: int, req: schemas.AttritionJoinResignTransferInHiCoupling, db: Session = Depends(get_db)):
    jrtTypes = ["Join", "Resign", "Transfer In", "Transfer Out"]
    
    # Check Attr ID
    jrt_q = db.query(AttritionJoinResignTransfer).filter(
        AttritionJoinResignTransfer.id == id
    )
    try:
        jrt = jrt_q.one()
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No AttrJRT of ID ({id}) was found!")

    # type_id, NIK, Div
    try:
        type_id = jrtTypes.index(req.category) + 1
        emp = get_emp_by_nik(req.employee_nik, db)
        # div = get_div_by_shortname(req.division, db)
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Invalid Type ({req.category})!')

    stored_data = jsonable_encoder(jrt)
    stored_model = schemas.AttritionJoinResignTransfer(**stored_data)

    dataIn = schemas.AttritionJoinResignTransferIn(
        type_id     = type_id,
        staff_nik   = emp.staff_id,
        staff_name  = emp.name,
        date        = utils.tablestr_to_datetime(req.date),
        div_id      = int(req.division)
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    jrt_q.update(stored_data)
    db.commit()
    return updated

@router.delete('/admin/attrition/jrt_table/id/{id}')
def patch_jrt_attr_table_entry(id: int, db: Session = Depends(get_db)):
    # Check Attr ID
    jrt_q = db.query(AttritionJoinResignTransfer).filter(
        AttritionJoinResignTransfer.id == id
    )
    try:
        jrt = jrt_q.one()
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No AttrJRT of ID ({id}) was found!")
    
    jrt_q.delete()
    db.commit()
    return {'details': 'Deleted'}

# Attrition Rotation Table
@router.get('/admin/attrition/rot_table/year/{year}/month/{month}')
def get_rot_attr_table(year: int, month: int, db: Session = Depends(get_db)):
    rots = get_rotAttrs(year, db, month=month)

    res = []
    for r in rots:
        # from_div_name   = get_div_by_id(r.from_div_id, db).short_name
        # to_div_name     = get_div_by_id(r.to_div_id, db).short_name

        res.append({
            'id'            : r.id,
            'employee_name' : r.staff_name,
            'employee_nik'  : r.staff_nik,
            'date'          : r.date.strftime("%m/%d/%Y"),
            'from_div'      : r.from_div_id,
            'to_div'        : r.to_div_id
        })
    
    return res

@router.post('/admin/attrition/rot_table')
def create_rot_attr_table_entry(req: schemas.AttritionRotationInHiCoupling, db: Session = Depends(get_db)):   
    # NIK, Divs
    emp         = get_emp_by_nik(req.employee_nik, db)
    # from_div    = get_div_by_shortname(req.from_div, db)
    # to_div      = get_div_by_shortname(req.to_div, db)

    newRotAttr = AttritionRotation(
        staff_name  = emp.name,
        staff_nik   = emp.staff_id,
        date        = utils.tablestr_to_datetime(req.date),
        from_div_id = int(req.from_div),
        to_div_id   = int(req.to_div)
    )

    db.add(newRotAttr)
    db.commit()
    db.refresh(newRotAttr)

    return newRotAttr

@router.patch('/admin/attrition/rot_table/id/{id}')
def patch_rot_attr_table_entry(id: int, req: schemas.AttritionRotationInHiCoupling, db: Session = Depends(get_db)):    
    # Check Attr ID
    rot_q = db.query(AttritionRotation).filter(
        AttritionRotation.id == id
    )
    try:
        rot = rot_q.one()
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No AttrRotation of ID ({id}) was found!")

    # type_id, NIK, Div
    emp = get_emp_by_nik(req.employee_nik, db)
    # from_div    = get_div_by_shortname(req.from_div, db)
    # to_div      = get_div_by_shortname(req.to_div, db)

    stored_data = jsonable_encoder(rot)
    stored_model = schemas.AttritionRotation(**stored_data)

    dataIn = schemas.AttritionRotationIn(
        staff_name  = emp.name,
        staff_nik   = emp.staff_id,
        date        = utils.tablestr_to_datetime(req.date),
        from_div_id = int(req.from_div),
        to_div_id   = int(req.to_div)
    )

    new_data = dataIn.dict(exclude_unset=True)
    updated = stored_model.copy(update=new_data)

    stored_data.update(updated)

    rot_q.update(stored_data)
    db.commit()
    return updated

@router.delete('/admin/attrition/rot_table/id/{id}')
def patch_rot_attr_table_entry(id: int, db: Session = Depends(get_db)):
    # Check Attr ID
    rot_q = db.query(AttritionRotation).filter(
        AttritionRotation.id == id
    )
    try:
        rot = rot_q.one()
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No AttrRotation of ID ({id}) was found!")
    
    rot_q.delete()
    db.commit()
    return {'details': 'Deleted'}

### Utils ###
@router.get('/utils/divs')
def get_divs(db: Session = Depends(get_db)):
    divs = db.query(Division).filter(
        Division.short_name != "IAH"
    )

    res = []
    for d in divs:
        res.append({
            'id'            : str(d.id),
            'division'      : d.short_name
        })

    return res

@router.get('/utils/divs_with_IAH')
def get_divs_with_IAH(db: Session = Depends(get_db)):
    divs = db.query(Division).all()

    res = []
    for d in divs:
        res.append({
            'id'            : str(d.id),
            'division'      : d.short_name
        })

    return res

@router.get('/utils/title_project/{year}')
def get_project_titles(year:int, db: Session = Depends(get_db)):
    prjs = db.query(Project).filter(
        Project.year == year
    )

    res = []
    for p in prjs:
        res.append({
            'id'            : str(p.id),
            'project_title' : p.name
        })

    return res

@router.get('/utils/title_project_v2/year/{year}')
def get_project_titles_v2(year:int, db: Session = Depends(get_db)):
    prjs = db.query(Project).filter(
        Project.year == year
    )

    res = []
    for p in prjs:
        res.append({
            'title' : p.name
        })

    return res

@router.get('/utils/title_project_v3/year/{year}')
def get_project_titles_v3(year:int, db: Session = Depends(get_db)):
    prjs = db.query(Project).filter(
        Project.year == year
    )

    res = []
    for p in prjs:
        res.append(p.name)

    return res

@router.get('/utils/project_by_nik/{year}/{nik}')
def get_project_by_NIK(year:int, nik: str, db: Session = Depends(get_db)):
    # Check NIK
    emp = get_emp_by_nik(req.nik,db)

    # Get Projects
    prjs = db.query(Project).filter(
        Project.year == year,
        Project.tl.has(id=emp.id)
    )

    res = []
    for p in prjs:
        res.append({
            'id'            : str(p.id),
            'project_title' : p.name
        })

    return res

def get_divs_name_exclude_IAH(db: Session = Depends(get_db)):
    divs = db.query(Division).filter(
        Division.short_name != "IAH"
    )

    res = []
    for d in divs:
        res.append(d.short_name)
    
    return res

def get_div_by_shortname(shortname: str , db: Session):
    div_q = db.query(Division).filter(
        Division.short_name == shortname
    )

    try:
        div = div_q.one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Div of shortname ({shortname}) was not found!')
    except MultipleResultsFound:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Multiple Divs of shortname ({shortname}) were found!')

    return div

def get_div_by_id(div_id: int, db: Session = Depends(get_db)):
    div_q = db.query(Division).filter(
        Division.id == div_id
    )

    try:
        div = div_q.one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Div of ID ({div_id}) was not found!')
    except MultipleResultsFound:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Multiple Divs of ID ({div_id}) were found!')

    return div

def create_or_update_mActual(data, db: Session):
    actual_query = db.query(MonthlyActualBudget).filter(
        MonthlyActualBudget.year == data['year'],
        MonthlyActualBudget.month == data['month']
    )

    try:
        actual_db = actual_query.one_or_none()
    except MultipleResultsFound:
        raise MultipleResultsFound(f"Multiple mActual with year/month({data['year']}/{data['month']})")

    if actual_db: # Exists
        # Update
        stored_data = jsonable_encoder(actual_db)
        stored_model = schemas.MonthlyActualBudgetIn(**stored_data)
        
        updated = stored_model.copy(update=data)
        stored_data.update(updated)
        actual_query.update(stored_data)
        db.commit()
    else:
        # Create
        newMonthActualBudget = MonthlyActualBudget(
            year                        = data['year'],
            month                       = data['month'],
            staff_salaries              = data['staff_salaries'],
            staff_training_reg_meeting  = data['staff_training_reg_meeting'],
            revenue_related             = data['revenue_related'],
            it_related                  = data['it_related'],
            occupancy_related           = data['occupancy_related'],
            other_transport_travel      = data['other_transport_travel'],
            other_other                 = data['other_other'],
            indirect_expense            = data['indirect_expense'],
            remark                      = ""
        )

        db.add(newMonthActualBudget)
        db.commit()
        db.refresh(newMonthActualBudget)

def create_or_update_mBudget(data, db: Session):
    budget_query = db.query(MonthlyBudget).filter(
        MonthlyBudget.year == data['year'],
        MonthlyBudget.month == data['month']
    )

    try:
        budget_db = budget_query.one_or_none()
    except MultipleResultsFound:
        raise MultipleResultsFound(f"Multiple mBudget with year/month({data['year']}/{data['month']})")

    if budget_db:
        # Update
        stored_data = jsonable_encoder(budget_db)
        stored_model = schemas.MonthlyBudgetIn(**stored_data)
        
        updated = stored_model.copy(update=data)
        stored_data.update(updated)
        budget_query.update(stored_data)
        db.commit()
    else:
        # Create
        newMonthlyBudget = MonthlyBudget(
            year                        = data['year'],
            month                       = data['month'],
            staff_salaries              = data['staff_salaries'],
            staff_training_reg_meeting  = data['staff_training_reg_meeting'],
            revenue_related             = data['revenue_related'],
            it_related                  = data['it_related'],
            occupancy_related           = data['occupancy_related'],
            other_transport_travel      = data['other_transport_travel'],
            other_other                 = data['other_other'],
            indirect_expense            = data['indirect_expense']
        )

        db.add(newMonthlyBudget)
        db.commit()
        db.refresh(newMonthlyBudget)

def create_or_update_yBudget(data, db: Session):
    del data['month']

    budget_query = db.query(YearlyBudget).filter(
        YearlyBudget.year == data['year']
    )

    try:
        budget_db = budget_query.one_or_none()
    except MultipleResultsFound:
        raise MultipleResultsFound(f"Multiple yBudget with year({data['year']})")

    if budget_db:
        # Update
        stored_data = jsonable_encoder(budget_db)
        stored_model = schemas.YearlyBudgetIn(**stored_data)
        
        updated = stored_model.copy(update=data)
        stored_data.update(updated)
        budget_query.update(stored_data)
        db.commit()
    else:
        # Create
        newYearlyBudget = YearlyBudget(
            year                        = data['year'],
            staff_salaries              = data['staff_salaries'],
            staff_training_reg_meeting  = data['staff_training_reg_meeting'],
            revenue_related             = data['revenue_related'],
            it_related                  = data['it_related'],
            occupancy_related           = data['occupancy_related'],
            other_transport_travel      = data['other_transport_travel'],
            other_other                 = data['other_other'],
            indirect_expense            = data['indirect_expense']
        )

        db.add(newYearlyBudget)
        db.commit()
        db.refresh(newYearlyBudget)

def get_project_status_id(inputText):
    statuses= ["Not Started", "Planning", "Fieldwork", "Reporting", "Sign-off", "Completed"]

    try:
        stat_id = statuses.index(inputText)+1
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Project Status ({inputText}) is invalid!')

    return stat_id

def _create_employee_from_table(req: schemas.EmployeeInHiCoupling, db : Session):
    # Check Division ID
    div_q = db.query(Division).filter(
        Division.id == req.divison
    )

    try:
        div = div_q.one()
    except MultipleResultsFound:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Multiple Division of ID ({req.divison}) was found!')
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'No Division of ID ({req.divison}) was found!')


    role_id = utils.role_str_to_id(req.role)

    new_emp = Employee(
        name    = req.staffName,
        email   = req.email,
        pw      = hashing.bcrypt("pass"),

        staff_id                = req.staffNIK,
        div_stream              = req.stream,
        corporate_title         = req.corporateTitle,
        corporate_grade         = req.corporateGrade,
        date_of_birth           = utils.tablestr_to_datetime(req.dateOfBirth),
        date_first_employment   = utils.tablestr_to_datetime(req.dateStartFirstEmployment),
        date_first_uob          = utils.tablestr_to_datetime(req.dateJoinUOB),
        date_first_ia           = utils.tablestr_to_datetime(req.dateJoinIAFunction),
        gender                  = req.gender,
        year_audit_non_uob      = req.auditNonUOBExp,
        edu_level               = req.educationLevel,
        edu_major               = req.educationMajor,
        edu_category            = req.educationCategory,
        ia_background           = req.IABackgground,
        ea_background           = req.EABackground,
        active                  = True,

        div_id = div.id,
        role_id= role_id
    )

    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)

    return new_emp

def get_all_active_emps(db: Session):
    return db.query(Employee).filter(
        Employee.active == True
    ).all()

def get_emp(input_id, db: Session):
    if not input_id:
        return None

    emp_q = db.query(Employee).filter(
        Employee.id == input_id
    )

    try:
        emp = emp_q.one()
    except MultipleResultsFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Multiple Employee of ID ({input_id}) was found!")
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Employee of ID ({input_id}) was not found!")

    return emp

def get_emp_by_nik(input_nik, db: Session):
    if not input_nik or len(input_nik) == 0:
        return None
    
    emp_q = db.query(Employee).filter(
        Employee.staff_id == input_nik,
        Employee.active == True
    )

    try:
        emp = emp_q.one()
    except MultipleResultsFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Multiple Employee of NIK ({input_nik}) was found!")
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Employee of NIK ({input_nik}) was not found!")

    return emp

def get_yAttr_by_div_shortname(year: int, short_name: str, db: Session):
    yAttr_q = db.query(YearlyAttrition).filter(
        YearlyAttrition.year == year,
        YearlyAttrition.div.has(short_name = short_name)
    )

    try:
        yAttr = yAttr_q.one()
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f'No YearlyAttrition of div shortname ({short_name}) and year ({year}) was found'
        )
    except MultipleResultsFound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f'Found Multiple YearlyAttritions of div shortname ({short_name}) and year ({year})!'
        )
    
    return yAttr

def get_jrtAttrs(year: int, db: Session, div_id: int = None, month: int = None):

    startDate   = datetime.date(year,1,1)   if not month else datetime.date(year,month,1)
    endDate     = datetime.date(year,12,31) if not month else datetime.date(year,month,calendar.monthrange(year,month)[1])
    

    if div_id:
        return db.query(AttritionJoinResignTransfer).filter(
            AttritionJoinResignTransfer.date >= startDate,
            AttritionJoinResignTransfer.date <= endDate,
            AttritionJoinResignTransfer.div_id == div_id
        ).all()
    else:
        return db.query(AttritionJoinResignTransfer).filter(
            AttritionJoinResignTransfer.date >= startDate,
            AttritionJoinResignTransfer.date <= endDate,
        ).all()

def get_rotAttrs(year: int, db: Session, div_id: int = None, month: int = None):
    startDate   = datetime.date(year,1,1)   if not month else datetime.date(year,month,1)
    endDate     = datetime.date(year,12,31) if not month else datetime.date(year,month,calendar.monthrange(year,month)[1])

    if div_id:
        return db.query(AttritionRotation).filter(
            AttritionRotation.date >= startDate,
            AttritionRotation.date <= endDate,
        ).filter(or_(
            AttritionRotation.from_div_id == div_id,
            AttritionRotation.to_div_id == div_id
        )).all()
    else:
        return db.query(AttritionRotation).filter(
            AttritionRotation.date >= startDate,
            AttritionRotation.date <= endDate,
        ).all()

def extract_highest_smr_level(certs):
    """Returns a tuple of Two Ints (max-smr-Level, Certs ID) which indicates the highest proof-exist smr certs from a given certs list"""

    max_smr = [-1, 0]
    for c in certs:
        smr_level = utils.extract_SMR_level(c.cert_name)
        
        if smr_level:
            if c.cert_proof and smr_level > max_smr[0]:
                max_smr = [smr_level, c.id]
        elif c.cert_name == "SMR In Progress" and max_smr[0] < 1:
            max_smr = [0, c.id]

    return (max_smr[0], max_smr[1])

def is_cert_smr_related(cert):
    smr_level = utils.extract_SMR_level(cert.cert_name)
    return smr_level or cert.cert_name == "SMR In Progress"

def get_cert_by_id(id:int, db:Session):
    cert_q = db.query(Certification).filter(
        Certification.id == id
    )

    try:
        return cert_q.one()
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No Cert of ID ({id}) was found!")

def get_prj_by_id(id:int, db:Session):
    prj_q = db.query(Project).filter(
        Project.id == id
    )

    try:
        return prj_q.one()
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No Project of ID ({id}) was found!")

def get_busu_by_id(id:int, db:Session):
    busu_q = db.query(BUSUEngagement).filter(
        BUSUEngagement.id == id
    )

    try:
        return busu_q.one()
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No BUSUEngagement of ID ({id}) was found!")

def get_training_by_id(id:int, db:Session):
    train_q = db.query(Training).filter(
        Training.id == id
    )

    try:
        return train_q.one()
    except NoResultFound:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No Training of ID ({id}) was found!")
 
def get_cert_by_empnik_certname(nik:str, cname:str, db:Session):
    cert_q = db.query(Certification).filter(
        Certification.cert_name == cname,
        Certification.owner.has(staff_id=nik),
        Certification.owner.has(active=True)
    )

    return cert_q.one()