import datetime
import re
from decimal import Decimal
from models import QAIP

### Budget ###
def format_budget_numbering(res):
    for r in res:
        a,b,c,d,e = int(r['budgetYear']), int(r['budgetMonth']), int(r['budgetMonthTD']), int(r['actualMonth']), int(r['actualMonthTD'])
        r['budgetYear']     = f'{a:,}'
        r['budgetMonth']    = f'{b:,}'
        r['budgetMonthTD']  = f'{c:,}'
        r['actualMonth']    = f'{d:,}'
        r['actualMonthTD']  = f'{e:,}'

    return res

### QA Result ###
def qa_to_category_str(x: QAIP):
    res = []

    x.qaf_category_clarity      and res.append("Clarity")
    x.qaf_category_completeness and res.append("Completeness")
    x.qaf_category_consistency  and res.append("Consistency")
    x.qaf_category_others       and res.append("Others")

    return res

def qa_to_stage_str(x: QAIP):
    res = []

    x.qaf_stage_planning        and res.append("Planning")
    x.qaf_stage_fieldwork       and res.append("Fieldwork")
    x.qaf_stage_reporting       and res.append("Reporting")
    x.qaf_stage_post_audit_act  and res.append("Post Audit Activity")

    return res

def qa_to_delivs_str(x: QAIP):
    res = []

    x.qaf_deliverables_1a  and res.append("Auditable Entity Information")
    x.qaf_deliverables_1b  and res.append("Risk Profiles (RAP/ORP)")
    x.qaf_deliverables_1c  and res.append("Audit Program")
    x.qaf_deliverables_1d  and res.append("Audit Sampling Plan")
    x.qaf_deliverables_1e  and res.append("MGO Rating")
    x.qaf_deliverables_1f  and res.append("Out of Scope/Reliance Area")
    x.qaf_deliverables_1g  and res.append("3LoD Reliance")
    x.qaf_deliverables_1h  and res.append("Risk Hotspot Coverage")
    x.qaf_deliverables_1i  and res.append("Audit Engagement Information")
    x.qaf_deliverables_1j  and res.append("Time Allocation")
    x.qaf_deliverables_1k  and res.append("Approval from DH")
    x.qaf_deliverables_2   and res.append("Working Paper")
    x.qaf_deliverables_3   and res.append("Audit Documentation")
    x.qaf_deliverables_4   and res.append("Checklist for Supervisory Review")
    x.qaf_deliverables_5   and res.append("Audit Report")
    x.qaf_deliverables_6   and res.append("Corrective Actions Closure")
    x.qaf_deliverables_7   and res.append("Others")

    return res

def qa_type_str_to_id(text):
    types = [
        "Plan - Regular", 
        "Plan - Thematic",
        "Regulatory",
        "Special Review"
    ]

    return types.index(text)+1 if text in types else 0

def qa_gradingres_str_to_id(text):
    res = [
        "Generally Conforms",
        "Partially Conforms",
        "Does Not Conform"
    ]

    return res.index(text)+1 if text in res else 0

### Untagged ###
def find_index(listOfDict, dict_key, value):
    return next((index for (index, d) in enumerate(listOfDict) if d[dict_key] == value), None)

def str_to_datetime(text):
    return datetime.datetime.strptime(text, "%m/%d/%Y")

def formstr_to_datetime(text):
    return datetime.datetime.strptime(text, "%Y-%m-%d")

def tablestr_to_datetime(text):
    try:
        return datetime.datetime.strptime(text, "%m/%d/%Y")
    except ValueError:
        text = text[0:10]
        d = datetime.datetime.strptime(text, "%Y-%m-%d")
        d += datetime.timedelta(days=1)
        return d

def date_to_str(date: datetime.date):
    return date.strftime("%m/%d/%Y")

def div_str_to_divID(text):
    divs    = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    
    return divs.index(text)+1 if text in divs else 0

def role_str_to_id(text):
    roles   = ["User", "Power User", "Administrator"]
    return roles.index(text)+1

def get_year_diff_to_now(start_date, now = None):
    today = datetime.date.today() if not now else now
    return today.year - start_date.year - ((today.month, today.day) < (start_date.month, start_date.day))

def get_gen(dob):
    gen_x_youngest = datetime.date(1975,12,31)
    gen_y_youngest = datetime.date(1989,12,31)

    if dob <= gen_x_youngest:
        return "Gen X"
    elif dob <= gen_y_youngest:
        return "Gen Y"
    else:
        return "Gen Z"

def extract_SMR_level(text):
    if re.search('SMR Level [0-9]', text):
        return int(text[-1])
    else:
        return None

def calc_single_csf_score(csf):
    atps = [
        csf.atp_1, csf.atp_2, csf.atp_3,
        csf.atp_4, csf.atp_5, csf.atp_6
    ]

    acs = [
        csf.ac_1, csf.ac_2, csf.ac_3,
        csf.ac_4, csf.ac_5, csf.ac_6
    ]

    paws = [
        csf.paw_1, csf.paw_2, csf.paw_3
    ]

    overall_csf = (sum(atps)/len(atps) + sum(acs)/len(acs) + sum(paws)/len(paws)) / 3

    return round(overall_csf,2)

def str_to_int_or_None(x):
    return int(x) if x.isnumeric() else None

def remove_exponent(num):
    num = Decimal(num)
    return num.to_integral() if num == num.to_integral() else num.normalize()
