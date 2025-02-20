from __deploy__                          import deploy 
from controllers.health_controller       import HealthController
from controllers.loja_controller         import LojaController
from controllers.regional_controller     import RegionalController
from controllers.usuario_controller      import UsuarioController
from controllers.tarefa_controller       import TarefaController
from controllers.montagem_controller     import MontagemController
from controllers.resource_controller     import ResourceController
from controllers.configuracao_controller import ConfiguracaoController
from controllers.rota_controller         import RotaController

def set_routes(app):
	set_get_routes(app)
	set_post_routes(app)
	set_put_routes(app)
	set_delete_routes(app)

def set_get_routes(app):

	#HEALTH
	app.add_url_rule("/api/health/ping", view_func=HealthController().ping, methods=['GET'])
	app.add_url_rule("/datasnap/rest/health/status", view_func=HealthController().status, methods=['GET'])
	app.add_url_rule("/datasnap/rest/health/statusdb", view_func=HealthController().statusdb, methods=['GET'])

	#RESOURCE
	app.add_url_rule("/api/resource", view_func=ResourceController().get_list_resources, methods=['GET'])
	app.add_url_rule("/api/resource/<string:guid>", view_func=ResourceController().get_resource_by_guid, methods=['GET'])
	app.add_url_rule("/api/resource/<string:guid>/data", view_func=ResourceController().get_resource_data_by_guid, methods=['GET'])

	#LOJA
	app.add_url_rule("/api/loja", view_func=LojaController().get_list_lojas, methods=['GET'])
	app.add_url_rule("/api/loja/<string:guid>", view_func=LojaController().get_loja_by_guid, methods=['GET'])
	app.add_url_rule("/api/loja_user", view_func=LojaController().get_list_lojas_by_user, methods=['GET'])

	#REGIONAL
	# app.add_url_rule("/api/regional", view_func=RegionalController().get_list_regionais, methods=['GET'])
	# app.add_url_rule("/api/regional/<string:guid>", view_func=RegionalController().get_regional_by_guid, methods=['GET'])

	#USUARIO
	# app.add_url_rule("/api/usuario", view_func=UsuarioController().get_list_usuarios, methods=['GET'])
	# app.add_url_rule("/api/usuario/<string:guid>", view_func=UsuarioController().get_usuario_by_guid, methods=['GET'])

	#MONTADOR
	# app.add_url_rule("/api/montador", view_func=UsuarioController().get_list_montadores, methods=['GET'])
	app.add_url_rule("/api/montador/<string:guid>/tarefa", view_func=TarefaController().get_tarefa_montador_by_guid_montador, methods=['GET'])

	#TAREFA
	app.add_url_rule("/api/tarefa", view_func=TarefaController().get_list_tarefas, methods=['GET'])
	app.add_url_rule("/api/tarefa/<string:guid>", view_func=TarefaController().get_tarefa_by_guid, methods=['GET'])		

	#MONTAGEM
	app.add_url_rule("/api/montagem", view_func=MontagemController().get_list_montagens, methods=['GET'])
	app.add_url_rule("/api/montagem/<string:guid>", view_func=MontagemController().get_montagem_by_guid, methods=['GET'])
	app.add_url_rule("/api/montagem/<string:guid>/detalhe", view_func=MontagemController().get_montagem_by_guid_with_detail, methods=['GET'])
	app.add_url_rule("/api/montagem/groupby/<string:type>", view_func=MontagemController().get_list_montagens_group_by, methods=['GET'])
	app.add_url_rule("/api/montagem/groupby/detail/<string:type>", view_func=MontagemController().get_list_montagens_group_by_detail, methods=['GET'])

	#CONFIGURACAO
	app.add_url_rule("/api/configuracao", view_func=ConfiguracaoController().get_list_configuracao, methods=['GET'])
	app.add_url_rule("/api/configuracao/<string:guid>", view_func=ConfiguracaoController().get_configuracao_by_name, methods=['GET'])		
	
	# app.add_url_rule("/api/configuracao/notification_center", view_func=ConfiguracaoController().get_configuracao_stomp, methods=['GET'])

	#ROTA
	app.add_url_rule("/api/rota", view_func=RotaController().get_list_rotas, methods=['GET'])
	app.add_url_rule("/api/rota/<string:guid>", view_func=RotaController().get_rota_by_guid, methods=['GET'])

def set_post_routes(app):
	#DEPLOY
	app.add_url_rule("/api/deploy", view_func=deploy.deploy, methods=['POST'])
		
	#LOJA
	# app.add_url_rule("/api/loja", view_func=LojaController().save_loja, methods=['POST'])

	#REGIONAL
	# app.add_url_rule("/api/regional", view_func=RegionalController().save_regional, methods=['POST'])
	
	#USUARIO
	# app.add_url_rule("/api/usuario", view_func=UsuarioController().save_usuario, methods=['POST'])

	#TAREFA
	app.add_url_rule("/api/tarefa", view_func=TarefaController().save_tarefa, methods=['POST'])

	#MONTAGEM
	app.add_url_rule("/api/montagem", view_func=MontagemController().save_montagem, methods=['POST'])	
	app.add_url_rule("/api/montagem/<string:guid>/status", view_func=MontagemController().insert_status, methods=['POST'])
	app.add_url_rule("/api/montagem/status/<string:guid_status>/evidencia", view_func=MontagemController().add_evidencia, methods=['POST'])

	#INTEGRAÇÃO 
	app.add_url_rule("/api/integracao/loja", view_func=LojaController().save_loja_integracao, methods=['POST'])	
	app.add_url_rule("/api/integracao/regional", view_func=RegionalController().save_regional_integracao, methods=['POST'])

	#CONFIGURACAO
	app.add_url_rule("/api/configuracao", view_func=ConfiguracaoController().save_configuracao, methods=['POST'])

	#ROTA
	app.add_url_rule("/api/rota", view_func=RotaController().save_rota, methods=['POST'])

def set_put_routes(app):
	#LOJA
	# app.add_url_rule("/api/loja/<string:guid>", view_func=LojaController().update_loja, methods=['PUT'])

	#REGIONAL
	# app.add_url_rule("/api/regional/<string:guid>", view_func=RegionalController().update_regional, methods=['PUT'])

	#USUARIO
	# app.add_url_rule("/api/usuario/<string:guid>", view_func=UsuarioController().update_usuario, methods=['PUT'])

	#TAREFA
	app.add_url_rule("/api/tarefa/<string:guid>", view_func=TarefaController().update_tarefa, methods=['PUT'])

	#MONTAGEM
	app.add_url_rule("/api/montagem/<string:guid>", view_func=MontagemController().update_montagem, methods=['PUT'])
	
	#CONFIGURACAO
	app.add_url_rule("/api/configuracao/<string:guid>", view_func=ConfiguracaoController().update_configuracao, methods=['PUT'])

	#ROTA
	app.add_url_rule("/api/rota/<string:guid>", view_func=RotaController().update_rota, methods=['PUT'])

def set_delete_routes(app):
	#MONTAGEM
	app.add_url_rule("/api/montagem/<string:guid>/status", view_func=MontagemController().pop_status, methods=['DELETE'])

	#TAREFA
	app.add_url_rule("/api/tarefa/<string:guid>", view_func=TarefaController().pop_tarefa, methods=['DELETE'])

    #ROTA
	app.add_url_rule("/api/rota/<string:guid>", view_func=RotaController().pop_rota, methods=['DELETE'])