from bson.objectid import ObjectId
from models.model_base import ModelBase
from models.usuario_model import UsuarioModel

class RegionalModel(ModelBase):

	def __init__(self):
		self.connect()
		self.model = self.db.regional

	def save(self, document):
		return self.model.save(document)

	def update(self, guid, document):
		if (document.get("_id") != None):
			document.pop("_id")
		
		ret = self.model.update({"_id": ObjectId(guid)}, document)

		modelUser = self.db.usuario
		cur       = modelUser.find({"regional": {"$in": [guid]}})
		usuarios  = list(cur)

		for usuario in usuarios:
			if (usuario.get("list_lojas") != None):
				usuario.pop("list_lojas")

			UsuarioModel().update(str(usuario["_id"]), usuario)

		return ret

	def get_list_regionais(self, filter):
		cur = self.model.find(filter)
		return list(cur)

	def get_regional_by_guid(self, guid):
		cur = self.model.find({"_id": ObjectId(guid)})
		return list(cur)

	def get_regional_by_codigo(self, codigo):
		cur = self.model.find({"codigo": codigo})
		return list(cur)
