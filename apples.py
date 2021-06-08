import random, os, json


class Player():
	def __init__(self, name):
		self.name=name

class Game():
	is_started = False
	winner = ''

	def start(self, players):
		with open('/home/waltner_mason/a2a_flask/green_cards_jr.json', 'r') as f:
			self.green_cards = json.load(f)
		with open('/home/waltner_mason/a2a_flask/red_cards_jr.json', 'r') as f:
			self.red_cards = json.load(f)
		#deal out cards
		self.hands = {}
		#make a hand for each player
		for player in players:
			player.score = 0
			self.hands[player.name] = []
		for player in self.hands:
			for i in range(5):
				self.hands[player].append(self.red_cards.pop(random.randint(0,len(self.red_cards)-1)))
		self.green_card = self.green_cards.pop(random.randint(0,len(self.green_cards)-1))
		self.is_started = True
		self.judge = 0
		self.submission = {}
		self.winner = ''

	def new_card(self, name):
		self.hands[name].append(self.red_cards.pop(random.randint(0,len(self.red_cards)-1)))

		
	def new_turn(self):
		self.winner = ''
		self.submission={}
		self.judge += 1
		self.green_card = self.green_cards.pop(random.randint(0,len(self.green_cards)-1))
