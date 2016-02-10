'''
Strategy - 
observed that range is increasing with time for both buy and sell
buy everything at start, hold for 5-10 mins and sell it later...upto 5-10$ profit possible per share.
enable sell later only when scale increases...doing this twice in game is sufficient to build $10,000 profit.

not really possible to know how many you actually buy since buy can be open for really long time. have to work with heuristics.

money is not really a factor
1000 stock on either side is more important.
'''
import requests
import json
import math

venue = "FLWEX"
stock = "EAVI"
account = 'TAY60073625'

buy_target = 7400  #heuristically decided based on value around which stock value is fluctuating.
units_in_hand = 0
max_units = 1000 #not allowed to go more than 1000 on either side.
batch_size = 200

#qty, direction, price for order will be set later.
order = {
  "account": account,
  "venue": venue,
  "stock": stock,
  "orderType": "limit" 
}


hdr = {'X-Starfighter-Authorization' : '4a92bf2f7714296cad41c09b6de8235fc21e9529'}

def get_orderbook():
	url = 'https://api.stockfighter.io/ob/api/venues/'+venue+'/stocks/'+stock
	return requests.get(url).json()
	
def get_info_for_key(r, key):
	#return avg asks/bids price and sum_qty
	keyInfo = r.get(key)
	sum_price = 0
	sum_qty = 0
	if keyInfo != None:
		for info in keyInfo:
			sum_price += info['price'] * info['qty']
			sum_qty += info['qty']
		return (float(sum_price)/float(sum_qty), sum_qty) 
	else:
		return (-1, 0)

def stock_order(order, qty, direction, price):
	order['qty'] = qty
	order['direction'] = direction
	order['price'] = price
	return requests.post('https://api.stockfighter.io/ob/api/venues/'+venue+'/stocks/'+stock+'/orders',
	 		data = json.dumps(order), headers = hdr)

#Tasks end by itself when profit exceeds $ 10,000
while True:
	orderbook = get_orderbook()
	#for buying
	ask_price, ask_qty = get_info_for_key(orderbook, 'asks')
	ask_price = int(math.ceil(ask_price))
	print "asks_price: ", ask_price, "money: ", money, "units_in_hand: ", units_in_hand
	if ask_price <= buy_target and ask_price != -1:
		units = min(batch_size, max_units - (batch_size+units_in_hand) )
		#since we are not allowed to go 1000 shares on either side.
		if units > 0:
			r = stock_order(order, units, 'buy', ask_price) 			
			print "buying ", r.text
			units_in_hand += units

	#for selling
	bids_price, bids_qty = get_info_for_key(orderbook, 'bids')
	bids_price = int(math.floor(bids_price))
	print "bids_price: ", bids_price
	if bids_price > buy_target and bids_price != -1:
		if(units_in_hand > 0):
			units = units_in_hand
			if(units_in_hand < batch_size):
				units = units_in_hand
			else:
				units = batch_size
			r = stock_order(order, units, 'sell', bids_price)
			units_in_hand -= units
			print "selling ", r.text