import os
import shutil
import pathlib

DATA_FOLDER     = 'data'

FILES_FOLDER    = 'files'
CERTS_FOLDER    = 'certs'
BUDGET_FOLDER   = 'budget'

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

def delete_cert_files_dir():
    dir_name = pathlib.Path(f"{DATA_FOLDER}/{FILES_FOLDER}/{CERTS_FOLDER}")
    shutil.rmtree(dir_name)