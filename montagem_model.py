import uuid
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from bson.json_util import dumps, loads
from models.model_base import ModelBase
from flask import request
from models.resource_model import ResourceModel
from models.tarefa_model import TarefaModel
from models.usuario_model import UsuarioModel
from audit_center import AuditCenter
import math 

import usuario_list_loja

PROJECTION_MONTAGEM = {
	"codigo"        : True,
	"loja_venda"    : True,
	"loja_saida"    : True,
	"cliente"       : True,
	"origem"        : True,
	"tempo_execucao": True,
	"status"        : True,
	"usu_cad"       : True,
	"mon_cad"       : True,
	"usu_alt"       : True,
	"mon_alt"       : True
}

class MontagemModel(ModelBase):

	def __init__(self):
		self.connect()

		self.model = None
		if(self.db):
			self.model = self.db.montagem

	def __interval_date_time(self, start, end):
		elapsed = end - start
		#min,secs=divmod(elapsed.days * 86400 + elapsed.seconds, 60)
		#hour, minutes = divmod(min, 60)
		return elapsed #'%.2d:%.2d:%.2d' % (hour,minutes,secs)

	def save(self, document):
		document["cod"]  = self.model.count() +1
		guid_montagem = self.model.save(document)
		
		guid_tarefa = TarefaModel().save({"guid_montagem": str(guid_montagem),"tipo_servico": "Nova Montagem", "status": "pendente"})

		doc_status = {
			"guid" : uuid.uuid4().hex, 
			"status": "pendente",
			"data_hora": datetime.now().isoformat(),
			"mom_cad": datetime.now().isoformat(),
			"tarefa": {"guid" : str(guid_tarefa)}
		}
		
		self.insert_status(guid_montagem, doc_status)
		
		return {"guid_montagem": str(guid_montagem), "guid_tarefa": str(guid_tarefa)}

	def update(self, guid, document):
		if (document.get("_id") != None):
			document.pop("_id")

		return self.model.update({"_id": ObjectId(guid)}, document)

	def insert_status(self, guid, document):
		status = document["status"]
		mom_cad = datetime.now().isoformat()
		evidencias = []
		
		for evidencia in document.get("evidencias") or []:
			resource = {
				"nome": evidencia.get("nome"),
				"data": evidencia["data"],
				"tipo": evidencia.get("tipo")
			}
			
			file_guid = ResourceModel().save(resource)
			evidencias.append(file_guid)
			
		doc_status = {
			"guid" : document.get("guid_status") or uuid.uuid4().hex, 
			"status": status,
			"data_hora": document["data_hora"],
			"usu_cad": request.headers.get('guid-user'),
			"mom_cad": mom_cad,
			"tpMotivo": document.get("tpMotivo"),
			"observacao": document.get("observacao"),
			"evidencias": evidencias,
			"tarefa": document["tarefa"]
		}
		
		doc = self.model.update(
			{"_id": ObjectId(guid)},
			{
				"$set": {"status":  status},
				"$addToSet": {"historico_status": doc_status}
			}
		)

		# task = list(TarefaModel().get_tarefa_by_guid(doc_status["tarefa"]["guid"]))[0]
		task = list(TarefaModel().get_tarefa_by_guid(doc_status["tarefa"]["guid"]))

		if(not task):
			return 'não integrado'

		task = task[0]

		last_execution = datetime.strptime(mom_cad, "%Y-%m-%dT%H:%M:%S.%f")

		task_last_execution = task.get("last_execution")
		# if (task_last_execution):
		# 	print('**task_last_execution**')
		# 	print(task_last_execution)
		# 	if ('Z' in task_last_execution):
		# 		last_execution = datetime.strptime(task_last_execution, "%Y-%m-%dT%H:%M:%S.%f%z")	
		# 	else:
		# 		last_execution = datetime.strptime(task_last_execution, "%Y-%m-%dT%H:%M:%S.%f")
		
		time_execution = datetime.strptime("1900-1-1T00:00:00.001", "%Y-%m-%dT%H:%M:%S.%f")
		
		task_time_execution = task.get("time_execution")
		# if (task_time_execution):
		# 	if ('Z' in task_time_execution):
		# 		time_execution = datetime.strptime(task_time_execution, "%Y-%m-%dT%H:%M:%S.%f%z")
		# 	else:
		# 		time_execution = datetime.strptime(task_time_execution, "%Y-%m-%dT%H:%M:%S.%f")

		# if(task["status"] in ["iniciado", "reiniciado"]):
		# 	time_execution = time_execution + self.__interval_date_time(last_execution, datetime.now())
		
		TarefaModel().update(doc_status["tarefa"]["guid"], 
			{"$set": 
				{
					"status":  status, 
					"last_execution" : mom_cad,
					"time_execution" : str(time_execution.isoformat())
				}
			}
		)

		tempo_total    = None
		tempo_execucao = None
		data_hora      = None

		if(status == "iniciado"):
			data_hora = {"data_hora.inicio": document["data_hora"]}
		if(status in ["parado", "finalizado", "cancelado"]):
			data_hora = {"data_hora.fim": document["data_hora"]}
		
			mont = list(MontagemModel().get_montagem_by_guid(guid, True, False, False))
			mont = mont[0]

			if(mont["historico_status"]):
				dataST = mont["historico_status"][0]["data_hora"]

				if ('Z' in dataST):
					dataSTIni = datetime.strptime(dataST[:-1], "%Y-%m-%dT%H:%M:%S.%f")	
				else:
					dataSTIni = datetime.strptime(dataST, "%Y-%m-%dT%H:%M:%S.%f")

				dataSTFim = None
				if(len(mont["historico_status"]) > 1):
					st = mont["historico_status"][len(mont["historico_status"])-1]

					if(st["status"] in ["parado", "finalizado", "cancelado"]):
						dataST = st["data_hora"]

						if ('Z' in dataST):
							dataSTFim = datetime.strptime(dataST[:-1], "%Y-%m-%dT%H:%M:%S.%f")	
						else:
							dataSTFim = datetime.strptime(dataST, "%Y-%m-%dT%H:%M:%S.%f")
				
				if(not dataSTFim):
					dataSTFim = datetime.now()

				dif = dataSTFim - dataSTIni
				tempo_total = (str(dif.days) + ' dias e ' if(dif.days > 0) else "") + str(math.trunc(dif.seconds / 60 / 60)) + ' horas'

				dataaAux = datetime.strptime('1900-1-1T00:00:00.001', "%Y-%m-%dT%H:%M:%S.%f")
				dif      = time_execution - dataaAux
				tempo_execucao = (
					(str(dif.days) + ' dias e '                           if(dif.days > 0) else "") +
					(str(math.trunc(dif.seconds / 60 / 60)) + ' horas e ' if(math.trunc(dif.seconds / 60 / 60) > 0) else "") +
					(str(math.trunc(dif.seconds / 60) % 60) + ' minutos')
				)

		if(data_hora != None):
			TarefaModel().update(doc_status["tarefa"]["guid"], {"$set": data_hora})
		
		self.model.update(
			{"_id": ObjectId(guid)},
			{
				"$set": {
					"tempo_execucao": tempo_execucao,
					"tempo_total"   : tempo_total,
					"time_execution": str(time_execution.isoformat())
				},
			}
		)

		return doc

	def add_evidencia(self, guid_status, json_evidencia):
		file_guid = ResourceModel().save(json_evidencia)

		montagens = list(self.model.find({"historico_status.guid": guid_status}))

		if (len(montagens) == 0):
			print(guid_status + " - Status informado não foi encontrado!")
			return 'não integrado'
			# raise Exception("Status informado não foi encontrado!")

		historico_status = montagens[0]["historico_status"] 
		for status in historico_status: 
			if (status.get("guid") == guid_status): 
				evidencias = status["evidencias"] = status["evidencias"] or []
				evidencias.append(file_guid)

		doc = self.model.update({"historico_status.guid": guid_status}, { "$set": {"historico_status": historico_status}})

		return doc

	def get_list_montagens(self, filter={}):
		document = self.model.find(filter, PROJECTION_MONTAGEM)
		return list(document)

	def get_list_montagens_by_status(self, pStatus):
		return self.get_list_montagens({"status": pStatus})

	def get_montagem_by_guid(self, guid, with_detail, add_tarefa, remove_evidencia = False):
		projection = None
		if not(with_detail):
			projection = PROJECTION_MONTAGEM
		elif (remove_evidencia):
			projection = {'historico_status.evidencias' : False}

		document = list(self.model.find({"_id": ObjectId(guid)}, projection))

		if (add_tarefa):
			document[0]['tarefas'] = list(TarefaModel().get_tarefa_by_montagem(guid))

		return document

	def get_list_montagens_group_by(self, type, filter, detail):
		if(type == '1'):
			group_id   = "$loja_venda.codigo"
			group_name = {"$first": "$loja_venda.codigo"}
		elif(type == '2'):
			group_id   = {"$arrayElemAt": [ "$tarefas.guid_montador", 0 ] }
			group_name = {"$first": {"$arrayElemAt": [ "$tarefas.guid_montador", 0 ]} }
		elif(type == '3'):
			group_id   = {"$arrayElemAt": [ "$produtos.codigo", 0 ] }
			group_name = {"$first": {"$arrayElemAt": [ "$produtos.nome", 0 ]}}
		else:
			group_id   = {}
			group_name = {"$first": None}
		
		rootMontagem = {"$push": "$$ROOT"} if detail else {"$first": None}

		filter["tarefas.data_hora_previsto"] = {"$exists": True}

		if (filter.get("categoria") != None):
			if(filter.get("categoria") == 'Pendente'):
				filter["$or"]   = [{"tarefas.data_hora.fim": {"$exists": False}}, {"tarefas.data_hora.fim": {"$eq": ""}}]
			if(filter.get("categoria") == 'Prazo'):
				filter["$and"]  = [{"tarefas.data_hora.fim": {"$exists": True }}, {"tarefas.data_hora.fim": {"$ne": ""}}]
				filter["$expr"] = { "$lte": ["$tarefas.data_hora.fim", "$tarefas.data_hora_previsto.fim"] }
			if(filter.get("categoria") == 'Fora'):
				filter["$and"]  = [{"tarefas.data_hora.fim": {"$exists": True}}, {"tarefas.data_hora.fim": {"$ne": ""}}]
				filter["$expr"] = { "$gt": ["$tarefas.data_hora.fim", "$tarefas.data_hora_previsto.fim"] }

			filter.pop("categoria")

		listEmp  = usuario_list_loja.get_usuario_lista_loja(request.headers.get('guid-user'))
		# dts_usu  = UsuarioModel().get_list_montadores({})
		# list_usu = []

		listEmp  = request.headers.get('lojas').split(',')

		# for usuario in dts_usu:
		# 	list_usu.append( str(usuario["_id"]) )

		# filter["mont"]            = {"$in" : list_usu}
		# filter["loja_venda.guid"] = {"$in" : listEmp}

		if(not ("loja_venda.codigo" in filter) ):
			filter["loja_venda.codigo"] = {"$in" : listEmp}

		dts = self.model.aggregate([
			{	"$addFields": { "guid": {"$toString": "$_id"} }	},
			{
				"$lookup":{
					"from"        : "tarefa",
					"localField"  : "guid",
					"foreignField": "guid_montagem",
					"as"          : "tarefas"
				}
			},
			{  	"$addFields": {"mont"                : {"$arrayElemAt": [ "$tarefas.guid_montador"            , 0 ]} } },
			{  	"$addFields": {"data_previsto_inicio": {"$arrayElemAt": [ "$tarefas.data_hora_previsto.inicio", 0 ]} } },
			{  	"$addFields": {"data_previsto_fim"   : {"$arrayElemAt": [ "$tarefas.data_hora_previsto.fim"   , 0 ]} } },
			{  	"$addFields": {"data_inicio"         : {"$arrayElemAt": [ "$tarefas.data_hora.inicio"         , 0 ]} } },
			{  	"$addFields": {"data_fim"            : {"$arrayElemAt": [ "$tarefas.data_hora.fim"            , 0 ]} } },
			{	"$match": filter},
			{
				"$group":{
					"_id"    : group_id,
					"name"   : group_name,
					"total"  : {"$sum": 1},
					"tarefas": { 
						"$push":  { 
							"data_hora"         : "$tarefas.data_hora",
							"data_hora_previsto": "$tarefas.data_hora_previsto",
							"loja_venda"        : "$loja_venda.codigo",
						}
					},
					"montagens": rootMontagem,
				}
			},
			{	"$project": { "guid" : 0, "montagens.origem" : 0, "montagens.tarefas" : 0,
							  "montagens.endereco.complemento"         : 0, "montagens.endereco.distrito"   : 0,
							  "montagens.endereco.latitude"            : 0, "montagens.endereco.longitude"  : 0,
							  "montagens.endereco.ponto_referencia"    : 0, "montagens.historico_status"    : 0,
							  "montagens.produtos.dicas"               : 0, "montagens.produtos.fornecedor" : 0,
							  "montagens.produtos.grupo"               : 0, "montagens.produtos.marca"      : 0,
							  "montagens.produtos.instrucoes_montagem" : 0, "montagens.produtos.modelo"     : 0} },
			{
				"$sort":{ "total" : -1 }
			}
		])

		montagens = list(dts)
		
		for montagem in montagens:
			tarefas = montagem["tarefas"]
			
			montagem["pendente"] = 0
			montagem["prazo"   ] = 0
			montagem["fora"    ] = 0

			for tarefa in tarefas:
				if(len(tarefa["data_hora_previsto"]) == 0):
					continue


				data_hora_fim      = tarefa["data_hora"][0].get("fim") if len(tarefa["data_hora"]) > 0 else None
				data_hora_previsto = tarefa["data_hora_previsto"][0].get("fim")

				if ( (data_hora_fim == None) or (data_hora_fim == '') ):
					montagem["pendente"] += 1
				elif (data_hora_fim <= data_hora_previsto):
					montagem["prazo"] += 1
				else:
					montagem["fora"] += 1

			del montagem["tarefas"]

			if(not detail):
				del montagem["montagens"]

		return montagens

	def pop_status(self, guid):

		historico_status = list(self.model.find({"_id": ObjectId(guid)}))[0]["historico_status"]

		last_status = len(historico_status) 
		if (last_status == 0):
			raise Exception("Não existem status para a montagem informada")
		
		if (last_status == 1):
			raise Exception("O status de pendente não pode ser removido!")

		before_status  = historico_status[last_status-2]
		current_status = historico_status[last_status-1]

		self.model.update({"_id": ObjectId(guid)},
			{
				"$set": {"status": before_status["status"]},
				"$pop": { "historico_status": 1}
			}
		)
		
		TarefaModel().update(before_status["tarefa"]["guid"], {"$set": {"status":  before_status["status"]}})
		
		if(before_status["status"] == "agendado"):
			TarefaModel().update(before_status["tarefa"]["guid"], {"$set": {"data_hora_previsto": {} }})
			TarefaModel().update(before_status["tarefa"]["guid"], {"$set": {"data_hora": {} }})
		elif(before_status["status"] == "agendado"):
			TarefaModel().update(before_status["tarefa"]["guid"], {"$set": {"data_hora": {} }})
		elif(before_status["status"] in ["parado", "finalizado", "cancelado"]):
			TarefaModel().update(before_status["tarefa"]["guid"], {"$set": {"data_hora.fim":  before_status["data_hora"]}})
		else:
			TarefaModel().update(before_status["tarefa"]["guid"], {"$set": {"data_hora.fim": '' }})

		AuditCenter.post("montagem.historico_status", "DELETE", current_status, {})

		return before_status
