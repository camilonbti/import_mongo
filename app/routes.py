from flask import Blueprint, render_template, jsonify, request
from .database.mongo_connection import MongoConnection
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import logging
import os

# Configuração do logger
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configura o logger para montagens
montagens_logger = logging.getLogger('montagens')
montagens_logger.setLevel(logging.DEBUG)

# Handler para arquivo
log_file = os.path.join(log_dir, 'montagens.log')
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Formato do log
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Adiciona o handler ao logger
montagens_logger.addHandler(file_handler)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/test-connection', methods=['POST'])
def test_connection():
    try:
        mongo = MongoConnection()
        db = mongo.connect()
        mongo.close()
        return jsonify({"success": True, "message": "Conexão estabelecida com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro na conexão: {str(e)}"})

@main_bp.route('/montagens', methods=['GET'])
def get_montagens():
    mongo = None
    try:
        montagens_logger.info("Iniciando busca de montagens...")
        mongo = MongoConnection()
        db = mongo.connect()
        
        data_inicio = datetime.strptime("2025-02-01T00:00:00.000", "%Y-%m-%dT%H:%M:%S.%f")
        data_fim = datetime.strptime("2025-02-01T00:00:00.000", "%Y-%m-%dT%H:%M:%S.%f")
        
        montagens_logger.info(f"Buscando montagens entre {data_inicio} e {data_fim}")
        
        pipeline = [
            {
                "$match": {
                    "historico_status.data_hora": {
                        "$gte": data_inicio.isoformat(),
                        "$lte": data_fim.isoformat()
                    }
                }
            },
            {
                "$addFields": {
                    "guid": { "$toString": "$_id" }
                }
            },
            {
                "$lookup": {
                    "from": "tarefa",
                    "localField": "guid",
                    "foreignField": "guid_montagem",
                    "as": "tarefa_info"
                }
            },
            {
                "$unwind": {
                    "path": "$tarefa_info",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$lookup": {
                    "from": "usuario",
                    "let": { "montador_id": "$tarefa_info.guid_montador" },
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": { "$eq": [{ "$toString": "$_id" }, "$$montador_id"] }
                            }
                        }
                    ],
                    "as": "montador_info"
                }
            },
            {
                "$unwind": {
                    "path": "$montador_info",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$project": {
                    "montagem_id": { "$toString": "$_id" },
                    "origem_id": "$origem.id_origem",
                    "pedido_id": "$origem.id_pedido",
                    "cliente_nome": "$cliente.nome",
                    "cliente_cpf": "$cliente.cpf",
                    "produtos": {
                        "$map": {
                            "input": "$produtos",
                            "as": "produto",
                            "in": {
                                "produto_nome": "$$produto.nome",
                                "produto_codigo": "$$produto.codigo",
                                "produto_barras": "$$produto.codigo_barras",
                                "produto_qtd": "$$produto.quantidade",
                                "produto_preco": "$$produto.preco",
                                "produto_modelo": "$$produto.modelo",
                                "produto_marca": "$$produto.marca",
                                "produto_grupo": "$$produto.grupo",
                                "produto_fornecedor": "$$produto.fornecedor"
                            }
                        }
                    },
                    "loja_saida_codigo": "$loja_saida.codigo",
                    "loja_saida_nome": "$loja_saida.nome_fantasia",
                    "loja_venda_codigo": "$loja_venda.codigo",
                    "loja_venda_nome": "$loja_venda.nome_fantasia",
                    "status_montagem": "$status",
                    "montador_id": "$tarefa_info.guid_montador",
                    "montador_nome": { "$ifNull": ["$montador_info.nome", "Não atribuído"] },
                    "montador_email": { "$ifNull": ["$montador_info.email", "Não informado"] },
                    "montador_telefone": { "$ifNull": ["$montador_info.telefone", "Não informado"] },
                    "data_cadastro": { "$arrayElemAt": ["$historico_status.data_hora", 0] },
                    "data_ultima_alteracao": { "$arrayElemAt": ["$historico_status.data_hora", -1] },
                    # Novos campos da tarefa
                    "tarefa_status": "$tarefa_info.status",
                    "tarefa_tipo_servico": "$tarefa_info.tipo_servico",
                    "tarefa_data_hora": "$tarefa_info.data_hora",
                    "tarefa_data_hora_previsto": "$tarefa_info.data_hora_previsto",
                    "tarefa_time_execution": "$tarefa_info.time_execution",
                    "tarefa_last_execution": "$tarefa_info.last_execution",
                    # Campos calculados do tempo
                    "tempo_total": {
                        "$let": {
                            "vars": {
                                "primeiro_status": { "$arrayElemAt": ["$historico_status", 0] },
                                "ultimo_status": { "$arrayElemAt": ["$historico_status", -1] }
                            },
                            "in": {
                                "$concat": [
                                    { "$toString": {
                                        "$divide": [
                                            { "$subtract": [
                                                { "$dateFromString": { "dateString": "$$ultimo_status.data_hora" } },
                                                { "$dateFromString": { "dateString": "$$primeiro_status.data_hora" } }
                                            ]},
                                            3600000  # Converter para horas
                                        ]
                                    }},
                                    " horas"
                                ]
                            }
                        }
                    },
                    # Histórico de status completo
                    "historico_status": {
                        "$map": {
                            "input": "$historico_status",
                            "as": "status",
                            "in": {
                                "guid": "$$status.guid",
                                "status": "$$status.status",
                                "data_hora": "$$status.data_hora",
                                "observacao": "$$status.observacao",
                                "tpMotivo": "$$status.tpMotivo",
                                "evidencias": "$$status.evidencias"
                            }
                        }
                    }
                }
            }
        ]
        
        montagens_logger.info("Executando pipeline do MongoDB...")
        montagens_logger.debug(f"Pipeline: {pipeline}")
        
        montagens = list(db.montagem.aggregate(pipeline))
        montagens_logger.info(f"Total de montagens encontradas: {len(montagens)}")
        
        for montagem in montagens:
            montagens_logger.debug(f"""
Detalhes da Montagem:
ID: {montagem.get('montagem_id')}
Status: {montagem.get('status_montagem')}
Montador ID: {montagem.get('montador_id')}
Montador Nome: {montagem.get('montador_nome')}
Produtos: {montagem.get('produtos', [])}

Informações da Tarefa:
Status: {montagem.get('tarefa_status')}
Tipo de Serviço: {montagem.get('tarefa_tipo_servico')}
Data/Hora Prevista: {montagem.get('tarefa_data_hora_previsto')}
Última Execução: {montagem.get('tarefa_last_execution')}
Tempo de Execução: {montagem.get('tarefa_time_execution')}

Histórico de Status:
{montagem.get('historico_status', [])}

Tempo Total: {montagem.get('tempo_total')}
""")
        
        if mongo:
            mongo.close()
        
        return render_template('montagens.html', montagens=montagens, 
                             data_inicio=data_inicio.strftime("%d/%m/%Y"),
                             data_fim=data_fim.strftime("%d/%m/%Y"))
        
    except Exception as e:
        montagens_logger.error(f"Erro ao buscar montagens: {str(e)}", exc_info=True)
        if mongo:
            mongo.close()
        return jsonify({"error": str(e)}), 500