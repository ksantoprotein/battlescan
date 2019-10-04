# -*- coding: utf-8 -*-

from pprint import pprint
from time import sleep, time
import json

from requests import Session

from threading import Thread
from tkinter import *

from itertools import combinations

time_step = 2
n_step = 10


class Http():

	http = Session()
	
	
class Root():

	root = None
	def run(self):
		self.root = Tk()
	
	
class EsteemApi(Http):

	url = 'https://api.steemjs.com/'
	cmd = {
			"get_dynamic_global_properties": 'get_dynamic_global_properties',
			"get_block": 'get_block?blockNum=',
			}
			
			
	def get_dynamic_global_properties(self):
		cmd = ''.join([self.url, self.cmd["get_dynamic_global_properties"]])
		return(self.get_response(cmd))

		
	def get_block(self, block_num):
		cmd = ''.join([self.url, self.cmd["get_block"], str(block_num)])
		return(self.get_response(cmd))
		

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

		
	def get_response(self, cmd):
	
		n = 0
		while n < n_step:
			response = self.http.get(cmd)
			
			try:
				if str(response) == '<Response [200]>':
					return(response.json())
			except:
				print('??? ERROR in EsteemApi')
				
			print('error EsteemApi', n)
			sleep(time_step)
			n += 1
		return False
			


class SteemMonstersApi(Http, Root):

	url = 'https://steemmonsters.com/'
	#url = 'https://api.steemmonsters.io/'		# нет левела карт в коллекции юнита
	
	path_img = 'smbase/png/small/'
	ratings = {"chemp": [2800, 10000], "gold": [1900, 2799], "silver": [1000, 1899], "bronze": [100, 999]}
	colors = ['Red', 'Blue', 'Green', 'White', 'Black', 'Gold']
	
	# Если нужно графическая оболочка, то необходимо выполнить load_cards
	
	
	battles = {}
	
	
	def __init__(self):
	
	
		print('load steemmonsters')
		data = self.settings()
		
		self.version = 	data["version"]
		self.rulesets = {rule["name"]: rule["description"] for rule in data["battles"]["rulesets"] if rule["active"]}
		### Aim True, Armored Up, Back to Basics, Broken Arrows, Earthquake, Fog of War, Healed Out, Keep Your Distance, Little League
		### Lost Legendaries, Melee Mayhem, Reverse Speed, Rise of the Commons, Silenced Summoners, Standard, Super Sneak, Taking Sides
		### Target Practice, Unprotected, Up Close & Personal, Weak Magic

		
		print('version', self.version)
		#pprint(self.rulesets)
		
		self.cards = self.get_card_details()
		self.card_names = {card["id"]: card["name"] for card in self.cards}
	
		
		
	def scan_battle(self, trx_id):
	
		#print('connect', trx_id)
	
		while True:
		
			res_battle = self.get_battle_status(trx_id)
			
			if res_battle:
				try:
					status = int(res_battle["status"])
				except:
					pprint(res_battle)
					sleep(3)
					#input('stop')
					
				if status > 0:		# not opponent
				
					#print('change status', trx_id)
					try:
						timestamp = res_battle["match_date"].split('T')[1].split('.')[0]
					except:
						timestamp = res_battle["match_date"].split('T')[1]
					opponent_player = res_battle["opponent_player"]
					player = res_battle["player"]
					inactive = res_battle["inactive"]
					
					if status == 1:		#
						cmd = ' '.join([timestamp, player, 'VS', opponent_player, res_battle["ruleset"], res_battle["inactive"]])
					elif status == 2:		#
						cmd = ' '.join([timestamp, player, 'VS', opponent_player, 'END'])
					elif status in [3, 4]:		# cancel
						cmd = ' '.join([timestamp, player, 'CANCEL'])
					else:
						
						pprint(res_battle)
						#input()
						
					self.battles.pop(trx_id)
					
					ratings = [value[1]  for key, value in self.battles.items()]
					ratings.sort(reverse = True)
					print(cmd, 'total units = ', len(sm.battles), ratings)
					
					break
					
				else:
					sleep(1)
					
		return
			
			
	def sm_run(self):
	
	
		while True:
			self.update_find_match()
			print('sleep 0 sec\n')
			sleep(0)
			
		
	def update_find_match(self):

		start_block = False
		self.battle = {"bronze": [], "silver": [], "gold": [], "chemp": []}

		raw = self.get_from_block(1000000000)
		if raw:
			for line in raw:
				start_block = line["block_num"] if not start_block else start_block
				if line["block_num"] + 3 * 20 < start_block:
					print('break block')
					break
				if self.check_find_match(line):
					#pprint(line)
					#input()
					pass
		#pprint(self.battle)
		self.battle["chemp"].sort(reverse = True)
		print(self.battle["chemp"])
					
		#self.battle["gold"].sort(reverse = True)
		#print(self.battle["gold"])
		return
		
		
	def check_find_match(self, line):
	
		if line["type"] == 'find_match' and line["success"]:
			line["data"] = json.loads(line["data"])		# convert str => dict
			if line["data"]["match_type"] == 'Ranked':
				id, player = line["id"], line["player"]
				res_battle = self.get_battle_status(id)
				if res_battle:
					if res_battle["status"] == 0:		# not opponent
						#res_player = self.get_player_details(player)
						res_player = self.get_player_login(player)
						#quests = self.get_player_quests(player)
						quests = True

						if res_player and quests:
						
							rank = res_player["max_rank"]
							sub = res_player["settings"].get("submit_hashed_team", False)
							hide = 'hide' if sub else None
							
							#quest = quests["name"] if int(quests["completed_items"]) < 5 else None
							quest = ''
								
							rating = res_player["rating"]
							if rating >= 2800:
								cmd = "chemp"
							elif rating >= 1900:
								cmd = "gold"
							elif rating >= 1000:
								cmd = "silver"
							elif rating >= 100:
								cmd = "bronze"
							else:
								cmd = False
							
							if cmd:
								self.battle[cmd].append([rating, player, rank, hide, quest])
				
				return True
		
		return False
		
		
		
		
	### TOTAL ###
	
	def settings(self):
		cmd = ''.join([self.url, 'settings'])
		return(self.get_response(cmd))
		
	def get_from_block(self, block_num):
		cmd = ''.join([self.url, 'transactions/history?from_block=', str(block_num)])
		return(self.get_response(cmd))
		
	def is_rating(self, rating):
		# По рейтингу возвращает тип лиги chemp, gold, silver, bronze или None
		# ratings = {"chemp": [2800, 10000], "gold": [1900, 2799], "silver": [1000, 1899], "bronze": [100, 999]}
		liga = [cmd for cmd, value in self.ratings.items() if value[0] <= int(rating) <= value[1]]
		return(liga[0] if liga else None)
	
	### PLAYER ###
	
	def get_collection(self, player):
		cmd = ''.join([self.url, 'cards/collection/', player])
		return(self.get_response(cmd))
		
	def get_player_collection(self, player):	### resolve {uid: {name:, level:}}
		return(self.resolve_collection(self.get_collection(player)))

	def get_player_login(self, player):
		cmd = ''.join([self.url, 'players/login?name=', player])
		return(self.get_response(cmd))
		
	def is_submit_hashed_team(self, player):
		# Скрывает ли юнит свои карты перед боем
		data = self.get_player_login(player)
		try:
			hide = data["settings"]["submit_hashed_team"]
		except:
			hide = False
		return(hide)
		
	def is_player_liga(self, player):
		# В какой лиге играет юнит
		data = self.get_player_login(player)
		return(self.is_rating(data["rating"]))
		
	def get_player_details(self, player):
		cmd = ''.join([self.url, 'players/details?name=', player])
		return(self.get_response(cmd))
		
	def get_player_quests(self, player):
		cmd = ''.join([self.url, 'players/quests?username=', player])
		return(self.get_response(cmd))

	def is_player_quests(self, player):
		data = self.get_player_quests(player)
		if isinstance(data, list):
			if int(data[0]["completed_items"]) < int(data[0]["total_items"]):
				return({data[0]["name"]: int(data[0]["completed_items"])})
		else:
			print('error quest', data)
		return False
		
	def get_player_all(self, player):
		login = self.get_player_login(player)
		rating = int(login["rating"])
		data = {
					"rating": rating,
					"hide": login["settings"].get("submit_hashed_team", None),
					"liga": self.is_rating(rating),
					"timestamp": time(),
					#"quest": self.is_player_quests(player),
					#"battle": None,
					#"collection": self.resolve_collection(self.get_collection(player)),
				}
		return(data)
		
		
	### CARDS ###
	
	def get_card_details(self, reload = False):
		try:
			with open('get_details.json', 'r', encoding = 'utf8') as f:
				cards = json.load(f)
				#print('load card_details ok')
		except:
			reload = True				# not exist file
		if reload:
			cmd = ''.join([self.url, 'cards/get_details'])
			cards = self.get_response(cmd)
			with open('get_details.json', 'w', encoding = 'utf8') as f:
				json.dump(cards, f, ensure_ascii = False)
		return(cards)
		
	def get_cards_stats(self):
		cmd = ''.join([self.url, 'cards/stats'])
		return(self.get_response(cmd))
		
	def find_cards(self, id):
		ids = ','.join(id) if isinstance(id, list) else id
		cmd = ''.join([self.url, 'cards/find?ids=', ids])
		return(self.get_response(cmd))
		
	def load_cards(self):
		print('load cards')
		### self.run()		# Инициализация Tkinter
		
		#self.cards = self.get_card_details()
		#self.card_names = {card["id"]: card["name"] for card in self.cards}
		self.card_files = {name: ''.join([self.path_img, name, '.png']) for id, name in self.card_names.items()}
		self.card_photos = {name: PhotoImage(file = file) for name, file in self.card_files.items()}
		
	def resolve_collection(self, collection):
		cards = {}
		for card in collection["cards"]:
			cards[card["uid"]] = {"name": self.card_names[card["card_detail_id"]], "level": card["level"]}
		return(cards)
		
	def resolve_team(self, team, player):
		collection = self.get_player_collection(player)
		csv = [str(collection[card]["level"]) + ':' + collection[card]["name"] for card in team]
		return(csv)
		
	def convert_team_to_csv(self, team, ruleset, mana_cap):
	
		liga = self.is_rating(team["rating"])
		if liga:
			try:
				color = team["color"]
				summoner = str(team["summoner"]["level"]) + ':' + self.card_names[team["summoner"]["card_detail_id"]]
				monsters = [str(monster["level"]) + ':' + self.card_names[monster["card_detail_id"]] for monster in team["monsters"]]
			
				csv = ','.join([liga, ruleset, str(mana_cap), color, summoner] + monsters)
				return(csv)
			except:
				pprint(team)
				input('Error convert')
		return False
		
		
	### BATTLE ###
	
	def get_battle_history(self, player):
		cmd = ''.join([self.url, 'battle/history?player=', player])
		return(self.get_response(cmd))

	def get_battle_history_team(self, player):
		data = self.get_battle_history(player)
		battles = []
		if data:
			for line in data["battles"]:
				battle = {cmd: line[cmd] for cmd in ['mana_cap', 'ruleset', 'inactive']}
				details = json.loads(line["details"])
				type_result = details.get("type", None)
				if not type_result:
					for type_team in ['team1', 'team2']:
						team = details.get(type_team, None)
						if team:
							team["player"] == player
							battle["color"] = team["color"]
							summoner = [{ "name": self.card_names[team["summoner"]["card_detail_id"]], "level": team["summoner"]["level"]}]
							monsters = [{ "name": self.card_names[m["card_detail_id"]], "level": m["level"]} for m in team["monsters"]]
							battle["team"] = summoner + monsters
							battles.append(battle)
							break
		return(battles)
		
	def get_battle_result(self, id):
		cmd = ''.join([self.url, 'battle/result?id=', str(id)])
		return(self.get_response(cmd))
		
	def get_battle_status(self, id):
		cmd = ''.join([self.url, 'battle/status?id=', str(id)])
		return(self.get_response(cmd))

	
	### MARKET ###
		
	def get_price(self):
		data = self.settings()
		if data:
			price = {"SBD": data["sbd_price"], "STEEM": data["steem_price"]}
			return(price)
		return False
		
	def get_for_sale(self):
		cmd = ''.join([self.url, 'market/for_sale'])
		return(self.get_response(cmd))
		
	def get_market_for_sale_grouped(self):
		cmd = ''.join([self.url, 'market/for_sale_grouped'])
		return(self.get_response(cmd))
		
	### END ###
		
		
	def get_response(self, cmd):
	
		n = 0
		while n < n_step:
			response = self.http.get(cmd)
			
			try:
				if str(response) == '<Response [200]>':
					return(response.json())
			except:
				print('??? ERROR in SteemMonstersApi', n)
			
			sleep(time_step)
			n += 1
		return False
		

		
			

if __name__ == '__main__':

	print('connect')
	input('try call?')
	
	sm = SM()
	api = EsteemApi()
	
	last_block = api.get_head_block() - 1 * 20		#aka 1 min
	print('replay... wait')
	
	while True:
		time_start = time()
		head_block = api.get_head_block()
	
		for b in range(last_block, head_block):
			#print('next block', b)
			
			i = api.get_block(b)
			timestamp = i["timestamp"].split('T')[1]

			# check custom
			for tx in i["transactions"]:	###
				for op in tx["operations"]:
					if op[0] == 'custom_json':
					
					
						id = op[1].get('id')
						
						if id == 'sm_find_match':
							data = json.loads(op[1].get('json'))
							
							if data["match_type"] == 'Ranked':
							
								player = op[1].get('required_posting_auths')[0]
								trx_id = tx.get('transaction_id')
								res_battle = sm.get_battle_status(trx_id)
								
								if res_battle:
									try:
										status = int(res_battle["status"])
									except:
										pprint(res_battle)
										sleep(3)
										#input('stop')
										
									if status == 0:		# not opponent
										
										res_player = sm.get_player_login(player)
										if res_player:
										
											rank = res_player["max_rank"]
											sub = res_player["settings"].get("submit_hashed_team", False)
											hide = 'hide' if sub else None
												
											rating = res_player["rating"]
											if rating >= 2800:
												cmd = "chemp"
											elif rating >= 1900:
												cmd = "gold"
											elif rating >= 1000:
												cmd = "silver"
											elif rating >= 100:
												cmd = "bronze"
											else:
												cmd = False
											
											if cmd in ['chemp']:
												#print(cmd, rating, player, 'find battle', trx_id)
												sm.battles[trx_id] = [player, rating, hide]
												
												ratings = [value[1]  for key, value in sm.battles.items()]
												ratings.sort(reverse = True)
												print(cmd, timestamp, player, rating, hide, 'total = ', len(sm.battles), ratings)
												
												sm_thread = Thread(target = sm.scan_battle, args = [trx_id])
												sm_thread.start()

										
									'''
									elif status == 1:		#
										opponent_player = res_battle["opponent_player"]
										print(player, 'VS', opponent_player, res_battle["ruleset"])
										#pprint(res_battle["team"])
									elif status == 2:		#
										opponent_player = res_battle["opponent_player"]
										print(player, 'VS', opponent_player, 'END')
										#pprint(res_battle["team"])
									elif status in [3, 4]:		# cancel
										opponent_player = res_battle["opponent_player"]
										print(player, 'CANCEL')
										#pprint(res_battle["team"])
									else:
										
										pprint(res_battle)
										input()
									'''
								
								
						elif id[:2] == 'sm':

							pass
							#pprint(tx)
							#input('next?')
							
		time_end = time()
		d = round(time_end - time_start)
		tt = 3 - d		###
		if tt < 0:
			tt = 0
			
		last_block = head_block

		#print('sleep', tt, 'sec')
		sleep(tt)
		
							

