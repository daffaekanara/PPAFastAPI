from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Date
from sqlalchemy.orm import relationship
from database import Base

class Division(Base):
    __tablename__ = 'divisions'
    id = Column(Integer, primary_key=True, index=True)
    short_name  = Column(String)
    long_name   = Column(String)
    dh_id       = Column(Integer)

    employees_of_div = relationship("Employee", back_populates="part_of_div")

    div_trainBudgets    = relationship("TrainingBudget", back_populates="div")
    div_yearlyAttr      = relationship("YearlyAttrition", back_populates="div")
    div_projects        = relationship("Project", back_populates="div")
    
    csfs_by_invdiv  = relationship("CSF", back_populates="by_invdiv_div")

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, index=True)
    name    = Column(String)
    email   = Column(String)
    pw      = Column(String)

    staff_id                = Column(String)
    div_stream              = Column(String)
    corporate_title         = Column(String)
    corporate_grade         = Column(String)
    date_of_birth           = Column(Date)
    date_first_employment   = Column(Date)
    date_first_uob          = Column(Date)
    date_first_ia           = Column(Date)
    gender                  = Column(String)
    year_audit_non_uob      = Column(Integer)
    edu_level               = Column(String)
    edu_major               = Column(String)
    edu_category            = Column(String)
    ia_background           = Column(Boolean)
    ea_background           = Column(Boolean)
    active                  = Column(Boolean)


    div_id = Column(Integer, ForeignKey('divisions.id'))
    part_of_div = relationship("Division", back_populates="employees_of_div") # division id

    role_id = Column(Integer, ForeignKey('roles.id'))
    role = relationship("Role", back_populates="users")

    emp_trainings       = relationship("Training", back_populates="employee")
    emp_trainingtargets = relationship("TrainingTarget", back_populates="trainee")
    emp_certifications  = relationship("Certification", back_populates="owner")
    emp_prj_tl          = relationship("Project", back_populates="tl")
    emp_busu_engs       = relationship("BUSUEngagement", back_populates="creator")
    emp_social_contrib  = relationship("SocialContrib", back_populates="creator")

class Certification(Base):
    __tablename__ = 'certifications'
    id = Column(Integer, primary_key=True, index=True)

    cert_name   = Column(String)
    cert_proof  = Column(String)

    emp_id = Column(Integer, ForeignKey('employees.id'))
    owner = relationship("Employee", back_populates="emp_certifications")

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    users = relationship("Employee", back_populates="role")

class Annoucement(Base):
    __tablename__ = 'annoucements'
    id              = Column(Integer, primary_key=True, index=True)
    type_name       = Column(String)
    body            = Column(String)

# Training
class Training(Base):
    __tablename__ = 'trainings'
    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String)
    date            = Column(Date)
    duration_hours  = Column(Float)
    proof           = Column(String)

    budget          = Column(Float)
    realization     = Column(Float)
    charged_by_fin  = Column(Float)
    remark          = Column(String)
    mandatory_from  = Column(String)

    emp_id          = Column(Integer, ForeignKey('employees.id'))
    employee        = relationship("Employee", back_populates="emp_trainings") #employee id

class TrainingTarget(Base):
    __tablename__ = 'trainingtargets'
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    target_hours = Column(Float)

    emp_id = Column(Integer, ForeignKey('employees.id'))
    trainee = relationship("Employee", back_populates="emp_trainingtargets") #employee id

class TrainingBudget(Base):
    __tablename__ = 'trainingbudgets'
    id      = Column(Integer, primary_key=True, index=True)
    year    = Column(Integer)
    budget  = Column(Float)

    div_id  = Column(Integer, ForeignKey('divisions.id'))
    div     = relationship("Division", back_populates="div_trainBudgets")

class DebugParent(Base):
    __tablename__ = 'debugparent'
    id          = Column(Integer, primary_key=True, index=True)
    first_name  = Column(String)
    last_name   = Column(String)

# Social Contributions
class SocialContrib(Base):
    __tablename__ = 'socialcontribs'
    id          = Column(Integer, primary_key=True, index=True)
    date        = Column(Date)
    topic_name  = Column(String)

    creator_id  = Column(Integer, ForeignKey('employees.id'))
    creator     = relationship("Employee", back_populates="emp_social_contrib")

    social_type_id  = Column(Integer, ForeignKey('socialtypes.id'))
    social_type     = relationship("SocialType", back_populates="contribs")

class SocialType(Base):
    __tablename__ = 'socialtypes'
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String)

    contribs    = relationship("SocialContrib", back_populates="social_type")

# Attrition
class AttrType(Base):
    __tablename__ = 'attrtypes'
    id      = Column(Integer, primary_key=True, index=True)
    name    = Column(String)

    attrs = relationship("AttritionJoinResignTransfer", back_populates="type")

class AttritionJoinResignTransfer(Base):
    __tablename__ = 'attritionjoinresigntransfers'
    id          = Column(Integer, primary_key=True, index=True)

    type_id     = Column(Integer, ForeignKey('attrtypes.id'))
    type        = relationship("AttrType", back_populates="attrs")

    staff_name  = Column(String)
    date        = Column(Date)
    div_id      = Column(Integer)

class AttritionRotation(Base):
    __tablename__ = 'attritionrotations'
    id          = Column(Integer, primary_key=True, index=True)

    staff_name  = Column(String)
    date        = Column(Date)

    from_div_id = Column(Integer)
    to_div_id   = Column(Integer)

class YearlyAttrition(Base):
    __tablename__ = 'yearlyattritions'
    id              = Column(Integer, primary_key=True, index=True)
    year            = Column(Integer)
    start_headcount = Column(Integer)
    budget_headcount= Column(Integer)
    div_id  = Column(Integer, ForeignKey('divisions.id'))
    div     = relationship("Division", back_populates="div_yearlyAttr")

# BU/SU Engagement
class EngagementType(Base):
    __tablename__ = 'engagementtypes'
    id      = Column(Integer, primary_key=True, index=True)
    name    = Column(String)

    engagements = relationship("BUSUEngagement", back_populates="eng_type")

class BUSUEngagement(Base):
    __tablename__ = 'busuengagements'
    id              = Column(Integer, primary_key=True, index=True)
    activity_name   = Column(String)
    date            = Column(Date)
    proof           = Column(String)

    eng_type_id     = Column(Integer, ForeignKey('engagementtypes.id'))
    eng_type        = relationship("EngagementType", back_populates="engagements")

    creator_id  = Column(Integer, ForeignKey('employees.id'))
    creator     = relationship("Employee", back_populates="emp_busu_engs")

# Audit Projects
class ProjectStatus(Base):
    __tablename__ = 'projectstatus'
    id      = Column(Integer, primary_key=True, index=True)
    name    = Column(String)

    status_of_projects = relationship("Project", back_populates="status")

class Project(Base):
    __tablename__ = 'projects'
    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String)
    used_DA         = Column(Boolean)
    completion_PA   = Column(String)
    is_carried_over = Column(Boolean)
    timely_report   = Column(Boolean)
    year            = Column(Integer)

    status_id       = Column(Integer, ForeignKey('projectstatus.id'))
    status          = relationship("ProjectStatus", back_populates="status_of_projects")

    div_id  = Column(Integer, ForeignKey('divisions.id'))
    div     = relationship("Division", back_populates="div_projects")

    tl_id   = Column(Integer, ForeignKey('employees.id'))
    tl      = relationship("Employee", back_populates="emp_prj_tl")

    csfs = relationship("CSF", back_populates="prj")
    qaips= relationship("QAIP", back_populates="prj")

# Budgets
class YearlyBudget(Base):
    __tablename__ = 'yearlybudgets'
    id                          = Column(Integer, primary_key=True, index=True)
    year                        = Column(Integer)
    staff_salaries              = Column(Float)
    staff_training_reg_meeting  = Column(Float)
    revenue_related             = Column(Float)
    it_related                  = Column(Float)
    occupancy_related           = Column(Float)
    other_transport_travel      = Column(Float)
    other_other                 = Column(Float)
    indirect_expense            = Column(Float)

class MonthlyBudget(Base):
    __tablename__ = 'monthlybudgets'
    id                          = Column(Integer, primary_key=True, index=True)
    year                        = Column(Integer)
    month                       = Column(Integer)
    staff_salaries              = Column(Float)
    staff_training_reg_meeting  = Column(Float)
    revenue_related             = Column(Float)
    it_related                  = Column(Float)
    occupancy_related           = Column(Float)
    other_transport_travel      = Column(Float)
    other_other                 = Column(Float)
    indirect_expense            = Column(Float)

class MonthlyActualBudget(Base):
    __tablename__ = 'monthlyactualbudgets'
    id                          = Column(Integer, primary_key=True, index=True)
    year                        = Column(Integer)
    month                       = Column(Integer)
    staff_salaries              = Column(Float)
    staff_training_reg_meeting  = Column(Float)
    revenue_related             = Column(Float)
    it_related                  = Column(Float)
    occupancy_related           = Column(Float)
    other_transport_travel      = Column(Float)
    other_other                 = Column(Float)
    indirect_expense            = Column(Float)
    remark                      = Column(String)

# QAIP
class QAIP(Base):
    __tablename__ = 'qaips'
    id                  = Column(Integer, primary_key=True, index=True)

    prj_id              = Column(Integer, ForeignKey('projects.id'))
    prj                 = relationship("Project", back_populates="qaips")

    qa_type_id          = Column(Integer, ForeignKey('qatypes.id'))
    qa_type             = relationship("QAType", back_populates="qaips")

    qa_grading_result_id= Column(Integer, ForeignKey('qagradingresults.id'))
    qa_grading_result   = relationship("QAGradingResult", back_populates="qaips")

    qaf_category_clarity        = Column(Boolean)
    qaf_category_completeness   = Column(Boolean)
    qaf_category_consistency    = Column(Boolean)
    qaf_category_others         = Column(Boolean)
    qaf_stage_planning          = Column(Boolean)
    qaf_stage_fieldwork         = Column(Boolean)
    qaf_stage_reporting         = Column(Boolean)
    qaf_stage_post_audit_act    = Column(Boolean)
    qaf_deliverables_1a         = Column(Boolean)
    qaf_deliverables_1b         = Column(Boolean)
    qaf_deliverables_1c         = Column(Boolean)
    qaf_deliverables_1d         = Column(Boolean)
    qaf_deliverables_1e         = Column(Boolean)
    qaf_deliverables_1f         = Column(Boolean)
    qaf_deliverables_1g         = Column(Boolean)
    qaf_deliverables_1h         = Column(Boolean)
    qaf_deliverables_1i         = Column(Boolean)
    qaf_deliverables_1j         = Column(Boolean)
    qaf_deliverables_1k         = Column(Boolean)
    qaf_deliverables_2          = Column(Boolean)
    qaf_deliverables_3          = Column(Boolean)
    qaf_deliverables_4          = Column(Boolean)
    qaf_deliverables_5          = Column(Boolean)
    qaf_deliverables_6          = Column(Boolean)
    qaf_deliverables_7          = Column(Boolean)
    qa_sample                   = Column(Boolean)

class QAType(Base):
    __tablename__ = 'qatypes'
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String)

    qaips       = relationship("QAIP", back_populates="qa_type")

class QAGradingResult(Base):
    __tablename__ = 'qagradingresults'
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String)

    qaips       = relationship("QAIP", back_populates="qa_grading_result")

# CSF
class CSF(Base):
    __tablename__ = 'csfs'
    id                  = Column(Integer, primary_key=True, index=True)
    client_name         = Column(String)
    client_unit         = Column(String)
    csf_date            = Column(Date)
    atp_1               = Column(Float)
    atp_2               = Column(Float)
    atp_3               = Column(Float)
    atp_4               = Column(Float)
    atp_5               = Column(Float)
    atp_6               = Column(Float)
    ac_1                = Column(Float)
    ac_2                = Column(Float)
    ac_3                = Column(Float)
    ac_4                = Column(Float)
    ac_5                = Column(Float)
    ac_6                = Column(Float)
    paw_1               = Column(Float)
    paw_2               = Column(Float)
    paw_3               = Column(Float)

    prj_id  = Column(Integer, ForeignKey('projects.id'))
    prj     = relationship("Project", back_populates="csfs")

    by_invdiv_div_id = Column(Integer, ForeignKey('divisions.id'))
    by_invdiv_div    = relationship("Division", back_populates="csfs_by_invdiv")

# States
class ServerState(Base):
    __tablename__ = 'serverstate'
    id      = Column(Integer, primary_key=True, index=True)
    name    = Column(String)
    value   = Column(Boolean)