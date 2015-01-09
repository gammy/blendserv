#!/usr/bin/env python3
# Usage example:
# Get current blender state:
# curl --user user:pass http://hostname:port
# Set current blender state (to on)
# curl --user user:pass --data 'blender=1' http://hostname:port

import http.server
import socketserver
import base64
import urllib
import signal
import RPIO

srv_info = {'port': 8192, # Listening port
	    'host': '',   # Listening host
	    'user': b'foop',
	    'pass': b'froopberry'}

TIMEOUT_BLENDER_OFF = 7 * 60
PIN_BLENDER = 18 # RPIO 1 on Raspberry Pi model B

def handle_sigalrm(sig, frame):
	print("SIGALRM")
	blender.set(False)

# XXX Not thread safe (uses SIGALRM)
class Blender():

	pin = None
	state = False
	
	def __init__(self, pin):
		self.pin = pin
		RPIO.setup(self.pin, RPIO.OUT)
		RPIO.setmode(RPIO.BCM)
		self.set(False)
		signal.signal(signal.SIGALRM, handle_sigalrm)

	def set(self, state):
		print('Setting RPIO pin {:} to {:}'.format(self.pin, state))
		RPIO.output(self.pin, state)
		signal.alarm(TIMEOUT_BLENDER_OFF if state else 0)
		self.state = state

	def get(self):
		return self.state
#		return RPIO.input(self.pin)


class WebServer(http.server.SimpleHTTPRequestHandler):

	def authenticate(self):
		auth_header = None

		if 'Authorization' in self.headers:
			auth_header = bytes(self.headers.get('Authorization'), 'ASCII')

#		print(self.headers)

		if not auth_header or auth_header != srv_info['auth']:
			self.do_AUTHHEAD()
			self.wfile.write(b'Authorization required')
			return False

		# Valid request
		self.do_HEAD()
		return True

	def do_HEAD(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_AUTHHEAD(self):
		self.send_response(401)
		self.send_header('WWW-Authenticate', 'Basic realm="Blender"')
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_GET(self):
		if not self.authenticate():
			return

		self.wfile.write(b'1\n' if blender.state else b'0\n')

	def do_POST(self):
		if not self.authenticate():
			return

		length = int(self.headers.get('content-length'))
		data = self.rfile.read(length)
		data = urllib.parse.parse_qs(data.decode('utf-8'))

		if 'blender' in data:
			state = data['blender'][0]

			if state != '1' and state != '0':
				return

			state = True if state == '1' else False

			if blender.get() != state:
				blender.set(state)

		self.wfile.write(b'1\n' if blender.state else b'0\n')

blender = Blender(PIN_BLENDER)

lp = srv_info['user'] + b':' + srv_info['pass']
srv_info['auth'] = b'Basic ' + base64.b64encode(lp)

server = socketserver.TCPServer((srv_info['host'], 
				 srv_info['port']), WebServer, False)

server.allow_reuse_address = True # SO_REUSEADD (allows rebinding the port)
server.server_bind()     # Manually bind, to support allow_reuse_address
server.server_activate() # (see above comment)

handler = http.server.SimpleHTTPRequestHandler

print("Server bound to interface '{:}', port {:}".format(srv_info['host'], srv_info['port']))
server.serve_forever()
