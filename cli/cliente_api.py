"""
Script de linha de comando para acessar/testar API

"""
import fitz
import warnings
warnings.simplefilter('ignore')
USAGE = """
Script de linha de comando para acessar/testar API
python cli/cliente_api.py         # Esta tela
python cli/cliente_api.py -usage  # Esta tela
python cli/cliente_api.py -help   # Mostra opções
# Informe o endereço do Servidor com:
# --base_url https://ajna.labin.rf08.srf/transito 
# Envia um PDF local para o Servidor
python cli/cliente_api.py --carregar --numero_dta=1234 --filename msc-thesis.pdf
# Envia um PDF para Servidor gerando PNGs localmente
python cli/cliente_api.py --carregarpngs --numero_dta=1234 --filename msc-thesis.pdf
# Lista documentos(filenames) vinculados à DTA no Servidor
python cli/cliente_api.py --numero_dta=1234
# Lista páginas do documento(filename) vinculado à DTA no Servidor
python cli/cliente_api.py --numero_dta=1234 --filename msc-thesis.pdf
# Faz download do PNG
python cli/cliente_api.py --oid abcdef0012126e
"""
import os
import sys

import click
import requests

sys.path.append('.')

BASE_URL = 'https://ajna.labin.rf08.srf/transito'


def carrega_pngs(base_url, numero_dta, filename):
    """
    Processa PDF localmente e envia somente PNGs

    :param base_url: Endereço raiz do Servidor da API
    :param numero_dta: Número da DTA cujo anexo está sendo informado
    :param filename: Arquivo de anexo da DTA
    """
    pdf = fitz.open(filename)
    for npagina, page in enumerate(pdf, 1):
        pix = page.getPixmap()
        files = {'file': ('%s.png' %npagina, pix.getPNGData())}
        print('Enviando página %s' % npagina)
        rv = requests.post(base_url + '/api/insert_pagina',
                           data={'numero_dta': numero_dta,
                                 'filename': filename,
                                 'npagina': npagina},
                           files=files,
                           verify=False)
        print(rv.status_code)
        print(rv.text)


def carrega_pdf(base_url, numero_dta, filename):
    files = {'file': open(filename, 'rb')}
    print(files)
    rv = requests.post(base_url + '/api/processa_pdf',
                       data={'numero_dta': numero_dta},
                       files=files,
                       verify=False)
    print(rv.status_code)
    print(rv.text)


def lista_documentos(base_url, numero_dta):
    rv = requests.get(base_url + '/api/get_documentos/%s' % numero_dta,
                      verify=False)
    print(rv.status_code)
    print(rv.text)
    return


def get_paginas(base_url, numero_dta, filename):
    rv = requests.post(base_url + '/api/get_npaginas',
                       data={'numero_dta': numero_dta,
                             'filename': os.path.basename(filename)},
                       verify=False)
    print(rv.status_code)
    print(rv.text)
    npaginas = int(rv.json()['npaginas'])
    rv = requests.post(base_url + '/api/get_paginas',
                       data={'numero_dta': numero_dta,
                             'filename': os.path.basename(filename)},
                       verify=False)
    print(rv.status_code)
    print(rv.text)


def get_pagina_id(base_url, id):
    rv = requests.get(base_url + '/api/get_pagina_id/%s' % id,
                      verify=False)
    print(rv.status_code)


@click.command()
@click.option('--base_url', help='Endereço da API. Padrão: %s' % BASE_URL,
              default=BASE_URL)
@click.option('--numero_dta', help='Número da DTA')
@click.option('--filename', help='Nome do arquivo anexo')
@click.option('--carregar', is_flag=True,
              help='Se indicado, carrega filename.' + \
                   ' Se não indicado, consulta Servidor.')
@click.option('--carregarpngs', is_flag=True,
              help='Se indicado, processa filename localmente e envia pngs.' + \
                   '. Se não indicado, consulta Servidor.')
@click.option('--oid', help='ObjectId do arquivo png a baixar')
@click.option('--usage', is_flag=True,
              help='Mostrar exemplos de uso.')
def cli(base_url, numero_dta, filename, carregar, carregarpngs, oid, usage):
    if usage:
        print(USAGE)
        sys.exit(0)
    if oid:
        get_pagina_id(base_url, oid)
    else:
        if carregar:
            carrega_pdf(base_url, numero_dta, filename)
        elif carregarpngs:
            carrega_pngs(base_url, numero_dta, filename)
        else:
            if filename:
                get_paginas(base_url, numero_dta, filename)
            else:
                lista_documentos(base_url, numero_dta)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print(USAGE)
    else:
        cli()
