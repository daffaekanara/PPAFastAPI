import datetime
import re

def find_index(listOfDict, dict_key, value):
    return next((index for (index, d) in enumerate(listOfDict) if d[dict_key] == value), None)

def str_to_datetime(text):
    return datetime.datetime.strptime(text, "%m/%d/%Y")

def date_to_str(date: datetime.date):
    return date.strftime("%m/%d/%Y")

def div_str_to_divID(text):
    divs    = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]
    
    return divs.index(text)+1 if text in divs else 0

def role_str_to_id(text):
    roles   = ["User", "Power User", "Administrator"]
    return roles.index(text)+1

def get_year_diff_to_now(start_date):
    today = datetime.date.today()
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