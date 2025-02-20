from controllers.controller import Controller
from flask import Flask, request
from bson.json_util import dumps
from models.usuario_model import UsuarioModel

class UsuarioController(Controller):

	def save_usuario(self):
		result = UsuarioModel().save(request.json)
		return dumps(result)

	def update_usuario(self, guid):
		result = UsuarioModel().update(guid, request.json)
		return dumps(result)

	def get_list_usuarios(self):
		dataset = UsuarioModel().get_list_usuarios(self.getFilter())
		return dumps(dataset)

	def get_usuario_by_guid(self, guid):
		dataset = UsuarioModel().get_usuario_by_guid(guid)
		return dumps(dataset)

	def get_list_montadores(self):
		dataset = UsuarioModel().get_list_montadores(self.getFilter())
		return dumps(dataset)