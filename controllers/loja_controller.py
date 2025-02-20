from controllers.controller import Controller
from flask import Flask, request
from bson.json_util import dumps
from models.loja_model import LojaModel
from datetime import datetime
from models.integracao_error_model import IntegracaoError

class LojaController(Controller):

	def save_loja(self):
		result = LojaModel().save(request.json)
		return dumps(result)

	def save_loja_integracao(self):
		try:
			document = request.json
			document["user_cad"] = "integracao"
			document["mom_cad"] = datetime.now().isoformat()
			loja = LojaModel().get_loja_by_codigo(document["codigo"])

			if (len(loja) == 0):
				result = LojaModel().save(document)
			else:
				result = LojaModel().update(str(loja[0]["_id"]), document)
			
			return dumps(result)
		except Exception as e: 
			return IntegracaoError().log(e, request)

	def get_list_lojas(self):
		dataset = LojaModel().get_list_lojas(self.getFilter())
		return dumps(dataset) 

	def get_list_lojas_by_user(self):
		dataset = LojaModel().get_list_lojas_by_user(self.getFilter())
		return dumps(dataset) 

	def get_loja_by_guid(self, guid):
		dataset = LojaModel().get_loja_by_guid(guid)
		return dumps(dataset)

	def update_loja(self, guid):
		result = LojaModel().update(guid, request.json)
		return dumps(result)