from sqlalchemy import BigInteger, Column, VARCHAR, Boolean, Integer
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata

tipoConteudo = [
    'Nada',
    'Fatura',
    'Planilha',
    'Termo',
    'Outro'
]


class Enumerado:

    @classmethod
    def get_tipo(cls, listatipo: list, id: int = None):
        if (id is not None) and isinstance(id, int):
            return listatipo[id]
        else:
            return [(id, item) for id, item in enumerate(listatipo)]

    @classmethod
    def tipoConteudo(cls, id=None):
        return cls.get_tipo(tipoConteudo, id)


class DTA(Base):
    __tablename__ = 'dta_dtas'
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    numero = Column(VARCHAR(10), index=True, nullable=False)
    anexos = relationship('Anexo', back_populates='dta')


class Anexo(Base):
    __tablename__ = 'dta_anexos'
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    dta_id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                    ForeignKey('dta_dtas.id'))
    dta = relationship('DTA', back_populates='anexos')
    nomearquivo = Column(VARCHAR(200), index=True, nullable=False)
    observacoes = Column(VARCHAR(200), index=True, nullable=False)
    temconteudo = Column(Boolean(), index=True)
    qualidade = Column(Integer(), index=True)
    tipoconteudo = Column(Integer(), index=True)

    def get_tipoconteudo(self):
        return Enumerado.tipoConteudo(self.unidadedemedida)


if __name__ == '__main__':
    import sys

    sys.path.insert(0, '.')
    from transito.main import engine, session

    metadata.create_all(engine,
                        [
                            metadata.tables['dta_dtas'],
                            metadata.tables['dta_anexos'],
                        ])

    dta = DTA()
    dta.numero = '1234'
    session.add(dta)
    session.commit()
    session.refresh(dta)
    anexo = Anexo()
    anexo.dta_id = dta.id
    anexo.nomearquivo = 'Anexo1.pdf'
    anexo.observacoes = 'TESTE 1'
    session.add(anexo)
    anexo2 = Anexo()
    anexo2.dta_id = dta.id
    anexo2.nomearquivo = 'Anexo2.pdf'
    anexo2.observacoes = 'TESTE 2'
    session.add(anexo2)
    session.commit()
