import os
import json
from pymongo import MongoClient
from environment import Config
from flask import request

# print("Abrindo conexão com o banco de dados")
# config_db = Config["database"]
# connection = MongoClient(config_db["host"])
# db = connection[config_db["database"]]

class Connection():

    db = None

    def createConnection(self, ignoreErroDB = False):
        try:
            # print("Abrindo conexão com o banco de dados")
            f     = open(os.environ['NBTI_NBSUPERSERVICE_CONFIGPATH'], "r", encoding='utf-8-sig')
            conf  = json.loads(f.read())
            token = request.headers.get("client-token").upper()

            if(not (token in conf)):
                raise Exception("Token do cliente inválido")

            config_db = conf[token]

            host  = config_db["Database_Mongo"]
            # host = uri[None : uri.find(':')]
            # path = uri[uri.find(':')+1 : None]
            # host = '127.0.0.1'

            # database_uri = "mongodb://"+host+"/?gssapiServiceName=mongodb"
            database_uri = "mongodb://"+host+"/"

            # connection   = MongoClient(database_uri, username='admin_atlz', password='ekwitGvy1')
            connection   = MongoClient(database_uri)

            self.db = connection["controllFixer_" + config_db["emrpesa"]]
        except Exception as e: 
            if(not ignoreErroDB):
                from models.integracao_error_model import IntegracaoError
                return IntegracaoError().log(e, request)


