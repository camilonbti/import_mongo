import json
import pandas as pd
from pathlib import Path
import ijson
import os
import logging
from datetime import datetime
import re

def setup_logging():
    """Configura logging com arquivos separados para logs gerais e de erro."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Arquivo de log geral
    log_file = os.path.join(current_dir, f'process_log_{timestamp}.txt')
    # Arquivo de log específico para erros de dados
    error_log_file = os.path.join(current_dir, f'error_log_{timestamp}.txt')
    
    # Configura logger geral
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Configura logger de erro
    error_logger = logging.getLogger('error_logger')
    error_logger.setLevel(logging.WARNING)
    error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    error_logger.addHandler(error_handler)
    
    return log_file, error_log_file

def sanitize_string(value):
    """Sanitiza valores string para inserção SQL."""
    if value is None:
        return ''
    sanitized = str(value).replace("'", "''")
    sanitized = ''.join(char for char in sanitized if char.isprintable())
    return sanitized[:120]  # Limita o tamanho da string para 120 caracteres

def extract_nested_value(data, field_name):
    """Extrai valores de estruturas aninhadas, tratando vários formatos."""
    if not data:
        return None
        
    if isinstance(data, dict):
        if 'origem' in data and isinstance(data['origem'], dict):
            if field_name in data['origem']:
                return data['origem'][field_name]
        
        if field_name in data:
            return data[field_name]
            
        if 'codigo' in data:
            return data['codigo']
            
    return data

def safe_int_conversion(value, field_name='unknown', record_info=''):
    """Converte valores para inteiro com log detalhado de erros."""
    if value is None:
        return 0
        
    actual_value = extract_nested_value(value, field_name)
    
    if isinstance(actual_value, dict):
        logging.getLogger('error_logger').warning(
            f"Estrutura aninhada complexa para {field_name}: {actual_value}\n"
            f"Informações do registro: {record_info}"
        )
        return 0
        
    try:
        if isinstance(actual_value, str):
            cleaned = re.sub(r'[^\d.-]', '', actual_value)
            if cleaned:
                return int(float(cleaned))
            return 0
        elif isinstance(actual_value, (int, float)):
            return int(actual_value)
        else:
            logging.getLogger('error_logger').warning(
                f"Tipo inesperado para {field_name}: {type(actual_value)}\n"
                f"Valor: {actual_value}\nInformações do registro: {record_info}"
            )
            return 0
    except (ValueError, TypeError) as e:
        logging.getLogger('error_logger').warning(
            f"Erro de conversão para {field_name}: '{actual_value}'\n"
            f"Erro: {str(e)}\nInformações do registro: {record_info}"
        )
        return 0

def extract_product_info(product, record_info):
    """Extrai e valida informações do produto com log detalhado."""
    if not isinstance(product, dict):
        logging.getLogger('error_logger').warning(
            f"Estrutura de produto inválida: {product}\nInformações do registro: {record_info}"
        )
        return None
    
    product_data = {
        'id_produto': 0,
        'produto': '',
        'codigo_barras': '',
        'quantidade': 1,
        'marca': '',
        'grupo': '',
        'fornecedor': ''
    }
    
    if 'id_produto' in product:
        product_data['id_produto'] = safe_int_conversion(product.get('id_produto'), 'id_produto', record_info)
        product_data['produto'] = sanitize_string(product.get('produto', ''))
        product_data['codigo_barras'] = sanitize_string(product.get('codigo_barras', ''))
        product_data['quantidade'] = safe_int_conversion(product.get('quantidade'), 'quantidade', record_info)
        product_data['marca'] = sanitize_string(product.get('marca', ''))
        product_data['grupo'] = sanitize_string(product.get('grupo', ''))
        product_data['fornecedor'] = sanitize_string(product.get('fornecedor', ''))
    
    elif 'guid' in product and 'nome' in product:
        product_data['id_produto'] = safe_int_conversion(product.get('codigo'), 'codigo', record_info)
        product_data['produto'] = sanitize_string(product.get('nome', ''))
        product_data['codigo_barras'] = sanitize_string(product.get('codigo_barras', ''))
        product_data['quantidade'] = safe_int_conversion(product.get('quantidade'), 'quantidade', record_info)
        product_data['marca'] = sanitize_string(product.get('marca', ''))
        product_data['grupo'] = sanitize_string(product.get('grupo', ''))
        product_data['fornecedor'] = sanitize_string(product.get('fornecedor', ''))
    
    if not product_data['id_produto'] or not product_data['produto']:
        logging.getLogger('error_logger').warning(
            f"Dados críticos do produto ausentes:\n"
            f"Original: {product}\n"
            f"Extraído: {product_data}\n"
            f"Informações do registro: {record_info}"
        )
    
    return product_data

def generate_sql_insert(item, product):
    """Gera uma instrução SQL INSERT com formatação e sanitização adequadas."""
    record_info = f"Estrutura original: {str(item)[:200]}..."
    
    cliente_data = item.get("cliente", {})
    if isinstance(cliente_data, dict):
        cliente_nome = sanitize_string(cliente_data.get("nome", ""))
        cpf_cliente = sanitize_string(cliente_data.get("cpf", ""))
    else:
        logging.getLogger('error_logger').warning(f"Estrutura de cliente inesperada: {cliente_data}")
        cliente_nome = ""
        cpf_cliente = ""
    
    values = {
        'id_origem': safe_int_conversion(
            extract_nested_value(item, "id_origem"),
            "id_origem",
            record_info
        ),
        'id_pedido': safe_int_conversion(
            extract_nested_value(item, "id_pedido"),
            "id_pedido",
            record_info
        ),
        'cpf': cpf_cliente,
        'cliente': cliente_nome,
        'id_produto': safe_int_conversion(product.get("id_produto"), "id_produto", record_info),
        'produto': sanitize_string(product.get("produto", "")),
        'codigo_barras': sanitize_string(product.get("codigo_barras", "")),
        'quantidade': safe_int_conversion(product.get("quantidade"), "quantidade", record_info),
        'marca': sanitize_string(product.get("marca", "")),
        'grupo': sanitize_string(product.get("grupo", "")),
        'fornecedor': sanitize_string(product.get("fornecedor", "")),
        'loja_venda': safe_int_conversion(
            extract_nested_value(item.get("loja_venda", {}), "codigo"),
            "loja_venda",
            record_info
        ),
        'loja_saida': safe_int_conversion(item.get("loja_saida"), "loja_saida", record_info)
    }
    
    if values['id_origem'] == 0 or values['id_pedido'] == 0:
        logging.getLogger('error_logger').warning(
            f"ID zero detectado:\n"
            f"id_origem: {values['id_origem']}\n"
            f"id_pedido: {values['id_pedido']}\n"
            f"Dados originais: {record_info}"
        )
    
    sql = (
        "INSERT INTO MONTAGENS_MONGO ("
        "ID_ORIGEM, ID_PEDIDO, CPF, CLIENTE, ID_PRODUTO, PRODUTO, "
        "CODIGO_BARRAS, QUANTIDADE, MARCA, GRUPO, FORNECEDOR, LOJA_VENDA, LOJA_SAIDA"
        ") VALUES ("
        f"{values['id_origem']}, "
        f"{values['id_pedido']}, "
        f"'{values['cpf']}', "
        f"'{values['cliente']}', "
        f"{values['id_produto']}, "
        f"'{values['produto']}', "
        f"'{values['codigo_barras']}', "
        f"{values['quantidade']}, "
        f"'{values['marca']}', "
        f"'{values['grupo']}', "
        f"'{values['fornecedor']}', "
        f"{values['loja_venda']}, "
        f"{values['loja_saida']}"
        ");"
    )
    return sql

def create_new_sql_file(base_path, file_number):
    """Cria um novo arquivo SQL com controle de transação."""
    file_path = f"{base_path}_{file_number}.sql"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("SET TRANSACTION;\n\n")
    return file_path

def process_json_to_sql(json_file_path):
    """Processa arquivo JSON e gera múltiplos arquivos SQL com tratamento de erro adequado."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_sql_path = os.path.join(current_dir, "script")
    
    # Contadores para análise
    total_records = 0
    processed_count = 0
    error_count = 0
    empty_products_count = 0
    records_with_products = 0
    total_products = 0
    
    # Controle de arquivos SQL
    current_file_number = 1
    records_in_current_file = 0
    current_sql_file = create_new_sql_file(base_sql_path, current_file_number)
    
    try:
        logging.info(f"Iniciando processamento do JSON de: {json_file_path}")
        
        with open(json_file_path, 'rb') as json_file:
            parser = ijson.items(json_file, 'item')
            
            for item in parser:
                total_records += 1
                try:
                    if isinstance(item.get('id_origem'), dict) or isinstance(item.get('id_pedido'), dict):
                        logging.getLogger('error_logger').info(f"Estrutura de ID aninhada encontrada: {str(item)[:500]}...")
                    
                    produtos = item.get("produtos", [])
                    if not produtos:
                        empty_products_count += 1
                        logging.getLogger('error_logger').warning(f"Nenhum produto encontrado no registro: {str(item)[:200]}...")
                        continue
                    
                    records_with_products += 1
                    total_products += len(produtos)
                        
                    for product in produtos:
                        # Verifica se precisamos criar um novo arquivo
                        if records_in_current_file >= 40000:
                            with open(current_sql_file, "a", encoding="utf-8") as f:
                                f.write("\nCOMMIT WORK;\n")
                            current_file_number += 1
                            current_sql_file = create_new_sql_file(base_sql_path, current_file_number)
                            records_in_current_file = 0
                        
                        product_info = extract_product_info(product, str(item)[:200])
                        if not product_info:
                            error_count += 1
                            continue
                            
                        sql_insert = generate_sql_insert(item, product_info)
                        with open(current_sql_file, "a", encoding="utf-8") as f:
                            f.write(sql_insert + "\n")
                        
                        processed_count += 1
                        records_in_current_file += 1
                        
                        if processed_count % 1000 == 0:
                            logging.info(f"Processados {processed_count} registros...")
                            
                except Exception as e:
                    error_count += 1
                    logging.getLogger('error_logger').error(
                        f"Erro ao processar registro:\n"
                        f"Erro: {str(e)}\n"
                        f"Dados do registro: {str(item)[:500]}..."
                    )
                    continue
        
        # Fecha o último arquivo SQL
        with open(current_sql_file, "a", encoding="utf-8") as f:
            f.write("\nCOMMIT WORK;\n")
        
        # Log de estatísticas finais
        logging.info("\n=== Estatísticas de Processamento ===")
        logging.info(f"Total de registros lidos: {total_records}")
        logging.info(f"Registros com produtos: {records_with_products}")
        logging.info(f"Registros sem produtos: {empty_products_count}")
        logging.info(f"Total de produtos encontrados: {total_products}")
        logging.info(f"Produtos processados com sucesso: {processed_count}")
        logging.info(f"Produtos com falha: {error_count}")
        logging.info(f"Arquivos SQL gerados: {current_file_number}")
        logging.info(f"Caminho base dos arquivos SQL: {base_sql_path}")
        logging.info("=========================\n")
        
    except Exception as e:
        logging.error(f"Erro fatal ao processar arquivo JSON: {str(e)}")
        raise