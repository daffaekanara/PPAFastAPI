from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Date
from sqlalchemy.orm import relationship
from database import Base

class Division(Base):
    __tablename__ = 'divisions'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    employees_of_div = relationship("Employee", back_populates="part_of_div")

    div_socialcontribs = relationship("SocialContrib", back_populates="div")

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

class TrainingTarget(Base):
    __tablename__ = 'trainingtargets'
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    target_days = Column(Float)

    emp_id = Column(Integer, ForeignKey('employees.id'))
    trainee = relationship("Employee", back_populates="emp_trainingtargets") #employee id

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

 