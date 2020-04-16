#https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_PDF_Viewer.py
#pip install PyMuPDF PySimpleGUI mysql.connector pillow pymongo
import PySimpleGUI as sg
from sys import exit
import re
import ArquivoPDF
import Dossie
import ConformidadeDossie

sg.theme('Dark Blue 3')

fonte = 'Arial '
fonte_tamanhoNormal = '10 '
fonte_negrito = 'bold '
sg.SetOptions(font=fonte+fonte_tamanhoNormal, auto_size_buttons=True, border_width=1, element_padding=(2,1))


def selecionarArquivo():
    """Abre janela para que o usuário indique o arquivo a ser carregado
    """
    nomeArq = sg.popup_file('PDF Browser', 'Abrir Arquivo PDF', file_types=(("Arquivo PDF", "*.pdf"),))
    if nomeArq is None:
        print(f'Operação cancelada pelo usuário.')
        exit(0)
    if nomeArq.strip() is '':
        print(f'Arquivo não selecionado pelo usuário.')
        exit(0)
    return nomeArq


def criarJanela(conformidade, indiceDossie=0, indiceArq=0, indiceFiltros=0):

    # Abaixo relação de icones para botões - Base64 String
    # https://pysimplegui.readthedocs.io/en/latest/cookbook/
    # https://www.iconfinder.com/icons/3671851/full_screen_icon
    #iconFullScreen = b''
    # https://www.iconfinder.com/icons/809309/fold_interface_layout_page_page_fold_icon
    #iconSupEsq = b'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACd0lEQVR4Xu2bPUscQRiAH79K/0Ea/RMSBYUgoogJREXBRg3a2AiKpWirhATSpYhJo4VWdmohKoiW/oFgaSdiofiB8soeHufeerezMzczO1ffzO3zzLsz7ztzUwe0AH+BdqCRfHwegGNgog44ADrzwf2G8lAE3Odo5EsNPIiAp5yO/gt2EFAmAr4DJ55FRgcwW8pULgKGgS3PBIwCG0FAiYEQAWXmgPAKhDkgTIJhFQjLYMgD/DKgLRFSKaZWgQVDnq0TsAZMGoKXn7FKwDbwFXjMo4AjoAe4NQhvTQScAV3AlWF4KwT8B6Qmv6gBvBUC9oF+4CavAoR7D/hSIwnWrAK1kmCNgFpFglEBMuGdA58S3nfTkWBMgCx1vcAlsAkMWCLBiIBD4HPROt8ErANDFkjQLkDS25GYDK8B+AeMvSOhT3NqrFWAFDZTCQD1wG/gW4wEqSbngB+a8wNtAlYqLGllC/4XMFMEKsXQNPBHM7zWTLDaZ5c9gHngLnotTG29aYuAagXI9xeBU2AnTeOUbawSkJJBqVkQEA5HHTsd7o4myWalwH9t/AFoK+3L1tNhgd+N/sGSEX98N7YKkMRqXCt51LmtAiQ3GCx6RhUXH6PlNu5VWvZdQCI8sOSzgHfhJax8FVARvK8CKob3UUBV8L4JqBreJwGp4H0RkBreBwFK8K4LUIZ3WUAm8K4KyAzeRQGZwrsmIHN4lwRogXdFgNxnlO3z2HpeSlqVzQIXqsFrXfBJEfAzOrhQkavSVi43vdnALOpwWXXkC325eG0uM/ikCFAZPZ1tM4UvCHDl6mzm8AUBLlye1gJfENAKyD68rdfntcGLgGfX+RuJrIZWZQAAAABJRU5ErkJggg=='

    dossie = conformidade.listaDossies[indiceDossie] # Inicia com o primeiro dossie
    arq = dossie.listaArquivos[indiceArq]

    ZoomBotoes1 = [
        [sg.Button('.',  size=(4, 2), key=(i,j), pad=(0,0)) for j in range(2)] for i in range(2)
    ]

    ZoomBotoes2 = [
        #[sg.Button('Original', image_data=iconFullScreen, size=(8, 4), key=("0"), pad=(0,0))],
        [sg.Button('100%', size=(7, 2), key=("Original"), pad=(0,0))],
        [sg.Button('Girar', size=(7, 2), key=("Girar"), pad=(0, 0))]
    ]

    frameZoom = [
        [
            sg.Frame('Zoom:', [
                [sg.Column(ZoomBotoes1), sg.Column(ZoomBotoes2)]
            ])
        ]
    ]

    selecioneDossie = [
        [sg.Text('Selecione o Dossiê:')],
        [sg.Listbox(values=conformidade.listaDossieNum(), size=(20, 5), key='lbDossies', enable_events=True)]
    ]

    if indiceFiltros == 0:
        indiceFiltros = 'Por Analisar'
    elif indiceFiltros == 1:
        indiceFiltros = 'Concluídos'
    else:
        indiceFiltros = 'Todos'

    filtroDossie = [
        [sg.Text('Filtro de Dossiê:')],
        [sg.Combo(values=['Por Analisar','Concluídos','Todos'],  default_value=indiceFiltros, size=(12, 1), key='cbFiltroDossies', enable_events=True)],
        [sg.Text(size=(1, 1), font=fonte + '1 ')],
        [
            sg.Text(size=(1, 1), font=fonte+'1 '),
            sg.Button('Gravar\nAnalise', size=(8, 2), key="GravarAnalise", pad=(0,0)),
        ],
    ]

    # Define compomnetes de interface que não exigem atualização a cada mudança de arquivo
    Navegacao_listaArquivos = [
        [sg.Listbox(values=dossie.listaNomesArquivos, size=(100, 10), key='lbArquivos', enable_events=True)]
    ]

    FrameNavegacao = [
        [sg.Column(filtroDossie), sg.Column(selecioneDossie), sg.Column(frameZoom)],
        [sg.Text(size=(1, 1), font=fonte+'1 ')],
        [sg.Text('Selecione o documento para análise:')],
        [sg.Column(Navegacao_listaArquivos, size=(411, 90), scrollable=True)],
        [sg.Text(size=(1, 1), font=fonte+'1 ')],
    ]

    DossieDescricoes = [
        [
            sg.Text(size=(13, 1)),
            sg.Button('Anterior', key='DescrAnt'),
            sg.InputText(f'1 de {str(len(dossie.listaDescrCarga))}', size=(10, 1), justification='center', key='gotoDescr'),
            sg.Button('Próxima', key='DescrProx')
         ],
        [sg.Text(f'{dossie.listaDescrCarga[0]}', size=(52, 2), key='DescricaoCarga')],
    ]

    Dossie_ListaDocObrig = [
        [
            sg.Text(text=str(i+1)+". "+str(x).strip())
        ] for i, x in enumerate(dossie.docObrigatorios)
    ]

    FrameDossie = [
        [sg.Frame(f' Descrições: ', DossieDescricoes)],
        [sg.Frame(f' Documentos obrigatórios: ',
                  [
                      [sg.Column(Dossie_ListaDocObrig, key='colunaDocObrig', size=(403, 220), scrollable=True)]
                  ])
         ]
    ]

    Arquivo_Classificacao = [
        [
            sg.Checkbox(text=f'{str(i + 1)}.{str(x).strip()}', size=(60, 5), key='cbDocObrig'+str(i), enable_events=True)
        ] for i, x in enumerate(dossie.docObrigatorios)
    ]

    FrameArquivo = [
        [sg.Text(f'{str(arq.nomeTratado)}', size=(50, 1), key='arquivoSelecionadoTratadoT2', font=fonte+fonte_tamanhoNormal+fonte_negrito)],
        [sg.Text(size=(1, 1), font=fonte+'1 ')],
        [sg.Text(f'Este documento contém...', font=fonte+fonte_tamanhoNormal+fonte_negrito)],
        [sg.Column(Arquivo_Classificacao, size=(403, 92), scrollable=True)],
        [sg.Text(size=(1, 1), font=fonte+'1 ')],
        [sg.Text(f'Constatações sobre o documento:', font=fonte+fonte_tamanhoNormal+fonte_negrito)],

        [sg.Checkbox(f'Falta algo', key='docIncompleto', disabled=False)],
        [sg.Checkbox(f'Baixa qualidade', key='docQualidade', disabled=False)],
        [sg.Text(size=(1, 1), font=fonte+'1 ')],
        [sg.Text(f'Observação sobre o documento:', font=fonte+fonte_tamanhoNormal+fonte_negrito)],
        [sg.Multiline(size=(58, 4), key='obs', disabled=False)]
    ]


    layoutEsquerda = [
        [sg.Text(f'Usuário: {conformidade.cpf()}', font=fonte + fonte_tamanhoNormal + fonte_negrito)],
        [sg.Frame(' NAVEGAÇÃO ', FrameNavegacao)],
        [sg.Text(size=(1, 1), font=fonte+'1 ')],
        [sg.TabGroup([
            [sg.Tab('CLASSIFICAR DOCUMENTO', FrameArquivo, key='tab1'),
             sg.Tab(f'STATUS DO DOSSIÊ {str(dossie.numeroDossie)}', FrameDossie, key='tab2')]
            ], key='tabGroup')
         ]
    ]

    layoutPDF = [
        [
            sg.Text('Pág:'),
            sg.Button('Anterior', key='PagAnt'),
            sg.InputText(f'1 de {str(arq.pagQtde)}', size=(10, 1), justification='center', key='gotoPag'),
            sg.Button('Próxima', key='PagProx'),
            sg.Text(f'{str(arq.nomeTratado)}', size=(50, 1), key='arquivoSelecionadoTratadoT1')
        ],

        [sg.Column( [
            [ sg.Image(data=arq.pagImg(pagNum=0, zoom=0), key='image_elem') ]
            ] , size=(845, 645), scrollable=True, key='colunaPag')]
#           ], size = (600, 645), scrollable = True, key = 'colunaPag')]
    ]

    layout = [[sg.Column(layoutEsquerda), sg.Column(layoutPDF)]]

    win=  sg.Window("Análise de conformidade de documentos", layout, return_keyboard_events=True, resizable=True,
                     location=(100,0), auto_size_text=True, auto_size_buttons=True, margins=(1,1), finalize=True)

    win.Element('lbDossies').Update(set_to_index=indiceDossie)
    win.Element('lbArquivos').Update(set_to_index=indiceArq)

    return win

def corrigePosicao(x, max):
    max -= 1
    if x > max:
        x = 0
    elif x < 0:
        x = max
    return x

def interfaceLogin():
    layout_esquerda = [
        [sg.Text('CPF:'), sg.Input(key='user', size=(12, 1))],
        [sg.Text('Senha:'), sg.Input(key='password', size=(12, 1), password_char='*')]
    ]

    layout_direita = [
        [sg.Text('', size=(1,1), font=fonte+'2 ')],
        [ sg.Button('Login', size=(6, 1), key=("btnLogin"), pad=(0, 0))]
    ]

    layout = [
        [sg.Column(layout_esquerda), sg.Column(layout_direita)]
    ]

    win = sg.Window('Login', layout,
                    auto_size_text=False,
                    default_element_size=(10, 1),
                    text_justification='r',
                    return_keyboard_events=True,
                    grab_anywhere=False)

    login = []
    while True:
        event, values = win.read()
        if event is None:
            login = None
            break

        if event == 'btnLogin':
            login.append(values['user'])
            login.append(values['password'])
            break

    win.close()
    win = None
    if login is not None:
        print(f'Login { login}')
        if login[0] is None or str(login[0]).strip() == '':
            login = None
            sg.PopupError('Informe o usuário!')
            interfaceLogin()
        if login[1] is None or str(login[1]).strip() == '':
            login = None
            sg.PopupError('Informe a senha!')
            interfaceLogin()
    return login

def exibirInterface(cpf=None, password=None):
    """Abre janela que exibe relação de arquivos PDF
    """
    if cpf is None:
        login = interfaceLogin()
        if login is None:
            print(f'Login abortado!')
            exit(0)
        else:
            cpf = login[0]
            password = login[1]
            login = None

    conformidade = ConformidadeDossie.ConformidadeDossie(cpf, password)

    # Inicialização das variáveis necessárias para o funcionamento da interface
    # Sempre que um novo aquivo for carregado, estas variáveis precisam ser atualizadas
    indiceFiltros = 0
    indiceDossie = 0
    indiceArq = 0
    pagAtual = 0
    descrAtual = 0
    old_page = 0
    zoom = 0
    old_zoom = 0  # Zoom pode ser ativado e desativado
    girar = 0

    dossie = conformidade.listaDossies[indiceDossie] # Inicia com o primeiro dossie
    arq = dossie.listaArquivos

    print(f'dossie {dossie}')
    #print(f'dossie URL {dossie.listaURL}')
    #print(f'dossie Arq {arq}')

    arq = arq[indiceArq]

    print(f'{arq.nome} com {arq.pagQtde} pág.')

    zoom_buttons = ("Original", (0, 0), (0, 1), (1, 0), (1, 1), "Girar")

    # Cria janela
    win = criarJanela(conformidade, indiceDossie, indiceArq)

    filtroDossieOLD = win.Element('cbFiltroDossies').Get()

    # Redimensionar janela - por fazer
    #win.Element('colunaPag').set_size(size=(600, 645))
    #win.Refresh()

    while True:
        force_page = False
        event, values = win.read(timeout=100)
        #print(f'event {event} {type(event)}')

        if event is None: # Clique em 'X' (fechar janela)
            break

        elif event in ("Escape:27",):  # Tecla ESQ
            break

        elif event[0] == chr(13):  # Tecla Enter
            try:
                pagAtual = int(values[0]) - 1  # converte para inteiro
                pagAtual = corrigePosicao(pagAtual, arq.pagQtde)
            except:
                pagAtual = 0
            win.Element('gotoPag').Update(str(pagAtual + 1))

        elif event == 'GravarAnalise':
            #print(win.Element('cbDocObrig').get)
            print(f"values {values}")

        elif event[0:len('cbDocObrig')] == 'cbDocObrig':
            temp = re.sub('^\d+\.','', win.Element(event).Text)
            #tipo =
            print(f"dossie.numeroDossie:{dossie.numeroDossie} ")
            print(f"temp{temp} dossie.numeroDossie:{dossie.numeroDossie} arq.nome:{arq.nome} zoom:{zoom} girar:{girar} cpf:{cpf} pagAtual:{pagAtual}")
            print(f"values {values}")



        elif event == 'DescrAnt':
            descrAtual -= 1
        elif event == 'DescrProx':
            descrAtual += 1

        if event == 'DescrAnt' or event == 'DescrProx':
            descrAtual = corrigePosicao(descrAtual, len(dossie.listaDescrCarga))
            win.Element('DescricaoCarga').Update(str(dossie.listaDescrCarga[descrAtual]))
            win.Element('gotoDescr').Update(str(descrAtual + 1) + " de " + str(len(dossie.listaDescrCarga)))

        elif event in ("PagProx", "Next:34", "MouseWheel:Down"):
            pagAtual = corrigePosicao(pagAtual+1, arq.pagQtde)

        elif event in ("PagAnt", "Prior:33", "MouseWheel:Up"):
            pagAtual = corrigePosicao(pagAtual-1, arq.pagQtde)

        elif event == (0, 0): #Superior Esquerdo
            zoom = 1
        elif event == (0, 1): #Sup Dir
            zoom = 2
        elif event == (1, 0): #Inferior Esquerdo
            zoom = 3
        elif event == (1, 1): #Inf Dir
            zoom = 4
        elif event == "Original":  #Full screen
            zoom = 0
        elif event == "Girar":  #Girar a página
            force_page = True
            girar = girar + 90
            if girar == 360:
                girar = 0
            print(f'Rotação da página {girar}º')
            # Redimensionar janela - por fazer
            #if girar == 90 or girar == 270:
            #    win.Element('colunaPag').set_size(size=(880, 645))
            #else:
            #    win.Element('colunaPag').set_size(size=(600, 645))

        # evita processar a mesma página mais de uma vez
        if pagAtual != old_page:
            zoom = old_zoom = 0
            force_page = True

        if event in zoom_buttons and zoom != old_zoom:
            print(f'zoom {zoom} old_zoom{old_zoom}')
            old_zoom = zoom
            force_page = True

        if event == 'cbFiltroDossies' and filtroDossieOLD != values["cbFiltroDossies"]:
            filtroDossieOLD = values["cbFiltroDossies"]
            print(f'Filtrar Dossiê: {values["cbFiltroDossies"]}')

#            conformidade = ConformidadeDossie.ConformidadeDossie(cpf, password)
            if filtroDossieOLD == 'Todos':
                conformidade.carregarDossies(todos=True)
                indiceFiltros = 2
            elif filtroDossieOLD == 'Concluídos':
                conformidade.carregarDossies(analisar=False)
                indiceFiltros = 1
            else:
                conformidade.carregarDossies(analisar=True)
                indiceFiltros = 0

            if conformidade.listaDossies[0].numeroDossie is None:
                pagAtual = 0
                descrAtual = 0
                old_page = 0
            event = 'lbDossies'

        if len(values["lbDossies"]) > 0:
            oldDossie = str(values["lbDossies"][0]).strip()
        else:
            oldDossie = None

        if event == 'lbDossies' and (str(dossie.numeroDossie).strip() != oldDossie \
                or conformidade.listaDossies[0].numeroDossie is None):
            print(f'Mudar dossiê...')
            print(f'Dossie corrente {dossie.numeroDossie}')
            #print(dossie.listaNomesArquivos)
            #print(dossie.listaDescrCarga)

            # Limpar lista de arquivos para desalocar memória
            # Evita estouro de memória que resulta em encerramento abrupto da aplicação
            dossie.limparArquivos

            if conformidade.listaDossies[0].numeroDossie is None:
                indiceDossie = 0
                dossie = conformidade.listaDossies[0]  # Inicia com o primeiro dossie
            else:
                indiceDossie = win.FindElement('lbDossies').GetIndexes()
                if len(indiceDossie) > 0:
                    indiceDossie = win.FindElement('lbDossies').GetIndexes()[0]
                else:
                    indiceDossie = 0
                dossie = conformidade.listaDossies[indiceDossie]

            indiceArq = 0

            print(f'Novo dossie {dossie.numeroDossie}')
            #print(f'dossie.listaNomesArquivos {dossie.listaNomesArquivos}')

            # Só é possível modificar o conteúdo de uma janela depois desabilitar
            win.Disable()
            winOld = win
            win = criarJanela(conformidade, indiceDossie, indiceArq, indiceFiltros)
            win.Enable()
            win.TKroot.focus_force() # Traz o foco para a janela criada
            winOld.Close() # Fecha a janela anterior
            winOld = None # libera da memória

            event = 'lbArquivos'

        if len(values["lbArquivos"]) > 0:
            oldArquivo = str(values["lbArquivos"][0]).strip()
        else:
            oldArquivo = None

        if event == 'lbArquivos' and (str(dossie.listaArquivos[indiceArq].nome).strip() != oldArquivo \
                or conformidade.listaDossies[0].numeroDossie is None):
            force_page = True
            pagAtual = 0
            girar = 0 #modificar aqui quando armazenar rotação da página em banco de dados
            zoom = 0  # Zoom pode ser ativado e desativado

            indiceArq = win.FindElement('lbArquivos').GetIndexes()
            if len(indiceArq) > 0:
                indiceArq = win.FindElement('lbArquivos').GetIndexes()[0]
            else:
                indiceArq = 0
            arq = dossie.listaArquivos[indiceArq]

            print(f'Mudar arquivo...')
            print(f'{arq.nome} com {arq.pagQtde} pág.')

        if force_page:
            print(f'Atualizar imagem de de arquivo')
            old_page = pagAtual
            old_zoom = zoom
            win.Element('arquivoSelecionadoTratadoT1').Update(str(arq.nomeTratado))
            win.Element('arquivoSelecionadoTratadoT2').Update(str(arq.nomeTratado))
            win.Element('image_elem').Update(data=arq.pagImg(pagNum=pagAtual, zoom=zoom, girar=girar))
            win.Element('gotoPag').Update(str(pagAtual + 1) + " de " + str(arq.pagQtde))
            win.Refresh()
    conformidade._mysql._close()




#ConformidadeDossie = ConformidadeDossie.ConformidadeDossie(cpf='03141019932', password='mysql2Flai!')
#exibirInterface(ConformidadeDossie)
#exibirInterface()
exibirInterface(cpf='03141019932', password='mysql2Flai!')

