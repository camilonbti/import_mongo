from controllers.controller import Controller
from flask import Flask, request
from bson.json_util import dumps
from models.rota_model import RotaModel
from models.loja_model import LojaModel
from datetime import datetime
from models.integracao_error_model import IntegracaoError
from lib.json_zip import json_zip

class RotaController(Controller):

    def save_rota(self):
        result = RotaModel().save(request.json)
        return dumps(result)

    def update_rota(self, guid):
        result = RotaModel().update(guid, request.json)
        return dumps(result)

    def get_list_rotas(self):
        dataset = RotaModel().get_list_rotas(self.getFilter())
        return dumps( json_zip(dataset) )

    def get_rota_by_guid(self, guid):
        dataset = RotaModel().get_rota_by_guid(guid)
        return dumps( json_zip(dataset) )

    def pop_rota(self, guid):
        dataset = RotaModel().pop_rota(guid)
        return dumps(dataset)