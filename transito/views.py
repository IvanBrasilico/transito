"""
Transito
========================

Entrada básica: menu, logins, etc
--------------------------

"""
import os

from flask import (Flask, render_template, request)
from flask_bootstrap import Bootstrap
# from flask_cors import CORS
from flask_login import current_user
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_wtf.csrf import CSRFProtect

from transito.conf import APP_PATH, SECRET, logger, logo

app = Flask(__name__, static_url_path='/static')
csrf = CSRFProtect(app)
Bootstrap(app)
nav = Nav()
nav.init_app(app)


def configure_app(sqlsession, mongodb):
    """Configurações gerais e de Banco de Dados da Aplicação."""
    app.config['DEBUG'] = os.environ.get('DEBUG', 'None') == '1'
    if app.config['DEBUG'] is True:
        app.jinja_env.auto_reload = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.secret_key = SECRET
    app.config['SECRET_KEY'] = SECRET
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['sqlsession'] = sqlsession
    app.config['mongo_transito'] = mongodb
    return app


ALLOWED_EXTENSIONS = set(['csv', 'zip', 'txt', 'png', 'jpg', 'jpeg', 'sch'])


def allowed_file(filename, extensions=ALLOWED_EXTENSIONS):
    """Checa extensões permitidas."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions


def valid_file(file, extensions=['jpg', 'jpeg', 'png']):
    """Valida arquivo passado e retorna validade e mensagem."""
    if not file or file.filename == '' or not allowed_file(file.filename, extensions):
        if not file:
            mensagem = 'Arquivo nao informado'
        elif not file.filename:
            mensagem = 'Nome do arquivo vazio'
        else:
            mensagem = 'Nome de arquivo não permitido: ' + \
                       file.filename
            # print(file)
        return False, mensagem
    return True, None


@app.before_request
def log_every_request():
    """Envia cada requisição ao log."""
    name = 'No user'
    # if current_user and current_user.is_authenticated:
    #    name = current_user.name
    logger.info(request.url + ' - ' + name)


def get_user_save_path():
    user_save_path = os.path.join(APP_PATH,
                                  app.config.get('STATIC_FOLDER', 'static'),
                                  current_user.name)
    if not os.path.exists(user_save_path):
        os.mkdir(user_save_path)
    return user_save_path


@app.route('/')
def index():
    """View retorna index.html ou login se não autenticado."""
    return render_template('index.html')


@nav.navigation()
def mynavbar():
    """Menu da aplicação."""
    items = [View('Home', 'index'),
             View('Avaliar PDFs trânsito', 'avalia'),
             ]
    return Navbar(logo, *items)
