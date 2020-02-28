import os
import sys

from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware

sys.path.append('.')
os.environ['DEBUG'] = '1'
from transito.main import app

if __name__ == '__main__':
    print('Iniciando Servidor...')
    port = 5010
    application = DispatcherMiddleware(app,
                                       {
                                           '/transito': app
                                       })
    run_simple('localhost', port, application, use_reloader=True)
