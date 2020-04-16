import sys
from flask_wtf import FlaskForm

sys.path.append('.')

from transito.models.dta import Enumerado
from wtforms import IntegerField, TextAreaField, SelectField, BooleanField, StringField


class AnexoForm(FlaskForm):
    id = IntegerField('ID')
    dta_id = IntegerField('OVR')
    observacoes = TextAreaField(u'Observações',
                                render_kw={'rows': 5, 'cols': 100},
                                default='')
    temconteudo = BooleanField(u'Desmarcar se arquivo vazio',
                               default=1)
    qualidade = IntegerField(u'Qualidade da digitalização (0 a 10)',
                             default='')
    tipoconteudo = SelectField('Enumerado de Tipo do Conteúdo', default=0)
    nomearquivo = StringField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tipoconteudo.choices = Enumerado.tipoConteudo()
