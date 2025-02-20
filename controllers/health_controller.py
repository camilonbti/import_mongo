import os
# import psutil
from bson.json_util import dumps

class HealthController():

	def ping(self):
		return '{"status" : "ok.."}'

	def status(self):
		status = {
			"memory"         : '{:.2f}'.format(self.memory()),
			"nrTransactions" : 'na',
			"nrConnections"  : 'na',
			"dtUltRequest"   : 'na',
			"nrRequests"     : 'na'
		}

		return dumps(status)

	def statusdb(self):
		return 'ok'

	def memory(self):
		process = psutil.Process(os.getpid())
		return process.memory_percent()

