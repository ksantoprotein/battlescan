# -*- coding: utf-8 -*-

from requests import Session

import json
from .storage import nodes
from time import sleep
from pprint import pprint
from itertools import cycle


class Http():

	http = Session()


class RpcClient(Http):

	""" Simple Steem JSON-RPC API
		This class serves as an abstraction layer for easy use of the Steem API.

		rpc = RpcClient(nodes = nodes) or rpc = RpcClient()
		Args:
			nodes (list): A list of Steem HTTP RPC nodes to connect to.
		
		any call available to that port can be issued using the instance
		rpc.call('command', *parameters)
	"""
	
	headers = {'User-Agent': 'thallid', 'content-type': 'application/json'}

	
	def __init__(self, report = False, **kwargs):

		self.report = report
		self.num_retries = kwargs.get("num_retries", 5)		# Количество попыток подключения к ноде
		self.nodes = cycle(kwargs.get("nodes", nodes))		# Перебор нод
		self.url = next(self.nodes)
		
		
	def get_response(self, payload):
	
		data = json.dumps(payload, ensure_ascii = False).encode('utf8')
	
		while True:
		
			if self.report:
				print("Trying to connect to node %s" % self.url)
				
			n = 1
			while n < self.num_retries:
				try:
					response = self.http.post(self.url, data = data, headers = self.headers)
					return(response)
				except:
					sleeptime = (n - 1) * 2
					if self.report:
						print("Lost connection to node during rpcconnect(): %s (%d/%d) " % (self.url, n, self.num_retries))
						print("Retrying in %d seconds" % sleeptime)
					sleep(sleeptime)
					n += 1
			self.url = next(self.nodes)			# next node
				
		return False

					
	def call(self, name, *params):
	
		payload = {"method": 'condenser_api.' + name, "params": params, "id": 1, "jsonrpc": '2.0'}
		response = self.get_response(payload)

		if response.status_code != 200:
			if self.report:
				print('ERROR status_code', response.text)
			return False
		
		res = response.json()
		
		if 'error' in res:
			if self.report:
				pprint(res["error"]["message"])
			return False
			
		return(res["result"])


#----- main -----
if __name__ == '__main__':

	pass