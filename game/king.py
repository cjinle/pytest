#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random


class King:
	base_cards = [
		0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,
		0x11,0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,0x1a,0x1b,0x1c,0x1d,
		0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x29,0x2a,0x2b,0x2c,0x2d,
		0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,0x3a,0x3b,0x3c,0x3d,
	]
	base_chips = 100
	desktop_cards = []
	stock_cards = []
	users = []
	is_start = False
	current_idx = 0

	def start(self):
		for idx in range(5):
			self.users.append(self.create_user(idx))
		self.rand_cards()
		self.is_start = True

	def rand_cards(self):
		tmp = self.base_cards
		random.shuffle(tmp)
		idx = 0
		for card in tmp[:25]:
			if idx == 5: idx = 0
			self.users[idx]['cards'].append(card)
			idx += 1

		self.stock_cards = tmp[25:]
		print("stock cards: ", self.tohex(self.stock_cards))

	def create_user(self, seat_id):
		return {"win": 0, "lose": 0, "cards": []}

	def output(self):
		print("desktop cards: ", self.desktop_cards)
		print("stock cards: ", self.stock_cards)
		for idx,user in enumerate(self.users):
			print("#{0} win: {1}, lose: {2} cards: {3}".format(idx, user['win'], \
			 user['lose'], self.tohex(user['cards'])))

	def tohex(self, arr):
		return ["%02X" % x for x in arr]

	def get_real_card_num(self, card):
		return card & 0x0f

	def get_cards_sum(self, seat_id):
		num = 0
		for card in self.users[seat_id]['cards']:
			num = num + (card & 0x0f)
		return num

	def to_result(self, seat_id):
		self.output()
		print("-------- result ---------")
		target_num = self.get_cards_sum(seat_id)
		isWin = True
		result_nums = []
		for idx, user in enumerate(self.users):
			tmp_num = self.get_cards_sum(idx)
			if idx != seat_id:
				if isWin and tmp_num <= target_num:
					isWin = False
		result_str = ("LOSE", "WIN")
		for idx, user in enumerate(self.users):
			tmp_num = self.get_cards_sum(idx)
			if idx == seat_id:
				result_idx = int(isWin)
			else:
				result_idx = int(not isWin)
			print("#{0} {1} {2} {3}".format(idx, tmp_num, result_str[result_idx], self.tohex(user['cards'])))
		self.is_start = False
		return

	def play_cards(self, seat_id):
		same_card_idxs = []
		card_sum = 0
		last_card = 0
		if len(self.desktop_cards) > 0:
			last_card = self.desktop_cards[0]

		for idx, card in enumerate(self.users[seat_id]['cards']):
			card_num = card & 0x0f
			card_sum += card_num
			if card_num == (last_card&0x0f):
				same_card_idxs.append(idx)

		# need to finish
		if card_sum <= len(self.users[seat_id]['cards'])*3:
			self.to_result(seat_id)
			return
		
		con_idxs = []
		if len(same_card_idxs) > 0:
			con_idxs = same_card_idxs
		else:
			max_card_num = 0
			if len(self.stock_cards) == 0:
				self.to_result(seat_id)
				return

			self.users[seat_id]['cards'].append(self.stock_cards.pop(0))
			for idx, card in enumerate(self.users[seat_id]['cards']):
				card_num = card & 0x0f
				if card_num > max_card_num:
					con_idxs = [idx]
					max_card_num = card_num
				elif card_num == max_card_num:
					con_idxs.append(idx)
		
		new_user_cards = []	
		for idx, card in enumerate(self.users[seat_id]['cards']):
			if idx in con_idxs:
				print("#{0} put card: {1}".format(seat_id, self.tohex([card])))
				self.desktop_cards.insert(0, card)
				continue
			new_user_cards.append(card)
		self.users[seat_id]['cards'] = new_user_cards



if __name__ == '__main__':
	print("hello king")
	obj = King()
	obj.start()
	obj.output()
	seat_id = 0
	while obj.is_start:
		if seat_id >= 5: seat_id = 0
		obj.play_cards(seat_id)
		seat_id += 1
