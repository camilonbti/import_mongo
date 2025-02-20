from database import Connection
from bson.objectid import ObjectId
from datetime import datetime
from flask import request

def get_data_json(data):
	if (data.get("_id") != None):
		data["_id"] = ObjectId(str(data["_id"]))

	return data

class AuditCenter():

	@staticmethod
	def post(collection, action, data, new_data):
		audit = {  
			"action"    : action,
			"mom_op"    : datetime.now().isoformat(),
			"usu_op"    : request.headers.get('guid-user'),
			"collection": collection,
			"data"      : get_data_json(data),
			"new_data"  : get_data_json(new_data)
		}

		conn = Connection()
		conn.createConnection()
		db = conn.db

		db.audit_center.save(audit)