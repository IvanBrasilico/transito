import requests
import os
import sys

sys.path.append('.')

BASE_URL = 'http://localhost:5010'
filename = sys.argv[1]
files = {'file': open(filename, 'rb')}
print(files)
rv = requests.post(BASE_URL + '/api/processa_pdf',
                   data={'numero_dta': '1234'},
                   files=files)
print(rv.status_code)
print(rv.text)

rv = requests.get(BASE_URL + '/api/get_documentos/1234')
print(rv.status_code)
print(rv.text)

rv = requests.post(BASE_URL + '/api/get_npaginas',
                   data={'numero_dta': '1234',
                         'filename': os.path.basename(filename)})
print(rv.status_code)
print(rv.text)
npaginas = int(rv.json()['npaginas'])

rv = requests.post(BASE_URL + '/api/get_paginas',
                   data={'numero_dta': '1234',
                         'filename': os.path.basename(filename)})
print(rv.status_code)
print(rv.text)

for pagina in rv.json()['paginas']:
    print(pagina)
