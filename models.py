from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Date
from sqlalchemy.orm import relationship
from database import Base

class Division(Base):
    __tablename__ = 'divisions'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    employees_of_div = relationship("Employee", back_populates="part_of_div")

    div_socialcontribs  = relationship("SocialContrib", back_populates="div")
    div_monthlyAttr     = relationship("MonthlyAttrition", back_populates="div")
    div_yearlyAttr      = relationship("YearlyAttritionConst", back_populates="div")
    div_busuengagements = relationship("BUSUEngagement", back_populates="div")
    div_projects        = relationship("Project", back_populates="div")

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    pw = Column(String)

    div_id = Column(Integer, ForeignKey('divisions.id'))
    part_of_div = relationship("Division", back_populates="employees_of_div") # division id

    emp_trainings = relationship("Training", back_populates="employee")

    emp_trainingtargets = relationship("TrainingTarget", back_populates="trainee")

# Training
class Training(Base):
    __tablename__ = 'trainings'
    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String)
    date            = Column(Date)
    duration_days   = Column(Float)
    proof           = Column(Boolean)

    emp_id          = Column(Integer, ForeignKey('employees.id'))
    employee        = relationship("Employee", back_populates="emp_trainings") #employee id
    
    budget          = relationship("TrainingBudget", back_populates="training")

class TrainingTarget(Base):
    __tablename__ = 'trainingtargets'
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    target_days = Column(Float)

    emp_id = Column(Integer, ForeignKey('employees.id'))
    trainee = relationship("Employee", back_populates="emp_trainingtargets") #employee id

class TrainingBudget(Base):
    __tablename__ = 'trainingbudgets'
    id = Column(Integer, primary_key=True, index=True)

    budget          = Column(Float)
    realization     = Column(Float)
    charged_by_fin  = Column(Float)

    training_id = Column(Integer, ForeignKey('trainings.id'))
    training = relationship("Training", back_populates="budget")


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

    div_id  = Column(Integer, ForeignKey('divisions.id'))
    div     = relationship("Division", back_populates="div_socialcontribs")

    social_type_id  = Column(Integer, ForeignKey('socialtypes.id'))
    social_type     = relationship("SocialType", back_populates="contribs")

class SocialType(Base):
    __tablename__ = 'socialtypes'
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String)

    contribs    = relationship("SocialContrib", back_populates="social_type")

# Attrition
class MonthlyAttrition(Base):
    __tablename__ = 'monthlyattritions'
    id              = Column(Integer, primary_key=True, index=True)
    joined_count    = Column(Integer)
    resigned_count  = Column(Integer)
    transfer_count  = Column(Integer)
    month           = Column(Integer)
    year            = Column(Integer)
    div_id  = Column(Integer, ForeignKey('divisions.id'))
    div     = relationship("Division", back_populates="div_monthlyAttr")

class YearlyAttritionConst(Base):
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
    proof           = Column(Boolean)

    eng_type_id     = Column(Integer, ForeignKey('engagementtypes.id'))
    eng_type        = relationship("EngagementType", back_populates="engagements")

    div_id  = Column(Integer, ForeignKey('divisions.id'))
    div     = relationship("Division", back_populates="div_busuengagements")

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
    completion_PA   = Column(Boolean)
    is_carried_over = Column(Boolean)

    status_id       = Column(Integer, ForeignKey('projectstatus.id'))
    status          = relationship("ProjectStatus", back_populates="status_of_projects")

    div_id  = Column(Integer, ForeignKey('divisions.id'))
    div     = relationship("Division", back_populates="div_projects")

# Budgets
class MonthlyBudget(Base):
    __tablename__ = 'monthlybudget'
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
    __tablename__ = 'monthlyactualbudget'
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
