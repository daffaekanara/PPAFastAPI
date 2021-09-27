import os
import shutil
import pathlib
from datetime import datetime

DATA_FOLDER     = 'data'

FILES_FOLDER    = 'files'
HISTORY_FOLDER  = 'history'

CERTS_FOLDER    = 'certs'
BUDGET_FOLDER   = 'budget'
TRAIN_PROOF_FOLDER = 'trainings'
BUSU_ENG_FOLDER = 'busu'
PA_CMPLT_FOLDER = 'pa_completion'



def is_file_exist(filepath:str):
    return os.path.isfile(filepath)

def write_pa_completion_proof(prj_id, data, filename):
    dir_name = os.path.join(DATA_FOLDER, FILES_FOLDER, PA_CMPLT_FOLDER)
    os.makedirs(dir_name, exist_ok=True)

    new_fname = f"{prj_id}.{filename.split('.')[-1]}"

    # Check if cert with same name exist
    for (idirpath, dirnames, filenames) in os.walk(dir_name):
        for fname in filenames:
            if fname.split('.')[0] == new_fname.split('.')[0]:
                os.remove(os.path.join(dir_name, fname))
        break # Only walk first level dir
    
    # Write proof
    full_filepath = os.path.join(dir_name, new_fname)
    f = open(full_filepath, 'wb')
    f.write(data)
    f.close()

    return full_filepath

def write_busu_proof(eng_id, emp_id, data, filename):
    dir_name = os.path.join(DATA_FOLDER, FILES_FOLDER, BUSU_ENG_FOLDER, str(emp_id))
    os.makedirs(dir_name, exist_ok=True)

    new_fname = f"{eng_id}.{filename.split('.')[-1]}"

    # Check if cert with same name exist
    for (idirpath, dirnames, filenames) in os.walk(dir_name):
        for fname in filenames:
            if fname.split('.')[0] == new_fname.split('.')[0]:
                os.remove(os.path.join(dir_name, fname))
        break # Only walk first level dir
    
    # Write proof
    full_filepath = os.path.join(dir_name, new_fname)
    f = open(full_filepath, 'wb')
    f.write(data)
    f.close()

    return full_filepath

def write_training_proof(train_id, emp_id, data, filename):
    dir_name = os.path.join(DATA_FOLDER, FILES_FOLDER, TRAIN_PROOF_FOLDER, str(emp_id))
    os.makedirs(dir_name, exist_ok=True)

    new_fname = f"{train_id}.{filename.split('.')[-1]}"

    # Check if cert with same name exist
    remove_duplicate_file(dir_name, new_fname)
    
    # Write proof
    full_filepath = os.path.join(dir_name, new_fname)
    f = open(full_filepath, 'wb')
    f.write(data)
    f.close()

    return full_filepath

def write_cert(cert_name, emp_id, data, filename):
    dir_name = os.path.join(DATA_FOLDER, FILES_FOLDER, CERTS_FOLDER, str(emp_id))
    os.makedirs(dir_name, exist_ok=True)

    new_fname = f"{cert_name}.{filename.split('.')[-1]}"

    # Check if cert with same name exist
    for (idirpath, dirnames, filenames) in os.walk(dir_name):
        for fname in filenames:
            if fname.split('.')[0] == new_fname.split('.')[0]:
                os.remove(os.path.join(dir_name, fname))
        break # Only walk first level dir

    # Write Cert
    full_filepath = os.path.join(dir_name, new_fname)
    f = open(full_filepath, 'wb')
    f.write(data)
    f.close()

    return full_filepath

def write_mrpt(data, filename):
    dir_name = os.path.join(DATA_FOLDER, FILES_FOLDER, BUDGET_FOLDER)
    os.makedirs(dir_name, exist_ok=True)

    now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_fname = f"MRPT_{now_str}.xlsx"

    # Write MRPT
    full_filepath = os.path.join(dir_name, new_fname)
    f = open(full_filepath, 'wb')
    f.write(data)
    f.close()

    return full_filepath

def delete_file(filepath):
    os.remove(filepath)

def delete_cert_files_dir():
    dir_name = pathlib.Path(f"{DATA_FOLDER}/{FILES_FOLDER}/{CERTS_FOLDER}")
    shutil.rmtree(dir_name)

### Historic
def migrate_training_proof(old_filepath:str, year:int, emp_id:int, train_id:int):
    dir_name = os.path.join(DATA_FOLDER, HISTORY_FOLDER, str(year), TRAIN_PROOF_FOLDER, str(emp_id))
    os.makedirs(dir_name, exist_ok=True)

    _, old_filename = os.path.split(old_filepath)
    new_fname = f"{train_id}.{old_filename.split('.')[-1]}"

    remove_duplicate_file(dir_name, new_fname)

    # Migrate
    full_filepath = os.path.join(dir_name, new_fname)
    shutil.copy(old_filepath, full_filepath)
    
    return full_filepath

def migrate_busu_proof(old_filepath:str, year:int, emp_id:int, busu_id:int):
    dir_name = os.path.join(DATA_FOLDER, HISTORY_FOLDER, str(year), BUSU_ENG_FOLDER, str(emp_id))
    os.makedirs(dir_name, exist_ok=True)

    _, old_filename = os.path.split(old_filepath)
    new_fname = f"{busu_id}.{old_filename.split('.')[-1]}"

    remove_duplicate_file(dir_name, new_fname)

    # Migrate
    full_filepath = os.path.join(dir_name, new_fname)
    shutil.copy(old_filepath, full_filepath)
    
    return full_filepath

def migrate_pa_completion(old_filepath:str, year:int, prj_id:int):
    dir_name = os.path.join(DATA_FOLDER, HISTORY_FOLDER, str(year), PA_CMPLT_FOLDER, str(prj_id))
    os.makedirs(dir_name, exist_ok=True)

    _, old_filename = os.path.split(old_filepath)
    new_fname = f"{prj_id}.{old_filename.split('.')[-1]}"

    remove_duplicate_file(dir_name, new_fname)

    # Migrate
    full_filepath = os.path.join(dir_name, new_fname)
    shutil.copy(old_filepath, full_filepath)
    
    return full_filepath

def migrate_cert(old_filepath:str, year:int, emp_id:int, cert_id:int):
    dir_name = os.path.join(DATA_FOLDER, HISTORY_FOLDER, str(year), CERTS_FOLDER, str(emp_id), str(cert_id))
    os.makedirs(dir_name, exist_ok=True)

    _, old_filename = os.path.split(old_filepath)
    new_fname = f"{cert_id}.{old_filename.split('.')[-1]}"

    remove_duplicate_file(dir_name, new_fname)

    # Migrate
    full_filepath = os.path.join(dir_name, new_fname)
    shutil.copy(old_filepath, full_filepath)
    
    return full_filepath


### utils
def remove_duplicate_file(dir_name, new_fname):
    # Check if file with same name exist
    for (idirpath, dirnames, filenames) in os.walk(dir_name):
        for fname in filenames:
            if fname.split('.')[0] == new_fname.split('.')[0]:
                os.remove(os.path.join(dir_name, fname))
                return True
        break # Only walk first level dir
    
    return False