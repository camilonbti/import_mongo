import logging
from pathlib import Path
import os
from process_json import process_json_to_sql, setup_logging

def main():
    """Função principal de execução com tratamento de erros adequado."""
    try:
        log_file, error_log_file = setup_logging()
        logging.info(f"Arquivos de log criados em:\nLog geral: {log_file}\nLog de erros: {error_log_file}")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        input_file = os.path.join(current_dir, "montagem.json")
        
        if not Path(input_file).exists():
            logging.error(f"Erro: Arquivo de entrada 'montagem.json' não encontrado em {current_dir}")
            return
        
        process_json_to_sql(input_file)
        
    except Exception as e:
        logging.error(f"Erro fatal: {str(e)}")
        raise

if __name__ == "__main__":
    main()