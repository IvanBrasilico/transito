"""
Bhadrasana.

Módulo Bhadrasana - AJNA
========================

Interface do Usuário - WEB
--------------------------

Módulo responsável por gerenciar bases de dados importadas/acessadas pelo AJNA,
administrando estas e as cruzando com parâmetros de risco.

Serve para a administração, pré-tratamento e visualização dos dados importados,
assim como para acompanhamento de registros de log e detecção de problemas nas
conexões internas.

Adicionalmente, permite o merge entre bases, navegação de bases, e
a aplicação de filtros/parâmetros de risco.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from transito.routes.dta import dta_app
from transito.views import configure_app

SQL_URI = os.environ.get('SQL_URI', 'mysql+pymysql://ivan@localhost:3306/transito')
engine = create_engine(SQL_URI)
Session = sessionmaker(bind=engine)
session = Session()
app = configure_app(session)
dta_app(app)

if __name__ == '__main__':
    print('Iniciando Servidor...')
    app.run(debug=app.config['DEBUG'])
