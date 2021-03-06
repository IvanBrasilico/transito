import sys
from _md5 import md5

import fitz
from PIL import Image
from bson import ObjectId
from gridfs import GridFS

if sys.platform == 'win32':
    sys.path.append('../ajna_docs/commons')
sys.path.append('.')
from transito.conf import logger

from transito.models.dta import Anexo


def edita_anexo(session, params):
    anexo = session.query(Anexo).filter(Anexo.id == params['id']).one()
    return gera_objeto(anexo,
                       session, params)


def lista_anexos(session, dta_id):
    try:
        dta_id = int(dta_id)
    except (ValueError, TypeError):
        return None
    return session.query(Anexo).filter(Anexo.dta_id == dta_id).all()


def get_anexo(session, anexo_id: int = None):
    if anexo_id is None or anexo_id == 'None':
        anexo = Anexo()
        return anexo
    return session.query(Anexo).filter(Anexo.id == anexo_id).one_or_none()


def gera_objeto(object, session, params):
    for key, value in params.items():
        if value and value != 'None':
            setattr(object, key, value)
    try:
        session.add(object)
        session.commit()
    except Exception as err:
        session.rollback()
        raise err
    return object


def insert_pagina(mongodb, png_image,
                  numero_dta: str, filename: str,
                  npagina: int) -> (ObjectId, bool):
    """
    Insere um png no fs.files. Se existir arquivo com mesmo md5 e filename,
    considera inserção repetida e retorna _id do existente.

    :param mongodb: Conexão e banco MongoDB
    :param png_image: conteúdo da imagem
    :param numero_dta: metadata.numero_dta
    :param filename: filename
    :param npagina: metadata.npagina
    :return: (ObjectId, True|False)
        ObjectId gerado ou _id de arquivo se já existe
        True se arquivo existe
        False se não existe e foi gerado novo documento
    """
    fs = GridFS(mongodb)
    content = png_image
    m = md5()
    m.update(content)
    grid_out = fs.find_one({'md5': m.hexdigest()})
    if grid_out:
        if grid_out.filename == filename:
            logger.warning(
                ' Arquivo %s Pagina %s MD5 %s  '
                'tentativa de inserir pela segunda vez!!' %
                (filename, npagina, m.hexdigest())
            )
            # File exists, abort!
            return grid_out._id, True
    # Insert File
    params = {'numero_dta': numero_dta, 'pagina': npagina}
    return fs.put(content, filename=filename,
                  metadata=params), False


def _processa_pdf(mongodb, numero_dta: str, filename: str, pdf):
    for npagina, page in enumerate(pdf, 1):
        pix = page.getPixmap()
        insert_pagina(mongodb, pix.getPNGData(),
                      numero_dta, filename, npagina)
    return npagina


def processa_pdf(mongodb, numero_dta: str, filename: str):
    pdf = fitz.open(filename)
    return _processa_pdf(mongodb, numero_dta, filename, pdf)


def processa_pdf_stream(mongodb, numero_dta: str, file):
    pdf = fitz.open(stream=file.read(), filetype='pdf')
    return _processa_pdf(mongodb, numero_dta, file.filename, pdf)


def get_documentos(mongodb, numero_dta: str) -> list:
    params = {'metadata.numero_dta': numero_dta}
    projection = {'filename': 1, '_id': -1}
    cursor = mongodb.fs.files.find(params, projection)
    filenames = set([document['filename'] for document in cursor])
    return list(filenames)


def get_paginas(mongodb, numero_dta: str, filename: str) -> list:
    params = {'filename': filename,
              'metadata.numero_dta': numero_dta}
    return list(mongodb.fs.files.find(params, {'_id': 1}))


def get_npaginas(mongodb, numero_dta: str, filename: str) -> int:
    params = {'filename': filename,
              'metadata.numero_dta': numero_dta}
    return mongodb.fs.files.count_documents(params)


def get_pagina(mongodb, numero_dta: str, filename: str, npagina: int) -> Image:
    params = {'filename': filename,
              'metadata.numero_dta': numero_dta,
              'metadata.pagina': npagina}
    document = mongodb.fs.files.find_one(params, {'_id': 1})
    print(document)
    if document is None:
        raise KeyError('Página não encontrada com os parâmetros: ' % params)
    return get_pagina_id(mongodb, document['_id'])


def get_pagina_id(conn, oid: str) -> Image:
    fs = GridFS(conn)
    _id = ObjectId(oid)
    grid_out = fs.get(_id)
    return grid_out.read()


if __name__ == '__main__':
    import os

    sys.path.append('.')

    filename = sys.argv[1]
    print('Testando PDF %s ' % filename)
    mongodb = MongoClient('mongodb://localhost')
    conn = mongodb['transito']
    print('Enviando páginas para o MongoDB')
    npaginas = processa_pdf(conn, '1234', os.path.basename(filename))
    print('Consultando páginas geradas')
    npaginas = get_npaginas(conn, '1234', filename)
    print('Páginas geradas: %s' % npaginas)
    for i in range(1, npaginas + 1):
        image = get_pagina(conn, '1234', filename, i)
        print('Salvando página %s em png' % i)
        image.save('%s.png' % i)
