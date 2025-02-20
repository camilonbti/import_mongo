from pymongo import MongoClient
import logging

class MongoConnection:
    # Constantes de conexão
    MONGO_HOST = '15.229.68.10'
    MONGO_PORT = 27017
    MONGO_DATABASE = 'controllFixer_Center-Moveis'
    
    def __init__(self):
        self.client = None
        self.db = None
    
    def connect(self):
        try:
            # Estabelece conexão com o MongoDB
            self.client = MongoClient(
                host=self.MONGO_HOST,
                port=self.MONGO_PORT
            )
            
            # Seleciona o banco de dados
            self.db = self.client[self.MONGO_DATABASE]
            
            # Verifica se a conexão está funcionando
            self.client.server_info()
            logging.info("Conexão com MongoDB estabelecida com sucesso")
            
            return self.db
            
        except Exception as e:
            logging.error(f"Erro ao conectar com MongoDB: {str(e)}")
            raise
    
    def close(self):
        if self.client:
            try:
                self.client.close()
                logging.info("Conexão com MongoDB fechada com sucesso")
            except Exception as e:
                logging.error(f"Erro ao fechar conexão com MongoDB: {str(e)}")