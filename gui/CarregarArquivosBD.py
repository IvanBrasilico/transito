import ConformidadeDossie

def CarregarArquivosBD(cpf, password):
    conformidade = ConformidadeDossie.ConformidadeDossie(cpf, password, salvarArquivosBD=True)

CarregarArquivosBD(cpf='03141019932', password='mysql2Flai!')
