import datetime
import re

def find_index(listOfDict, dict_key, value):
    return next((index for (index, d) in enumerate(listOfDict) if d[dict_key] == value), None)

def str_to_datetime(text):
    return datetime.datetime.strptime(text, "%m/%d/%Y")

def div_str_to_divID(text):
    divs    = ["WBGM", "RBA", "BRDS", "TAD", "PPA"]

    return divs.index(text)+1

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