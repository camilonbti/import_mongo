from datetime import datetime
from bson.objectid import ObjectId
from models.model_base import ModelBase
from flask import request
from models.usuario_model import UsuarioModel
import math 

import usuario_list_loja

class TarefaModel(ModelBase):

	def __init__(self):
		self.connect()
		self.model = self.db.tarefa

	def save(self, document):
		return self.model.save(document)

	def update(self, guid, document):
		if (document.get("_id") != None):
			document.pop("_id")

		return self.model.update({"_id": ObjectId(guid)}, document)

	def get_list_tarefas(self, filter):
		# listEmp  = usuario_list_loja.get_usuario_lista_loja(request.headers.get('guid-user'))
		# dts_usu  = UsuarioModel().get_list_montadores({})
		# list_usu = []

		listEmp  = request.headers.get('lojas').split(',')

		# for usuario in dts_usu:
		# 	list_usu.append( str(usuario["_id"]) )

		if (not ("$or" in filter)):
			filter["$or"] = [{"_id": {"$exists": True}}]

		if("only_agendado" in filter):
			# filter["$and"] = [{"montagem.loja_venda.guid": {"$in": listEmp }}, 
			# 				  {"guid_montador"           : {"$in": list_usu}},
			# 				  filter["$or"][0]
			filter["$and"] = [{"montagem.loja_venda.codigo": {"$in": listEmp }}, 
							#   {"guid_montador"           : {"$in": list_usu}},
							  filter["$or"][0]
			]

			newData = datetime.now()

			if(filter.get("montagem.status") == 'finalizado_prazo'):
				filter["$and"].append( {"data_hora.fim": {"$exists": True }})
				filter["$and"].append( {"data_hora.fim": {"$ne": ""}} )
				filter["$expr"] = { "$lte": ["$data_hora.fim", "$data_hora_previsto.fim"] }
				filter.pop("montagem.status")
			if(filter.get("montagem.status") == 'finalizado_fora'):
				filter["$and"].append( {"data_hora.fim": {"$exists": True }})
				filter["$and"].append( {"data_hora.fim": {"$ne": ""}} )
				filter["$expr"] = { "$gt": ["$data_hora.fim", "$data_hora_previsto.fim"] }
				filter.pop("montagem.status")
			if(filter.get("montagem.status") == 'agendado_prazo'):
				filter["$and"].append( {"data_hora.fim": {"$exists": False }})
				filter["$and"].append( {"data_hora_previsto.fim": {"$exists": True }})
				filter["$and"].append( {"data_hora_previsto.fim": {"$ne": ""}} )
				filter["$expr"] = { "$gt": ["$data_hora_previsto.fim", { "$dateToString": { "date": {"$toDate": datetime.strftime(newData, "%Y-%m-%dT%H:%M:%S.%f%z") }}} ]}
				filter.pop("montagem.status")
			if(filter.get("montagem.status") == 'agendado_fora'):
				filter["$and"].append( {"data_hora.fim": {"$exists": False }})
				filter["$and"].append( {"data_hora_previsto.fim": {"$exists": True }})
				filter["$and"].append( {"data_hora_previsto.fim": {"$ne": ""}} )
				filter["$expr"] = { "$lte": ["$data_hora_previsto.fim", { "$dateToString": { "date": {"$toDate": datetime.strftime(newData, "%Y-%m-%dT%H:%M:%S.%f%z") }}} ]}
				filter.pop("montagem.status")
			if(filter.get("montagem.status") == 'sem_agendamento'):
				for idx, val in enumerate(filter["$and"]):
					if("data_hora_previsto.fim" in val):
						filter["$and"].pop(idx)
				
				filter["$and"].append( {"data_hora_previsto.fim": {"$exists": False }})
				filter.pop("montagem.status")

			filter.pop("$or")
			filter.pop("only_agendado")
		elif("only_pendente" in filter):
			filter["$and"] = [
					{"data_hora_previsto.fim": {"$exists": False}},
					{"montagem.loja_venda.codigo": {"$in": listEmp }},
			]
			filter.pop("$or")
			filter.pop("only_pendente")
		else:
			filter["$or"] = [
					{"data_hora_previsto.fim": {"$exists": False}},
					# {"$and": [{"montagem.loja_venda.guid": {"$in": listEmp }}, 
					# 		  {"guid_montador"           : {"$in": list_usu}},
					# 		  filter["$or"][0] ] }
					{"$and": [{"montagem.loja_venda.codigo": {"$in": listEmp }}, 
							#   {"guid_montador"           : {"$in": list_usu}},
							  filter["$or"][0] ] }
			]

		if("exists_evidencia" in filter):
			if(filter["exists_evidencia"] == "0"):
				filter["$and"].append( {"montagem.historico_status.evidencias": { "$eq": [] }}  )
			else:
				filter["$and"].append( {"montagem.historico_status.evidencias": { "$gt": [] }}  )
			
			filter.pop("exists_evidencia")
		
		get_only_galeria = False
		if("only_galeria" in filter):
			get_only_galeria = True
			filter.pop("only_galeria")
		
		skip  = 0
		limit = 999999999
		if("skip" in filter):
			skip = int(filter["skip"])
			filter.pop("skip")
		if("limit" in filter):
			limit = int(filter["limit"])
			filter.pop("limit")

		get_count = False
		if("get_count" in filter):
			get_count = True
			filter.pop("get_count")

		cur = self.model.aggregate([
			{	"$addFields": { "guid": {"$toObjectId": "$guid_montagem"} }	},
			{
				"$lookup":{
					"from"        : "montagem",
					"localField"  : "guid",
					"foreignField": "_id",
					"as"          : "montagems"
				}
			},
			{  	"$addFields": { "produto"                 : {"$arrayElemAt": [ "$montagems.produtos", 0 ]} } },
			{	"$addFields": { "montagem"                : {"$arrayElemAt": [ "$montagems"         , 0 ] } } },
			{  	"$addFields": { "montagem.produto_nome"   : {"$arrayElemAt": [ "$produto.nome"      , 0 ]} } },
			{  	"$addFields": { "montagem.produto_codigo" : {"$arrayElemAt": [ "$produto.codigo"    , 0 ]} } },
			{  	"$addFields": { "montagem_status"         : {"$arrayElemAt": [ "$montagems.historico_status", 0 ]} } },
			{  	"$addFields": { "data_cadastro"           : {"$arrayElemAt": [ "$montagem_status.data_hora" , 0 ]} } },

			{	"$addFields": { "GUID_USUARIO"       : "$guid_montador" } },
			{  	"$addFields": { "ID_LOJA"            : {"$arrayElemAt": [ "$montagems.loja_venda.codigo", 0 ]} } },
			{  	"$addFields": { "produto_nome"       : {"$arrayElemAt": [ "$produto.nome"               , 0 ]} } },
			{  	"$addFields": { "produto_codigo"     : {"$arrayElemAt": [ "$produto.codigo"             , 0 ]} } },
			{  	"$addFields": { "produto_marca"      : {"$arrayElemAt": [ "$produto.marca"              , 0 ]} } },
			{  	"$addFields": { "produto_modelo"     : {"$arrayElemAt": [ "$produto.modelo"             , 0 ]} } },
			{  	"$addFields": { "produto_grupo"      : {"$arrayElemAt": [ "$produto.grupo"              , 0 ]} } },
			{  	"$addFields": { "produto_fornecedor" : {"$arrayElemAt": [ "$produto.fornecedor"         , 0 ]} } },

			{	"$project": { "montagems": 0, "guid" : 0, "montagem._id" : 0, "produto" : 0, #"montagem.origem" : 0, 
							  "montagem.endereco.complemento"         : 0, "montagem.endereco.distrito"   : 0,
							  "montagem.endereco.latitude"            : 0, "montagem.endereco.longitude"  : 0,
							  "montagem.endereco.ponto_referencia"    : 0, # "montagem.historico_status"    : 0,
							  "montagem.produtos.dicas"               : 0, "montagem.produtos.fornecedor" : 0,
							  "montagem.produtos.grupo"               : 0, "montagem.produtos.marca"      : 0,
							  "montagem.produtos.instrucoes_montagem" : 0, "montagem.produtos.modelo"     : 0,
							  "montagem_status"                       : 0} },
			{	"$match" : filter},
			{	"$skip"  : skip },
			{	"$limit" : limit }
		])

		tarefas = list(cur)
		tarefas_galeria = []

		if(get_count):
			return {"count" : len(tarefas)}

		for tarefa in tarefas:

			if(get_only_galeria):
				listEvidencia = []

				for historico in tarefa["montagem"]["historico_status"]:
					for evidendia in historico["evidencias"]:
						listEvidencia.append( evidendia )
				
				gale = self.db.resource.aggregate([
					{ "$match": {"_id" : {"$in": listEvidencia}} },
					{ "$project": {"_id": 0, "data": 1}}
				])
				
				galeria = {
					"guid_tarefa"   : str( tarefa["_id"] ),
					"guid_montagem" : tarefa["guid_montagem"],
					"galeria"       : list(gale)
				}

				tarefas_galeria.append( galeria )
			else:
				if("historico_status" in tarefa["montagem"]):
					mont   = tarefa["montagem"]
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

					dif   = dataSTFim - dataSTIni
					tarefa["tempo_total"] = (str(dif.days) + ' dias e ' if(dif.days > 0) else "") + str(math.trunc(dif.seconds / 60 / 60)) + ' horas'

					tarefa["montagem"].pop("historico_status")
				
				dataPrazoIni = None
				dataPrazoFim = None

				if(("data_hora" in tarefa) and ("inicio" in tarefa["data_hora"])):
					dataExec = tarefa["data_hora"]["inicio"]

					if ('Z' in dataExec):
						dataExecIni = datetime.strptime(dataExec[:-1], "%Y-%m-%dT%H:%M:%S.%f")
					else:
						dataExecIni = datetime.strptime(dataExec, "%Y-%m-%dT%H:%M:%S.%f")

					dataExecFim = None
					if(("fim" in tarefa["data_hora"])):
						dataExec = tarefa["data_hora"]["fim"]

						if ('Z' in dataExec):
							dataExecFim = datetime.strptime(dataExec[:-1], "%Y-%m-%dT%H:%M:%S.%f")
						else:
							dataExecFim = datetime.strptime(dataExec, "%Y-%m-%dT%H:%M:%S.%f")

						dataPrazoFim = dataExecFim
					
					if(not dataExecFim):
						dataExecFim = datetime.now()

					dif = dataExecFim - dataExecIni
					tarefa["tempo_execucao"] = (
						(str(dif.days) + ' dias e '                           if(dif.days > 0) else "") +
						(str(math.trunc(dif.seconds / 60 / 60)) + ' horas e ' if(math.trunc(dif.seconds / 60 / 60) > 0) else "") +
						(str(math.trunc(dif.seconds / 60) % 60) + ' minutos')
					)
				
				if(("data_hora" in tarefa) and ("fim" in tarefa["data_hora"])):
					tarefa["bi_id_status"] = 2
					tarefa["bi_status"]    = 'Finalizado'
				else:
					tarefa["bi_id_status"] = 1
					tarefa["bi_status"]    = 'Pendente'

				if(("data_hora_previsto" in tarefa) and ("fim" in tarefa["data_hora_previsto"])):
					dataExec = tarefa["data_hora_previsto"]["fim"]

					if ('Z' in dataExec):
						dataPrazoIni = datetime.strptime(dataExec[:-1], "%Y-%m-%dT%H:%M:%S.%f")
					else:
						dataPrazoIni = datetime.strptime(dataExec, "%Y-%m-%dT%H:%M:%S.%f")

					dataExec = tarefa["data_hora_previsto"]["fim"]

					if(not dataPrazoFim):
						dataPrazoFim = datetime.now()
					
					tarefa["bi_id_prazo"] = 1               if dataPrazoFim > dataPrazoIni else 2
					tarefa["bi_prazo"]    = 'Fora do Prazo' if dataPrazoFim > dataPrazoIni else 'No Prazo'

		if(get_only_galeria):
			return tarefas_galeria
		else:
			return tarefas

	def get_tarefa_by_guid(self, guid):
		cur = self.model.find({"_id": ObjectId(guid)})
		return self.add_info_in_tarefa(list(cur))

	def get_tarefa_by_montagem(self, guid_montagem):
		return self.model.find({"guid_montagem": guid_montagem})

	def get_tarefa_montador_by_guid_montador(self, guid_montador):
		cur = self.model.find({"guid_montador": guid_montador})
		return self.add_info_in_tarefa(list(cur), True)

	def add_info_in_tarefa(self, tarefas, remove_evidencia = False):
		from models.montagem_model import MontagemModel

		for tarefa in tarefas:
			guid_montagem = tarefa.get("guid_montagem")
			if (guid_montagem != None):
				montagem = MontagemModel().get_montagem_by_guid(guid_montagem, True, False, remove_evidencia)
				if len(montagem) > 0:
					tarefa["montagem"] = montagem[0] 

		return tarefas 
	
	def pop_tarefa(self, guid):

		tarefa = list(self.model.find({"_id": ObjectId(guid)}))

		if(tarefa[0]["status"] != "pendente"):
			raise Exception("Somente é permitido excluir uma tarefa Pendente.")

		guid_montagem = tarefa[0]["guid_montagem"]

		self.model.remove( {"_id": ObjectId(guid)} )

		list_tarefas = list(self.model.find({"guid_montagem": {"$eq": tarefa[0]["guid_montagem"]}}))

		if len(list_tarefas) == 0:
			self.db.montagem.remove( {"_id": ObjectId(guid_montagem)} )

		return []

