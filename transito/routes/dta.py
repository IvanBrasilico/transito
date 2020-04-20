import sys


from flask import request, render_template, url_for, flash, jsonify, Response
from flask_login import login_required
from werkzeug.utils import redirect

sys.path.append('.')

from transito.conf import logger
from transito.forms.dta import AnexoForm
from transito.models.dtamanager import lista_anexos, get_anexo, edita_anexo, processa_pdf_stream, \
    insert_pagina, get_documentos, get_paginas, get_npaginas, get_pagina, get_pagina_id
from transito.views import csrf, valid_file

from transito.models import api_client

base_url = api_client.BASE_URL
# TODO: Tranformar em comentário linha abaixo para consultar no Servidor.
#  Linha abaixo é apenas para testes locais
# base_url = 'https://localhost/transito'

def dta_app(app):
    @app.route('/avalia_api', methods=['GET', 'POST'])
    def avalia_api():
        session = app.config.get('sqlsession')
        numero_dta = request.args.get('numero_dta')
        filename = request.args.get('filename')
        npagina = request.args.get('npagina', 1)
        maxpaginas = 0
        listaanexos = []
        try:
            listaanexos = api_client.lista_documentos(base_url, numero_dta)
            if filename:
                maxpaginas = api_client.get_npaginas(base_url, numero_dta, filename)
            if not npagina:
                npagina = 1
            print(listaanexos, type(listaanexos))
        except Exception as err:
            flash(err)
            logger.error(err)  # , exc_info=True)
        return render_template('dta_anexos_api.html',
                               numero_dta=numero_dta,
                               filename=filename,
                               npagina=npagina,
                               maxpaginas=maxpaginas,
                               listaanexos=listaanexos)


    @app.route('/avalia', methods=['GET', 'POST'])
    def avalia():
        session = app.config.get('sqlsession')
        dta_id = request.args.get('dta_id', 1)
        anexo_id = request.args.get('item_id')
        oform = AnexoForm()
        listaanexos = []
        try:
            listaanexos = lista_anexos(session, dta_id)
            if anexo_id and anexo_id is not None:
                anexo = get_anexo(session, anexo_id)
                oform = AnexoForm(**anexo.__dict__)
        except Exception as err:
            flash(err)
            logger.error(err, exc_info=True)
        return render_template('dta_anexos.html',
                               listaanexos=listaanexos,
                               oform=oform)

    @app.route('/anexo', methods=['GET', 'POST'])
    # @login_required
    def dta_anexo():
        session = app.config.get('sqlsession')
        try:
            anexo_form = AnexoForm(request.form)
            anexo_form.validate()
            anexo = edita_anexo(session, dict(anexo_form.data.items()))
        except Exception as err:
            flash(err)
            logger.error(err, exc_info=True)
        return redirect(url_for('avalia', dta_id=anexo.dta_id))

    @app.route('/api/processa_pdf', methods=['POST'])
    @csrf.exempt
    def api_processa_pdf():
        conn = app.config.get('mongo_transito')
        try:
            numero_dta = request.form.get('numero_dta')
            if numero_dta is None:
                logger.error('Informe o parâmetro numero_dta')
                return jsonify({'msg': 'Informe o parâmetro numero_dta'}), 500
            file = request.files.get('file')
            if not file:
                return jsonify({'msg': 'Arquivo vazio'}), 500
            validfile, mensagem = \
                valid_file(file, extensions=['pdf'])
            if not validfile:
                print('Não é válido %s' % mensagem)
                return jsonify({'msg': mensagem}), 500
            npaginas = processa_pdf_stream(conn,
                                           numero_dta=numero_dta,
                                           file=file)
        except Exception as err:
            logger.error(str(err), exc_info=True)
            return jsonify({'msg': 'Erro: %s' % str(err)}), 500
        return jsonify({'msg': 'PDF incluído com %s páginas.' % npaginas}), 201

    def form_dta_filename_pagina(req_data):
        numero_dta = req_data.get('numero_dta')
        if numero_dta is None:
            logger.error('Informe o parâmetro numero_dta')
            raise KeyError('Informe o parâmetro numero_dta')
        filename = req_data.get('filename')
        if filename is None:
            logger.error('Informe o parâmetro filename')
            raise KeyError('Informe o parâmetro filename')
        npagina = req_data.get('npagina')
        if npagina is None:
            logger.error('Informe o parâmetro npagina')
            raise KeyError('Informe o parâmetro npagina')
        try:
            npagina = int(npagina)
        except ValueError:
            raise ValueError('npagina tem que ser um número inteiro. Recebi %s' %
                             npagina)
        return numero_dta, filename, npagina

    @app.route('/api/insert_pagina', methods=['POST'])
    @csrf.exempt
    def api_insert_pagina():
        conn = app.config.get('mongo_transito')
        try:
            numero_dta, filename, npagina = form_dta_filename_pagina(request.form)
            file = request.files.get('file')
            if not file:
                return jsonify({'msg': 'Arquivo vazio'}), 500
            validfile, mensagem = \
                valid_file(file, extensions=['png'])
            if not validfile:
                print('Não é válido %s' % mensagem)
                return jsonify({'msg': mensagem}), 500
            # content = file.read()
            logger.info('Chamar processa_pdf_bytes')
            _id, exists = insert_pagina(conn, file.read(),
                                        numero_dta, filename, npagina)
            if exists:
                return jsonify({'msg': 'Página %s já existente.' % npagina +
                                       ' id: %s' % str(_id)}), 201
        except Exception as err:
            logger.error(str(err), exc_info=True)
            return jsonify({'msg': 'Erro: %s' % str(err)}), 500
        return jsonify({'msg': 'Página %s incluída com sucesso.' % npagina +
                               ' id: %s' % str(_id)}), 201

    @app.route('/api/get_documentos/<numero_dta>', methods=['GET'])
    @csrf.exempt
    def api_get_documentos(numero_dta):
        conn = app.config.get('mongo_transito')
        lista_documentos = []
        try:
            lista_documentos = get_documentos(conn, numero_dta)
        except Exception as err:
            logger.error(str(err), exc_info=True)
            return jsonify({'msg': 'Erro: %s' % str(err)}), 500
        return jsonify({'documentos': lista_documentos}), 200

    def form_dta_filename(arequest, afunction, conn):
        req_data = arequest.json
        if req_data is None:
            req_data = arequest.form
        numero_dta = req_data.get('numero_dta')
        if numero_dta is None:
            logger.error('Informe o parâmetro numero_dta')
            raise KeyError('Informe o parâmetro numero_dta')
        filename = req_data.get('filename')
        if filename is None:
            logger.error('Informe o parâmetro filename')
            raise KeyError('Informe o parâmetro filename')
        return afunction(conn, numero_dta, filename)

    @app.route('/api/get_paginas', methods=['POST'])
    @csrf.exempt
    def api_get_paginas():
        conn = app.config.get('mongo_transito')
        try:
            lista_paginas = form_dta_filename(request, get_paginas, conn)
            lista_paginas = [str(item['_id']) for item in lista_paginas]
        except Exception as err:
            logger.error(str(err), exc_info=True)
            return jsonify({'msg': 'Erro: %s' % str(err)}), 500
        return jsonify({'paginas': lista_paginas}), 200

    @app.route('/api/get_npaginas', methods=['POST'])
    @csrf.exempt
    def api_get_npaginas():
        conn = app.config.get('mongo_transito')
        try:
            npaginas = form_dta_filename(request, get_npaginas, conn)
        except Exception as err:
            logger.error(str(err), exc_info=True)
            return jsonify({'msg': 'Erro: %s' % str(err)}), 500
        return jsonify({'npaginas': npaginas}), 200

    @app.route('/api/get_pagina', methods=['GET', 'POST'])
    @csrf.exempt
    def api_get_pagina():
        conn = app.config.get('mongo_transito')
        req_data = request.json
        if req_data is None:
            req_data = request.args
        try:
            numero_dta, filename, npagina = form_dta_filename_pagina(req_data)
            image = get_pagina(conn, numero_dta, filename, npagina)
        except Exception as err:
            logger.error(str(err), exc_info=True)
            return 'Erro: %s' % str(err), 500
        mimetype = 'image/png'
        return Response(response=image, mimetype=mimetype)

    @app.route('/api/get_pagina_id/<id>', methods=['GET'])
    @csrf.exempt
    def api_get_pagina_id(id):
        conn = app.config.get('mongo_transito')
        image = get_pagina_id(conn, id)
        mimetype = 'image/png'
        return Response(response=image, mimetype=mimetype)
