from bson.objectid import ObjectId
from models.model_base import ModelBase

class ConfiguracaoModel(ModelBase):

	def __init__(self):
		self.connect()
		self.model = self.db.configuracao

	def save(self, document):
		return self.model.save(document)

	def update(self, guid, document):
		if (document.get("_id") != None):
			document.pop("_id")

		return self.model.update({"_id": ObjectId(guid)}, document)

	def get_list_configuracao(self, filter):
		cur = self.model.find(filter)
		return list(cur)

	def get_configuracao_by_name(self, name):
		cur = self.model.find({"name" : name})
		return list(cur)
