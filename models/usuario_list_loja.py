from database import Connection
from bson.objectid import ObjectId
from flask import request

def get_usuario_lista_loja(guid_usuario, add_object_id = False):
	conn = Connection()
	conn.createConnection()
	db = conn.db

	model = db.usuario
	cur   = model.find({"_id": ObjectId(guid_usuario)})	
	task  = list(cur)
	
	if(task):
		if(not add_object_id):
			return task[0]["list_lojas"]
		else:
			lojas = []

			for loja in task[0]["list_lojas"]:
				lojas.append(ObjectId(loja))
			
			return lojas
	else:
		return []