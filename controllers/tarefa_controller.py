import json
import requests

from controllers.controller import Controller
from flask import request
from bson.json_util import dumps
from models.tarefa_model import TarefaModel
from models.montagem_model import MontagemModel
# from notification_center import NotificationCenter
from lib.json_zip import json_zip
from datetime import datetime
from environment import Config

class TarefaController(Controller):

	def save_tarefa(self):
		result = TarefaModel().save(request.json)
		#self.update_tarefa_assistencia(result, request.json)
		# NotificationCenter.notify_new_task(result)
		return dumps(result)

	def update_tarefa(self, guid):
		result = TarefaModel().update(guid, request.json)
		self.update_tarefa_assistencia(guid, request.json)
		# NotificationCenter.notify_update_task(result)
		return dumps(result)

	def get_list_tarefas(self):
		dataset = TarefaModel().get_list_tarefas(self.getFilter())
		# return dumps(dataset)
		return dumps( json_zip(dataset) )

	def get_tarefa_by_guid(self, guid):
		dataset = TarefaModel().get_tarefa_by_guid(guid)
		# return dumps(dataset)
		return dumps( json_zip(dataset) )

	def get_tarefa_montador_by_guid_montador(self, guid):
		dataset = TarefaModel().get_tarefa_montador_by_guid_montador(guid)
		# return dumps(dataset)
		return dumps( json_zip(dataset) )
	
	def pop_tarefa(self, guid):
		dataset = TarefaModel().pop_tarefa(guid)
		return dumps(dataset)

	def update_tarefa_assistencia(self, guid, item):
		ds_montagem = MontagemModel().get_montagem_by_guid(item["guid_montagem"], True, False)
		if (ds_montagem[0]["origem"].get("tipo") != "assistencia"):
			return
		
		dtIni = item["data_hora_previsto"]["inicio"] if ( ("data_hora_previsto" in item) and ("inicio" in item["data_hora_previsto"]) ) else ""
		dtFim = item["data_hora"]["fim"]             if ( ("data_hora"          in item) and ("fim"    in item["data_hora"])         ) else ""

		url = f'http://{Config["host_assistencia"]}/api/ASSISTENCIA/ASSISTENCIA_TAREFAS'
		obj = {
			"GUIDASSISTENCIA_TAREFAS" : guid,
			"GUIDASSISTENCIA"         : ds_montagem[0]["origem"]["id_origem"],
			"GUID_STATUS"             : "montagemstatus_" + item["status"],
			"GUID_USUARIO"            : item["id_usuario"],
			"DTABERTURA"              : datetime.now().isoformat(),
			"DTPREVISAO"              : dtIni,
			"DTFINALIZADO"            : dtFim,
			"DESCRICAO"               : f'(Montagem) {item["status"]}  -  {item["tipo_servico"]}',
			"READONLY"                : "S"
		}

		resp = requests.post(url, json=obj, headers={ "client-token" :request.environ['HTTP_CLIENT_TOKEN']})

		if (resp.status_code != 200):
			raise Exception(resp.reason)
		

