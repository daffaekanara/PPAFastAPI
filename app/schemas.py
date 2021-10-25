from typing import List, Optional
from pydantic import BaseModel
import datetime

class TempLoginForm(BaseModel):
    email: str
    password: str

class Division(BaseModel):
    short_name  :str
    long_name   :str
    dh_id       :int

class DivisionCreate(BaseModel):
    short_name  :str
    long_name   :str
    dh_id       :Optional[int]

class DivisionIn(BaseModel):
    short_name  :Optional[str]
    long_name   :Optional[str]
    dh_id       :Optional[int]

class DivisionInHiCoupling(BaseModel):
    id          : Optional[str]
    short_name  : Optional[str]
    long_name   : Optional[str]
    dh_id       : Optional[str]
    dh_name     : Optional[str]

class ShowDivision(BaseModel):
    short_name:str

    class Config():
        orm_mode = True

class Employee(BaseModel):
    name                    :str
    email                   :str
    pw                      :str
    staff_id                :str
    div_stream              :str
    corporate_title         :str
    corporate_grade         :str
    date_of_birth           :datetime.date
    date_first_employment   :datetime.date
    date_first_uob          :datetime.date
    date_first_ia           :datetime.date
    gender                  :str
    year_audit_non_uob      :int
    edu_level               :str
    edu_major               :str
    edu_category            :str
    ia_background           :bool
    ea_background           :bool
    active                  :bool
    div_id                  :int
    role_id                 :int

class EmployeeIn(BaseModel):
    name                    :Optional[str]
    email                   :Optional[str]
    pw                      :Optional[str]
    staff_id                :Optional[str]
    div_stream              :Optional[str]
    corporate_title         :Optional[str]
    corporate_grade         :Optional[str]
    date_of_birth           :Optional[datetime.date]
    date_first_employment   :Optional[datetime.date]
    date_first_uob          :Optional[datetime.date]
    date_first_ia           :Optional[datetime.date]
    gender                  :Optional[str]
    year_audit_non_uob      :Optional[int]
    edu_level               :Optional[str]
    edu_major               :Optional[str]
    edu_category            :Optional[str]
    ia_background           :Optional[bool]
    ea_background           :Optional[bool]
    active                  :Optional[bool]
    div_id                  :Optional[int]
    role_id                 :Optional[int]

class EmployeeInHiCoupling(BaseModel):
    id                          : Optional[str]
    staffNIK                    : Optional[str]
    staffName                   : Optional[str]
    email                       : Optional[str]
    role                        : Optional[str]
    divison                     : Optional[str]
    stream                      : Optional[str]
    corporateTitle              : Optional[str]
    corporateGrade              : Optional[str]
    dateOfBirth                 : Optional[str]
    dateStartFirstEmployment    : Optional[str]
    dateJoinUOB                 : Optional[str]
    dateJoinIAFunction          : Optional[str]
    asOfNow                     : Optional[str]
    age                         : Optional[str]
    gen                         : Optional[str]
    gender                      : Optional[str]
    auditUOBExp                 : Optional[str]
    auditNonUOBExp              : Optional[str]
    totalAuditExp               : Optional[str]
    educationLevel              : Optional[str]
    educationMajor              : Optional[str]
    educationCategory           : Optional[str]
    RMGCertification            : Optional[str]
    CISA                        : Optional[bool]
    CEH                         : Optional[bool]
    ISO                         : Optional[bool]
    CHFI                        : Optional[bool]
    IDEA                        : Optional[bool]
    QualifiedIA                 : Optional[bool]
    CBIA                        : Optional[bool]
    CIA                         : Optional[bool]
    CPA                         : Optional[bool]
    CA                          : Optional[bool]
    other_cert                  : Optional[str]
    IABackgground               : Optional[bool]
    EABackground                : Optional[bool]
    active                      : Optional[bool]

class ShowEmployee(BaseModel):
    name:str
    email:str
    part_of_div:ShowDivision

    class Config():
        orm_mode = True

class ShowEmployeeOnly(BaseModel):
    name:str
    email:str

    class Config():
        orm_mode = True

class Certification(BaseModel):
    cert_name   :str
    cert_proof  :str
    emp_id      :int

class CertificationIn(BaseModel):
    cert_name   :Optional[str]
    cert_proof  :Optional[str]
    emp_id      :Optional[int]

class Role(BaseModel):
    name   :str

class RoleIn(BaseModel):
    name   :Optional[str]

class Login(BaseModel):
    email: str
    password: str

class PasswordChangeIn(BaseModel):
    old_pw: str
    new_pw: str

class PasswordChangeAdminIn(BaseModel):
    nik     : str
    new_pw  : str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class Announcement(BaseModel):
    type_name       : str
    body            : str

class AnnouncementCreate(BaseModel):
    body            : str

# Trainings
class Training(BaseModel):
    name            :str
    duration_hours   :float
    date            :datetime.date
    proof           :str
    budget          :float
    realization     :float
    charged_by_fin  :float
    remark          :str
    mandatory_from  :str

    emp_id          :int

class TrainingIn(BaseModel):
    name            :Optional[str]
    duration_hours   :Optional[float]
    date            :Optional[datetime.date]
    proof           :Optional[str]
    budget          :Optional[float]
    realization     :Optional[float]
    charged_by_fin  :Optional[float]
    remark          :Optional[str]
    mandatory_from  :Optional[str]
    emp_id          :Optional[int]

class TrainingInHiCouplingForm(BaseModel):
  name              : Optional[str]
  date              : Optional[str]
  duration_hours    : Optional[int]
  remarks           : Optional[str]
  nik               : Optional[str]

class ShowTraining(BaseModel):
    name            :str
    duration_hours   :float
    date            :datetime.date
    proof           :str
    budget          :float
    realization     :float
    charged_by_fin  :float
    remark          :str
    mandatory_from  :str
    emp_id          :int
    employee        :Optional[ShowEmployeeOnly]
    
    class Config():
        orm_mode = True

class TrainingTarget(BaseModel):
    year:int
    target_hours:float
    emp_id:int

class TrainingTargetIn(BaseModel):
    year:Optional[int]
    target_hours:Optional[float]
    emp_id:Optional[int]

class TrainingBudget(BaseModel):
    year    :int
    budget  :float
    div_id  :int

class TrainingBudgetIn(BaseModel):
    year    :Optional[int]
    budget  :Optional[float]
    div_id  :Optional[int]

class TrainingBudgetInHiCoupling(BaseModel):
    id                : str
    division          : str
    budget            : float

class TrainingInHiCoupling(BaseModel):
    id                  : Optional[str]
    divison             : Optional[str]
    name                : Optional[str]
    nik                 : Optional[str]
    trainingTitle       : Optional[str]
    date                : Optional[str]
    numberOfHours       : Optional[int]
    budget              : Optional[int]
    costRealization     : Optional[int]
    chargedByFinance    : Optional[int]
    mandatoryFrom       : Optional[str]
    remark              : Optional[str]

class TrainingInHiCouplingUserPage(BaseModel):
    id                  : Optional[str]
    divison             : Optional[str]
    name                : Optional[str]
    nik                 : Optional[str]
    trainingTitle       : Optional[str]
    date                : Optional[str]
    numberOfHours       : Optional[int]
    budget              : Optional[int]
    costRealization     : Optional[int]
    chargedByFinance    : Optional[int]
    mandatoryFrom       : Optional[str]
    remark              : Optional[str]

class DebugParent(BaseModel):
    first_name:str
    last_name:str

class DebugParentIn(BaseModel):
    first_name:Optional[str]
    last_name:Optional[str]

# Social Contributions
class SocialType(BaseModel):
    name        :str

class SocialTypeIn(BaseModel):
    name        :Optional[str]

class ShowSocialType(BaseModel):
    name        :str

    class Config():
        orm_mode = True

class SocialContrib(BaseModel):
    date        :datetime.date
    topic_name  :str
    creator_id  :int
    social_type_id:int

class SocialContribIn(BaseModel):
    date        :Optional[datetime.date]
    topic_name  :Optional[str]
    creator_id  :Optional[int]
    social_type_id:Optional[int]

class SocialContribHiCouplingIn(BaseModel):
    date        :Optional[str]
    title       :Optional[str]
    category    :Optional[str]
    division    :Optional[str]
    creator_name:Optional[str]
    creator_nik :Optional[str]
    id          :Optional[str]

class SocialContribHiCouplingUserPageIn(BaseModel):
    date        :Optional[str]
    title       :Optional[str]
    category    :Optional[str]
    id          :Optional[str]

# Attrition
class AttrType(BaseModel):
    name    : str

class AttritionJoinResignTransfer(BaseModel):
    type_id     : int
    staff_name  : str
    staff_nik   : str
    date        : datetime.date
    div_id   : int

class AttritionJoinResignTransferIn(BaseModel):
    type_id     : Optional[int]
    staff_name  : Optional[str]
    staff_nik   : Optional[str]
    date        : Optional[datetime.date]
    div_id   : Optional[int]

class AttritionJoinResignTransferInHiCoupling(BaseModel):
    id              : Optional[str]
    employee_name   : Optional[str]
    employee_nik    : Optional[str]
    category        : Optional[str]
    date            : Optional[str]
    division        : Optional[str]


class AttritionRotation(BaseModel):
    staff_name  : str
    staff_nik   : str
    date        : datetime.date
    from_div_id : int
    to_div_id   : int

class AttritionRotationIn(BaseModel):
    staff_name  : Optional[str]
    staff_nik   : Optional[str]
    date        : Optional[datetime.date]
    from_div_id : Optional[int]
    to_div_id   : Optional[int]

class AttritionRotationInHiCoupling(BaseModel):
    id              : Optional[str]
    employee_name   : Optional[str]
    employee_nik    : Optional[str]
    date            : Optional[str]
    from_div        : Optional[str]
    to_div          : Optional[str]

class YearlyAttrition(BaseModel):
    year                :int
    start_headcount     :int
    budget_headcount    :int

    div_id              :int

class YearlyAttritionIn(BaseModel):
    year                :Optional[int]
    start_headcount     :Optional[int]
    budget_headcount    :Optional[int]
    
    div_id              :Optional[int]

class YearlyAttritionInHiCoupling(BaseModel):
    id              :Optional[str]
    division        :Optional[str]
    totalBudgetHC   :Optional[int]
    totalHCNewYear  :Optional[int]
    join            :Optional[int]
    rotation_in     :Optional[int]
    rotation_out    :Optional[int]
    transfer_in     :Optional[int]
    transfer_out    :Optional[int]
    attritionRate   :Optional[str]
    CurrentHC       :Optional[int]

# BUSU Engagement
class EngagementType(BaseModel):
    name :str

class EngagementTypeIn(BaseModel):
    name :Optional[str]

class BUSUEngagement(BaseModel):
    activity_name   : str
    date            : datetime.date
    proof           : str

    eng_type_id     : int

    creator_id      : int

class BUSUEngagementIn(BaseModel):
    activity_name   : Optional[str]
    date            : Optional[datetime.date]
    proof           : Optional[str]

    eng_type_id     : Optional[int]

    creator_id      : Optional[int]

class BUSUEngagementInHiCoupling(BaseModel):
    id          : Optional[str]
    nik         : Optional[str]
    division    : Optional[str]
    WorRM       : Optional[str]
    activity    : Optional[str]
    date        : Optional[str]

# Audit Projects
class ProjectStatus(BaseModel):
    name: str

class ProjectStatusIn(BaseModel):
    name: Optional[str]

class Project(BaseModel):
    name            :str
    used_DA         :bool
    completion_PA   :str
    is_carried_over :bool
    timely_report   :bool
    year            :int

    status_id       :int
    div_id          :int
    tl_id           :int

class ProjectIn(BaseModel):
    name            :Optional[str]
    used_DA         :Optional[bool]
    completion_PA   :Optional[str]
    is_carried_over :Optional[bool]
    timely_report   :Optional[bool]
    year            :Optional[int]

    status_id       :Optional[int]
    div_id          :Optional[int]
    tl_id           :Optional[int]

class ProjectInHiCoupling(BaseModel):
    auditPlan   : Optional[str]
    division    : Optional[str]
    div_id      :Optional[int]

    tl_name     : Optional[str]
    tl_nik      : Optional[str]

    status      : Optional[str]
    useOfDA     : Optional[bool]
    year        : Optional[int]

    is_carried_over : Optional[bool]
    timely_report   : Optional[bool]
    completion_PA   : Optional[bool]

# Budgets
class YearlyBudget(BaseModel):
    year                        :int
    staff_salaries              :float
    staff_training_reg_meeting  :float
    revenue_related             :float
    it_related                  :float
    occupancy_related           :float
    other_transport_travel      :float
    other_other                 :float
    indirect_expense            :float

class YearlyBudgetIn(BaseModel):
    year                        :Optional[int]
    staff_salaries              :Optional[float]
    staff_training_reg_meeting  :Optional[float]
    revenue_related             :Optional[float]
    it_related                  :Optional[float]
    occupancy_related           :Optional[float]
    other_transport_travel      :Optional[float]
    other_other                 :Optional[float]
    indirect_expense            :Optional[float]

class MonthlyBudget(BaseModel):
    year                        :int
    month                       :int
    staff_salaries              :float
    staff_training_reg_meeting  :float
    revenue_related             :float
    it_related                  :float
    occupancy_related           :float
    other_transport_travel      :float
    other_other                 :float
    indirect_expense            :float

class MonthlyBudgetIn(BaseModel):
    year                        :Optional[int]
    month                       :Optional[int]
    staff_salaries              :Optional[float]
    staff_training_reg_meeting  :Optional[float]
    revenue_related             :Optional[float]
    it_related                  :Optional[float]
    occupancy_related           :Optional[float]
    other_transport_travel      :Optional[float]
    other_other                 :Optional[float]
    indirect_expense            :Optional[float]

class MonthlyActualBudget(BaseModel):
    year                        :int
    month                       :int
    staff_salaries              :float
    staff_training_reg_meeting  :float
    revenue_related             :float
    it_related                  :float
    occupancy_related           :float
    other_transport_travel      :float
    other_other                 :float
    indirect_expense            :float
    remark                      :str

class MonthlyActualBudgetIn(BaseModel):
    year                        :Optional[int]
    month                       :Optional[int]
    staff_salaries              :Optional[float]
    staff_training_reg_meeting  :Optional[float]
    revenue_related             :Optional[float]
    it_related                  :Optional[float]
    occupancy_related           :Optional[float]
    other_transport_travel      :Optional[float]
    other_other                 :Optional[float]
    indirect_expense            :Optional[float]
    remark                      :Optional[str]

class BudgetTableInHiCoupling(BaseModel):
    id              : Optional[str]
    expenses        : str
    budgetYear      : float
    budgetMonth     : float
    budgetMonthTD   : Optional[float]
    actualMonth     : float
    actualMonthTD   : Optional[float]
    MTD             : Optional[str]
    YTD             : Optional[str]
    STDProRate      : Optional[str]
    overUnderBudget : Optional[str]
    variance        : Optional[str]

# QAIP
class QAIP(BaseModel):
    prj_id                      :int

    qa_type_id                  :int
    qa_grading_result_id        :int

    qaf_category_clarity        :bool
    qaf_category_completeness   :bool
    qaf_category_consistency    :bool
    qaf_category_others         :bool
    qaf_stage_planning          :bool
    qaf_stage_fieldwork         :bool
    qaf_stage_reporting         :bool
    qaf_stage_post_audit_act    :bool
    qaf_deliverables_1a         :bool
    qaf_deliverables_1b         :bool
    qaf_deliverables_1c         :bool
    qaf_deliverables_1d         :bool
    qaf_deliverables_1e         :bool
    qaf_deliverables_1f         :bool
    qaf_deliverables_1g         :bool
    qaf_deliverables_1h         :bool
    qaf_deliverables_1i         :bool
    qaf_deliverables_1j         :bool
    qaf_deliverables_1k         :bool
    qaf_deliverables_2          :bool
    qaf_deliverables_3          :bool
    qaf_deliverables_4          :bool
    qaf_deliverables_5          :bool
    qaf_deliverables_6          :bool
    qaf_deliverables_7          :bool
    qa_sample                   :bool

class QAIPIn(BaseModel):
    prj_id                      :Optional[int]

    qa_type_id                  :Optional[int]
    qa_grading_result_id        :Optional[int]
    
    qaf_category_clarity        :Optional[bool]
    qaf_category_completeness   :Optional[bool]
    qaf_category_consistency    :Optional[bool]
    qaf_category_others         :Optional[bool]
    qaf_stage_planning          :Optional[bool]
    qaf_stage_fieldwork         :Optional[bool]
    qaf_stage_reporting         :Optional[bool]
    qaf_stage_post_audit_act    :Optional[bool]
    qaf_deliverables_1a         :Optional[bool]
    qaf_deliverables_1b         :Optional[bool]
    qaf_deliverables_1c         :Optional[bool]
    qaf_deliverables_1d         :Optional[bool]
    qaf_deliverables_1e         :Optional[bool]
    qaf_deliverables_1f         :Optional[bool]
    qaf_deliverables_1g         :Optional[bool]
    qaf_deliverables_1h         :Optional[bool]
    qaf_deliverables_1i         :Optional[bool]
    qaf_deliverables_1j         :Optional[bool]
    qaf_deliverables_1k         :Optional[bool]
    qaf_deliverables_2          :Optional[bool]
    qaf_deliverables_3          :Optional[bool]
    qaf_deliverables_4          :Optional[bool]
    qaf_deliverables_5          :Optional[bool]
    qaf_deliverables_6          :Optional[bool]
    qaf_deliverables_7          :Optional[bool]
    qa_sample                   :Optional[bool]

class QAIPInHiCoupling(BaseModel):
	id              : str
	plan            : str
	auditProject    : str
	TL              : str
	divisionHead    : str
	result          : str
	category        : str
	stage           : str
	deliverable     : str
	noOfIssues      : int
	QASample        : bool

class QAIPFormInHiCoupling(BaseModel):
    projectTitle: str
    year		: int

    QAType		: str
    QAResults	: str

    qaf_category_clarity        : bool
    qaf_category_completeness   : bool
    qaf_category_consistency    : bool
    qaf_category_others         : bool
    qaf_stage_planning          : bool
    qaf_stage_fieldwork         : bool
    qaf_stage_reporting         : bool
    qaf_stage_post_audit_act    : bool
    qaf_deliverables_1a         : bool
    qaf_deliverables_1b         : bool
    qaf_deliverables_1c         : bool
    qaf_deliverables_1d         : bool
    qaf_deliverables_1e         : bool
    qaf_deliverables_1f         : bool
    qaf_deliverables_1g         : bool
    qaf_deliverables_1h         : bool
    qaf_deliverables_1i         : bool
    qaf_deliverables_1j         : bool
    qaf_deliverables_1k         : bool
    qaf_deliverables_2          : bool
    qaf_deliverables_3          : bool
    qaf_deliverables_4          : bool
    qaf_deliverables_5          : bool
    qaf_deliverables_6          : bool
    qaf_deliverables_7          : bool
    qa_sample                   : bool

class QAType(BaseModel):
    name    :str

class QATypeIn(BaseModel):
    name    :Optional[str]

class QAGradingResult(BaseModel):
    name    :str

class QAGradingResultIn(BaseModel):
    name    :Optional[str]

# CSF
class CSF(BaseModel):
    client_name         :str
    client_unit         :str
    csf_date            :datetime.date
    atp_1               :float
    atp_2               :float
    atp_3               :float
    atp_4               :float
    atp_5               :float
    atp_6               :float
    ac_1                :float
    ac_2                :float
    ac_3                :float
    ac_4                :float
    ac_5                :float
    ac_6                :float
    paw_1               :float
    paw_2               :float
    paw_3               :float

    prj_id              :int
    by_invdiv_div_id    :int

class CSFIn(BaseModel):
    client_name         :Optional[str]
    client_unit         :Optional[str]
    csf_date            :Optional[datetime.date]
    atp_1               :Optional[float]
    atp_2               :Optional[float]
    atp_3               :Optional[float]
    atp_4               :Optional[float]
    atp_5               :Optional[float]
    atp_6               :Optional[float]
    ac_1                :Optional[float]
    ac_2                :Optional[float]
    ac_3                :Optional[float]
    ac_4                :Optional[float]
    ac_5                :Optional[float]
    ac_6                :Optional[float]
    paw_1               :Optional[float]
    paw_2               :Optional[float]
    paw_3               :Optional[float]

    prj_id              :Optional[int]
    by_invdiv_div_id    :Optional[int]

class CSFInHiCoupling(BaseModel):
	id                  : Optional[str]
	division_project    : Optional[str]
	auditProject        : str
	clientName          : str
	unitJabatan         : str
	TL                  : Optional[str]
	CSFDate             : str
	atp1                : float
	atp2                : float
	atp3                : float
	atp4                : float
	atp5                : float
	atp6                : float
	atpOverall          : Optional[float]
	ac1                 : float
	ac2                 : float
	ac3                 : float
	ac4                 : float
	ac5                 : float
	ac6                 : float
	acOverall           : Optional[float]
	paw1                : float
	paw2                : float
	paw3                : float
	pawOverall          : Optional[float]
	overall             : Optional[float]
	division_by_inv     : str

class ServerState(BaseModel):
    name          : str
    value         : bool

class ServerStateIn(BaseModel):
    name          : Optional[str]
    value         : Optional[bool]

### Histories ###
class TrainingHistory(BaseModel):
    year        : int
    nik         : str
    division    : str
    emp_name    : str
    name        : str
    date        : datetime.date
    hours       : int
    budget      : float
    realized    : float
    charged     : float
    mandatory   : str
    remark      : str

class TrainingBudgetHistory(BaseModel):
    year        : int
    budget      : float
    division    : str

class ProjectHistory(BaseModel):
    year        : int
    p_name      : str
    div         : str
    tl_name     : str
    tl_nik      : str
    status      : str
    use_da      : bool
    carried_over: bool
    timely      : bool
    pa_proof    : str

class SocialContribHistory(BaseModel):
    year        : int
    div         : str
    category    : str
    sc_name     : str
    date        : datetime.date
    creator_name: str
    creator_nik : str

class AttritionMainTableHistory(BaseModel):
    year        : int
    division    : str
    hc_budget   : int
    hc_start    : int
    join        : int
    resign      : int
    r_in        : int
    r_out       : int
    t_in        : int
    t_out       : int

class AttritionJRTTableHistory(BaseModel):
    year        : int
    emp_name    : str
    emp_nik     : str
    category    : str
    date        : datetime.date
    division    : str

class AttritionRotationTableHistory(BaseModel):
    year        : int
    emp_name    : str
    emp_nik     : str
    date        : datetime.date
    from_div    : str
    to_div      : str

class CSFHistory(BaseModel):
    year        : int
    p_name      : str
    client_name : str
    client_unit : str
    date        : datetime.date
    atp_1       : float
    atp_2       : float
    atp_3       : float
    atp_4       : float
    atp_5       : float
    atp_6       : float
    ac_1        : float
    ac_2        : float
    ac_3        : float
    ac_4        : float
    ac_5        : float
    ac_6        : float
    paw_1       : float
    paw_2       : float
    paw_3       : float

    division        : str
    division_by_inv : str

class QAResultHistory(BaseModel):
    year                : int
    qa_type             : str
    p_name              : str
    tl_name             : str
    div_head            : str
    qa_grading_result   : str
    qaf_category        : str
    qaf_stage           : str
    qaf_deliv           : str
    issue_count         : int
    qa_sample           : bool

class BUSUHistory(BaseModel):
    year        : int
    tl_name     : str
    division    : str
    WorM        : str
    name        : str
    date        : datetime.date

class DivisionHistory(BaseModel):
    year        : int
    short_name  : str
    long_name   : str
    dh_name     : str
    dh_nik      : str

class EmployeeHistory(BaseModel):
    year                    : int
    name                    : str
    email                   : str
    staff_id                : str
    role                    : str

    division                : str
    div_stream              : str

    corporate_title         : str
    corporate_grade         : str
    gender                  : str
    edu_level               : str
    edu_major               : str
    edu_category            : str
    ia_background           : bool
    ea_background           : bool
    year_audit_non_uob      : int

    date_of_birth           : datetime.date
    date_first_employment   : datetime.date
    date_first_uob          : datetime.date
    date_first_ia           : datetime.date

class CertHistory(BaseModel):
    cert_name   : str
    cert_proof  : str
    emp_id      : int

class Migration(BaseModel):
    year: int

class DivisionMerge(BaseModel):
    mother_division : str
    child_division  : str