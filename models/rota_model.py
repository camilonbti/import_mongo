from bson.objectid import ObjectId
from models.model_base import ModelBase
from models.usuario_model import UsuarioModel

class RotaModel(ModelBase):

    def __init__(self):
        self.connect()
        self.model = self.db.rota

    def save(self, document):
        return self.model.save(document)

    def update(self, guid, document):
        if (document.get("_id") != None):
            document.pop("_id")

        return self.model.update({"_id": ObjectId(guid)}, document)
        
    def get_list_rotas(self, filter):
        cur = self.model.find(filter)
        return list(cur)

    def get_rota_by_guid(self, guid):
        cur = self.model.find({"_id": ObjectId(guid)})
        return list(cur)

    def pop_rota(self, guid):

        rota = list(self.model.find({"_id": ObjectId(guid)}))

        # if(rota[0]["status"] != "pendente"):
        #     raise Exception("Somente é permitido excluir uma rota Pendente.")

        self.model.remove( {"_id": ObjectId(guid)} )

        return []
