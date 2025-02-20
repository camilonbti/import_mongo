from bson.objectid import ObjectId
from models.model_base import ModelBase

class ResourceModel(ModelBase):

	def __init__(self):
		self.connect()
		self.model = self.db.resource

	def save(self, document):
		return self.model.save(document)

	def get_list_resources(self):
		cur = self.model.find({}, {"nome": True, "tipo": True})
		return list(cur)

	def get_resource_by_guid(self, guid):
		cur = self.model.find({"_id": ObjectId(guid)})
		return list(cur)
