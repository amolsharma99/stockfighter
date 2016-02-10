'''
If you start late you'll not be able to meet the goal, since proces follow increasing trend in long term
like a happy real life stock market.
make few initial conservative transactions, know the target and adjust accordingly.
'''
import requests
import json

venue = "PEOJEX"
stock = "LSI"
total = 100000
sumcnt = 0
target = 4000

order = {
  "account": 'ERS97111815',
  "venue": venue,
  "stock": stock,
  "price" : target,
  "qty": 2000,
  "direction": "buy",
  "orderType": "limit" 
}

hdr = {'X-Starfighter-Authorization' : '4a92bf2f7714296cad41c09b6de8235fc21e9529'}

def get_current_price():
	#return avg sale price and sum_qty
	url = 'https://api.stockfighter.io/ob/api/venues/'+venue+'/stocks/'+stock
	r = requests.get(url)
	asks = r.json().get('asks')
	print asks
	sum_price = 0
	sum_qty = 0
	if asks != None:
		for info in asks:
			sum_price += info['price'] * info['qty']
			sum_qty += info['qty']
		return (float(sum_price)/float(sum_qty), sum_qty) 
	else:
		return (-1, 0)

while True:
	price, qty = get_current_price()
	print price, qty
	if price <= target and price != -1:
		sumcnt += qty
		r = requests.post('https://api.stockfighter.io/ob/api/venues/'+venue+'/stocks/'+stock+'/orders',
	 	data = json.dumps(order), headers = hdr)
		print sumcnt, r.text