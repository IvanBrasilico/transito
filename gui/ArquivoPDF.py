import fitz
from PIL import Image, ImageChops
"""
print(fitz._doc__)

PyMuPDF 1.16.10: Python bindings for the MuPDF 1.16.0 library.
Version date: 2019-12-21 07:31:32.
Built for Python 3.7 on win32 (64-bit)
"""

class ArquivoPDF(object):
    _id = None
    _url = None
    _pagQtde = None
    _listaPag = [None]
    _tipo = None
    _legivel = None

    def __init__(self, url):
        self._url = url
        self.abrirArquivo(url)
        if self._url is not None:
            self._pagQtde = self._arquivo.pageCount
            self._listaPag = [None] * self._pagQtde  # Lista que armazena a imagem correspondente a cada página
        else:
            self._pagQtde = 0
            self._listaPag = [None]
        self._tipo = None
        self._legivel = None

    def abrirArquivo(self, url):
        #print("Construindo objeto ... {}".format(self))
        #print(f'url: {url}')
        if (url is None) or (url.strip() is ''):
            self._arquivo = None
            #print(f'Arquivo não informado corretamente, operação cancelada!')
            #exit(0)
        else:
            self._arquivo = fitz.open(url)
            return self

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, x):
        self._tipo = x

    @property
    def legivel(self):
        return self._legivel

    @legivel.setter
    def legivel(self, x):
        self._legivel = x

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, x):
        self._id = x

    @property
    def nome(self):
        x = str(self._url).split('/')
        x = str(x[-1]).split('\/')
        x = str(x[-1]).split('//')
        x = str(x[-1]).split('\\')
        return x[-1]

    @property
    def nomeTratado(self):
        x = str(self.nome).split('Documentos___Outros_')
        x = str(x[-1]).split('Fatura_Comercial_')
        x = str(x[-1]).split('Conhecimento_de_Embarque_')
        x = str(x[-1]).split('Comprovante___Outros_')
        x = str(x[-1]).split('Romaneio_de_Carga__')
        x = str(x[-1]).split('Manifesto_Internacional_de_Carga__')
        return x[-1]


    @property
    def url(self):
        return self._url

    @property
    def arquivo(self):
        return self._arquivo

    @property
    def pagQtde(self):
        return self._pagQtde

    @property
    def listaPag(self):
        return self._listaPag

    def carregarPag(self, pagNum):
        pagNum = int(pagNum)
        if pagNum < 0:
            pagNum = 0
        #print(f'carregarpag pagNum {pagNum}')
        pag = self._listaPag[pagNum]
        if not pag and self._pagQtde > 0:  # cria a lista, se ainda não existir
            self._listaPag[pagNum] = self._arquivo.loadPage(pagNum)  # Cria um objeto página para futuro processamento
            pag = self._listaPag[pagNum]
            #print(f'carregarpag pag {pag}')
        return pag

    def pagImg(self, pagNum, zoom=0, girar=0):
        """Retorna uma imagem de uma determinada página. Se o zoom for diferente de 0, um dos quadrantes de 4 páginas será ampliado e a imagem correspondente retornada.
        """
        print(f'zoom {zoom}')

        pix = None

        if self._pagQtde > 0:

            pag = self.carregarPag(pagNum)

            pag.setRotation(girar)

            r = pag.rect  # retângulo correspondente ao tamanho da página

            bbox = self.coordenadasBordas(pag.getPixmap(alpha=False))
            if bbox:
                r = fitz.Rect(bbox[0], bbox[1], bbox[2], bbox[3])

            ptMedio   = r.top_left    + (r.bottom_right - r.top_left)    * 0.5  # ponto médio do retângulo
            mBordaSup = r.top_left    + (r.top_right    - r.top_left)    * 0.5  # meio da borda superior
            mBordaEsq = r.top_left    + (r.bottom_left  - r.top_left)    * 0.5  # meio da borda esquerda
            mBordaDir = r.top_right   + (r.bottom_right - r.top_right)   * 0.5  # meio da borda direita
            mBordaInf = r.bottom_left + (r.bottom_right - r.bottom_left) * 0.5  # meio da borda inferior

            if   zoom == 1:  # quadrante superior esquerdo
                clip = fitz.Rect(r.top_left, ptMedio)
            elif zoom == 2:  # quadrante superior direito
                clip = fitz.Rect(mBordaSup, mBordaDir)
            elif zoom == 3:  # quadrante inferior esquerdo
                clip = fitz.Rect(mBordaEsq, mBordaInf)
            elif zoom == 4:  # quadrante inferior direito
                clip = fitz.Rect(ptMedio, r.bottom_right)

            if zoom == 0:  # Página inteira
                clip = fitz.Rect(bbox[0], bbox[1], bbox[2], bbox[3])
                pix = pag.getPixmap(alpha=False, matrix=fitz.Matrix(1, 1), clip=clip)
                #pix = pag.getPixmap(alpha=False)
            else:
                pix = pag.getPixmap(alpha=False, matrix=fitz.Matrix(2, 2), clip=clip)

            pix =  pix.getPNGData()  # retorna uma imagem pag

        return pix

    def coordenadasBordas(self, pix):
        """
        Retorna as coordenadas das bordas para posterior corte
        """
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples) # Converte da classe class 'fitz.fitz.Pixmap' para class 'PIL.Image.Image'
        bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
        diff = ImageChops.difference(img, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            #img = img.crop(bbox) # Utilizado para cortar imagem, mas a resolução ficou ruim. Essa função retorna apenas as coordenadas

            x = 3 # Fator de correção para definição de corte
            bbox = list(bbox)
            if (bbox[0] - x) >= 0:
                bbox[0] = bbox[0] - x #x0 = margem esquerda

            if (bbox[1] - x) >= 0:
                bbox[1] = bbox[1] - x #y0 = margem superior

            bbox[2] = bbox[2] + x #x1 = margem direita

            bbox[3] = bbox[3] + x #y1 = margem inferior

            return bbox
        else:
            return None

    '''
        @property
        def (self):
            return self._

        @.setter
        def (self, x):
            self._ = x
    '''

    def obterParagrafos(self, pag):
        paragrafos = pag.getText("blocks")
        #print('paragrafos')

        temp = ''
        texto = ''

        for x in paragrafos:
            temp = str(x[4])
            temp.strip()

            if temp not in (None, ''):
                temp = temp.replace("\n"," ")
                temp = temp.replace("\r"," ")

                x = re.search("[a-z]", temp[0])
                if (x):
                    texto = texto + temp
                else:
                    texto = texto + "\n" + temp

        #print(texto)
        return texto

    def extrairTexto(self, pagInicio, pagFim):
        """Retorna o texto de determinadas página.
        """
        pagInicio = int(pagInicio)
        pagFim =  int(pagFim)
        texto = ''
        print(f'pagInicio {pagInicio} pagFim {pagFim}')

        if pagFim > pagInicio:
            pagFim =  pagFim + 1
            print('loop')
            for x in range(pagInicio, pagFim):
                print(x)
                texto = texto + self.obterParagrafos(pag=self.carregarPag(pagNum=x))
        else:
            print("sem loop")
            texto = self.obterParagrafos(pag=self.carregarPag(pagNum=int(pagInicio)))
        return texto