import sys
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append('.')

from transito.models.dta import metadata, DTA, Anexo

from transito.models.dtamanager import edita_anexo, lista_anexos

engine = create_engine('sqlite://')
Session = sessionmaker(bind=engine)
session = Session()
metadata.create_all(engine)


class TestCase(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def debug(self) -> None:
        pass

    def test_DTA_Anexo(self):
        dta = DTA()
        dta.numero = '123'
        session.add(dta)
        session.commit()
        session.refresh(dta)
        anexo = Anexo()
        anexo.dta_id = dta.id
        anexo.nomearquivo = 'TESTE 1'
        anexo.observacoes = 'TESTE 1'
        session.add(anexo)
        session.commit()
        listaanexos = lista_anexos(session, dta.id)
        assert len(listaanexos) == 1
        params = {'id': listaanexos[0].id,
                  'nomearquivo': 'TESTE 2',
                  'observacoes': 'TESTE 2'}
        edita_anexo(session, params)
        listaanexos = lista_anexos(session, dta.id)
        assert len(listaanexos) == 1


if __name__ == '__main__':
    unittest.main()
