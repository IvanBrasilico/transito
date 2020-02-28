
# Form Avaliação Trânsito
Um pequeno boilerplate exemplificando uma aplicação Flask+Bootstrap+JQuery, utilizando os mesmos modelos que no AJNA.


Arquitetura:

* Instalação:

O arquivo setup.py contém as dependências configuradas.

Em um prompt Linux com Python3.6+, executar:
```
#git clone https://github.com/IvanBrasilico/transito
#cd transito
#python3.6 -m venv venv
#. venv/bin/activate
#pip install .[dev] # <-em produção não precisa do [dev] 
```

Em Windows com Anaconda instalado, abrir um prompt do Anaconda
```
#git clone https://github.com/IvanBrasilico/transito
#cd transito
#python -m venv venv
#venv/Scripts/activate.bat
#pip install .[dev] 
```

* Inicializar o Banco de Dados

No Servidor MySQL local, crie o Banco de Dados 'transito' e dê permissão. Para criar as tabelas já com alguns dados de teste:

```
#python transito/models/dta.py 
```

**É possível fazer os passos acima pelos menus do PyCharm.**

* Testando

```
#python -m pytest tests/
#tox
```

* Rodando localmente

```
#python wsgi_debug.py
```

* Rodando em produção

```
#gunicorn wsgi_production:app
```

Ver também arquivos Procfile (Heroku) e supervisor.conf (Supervisor)


* Estrutura de diretórios

/ 

Arquivos de configuração da instalação e deploy

/tests

Arquivos com testes automáticos

/transito

Arquivo com entradas gerais da aplicação

/forms

Formulários wtforms para facilitar a produção de HTML, 
validação e BIND entre camada de frontend e backend.

/models

Classes para comunicação com o banco de dados, acessadas preferencialmente somente por
*managers*.

Módulos *manager* para funcões ou classes que implementem as regras 
de negócio e comunicação entre os routes e os models.

/routes

Rotas/controladores básicos da interface web. Recebem as requisições, dão 
tratamento inicial mínimo e de fluxo de exceção, utilizam forms para BIND entre 
interface e  *managers*.

/templates

HTML e JavaScripts, a interface propriamente dita, utilizando templates Jinja

/static

HTML, CSS e JavaScript estáticos/de terceiros - na produção deve ser copiado para o Servidor web





