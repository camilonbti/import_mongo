from flask import Blueprint, render_template, jsonify, request
from .database.mongo_connection import MongoConnection
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        logger.info("Iniciando busca de montagens...")
        mongo = MongoConnection()
        db = mongo.connect()
        
        data_inicio = datetime.strptime("2025-02-01T00:00:00.000", "%Y-%m-%dT%H:%M:%S.%f")
        data_fim = data_inicio + timedelta(days=3)
        
        logger.info(f"Buscando montagens entre {data_inicio} e {data_fim}")
        
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
                    "data_ultima_alteracao": { "$arrayElemAt": ["$historico_status.data_hora", -1] }
                }
            }
        ]
        
        logger.info("Executando pipeline do MongoDB...")
        logger.debug(f"Pipeline: {pipeline}")
        
        montagens = list(db.montagem.aggregate(pipeline))
        logger.info(f"Total de montagens encontradas: {len(montagens)}")
        
        for montagem in montagens:
            logger.debug(f"""
Detalhes da Montagem:
ID: {montagem.get('montagem_id')}
Status: {montagem.get('status_montagem')}
Montador ID: {montagem.get('montador_id')}
Montador Nome: {montagem.get('montador_nome')}
Produtos: {montagem.get('produtos', [])}
""")
        
        if mongo:
            mongo.close()
        
        return render_template('montagens.html', montagens=montagens, 
                             data_inicio=data_inicio.strftime("%d/%m/%Y"),
                             data_fim=data_fim.strftime("%d/%m/%Y"))
        
    except Exception as e:
        logger.error(f"Erro ao buscar montagens: {str(e)}", exc_info=True)
        if mongo:
            mongo.close()
        return jsonify({"error": str(e)}), 500