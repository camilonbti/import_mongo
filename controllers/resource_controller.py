from flask import Flask, request
from bson.json_util import dumps
from models.resource_model import ResourceModel
from lib.json_zip import json_zip

class ResourceController():

	def save_resource(self):
		result = ResourceModel().save(request.json)
		return dumps(result)

	def get_list_resources(self):
		dataset = ResourceModel().get_list_resources()
		# return dumps(dataset)
		return dumps( json_zip(dataset) )

	def get_resource_by_guid(self, guid):
		dataset = ResourceModel().get_resource_by_guid(guid)
		return dumps(dataset)

	def get_resource_data_by_guid(self, guid):
		dataset = ResourceModel().get_resource_by_guid(guid)
		if (len(dataset) > 0):
			return dataset[0]["data"]
		
		return "undefined"