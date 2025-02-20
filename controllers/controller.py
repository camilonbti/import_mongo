from flask import Flask, request
from datetime import datetime

class Controller():

	def __getValueForBetween(self, type, value, addField):
		field  = value.split(';')[0]
		vStart = value.split(';')[1]
		vEnd   = value.split(';')[2]

		if( (type=='date') and (not vStart) ): 
			vStart = '2000-01-01T00:00:00:000Z'
		if( (type=='date') and (not vEnd) ):
			vEnd   = '2100-01-01T23:59:59:999Z'

		if(addField):
			return {field: {"$gte": vStart, "$lte": vEnd}}
		else:
			return {"$gte": vStart, "$lte": vEnd}

	def getFilter(self):
		filter = {}

		for key in request.args:
			value = request.args[key]

			if (value.startswith("LIKE_")):
				part_value = value.replace("LIKE_", "")
				value = {"$regex" : part_value, "$options" : "i"}

			elif (key.upper() == "BETWEEN"):
				key   = value.split(';')[0]
				value = self.__getValueForBetween(None, value, False)

			elif (key.upper() == "DBETWEEN"):
				key   = value.split(';')[0]
				value = self.__getValueForBetween('date', value, False)

			elif (key.upper() == "MATCH_BETWEEN"):
				key   = "$or"
				value = [ self.__getValueForBetween('date', value, True) ]

			filter[key] = value

		return filter