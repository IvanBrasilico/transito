"""Configurações específicas do Bhadrasana."""
import logging
import os
import pickle
import sys
import tempfile

from dominate.tags import img

APP_PATH = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_PATH, 'files')
CSV_FOLDER = os.path.join(APP_PATH, 'CSV')
CSV_DOWNLOAD = CSV_FOLDER
CSV_FOLDER_TEST = os.path.join(APP_PATH, 'tests/CSV')
ALLOWED_EXTENSIONS = set(['txt', 'csv', 'zip'])
tmpdir = tempfile.mkdtemp()

tmpdir = tempfile.mkdtemp()

logo = img(src='/static/material_logo.svg', height='40')

try:
    with open('SECRET', 'rb') as secret:
        try:
            SECRET = pickle.load(secret)
        except pickle.PickleError:
            SECRET = None
except FileNotFoundError:
    SECRET = None

if SECRET is None:
    SECRET = os.urandom(24)
    with open('SECRET', 'wb') as out:
        pickle.dump(SECRET, out, pickle.HIGHEST_PROTOCOL)

FORMAT_STRING = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO'),
                    format=FORMAT_STRING)
logger = logging.getLogger('transito')
try:
    fn = getattr(sys.modules['__main__'], '__file__')
    root_path = os.path.abspath(os.path.dirname(fn))
    if root_path.find('.exe') != -1:
        root_path = os.path.dirname(__file__)
except AttributeError:
    root_path = os.path.dirname(__file__)
log_file = os.path.join(root_path, 'error.log')
print('Fazendo log de erros e alertas no arquivo ', log_file)
error_handler = logging.FileHandler(log_file)

activity_file = os.path.join(root_path, 'access.log')
print('Fazendo log de atividade no arquivo ', activity_file)
activity_handler = logging.FileHandler(activity_file)

out_handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter(
    fmt=FORMAT_STRING,
    datefmt='%Y-%m-%d %H:%M')
error_handler.setFormatter(formatter)
activity_handler.setFormatter(formatter)
out_handler.setFormatter(formatter)
error_handler.setLevel(logging.WARNING)
activity_handler.setLevel(logging.INFO)
logger.addHandler(activity_handler)
logger.addHandler(error_handler)
