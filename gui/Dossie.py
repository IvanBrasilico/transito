import ArquivoPDF
import re

class Dossie(object):
    _mysql = None
    _tableArquivos = None

    _numeroDT = None
    _tipoDT = None
    _numeroDossie = None
    _extracaoData = None
    _extracaoHora = None
    _distribuicaoData = None
    _distribuicaoHora= None
    _tiposDocObrigatorios = None

    _listaIdCarga = []
    _listaFaturaNum = []
    _listaFaturaVlr = []
    _listaMoeda = []
    _listaDescrCarga = []

    _listaURL = []
    _listaArquivos = []

    _pathArquivos = None

    def __init__(self, numDT, tipoDT, numDossie, extracaoData, extracaoHora, mysql, tableArquivos, pathArquivos):
        self._numeroDT = numDT
        self._tipoDT = tipoDT
        self._numeroDossie = numDossie
        self._extracaoData = extracaoData
        self._extracaoHora = extracaoHora
        self._mysql = mysql
        self._tableArquivos = tableArquivos
        self._tiposDocObrigatorios = self._carregarTiposDocObrigatorios()

        self._listaIdCarga = []
        self._listaFaturaNum = []
        self._listaFaturaVlr = []
        self._listaMoeda = []
        self._listaDescrCarga = []

        self._listaURL = []
        self._listaArquivos = []

        self._pathArquivos = pathArquivos

    @property
    def numeroDT(self):
        return self._numeroDT

    @property
    def tipoDT(self):
        return self._tipoDT

    @property
    def numeroDossie(self):
        return self._numeroDossie

    @property
    def extracaoData(self):
        return self._extracaoData

    @property
    def extracaoHora(self):
        return self._extracaoHora

    # Para implementar ess trecho é necessário executar SQL, por hora desnecessário
    #@property
    #def distribuicaoData(self):
    #    return self._distribuicaoData
    #@property
    #def distribuicaoHora(self):
    #    return self._distribuicaoHora


    def _carregarTiposDocObrigatorios(self):
        semExigencias = tuple()
        semExigencias = (None, 'DTC - TRANSITO DE CONTEINER', 'DTT - BAGAGEM ACOMPANHADA EXTRAVIADA', \
                         'DTT - FEIRA EADI', 'DTT - ORIGEM EADI', 'DTT - PARTES E PECAS', \
                         'DTT - PASSAGEM PELO EXTERIOR', \
                         'DTT - BENS TRIP/PASSAG ORIG/DEST EXT, NAO CLAS COMO BAG', 'DTT - OUTROS')

        docObrigatorios = dict()
        docObrigatorios = {'DTA - ENTRADA COMUM': ['conhecimento de carga', 'fatura'], \
                           'DTA - ENTRADA ESPECIAL - BAGAGEM DESACOMPANHADA': ['conhecimento de carga'], \
                           'DTA - ENTRADA ESPECIAL - MALA DIPLOMATICA': ['conhecimento de carga'], \
                           'DTA - ENTRADA ESPECIAL - OUTRAS': ['conhecimento de carga'], \
                           'DTA - ENTRADA ESPECIAL - URNA FUNERARIA': ['conhecimento de carga'], \
                           'DTA - PASSAGEM COMUM': ['conhecimento de carga', 'fatura'], \
                           'DTA - PASSAGEM ESPECIAL - BAGAGEM DESACOMPANHADA': ['conhecimento de carga'], \
                           'DTA - PASSAGEM ESPECIAL - MALA DIPLOMATICA': ['conhecimento de carga'], \
                           'DTA - PASSAGEM ESPECIAL - OUTRAS': ['conhecimento de carga'], \
                           'DTA - PASSAGEM ESPECIAL - PARTES E PECAS': ['conhecimento de carga'], \
                           'DTA - PASSAGEM ESPECIAL - URNA FUNERARIA': ['conhecimento de carga'], \
                           'DTI - TRANSBORDO/BALDEACAO INTERNACIONAL': ['conhecimento de carga'], \
                           'DTT - COMAT': ['chave NFE de venda', 'chave NFE de transferência'], \
                           'DTT - LOJA FRANCA': ['chave NFE de venda'], \
                           'MIC-DTA - ENTRADA': ['conhecimento de carga', 'fatura', 'MIC DTA'], \
                           'MIC-DTA - PASSAGEM': ['conhecimento de carga', 'fatura', 'MIC DTA'], \
                           'TIF-DTA - ENTRADA': ['fatura', 'TIF DTA'], \
                           'TIF-DTA - PASSAGEM': ['fatura', 'TIF DTA'] }

        if self.tipoDT in semExigencias:
            return ''
        elif self.tipoDT in docObrigatorios.keys():
            return docObrigatorios.get(self.tipoDT)
        else:
            print("Erro! Tipo desconhecido de DT")
            exit(0)

    @property
    def listaIdCarga(self):
        return self._listaIdCarga

    def _numeroFaturaEstaNaDescricao(self, texto):
        texto = str(texto).strip().lower()
        #print(f'numeroFaturaEstaNaDescricao {texto}')
        listOfStrings = ["vide", "ver", "desc", "obs", "relac"]
        for x in listOfStrings:
            if x in texto:
                #print("Número de fatura no campo descrição")
                return True
        else:
            #print("Número de fatura em campo próprio")
            return False

    def _limparDescricao(self, textoOriginal):
        textoOriginal = str(textoOriginal).strip()

        diversas = False
        if 'divers' in textoOriginal.lower():
            diversas = True

        #print(textoOriginal)
        texto = re.sub(r'\b(\d+\,\d{2})\b', ' ', textoOriginal).strip()  # elimina valores
        # print(f'1 {texto}')

        texto = re.sub(r'[,-]', ' ', texto).strip()  # substitui virgula por espaço em branco
        # print(f'1 {texto}')

        texto = re.sub(r'\b[^\d\W]+\b', ' ', texto).strip()  # elimina palvras sem números
        # print(f'2 {texto}')

        texto = re.sub(r'[^A-Za-z0-9+]', ' ', texto).strip()  # elimina carcteres especiais e palavras acentuadas
        # print(f'3 {texto}')

        texto = re.sub(r'  ', ' ', texto).strip()  # elimina 2 espaços em branco
        # texto = re.search('\w*\D\w*', textoOriginal)

        texto = texto.strip()

        if (diversas):
            if texto != '':
                texto = texto + ' '
            texto = texto + 'Diversas'

        if texto == '':
            print('Não foi possível tratar a descrição')
            texto = None

        return texto

    @property
    def docObrigatorios(self):
        listaDoc = []
        for tipo in self._tiposDocObrigatorios:
            tipo = str(tipo).strip()
            #print(f'tipo {tipo}')
            if tipo == 'conhecimento de carga':
                for conhecimento in self.listaIdCarga:
                    listaDoc.append('Conhecimento '+str(conhecimento))
            elif tipo == 'fatura':
                #print(f'self._listaDescrCarga {self._listaDescrCarga}')
                for i, numFatura in enumerate(self.listaFaturaNum):
                    numFatura = str(numFatura).strip()
                    #print(f'i {i} numFatura {numFatura}')
                    if self._numeroFaturaEstaNaDescricao(numFatura):
                        temp = self._limparDescricao(str(self._listaDescrCarga[i]))
                        if temp is None:
                            listaDoc.append("Fatura " + stre(numFatura) + " " + str(self._listaDescrCarga[i]))
                        else:
                            listaDoc.append("Fatura " + temp)
                    else:
                        listaDoc.append("Fatura "+str(numFatura))
            else:
                listaDoc.append(tipo)
        return listaDoc

    @property
    def listaFaturaNum(self):
        return self._listaFaturaNum

    @property
    def listaFaturaVlr(self):
        return self._listaFaturaVlr

    @property
    def listaMoeda(self):
        return self._listaMoeda

    @property
    def listaDescrCarga(self):
        return self._listaDescrCarga

    @property
    def listaURL(self):
        if len(self._listaURL) < 1:
            self.__carregarURL()
        return self._listaURL

    def _nome(self, url):
        x = str(url).split('/')
        x = str(x[-1]).split('\/')
        x = str(x[-1]).split('//')
        x = str(x[-1]).split('\\')
        return x[-1]

    def __carregarURL(self):
        print("Carregando URL")
        dados = None
        dados = self._mysql.select(self._tableArquivos,
                   f"DOSSIE_NUM='{self.numeroDossie}' AND EXTRACAO_DATA='{self.extracaoData}' AND EXTRACAO_HORA='{self.extracaoHora}'", "DOSSIE_ARQ_URL")
        dados = dados[1]
        for linha in dados:
            if self._pathArquivos is not None:
                self._listaURL.append(self._pathArquivos+'\\'+self.numeroDossie+'\\'+self._nome(url=linha[0]))
                print(self._pathArquivos+'\\'+self.numeroDossie+'\\'+self._nome(url=linha[0]))
            else:
                self._listaURL.append(linha[0])

    @property
    def listaArquivos(self):
        if len(self._listaArquivos) < 1:
            self.__carregarArquivos()
        return self._listaArquivos

    @property
    def limparArquivos(self):
        self._listaArquivos = []

    def __carregarArquivos(self):
        print("Carregando Arquivos")
        self._listaArquivos = []
        if len(self.listaURL) > 0:
            for url in self.listaURL:
                #print(url)
                self._listaArquivos.append(ArquivoPDF.ArquivoPDF(url))
        else:
            self._listaArquivos.append(ArquivoPDF.ArquivoPDF(None))

    @property
    def listaNomesArquivos(self):
        listaNomes = []
        for obj in self.listaArquivos:
            listaNomes.append(obj.nome)
        return listaNomes



