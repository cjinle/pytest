#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

INVALID_CARD = 0
DESKTOP_CARD = 1
STOCK_CARD = 2
PASS_CARD = 3


class PyRamid:
	base_cards = [
		0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,
		0x11,0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,0x1a,0x1b,0x1c,0x1d,
		0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x29,0x2a,0x2b,0x2c,0x2d,
		0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,0x3a,0x3b,0x3c,0x3d,
	]
	desktop_cards = []
	stock_cards = []
	pass_cards = []
	update_indexs = []


	def __init__(self):
		pass

	def rand_cards(self):
		tmp = self.base_cards
		random.shuffle(tmp)
		self.desktop_cards = tmp[:28]
		self.stock_cards = tmp[28:]
		print("desktop cards: ", self.desktop_cards)
		print("stock cards: ", self.stock_cards)

	def output(self):
		pcard, scard, wcard = self.desktop_cards, self.stock_cards, self.pass_cards
		pcard = ["%02X" % x for x in pcard]
		scard = ["%02X" % x for x in scard]
		wcard = ["%02X" % x for x in wcard]

		print("      ",pcard[0])
		print("     ",pcard[1],pcard[2])
		print("    ",pcard[3],pcard[4],pcard[5])
		print("   ",pcard[6],pcard[7],pcard[8],pcard[9])
		print("  ",pcard[10],pcard[11],pcard[12],pcard[13],pcard[14])
		print(" ",pcard[15],pcard[16],pcard[17],pcard[18],pcard[19],pcard[20])
		print("",pcard[21],pcard[22],pcard[23],pcard[24],pcard[25],pcard[26],pcard[27])
		print("")
		print("stock_cards: ", scard)
		print("pass_cards: ", wcard)


	def del_cards(self, num1, num2):
		if (num1 & 0x0f) + (num2 & 0x0f) != 13:
			print("nums error", num1, num2)
			return
		ret = [1,1]
		card_types = [0,0]
		nums = [num1,num2]
		for idx, num in enumerate(nums):
			if num == 0:
				continue
			card_type = self.get_card_type(num)
			card_types[idx] = card_type
			if card_type == DESKTOP_CARD:
				if not self.check_desktop_card(num):
					ret[idx] = 0
					break
			elif card_type == STOCK_CARD:
				if not self.check_stock_card(num):
					ret[idx] = 0
					break
			elif card_type == PASS_CARD:
				if not self.check_pass_card(num):
					ret[idx] = 0
					break

		if sum(ret) != 2:
			print("nums error", num1, num2)
			return

		for idx, num in enumerate(nums):
			if card_types[idx] == DESKTOP_CARD:
				tmp_idx = self.desktop_cards.index(num)
				self.desktop_cards[tmp_idx] = 0
			elif card_types[idx] == STOCK_CARD:
				self.stock_cards.pop(0)
			elif card_types[idx] == PASS_CARD:
				self.pass_cards.pop(0)


	def get_card_type(self, num):
		if num in self.desktop_cards:
			return DESKTOP_CARD
		if num in self.stock_cards:
			return STOCK_CARD
		if num in self.pass_cards:
			return PASS_CARD

		return INVALID_CARD

	def check_desktop_card(self, num):
		if num == 0:
			return False
		if num not in self.desktop_cards:
			return False
		idx = self.desktop_cards.index(num)
		offset = 0
		if idx <= 0:
			offset = 1
		elif idx <= 2:
			offset = 2
		elif idx <= 5:
			offset = 3
		elif idx <= 9:
			offset = 4
		elif idx <= 14:
			offset = 5
		elif idx <= 20:
			offset = 6

		if offset > 0:
			if self.desktop_cards[idx+offset] != 0 or self.desktop_cards[idx+offset+1] != 0:
				return False

		return True

	def check_stock_card(self, num):
		if len(self.stock_cards) > 0 and num == self.stock_cards[0]:
			return True
		return False

	def check_pass_card(self, num):
		if len(self.pass_cards) > 0 and num == self.pass_cards[0]:
			return True
		return False

	def flop_card(self):
		if len(self.stock_cards) == 0:
			self.pass_cards.reverse()
			self.stock_cards, self.pass_cards = self.pass_cards, []
			return
		num = self.stock_cards.pop(0)
		self.pass_cards.insert(0, num)	

	def check_finish(self):
		if sum(self.desktop_cards) == 0:
			print("!!!! finish !!!!")

if __name__ == '__main__':
	print("hello pyramid")
	pr = PyRamid()
	pr.rand_cards()
	pr.output()
	while True:
		param = input("input > ")
		arr = param.split(' ')
		if len(arr) >= 1:
			if arr[0] == "1":
				pr.del_cards(int(arr[1], 16), int(arr[2], 16))
			elif arr[0] == "2":
				pr.flop_card()
			
		pr.output()
		pr.check_finish()



