# -*- coding: utf-8 -*-

from pprint import pprint
import json

from .rpc_client import RpcClient
from .storage import time_format

from datetime import datetime, timedelta
from time import sleep, time
from random import randint



class Api():

	def __init__(self, **kwargs):

		# Пользуемся своими нодами или новыми
		nodes = kwargs.pop("nodes", None)
		report = kwargs.pop("report", False)
		if nodes:
			self.rpc = RpcClient(nodes = nodes, report = report)
		else:
			self.rpc = RpcClient(report = report)

		
		##### ##### ##### ##### #####
		
	def get_block(self, n):
		return(self.rpc.call('get_block', int(n)))
		
	def get_ops_in_block(self, n, ops = False):
		return(self.rpc.call('get_ops_in_block', int(n), ops))
		
	def get_dynamic_global_properties(self):			### доделать таймер

		# Returns the global properties
		for n in range(3):
			prop = self.rpc.call('get_dynamic_global_properties')
			if not isinstance(prop, bool):
				prop["now"] = datetime.strptime(prop["time"], time_format)
				for p in ["head_block_number", "last_irreversible_block_num"]:
					value = prop.pop(p)
					prop[p] = int(value)
				return(prop)
			sleep(3)
			
		return(False)
		
	def get_irreversible_block(self):
		info = self.get_dynamic_global_properties()
		if info:
			return(info["last_irreversible_block_num"])
		return False

	def get_head_block(self):
		info = self.get_dynamic_global_properties()
		if info:
			return(info["head_block_number"])
		return False
		
		

		##### ##### ##### ##### #####
		
		
