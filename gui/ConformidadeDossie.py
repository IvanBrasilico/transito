import ArquivoPDF
import Dossie
import Mysql
import time

class ConformidadeDossie(object):
    _mysql = None
    _cpf = None
    _tableConformidadeDossie = 'CONFORMIDADE_DOSSIE_AMOSTRA'
    _tableArquivos = 'CONFORMIDADE_DOSSIE_DOC_AMOSTRA'
    _tableAnalise = 'CONFORMIDADE_DOSSIE_ANALISE_AMOSTRA'
    _pathArquivos = r'\\10.68.100.50\conformidade_dossie'
    _pathArquivos = None

    _listaDossies = []

    def __init__(self, cpf, password, salvarArquivosBD=False):
        self._cpf = str(cpf)
        self._mysql = Mysql.Mysql(user='u'+cpf, password=str(password))
        self._autenticarStorage()

        if salvarArquivosBD:
            self._salvarArquivosBD()
        else:
            self.carregarDossies()

    def _autenticarStorage(self):
        print("Autenticação no storage em desenvolvimento...")

    @property
    def listaDossies(self):
        return self._listaDossies

    def listaDossieNum(self):
        listaNum = []
        for obj in self._listaDossies:
            listaNum.append(obj.numeroDossie)
        return listaNum

    def cpf(self):
        return self._cpf

    def carregarDossieVazio(self):
        print("Não há dossiê para o filtro selecionado.")
        dossie = Dossie.Dossie(numDT=None, tipoDT=None, numDossie=None, extracaoData=None, extracaoHora=None,
                               mysql=self._mysql, tableArquivos=self._tableArquivos, pathArquivos=self._pathArquivos)
        self.listaDossies.append(dossie)
        dossie.listaIdCarga.append(None)
        dossie.listaFaturaNum.append(None)
        dossie.listaFaturaVlr.append(None)
        dossie.listaMoeda.append(None)
        dossie.listaDescrCarga.append(None)

    def carregarDossies(self, analisar=True, todos=False):
        self._listaDossies = []
        print("Carregando Dossies")

        condicao = "EXECUCAO_CPF='"+self._cpf+"'"

        if todos is False:
            if analisar:
                condicao += " AND CONCLUSAO_DATA IS NULL"
            else:
                condicao += " AND CONCLUSAO_DATA IS NOT NULL"

        dados = self._mysql.select(self._tableAnalise, condicao, "DOSSIE_NUM, EXTRACAO_DATA, EXTRACAO_HORA, DISTRIBUICAO_DATA, DISTRIBUICAO_HORA")
        dados = dados[1]

        condicao = ''
        if len(dados) > 0:
            for i, linha in enumerate(dados):
                if i > 0:
                    condicao += f" OR "
                condicao += f"(DOSSIE_NUM='{linha[0]}' AND EXTRACAO_DATA='{linha[1]}' AND EXTRACAO_HORA='{linha[2]}')"

            print(f'condicao {condicao}')
            dados = self._mysql.select(self._tableConformidadeDossie, condicao, "*")
            #print(dados[0])
            #print(dados[1])
            dados = dados[1]

            dossie = ''
            dossieNumTemp = ''
            faturaNumTemp = ''
            cargaDescr = ''
            idCarga = ''

            if len(dados) > 0:
                for linha in dados:
                    print(f"linha: {linha}")

                    if linha[0] != dossieNumTemp: # Novo Dossie
                        dossieNumTemp = linha[0]
                        dossie = Dossie.Dossie(numDT=dossieNumTemp, tipoDT=linha[1], numDossie=linha[2], extracaoData=linha[8], extracaoHora=linha[9],
                                               mysql=self._mysql, tableArquivos=self._tableArquivos, pathArquivos=self._pathArquivos)
                        self.listaDossies.append(dossie)

                    if linha[3] != idCarga:
                        idCarga = linha[3]
                        dossie.listaIdCarga.append(idCarga)

                    if linha[4] != faturaNumTemp: # Nova fatura
                        faturaNumTemp = linha[4]
                        dossie.listaFaturaNum.append(faturaNumTemp)
                        dossie.listaFaturaVlr.append(linha[5])
                        dossie.listaMoeda.append(linha[6])

                    #print(f'dossie {dossie.numeroDossie} linha[7] {linha[7]}')
                    if linha[7] != cargaDescr: # Nova descrição
                        cargaDescr = linha[7]
                        dossie.listaDescrCarga.append(cargaDescr)

                print("Carregamento concluído!")
            else:
                self.carregarDossieVazio()
        else:
            self.carregarDossieVazio()


    def obterBinarioArquivo(self, url):
        with open(url, 'rb') as file:
            dadosBinarios = file.read()
        return dadosBinarios

    def _nome(self, url):
        x = str(url).split('/')
        x = str(x[-1]).split('\/')
        x = str(x[-1]).split('//')
        x = str(x[-1]).split('\\')
        return x[-1]

    def _salvarArquivosBD(self):

        dados = self._mysql.select(self._tableArquivos, 'DOSSIE_ARQ is null AND DOSSIE_ARQ_URL is not null',
                                   'DOSSIE_NUM, EXTRACAO_DATA, EXTRACAO_HORA, DOSSIE_ARQ_URL')

        dados = dados[1]

        if len(dados) > 0:
            for linha in dados:
                where = f"DOSSIE_NUM='{linha[0]}' AND EXTRACAO_DATA='{linha[1]}' AND EXTRACAO_HORA='{linha[2]}' AND DOSSIE_ARQ_URL like '%{self._nome(linha[3])}'"
                self._mysql.update(self._tableArquivos, where, DOSSIE_ARQ=self.obterBinarioArquivo(url=linha[3]))
                #time.sleep(1) # aguarda 2 segundo
        else:
            print("Não há arquivos novos a serem carregados na base de dados.")

'''
        @property
        def (self):
            return self._

        @.setter
        def (self, x):
            self._ = x
    '''




