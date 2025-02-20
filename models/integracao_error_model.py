from bson.objectid import ObjectId
from models.model_base import ModelBase
from datetime import datetime, timedelta

class IntegracaoError(ModelBase):

	def __init__(self):
		try:
			self.ignoreErroDB = True

			self.connect()
			self.model = self.db.integracao_error
		except Exception:
			self.model = None

	def log(self, e, req):
		document = {
			"rota"     : req.url,
			"data_hora": datetime.now().isoformat(),
			"data"     : str(req.data, 'utf-8'),
			"error"    : str(e)
		} 

		protocolo = ''
		if(self.model != None):
			protocolo = str(self.model.save(document))

		return '{"error":"' + str(e) + '", "protocolo":"'+ str(protocolo) +'"}', 500

	def get_list_by_filter(self, filter):
		cur = self.model.find(filter)
		return list(cur)

	def get_list(self, filter):
		list = self.get_list_by_filter(filter)
		return list
