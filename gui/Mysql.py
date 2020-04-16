#pip install mysql.connector
import mysql

import mysql.connector
from mysql.connector import errorcode

class Mysql(object):
    __instance = None

    __host = None
    __user = None
    __password = None
    __database = None

    __session = None
    __connection = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'__instance'):
            cls.__instance = super(Mysql, cls).__new__(cls)
        return cls.__instance

    #host = '10.58.36.113'
    #host='127.0.0.1'
    def __init__(self, host='127.0.0.1', user='', password='', database='contagil'):
        self.__host = str(host)
        print(f'Host {self.__host}')
        self.__user = user
        self.__password = password
        self.__database = database

    #Abre uma conexão com a database
    def _open(self):
        if (self.__connection is None):
            print(f'Estabelecendo conexão com o Banco de Dados {str(self.__host)}')
            print(f'Usuário: {self.__user}')
            try:
                self.__connection = mysql.connector.connect(host=self.__host, user=self.__user, password=self.__password, database=self.__database)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print('Algo deu errado com nome de usuário ou senha')
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print('Database não existe')
                else:
                    print(err)
        else:
            self.__session.close()

        self.__session = self.__connection.cursor(buffered=True)
        self.__session.execute("SET GLOBAL max_allowed_packet=1073741824")

        print("Conexão estabelecida")

    # Encerra a conexão com a database
    def _close(self):
        self.__session.close()
        if self.__connection is not None:
            self.__connection.close()
        self.__connection = None

    # Insere dados
    def insert(self, table, *args, **kwargs):
        values = None
        query = "INSERT INTO %s " % table
        if kwargs:
            keys = kwargs.keys()
            values = kwargs.values()
            query += "(" + ",".join(["`%s`"]*len(keys)) % tuple(keys) + ") VALUES(" + ",".join(["%s"]*len(values)) + ")"
        elif args:
            values = args
            query += " VALUES(" + ",".join(["%s"]*len(values)) + ")"
        self._open()
        self.__session.execute(query, values)
        self.__connection.commit()
        #self._close()
        return self.__session.lastrowid

    # Busca dados
    def select(self, table, where=None, *args):
        result = None
        query = "SELECT "
        keys = args
        l = len(keys) - 1
        for i, key in enumerate(keys):
            query += str(key)
            if i < l:
                query += ","
        query += " FROM " + str(table)
        if where:
            query += " WHERE "+ str(where)

        print(query)

        self._open()
        self.__session.execute(query)
        print(f'Resultado da consulta: {self.__session.rowcount} linhas')

        result = self.__session.fetchall()
        sequence = []
        sequence.append(self.__session.column_names)
        sequence.append(result)

        #self._close()
        return sequence

    # Exclui Dados
    def delete(self, table, index):
        query = "DELETE FROM %s WHERE uuid=%d" % (table, index)
        self._open()
        self.__session.execute(query)
        self.__connection.commit()
        #self._close()

    # Atualiza dados
    def update(self, table, where, **kwargs):
        query = f"UPDATE {table} SET"
        #print(f'kwargs.keys(){kwargs.keys()}\nkwargs.values(){kwargs.values()}')

        records_to_update = []
        i = 0
        for key, value in kwargs.items():
            records_to_update.append((value))
            if i > 0:
                query += ","
            query += f" {key} = %s"
            i+=1

        if where:
            query += f" WHERE {str(where)}"

        query = str(query)
        query = query.replace("='None'", ' is null')
        query = query.replace("= 'None'", ' is null')
        query = query.replace('=None', ' is null')
        query = query.replace('= None', ' is null')

        print(f"{query}")

        self._open()
        self.__session.execute(query, records_to_update)
        self.__connection.commit()
        #self._close()

