import json
import hashlib
import hmac
import requests
import urllib.parse


class CoinPaymentsAPI:
	""" 
		currency=BTC&version=1&cmd=get_callback_address&key=your_api_public_key&format=json
	"""

	api_url = 'https://www.coinpayments.net/api.php'


	def __init__(self, public_key, private_key):
		self.format = 'json'
		self.private_key = private_key
		self.public_key = public_key
		self.version = 1


	def create_hmac(self, fields):
		"""
			Every API call has a SHA-512 HMAC signature generated with your private key.
			A server generates it's own HMAC signature and compares it with the API caller's.
			If they don't match the API call is discarded. The HMAC signature is sent as a HTTP
			header called 'HMAC'.

			https://www.coinpayments.net/apidoc-intro
		"""
		paybytes = urllib.parse.urlencode(fields).encode('utf8')
		sign = hmac.new(self.private_key, paybytes, hashlib.sha512).hexdigest()

		return paybytes, sign


	def send_request(self, fields):
		"""
			Returns a response (JSON) for 'fields' dict. 
		"""
		paybytes, sign = self.create_hmac(fields)
		headers = {
			'Content-Type': 'application/x-www-form-urlencoded',
			'hmac': sign
		}
		response = requests.post(self.api_url, headers=headers, data=paybytes)

		return response


	def get_suitable_fields(self, command, optional_fields={}):
		"""
			Returns 'fields' dict with optional fields if it's needed.
		"""
		fields = {
			'cmd': command,
			'key': self.public_key,
			'format': self.format,
			'version': self.version
		}
		fields.update(optional_fields)

		return fields


	def get_basic_info(self):
		"""
			https://www.coinpayments.net/apidoc-get-basic-info
		"""
		command = 'get_basic_info'

		return self.send_request(self.get_suitable_fields(command))


	def get_rates(self):
		"""
			https://www.coinpayments.net/apidoc-rates
		"""
		command = 'rates'
		optional_fields = {
			'short': 1,
			'accepted': 1
		}

		return self.send_request(self.get_suitable_fields(command, optional_fields))


	def get_coin_balances(self):
		"""
			https://www.coinpayments.net/apidoc-balances
		"""
		command = 'balances'

		return self.send_request(self.get_suitable_fields(command))


	def get_deposit_address(self, currency):
		"""
		Addresses returned by this API are for personal use deposits and reuse
		the same personal address(es) in your wallet. There is no fee for these
		deposits but they don't send IPNs. For commercial-use addresses see 
		https://www.coinpayments.net/apidoc-get-callback-address.
		"""
		command = 'get_deposit_address'
		optional_fields = {
			'currency': currency
		}

		return self.send_request(self.get_suitable_fields(command, optional_fields))
