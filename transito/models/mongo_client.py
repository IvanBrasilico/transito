import os

import requests

from transito.conf import logger



def lista_documentos(base_url, numero_dta):
    print('Fazendo request')
    print(base_url + '/api/get_documentos/%s' % numero_dta)
    rv = requests.get(base_url + '/api/get_documentos/%s' % numero_dta,
                      verify=False)
    print(rv.text)
    try:
        result = rv.json()['documentos']
        return result
    except Exception as err:
        logger.error(err)
        logger.error('Status code: %s Msg: %s' % (rv.status_code, rv.text))
        raise Exception(rv.text)


def get_npaginas(base_url, numero_dta, filename):
    rv = requests.post(base_url + '/api/get_npaginas',
                       data={'numero_dta': numero_dta,
                             'filename': os.path.basename(filename)},
                       verify=False)
    try:
        result = int(rv.json()['npaginas'])
        return result
    except Exception as err:
        logger.error(err)
        logger.error('Status code: %s Msg: %s' % (rv.status_code, rv.text))
        raise Exception(rv.text)


def get_paginas(base_url, numero_dta, filename):
    rv = requests.post(base_url + '/api/get_paginas',
                       data={'numero_dta': numero_dta,
                             'filename': os.path.basename(filename)},
                       verify=False)
    try:
        result = rv.json()
        return result
    except Exception as err:
        logger.error(err)
        logger.error('Status code: %s Msg: %s' % (rv.status_code, rv.text))
        raise Exception(rv.text)


def get_pagina_id(base_url, id):
    rv = requests.get(base_url + '/api/get_pagina_id/%s' % id,
                      verify=False)
    return rv.content, rv.status_code
