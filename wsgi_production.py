import sys

from werkzeug.middleware.dispatcher import DispatcherMiddleware

sys.path.append('.')

from transito.main import app

application = DispatcherMiddleware(app,
                                   {
                                       '/transito': app
                                   })
