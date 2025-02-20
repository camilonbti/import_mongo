from bson.objectid import ObjectId
from models.model_base import ModelBase
from flask import request

import usuario_list_loja


import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Float, ForeignKey, Table, Sequence
from sqlalchemy.orm import sessionmaker, relationship


class UsuarioModel(ModelBase):

	def __init__(self):
		self.connect()
		self.model = self.db.usuario

	def __set_list_lojas(self, document):
		if( (document.get("loja") != None ) and len(document["loja"]) ):
			document["list_lojas"] = document["loja"]
		else:
			modelRegional = self.db.regional
			list_lojas = []

			for regional in document["regional"]:
				cur   = modelRegional.find({"_id": ObjectId(regional)})
				task  = list(cur)
				
				for lojas in task:
					for loja in lojas["lojas"]:
						list_lojas.append(loja)
			
			document["list_lojas"] = list_lojas

	def save(self, document):
		self.__set_list_lojas(document)

		return self.model.save(document)

	def update(self, guid, document):
		if (document.get("_id") != None):
			document.pop("_id")
		
		self.__set_list_lojas(document)
		
		return self.model.update({"_id": ObjectId(guid)}, document)

	def get_list_usuarios(self, filter):
		cur = self.model.find(filter)
		return list(cur)

	def get_usuario_by_guid(self, guid):
		cur = self.model.find({"_id": ObjectId(guid)})
		return list(cur)

	def get_list_montadores(self, filter):
		listEmp = usuario_list_loja.get_usuario_lista_loja(request.headers.get('guid-user'))

		filter["is_montador"] = True
		
		if(listEmp):
			filter["list_lojas"] = {"$in": listEmp}

		cur = self.model.find(filter).sort("nome")
		return list(cur)

