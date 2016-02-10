'''
there are two guys that are fighting
1. Bickman -
hates the company. want to cover short at 0.
he belives trend will be downside. he will sell high and buy low.
2. Ian -
client of the company. defends and support the company.
he belives company will grow.
he will buy low and sell high.

Rules -
Cant go negative at any point.
avoid taking orders from the big guys...means don't buy if qty is huge.

observed in the pattern that in very large order are coming in b/w with >3lac and price less than $30-40 than normal price.
don't buy/sell to these 2 buys, chances of request getting stuck is high, which spoils you unit count limit.
you have a fix window of 1000 shares, you have buy low, sell high...buy again high and sell again more high and so on.


Strategy -
keep two moving avgs - 1. asks avg of last 1000 asks. 2. purchase avg of last 5 purchase.
buy if units_in_hand < max allowed if asks is less than ask avg.
sell if bid > purchase_avg of last 5 bids.

don't sell, buy if qty is exceptionally high since it will be very high or very low price,
chances of it getting fulfilled is less as per observed behaviour and it will spoil you units_in_hand count.

+10 while buying, -10 while selling so that chances of fulfilling increases, and i don't end up competiting
based on time and lose.

wss is not reliable, might have to restart if connection gets closed from stockfighter
websockets - wss://api.stockfighter.io/ob/api/ws/:trading_account/venues/:venue/tickertape/stocks/:stock

'''
import requests
import json
import math
from ws4py.client.threadedclient import WebSocketClient
from collections import deque

venue = "EUFHEX"
stock = "TSM"
account = 'HWS66644135'
json_decoder = json.decoder.JSONDecoder()
max_queue_len = 800
#dont want to reach if same value is send by ws again and again.
prev_bid = 0
prev_ask = 0
batch_size = 100
max_units = 0
units_in_hand = 0	

#interested in avg of last 1000 elements.
#bids_deque = deque(maxlen = max_queue_len) 
asks_deque = deque(maxlen = max_queue_len)
purchase_deque = deque(maxlen = 5)

#purchase_deque.append(4288)

#qty, direction, price for order will be set later.
order = {
  "account": account,
  "venue": venue,
  "stock": stock,
  "orderType": "limit" 
}

hdr = {'X-Starfighter-Authorization' : '4a92bf2f7714296cad41c09b6de8235fc21e9529'}


def stock_order(order, qty, direction, price):
	order['qty'] = qty
	order['direction'] = direction
	order['price'] = price
	return requests.post('https://api.stockfighter.io/ob/api/venues/'+venue+'/stocks/'+stock+'/orders',
	 		data = json.dumps(order), headers = hdr)


def process_msg(msg):
	json_msg = json_decoder.decode(str(msg))
	quote = json_msg.get('quote') 
	bid = quote.get('bid')
	ask = quote.get('ask')
	bid_size = quote.get('bidSize')
	ask_size = quote.get('askSize')
	#global bids_deque
	global asks_deque
	global purchase_deque
	global units_in_hand
	global prev_bid 
	global prev_ask
	print"Bid, Ask, units_in_hand - ", bid, ask, units_in_hand
	#selling
	if bid != None and units_in_hand > 0 and bid_size < 50000:
		purchase_avg = float(sum(purchase_deque))/float(len(purchase_deque))
		print "purchase avg - ", purchase_avg
		if bid > purchase_avg and prev_bid != bid:
			prev_bid = bid
			units = units_in_hand
			if(units_in_hand < batch_size):
				units = units_in_hand
			else:
				units = batch_size
			r = stock_order(order, units, 'sell', bid - 15)
			units_in_hand -= units
			print "selling ", r.text
	#buying		
	if ask != None and ask_size < 50000:
		asks_deque.append(ask)
		ask_avg = float(sum(asks_deque))/float(len(asks_deque))
		print "ask avg - ", ask_avg
		if ask < ask_avg and prev_ask != ask:
			prev_ask = ask
			#buy it
			units = min(batch_size, (max_units - units_in_hand))
			if units > 0:
				r = stock_order(order, units, 'buy', ask + 15) 			
				print "buying ", r.text
				units_in_hand += units
				purchase_deque.append(ask)


class CodeFighterWebSocketClient(WebSocketClient):
	def closed(self, code, reason=None):
		print "Closed down", code, reason
		return code
	
	def received_message(self, msg):
		process_msg(msg)   

try:
	ws = CodeFighterWebSocketClient('wss://api.stockfighter.io/ob/api/ws/'+account+'/venues/'+venue+'/tickertape/stocks/'+stock)
	ws.connect()
	ws.run_forever()
except KeyboardInterrupt:
	ws.close()