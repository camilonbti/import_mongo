import sys
from controllers.controller import Controller
from flask import request
from bson.json_util import dumps
from models.montagem_model import MontagemModel
from models.loja_model import LojaModel
# from notification_center import NotificationCenter
from models.integracao_error_model import IntegracaoError
from lib.json_zip import json_zip
from controllers.tarefa_controller import TarefaController
from models.tarefa_model import TarefaModel

class MontagemController(Controller):

	def save_montagem(self):
		try:
			if( MontagemModel().erro ):
				return MontagemModel().erro

			document = request.json
			document["user_cad"] = "integracao"

			# cod_loja_entrada = document["loja_venda"]["codigo"]
			# cod_loja_saida   = document["loja_saida"]["codigo"]

			# loja_entrada = LojaModel().get_loja_by_codigo(cod_loja_entrada)
			# if (len(loja_entrada) == 0):
			# 	raise Exception("Erro encontrado, loja de venda " + cod_loja_entrada + " não encontrada")
			
			# loja_saida = LojaModel().get_loja_by_codigo(cod_loja_saida)
			# if (len(loja_saida) == 0):
			# 	raise Exception("Erro encontrado, loja de saida " + cod_loja_saida + " não encontrada")
			
			result = MontagemModel().save(document)
			# NotificationCenter.notify_new_monting(result)
			
			return dumps(result)
		except Exception as e: 
			return IntegracaoError().log(e, request)

	def update_montagem(self, guid):
		result = MontagemModel().update(guid, request.json)
		return dumps(result)

	def insert_status(self, guid):
		result = MontagemModel().insert_status(guid, request.json)

		# print(request.json)
		if(request.json["tarefa"]):
			# tarefa = TarefaModel().get_tarefa_by_guid(request.json["tarefa"]["guid"])[0]
			
			tarefa = TarefaModel().get_tarefa_by_guid(request.json["tarefa"]["guid"])

			if(not tarefa):
				return 'não integrado'

			tarefa = tarefa[0]

			if(tarefa["montagem"]):
				tarefa.pop("montagem")

			# print(tarefa)
			TarefaController().update_tarefa_assistencia(request.json["tarefa"]["guid"], tarefa)

		# NotificationCenter.notify_insert_status(result)
		return dumps(result)

	def add_evidencia(self, guid_status):
		result = MontagemModel().add_evidencia(guid_status, request.json)
		return dumps(result)

	def get_list_montagens(self):
		status = request.args.get('status')

		if (status == None):
			dataset = MontagemModel().get_list_montagens(self.getFilter())
		else:
			dataset = MontagemModel().get_list_montagens_by_status(status)

		# return dumps(dataset)
		return dumps( json_zip(dataset) )

	def get_montagem_by_guid(self, guid):
		dataset = MontagemModel().get_montagem_by_guid(guid, False, False)
		# return dumps(dataset)
		return dumps( json_zip(dataset) )

	def get_montagem_by_guid_with_detail(self, guid):
		dataset = MontagemModel().get_montagem_by_guid(guid, True, True)
		# return dumps(dataset)
		return dumps( json_zip(dataset) )

	def get_list_montagens_group_by(self, type):
		dataset = MontagemModel().get_list_montagens_group_by(type, self.getFilter(), False)
		# return dumps(dataset)
		return dumps( json_zip(dataset) )

	def get_list_montagens_group_by_detail(self, type):
		dataset = MontagemModel().get_list_montagens_group_by(type, self.getFilter(), True)
		# return dumps(dataset) 
		return dumps( json_zip(dataset) )

	def pop_status(self, guid):
		dataset = MontagemModel().pop_status(guid)
		return dumps(dataset)
