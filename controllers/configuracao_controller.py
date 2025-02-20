from controllers.controller import Controller
from flask import Flask, request
from bson.json_util import dumps
from models.configuracao_model import ConfiguracaoModel
from environment import Config

class ConfiguracaoController(Controller):

	def save_configuracao(self):
		result = ConfiguracaoModel().save(request.json)
		return dumps(result)

	def get_list_configuracao(self):
		dataset = ConfiguracaoModel().get_list_configuracao(self.getFilter())
		return dumps(dataset) 

	def get_configuracao_by_name(self, guid):
		dataset = ConfiguracaoModel().get_configuracao_by_name(guid)
		return dumps(dataset)

	def update_configuracao(self, guid):
		conf = ConfiguracaoModel().get_configuracao_by_name(guid)

		if (len(conf) == 0) :
			return "Erro encontrado, configuração " + guid + " não encontrada", 400

		result = ConfiguracaoModel().update(str(conf[0]["_id"]), request.json)
		return dumps(result)

	# def get_configuracao_stomp(self):
	# 	return dumps(Config["stomp"])