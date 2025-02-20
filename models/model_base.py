from flask import Flask, request
from database import Connection

class ModelBase():
	db           = None
	ignoreErroDB = False
	erro         = ''
	
	def connect(self):
		conn = Connection()
		self.erro = conn.createConnection(self.ignoreErroDB)
		self.db   = conn.db