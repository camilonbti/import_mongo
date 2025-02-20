from controllers.controller import Controller
from flask import Flask, request
from bson.json_util import dumps
from models.regional_model import RegionalModel
from models.loja_model import LojaModel
from datetime import datetime
from models.integracao_error_model import IntegracaoError

class RegionalController(Controller):

	def save_regional(self):
		result = RegionalModel().save(request.json)
		return dumps(result)

	def save_regional_integracao(self):
		try:
			document = request.json
			document["user_cad"] = "integracao"
			document["mom_cad"] = datetime.now().isoformat()
			regional = RegionalModel().get_regional_by_codigo(document["codigo"])

			lojas_with_guid = []
			for item in document.get("lojas"):
				loja = LojaModel().get_loja_by_codigo(item)			

				if (len(loja) == 0) : 
					return "Erro encontrado, loja " + item + " não encontrada", 400
				
				lojas_with_guid.append(str(loja[0]["_id"]))

			document["lojas"] = lojas_with_guid
			if (len(regional) == 0):
				result = RegionalModel().save(document)
			else:
				result = RegionalModel().update(str(regional[0]["_id"]), document)
			
			return dumps(result)
		except Exception as e: 
			return IntegracaoError().log(e, request)

	def update_regional(self, guid):
		result = RegionalModel().update(guid, request.json)
		return dumps(result)

	def get_list_regionais(self):
		dataset = RegionalModel().get_list_regionais(self.getFilter())
		return dumps(dataset)

	def get_regional_by_guid(self, guid):
		dataset = RegionalModel().get_regional_by_guid(guid)
		return dumps(dataset)