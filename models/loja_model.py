from bson.objectid import ObjectId
from models.model_base import ModelBase
from flask import request

import usuario_list_loja

class LojaModel(ModelBase):

	def __init__(self):
		self.connect()
		self.model = self.db.loja

	def save(self, document):
		return self.model.save(document)

	def update(self, guid, document):
		if (document.get("_id") != None):
			document.pop("_id")

		return self.model.update({"_id": ObjectId(guid)}, document)		

	def get_list_lojas(self, filter):
		cur = self.model.find(filter)
		return list(cur)

	def get_list_lojas_by_user(self, filter):
		listEmp = usuario_list_loja.get_usuario_lista_loja(request.headers.get('guid-user'), True)
		
		if(listEmp):
			filter["_id"] = {"$in": listEmp}

		cur = self.model.find(filter)
		return list(cur)		

	def get_loja_by_guid(self, guid):
		cur = self.model.find({"_id": ObjectId(guid)})
		return list(cur)

	def get_loja_by_codigo(self, codigo):
		cur = self.model.find({"codigo" : codigo})
		return list(cur)
