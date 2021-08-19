import os

DATA_FOLDER     = 'data'

FILES_FOLDER    = 'files'
CERTS_FOLDER    = 'certs'
BUDGET_FOLDER   = 'budget'

def write_cert(cert_name, emp_id, data, filename):
    dir_name = os.path.join(DATA_FOLDER, FILES_FOLDER, CERTS_FOLDER, str(emp_id))
    os.makedirs(dir_name, exist_ok=True)

    new_fname = f"{cert_name}.{filename.split('.')[-1]}"

    full_filepath = os.path.join(dir_name, new_fname)

    f = open(full_filepath, 'wb')
    f.write(data)
    f.close()

    return full_filepath
