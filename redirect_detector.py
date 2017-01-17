# Redirect Detector Toolkit v11 2017/01/04

import http.client

# Parse URL
def parseUrl(url):
	out = {}
	try:
		pos = url.index('?') # Cause exception if symbol not found!
		out['query'] = url[pos + 1:]
		url = url[0:pos]
	except:
		pass
	pos = url.find('//')

	if pos != -1:
		out['protocol'] = url[0:pos - 1] or 'http' # ://
		url = url[pos + 2:]

	try:	
		pos = url.index('/')	
		out['host'] = url[0:pos]
		out['path'] = url[pos:]
	except:
		out['host'] = url
		out['path'] = '/'

	return out

# Create GET request
# @param {Dictionary} urlData, urlData = parseUrl(url)
# @return {response Object|Exception}
def directfetch(urlData, headers, timeout = 10.0, handleConnection = None):
	connectionMethod = http.client.HTTPConnection if urlData['protocol'] != 'https' else http.client.HTTPSConnection
	conn = connectionMethod(urlData['host'], timeout = timeout)
	
	try:
		# print('Connection init')
		# 3ty argument for data at request like post data (params)
		conn.request('GET', urlData['path'] + ('?' + urlData['query'] if 'query' in urlData else ''), '', headers)
		conn.sock.settimeout(timeout)
		out = conn.getresponse()
	except Exception as e:
		out = e
	else:
		if handleConnection is not None:
			handleConnection(conn, out)
		# print('Connection complete')
	# Attention refactor: conn.close broke document downloading
	conn.close()
	return out

# Api for working with cookie
class CookieManager(object):
	def __init__(self):
		self.domains = {}
	# parse and store value of cookie	
	def append(self, str):
		pos = str.index(';')
		if pos != -1:
			keyValue = str[0:pos]
			str = str[pos + 1:]
			parts = str.split(';')
			args = {}

			for key in parts:
				try:
					pos = key.index('=')

					if pos != -1:
						args[key[0:pos].strip().lower()] = key[pos + 1:].strip()
				except:
					args[key.strip().lower()] = True
			pos = keyValue.index('=')

			if pos != -1:
				key = keyValue[0:pos].strip()
				value = keyValue[pos + 1:].strip()

				if 'domain' in args:
					domain = args['domain'] 

					if domain not in self.domains:
						self.domains[domain] = {}
					self.domains[domain][key] = value
	# get cookie string for domain
	def getCookies(self, originalDomain):
		str = ''
		domain = '.' + originalDomain

		for domainPattern in self.domains:
			pos = domain.find(domainPattern)
			if(pos != -1):
				pairs = self.domains[domainPattern]
				for key in pairs:
					str += key + '=' + pairs[key] + ';'
		return str
	
# TODO set cookie collection as parameter	
class RedirectResolver(object):
	# HEADERS = { 
	# 	'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
	# 	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	# 	'Accept-Encoding': 'gzip, deflate, sdch, br',
	# 	'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
	# 	'Connection': 'keep-alive',
	# 	'Upgrade-Insecure-Requests': '1',
	# }
	# @param {Function} connectionHandler
	def __init__(self, headers, link = None, connectionHandler = None):
		self.cm = CookieManager()
		self.last_location = link
		self.log = []
		self.headers = headers

		self._curHost = None
		self._curProtocol = None
		self.f_connectionHandler = connectionHandler
	# Do redirect	
	# @return {Bool} redirected 
	def fetch(self, url):
		resp = None
		redirected = False
		log = {
			'fetch': url
		}
		
		urlData = parseUrl(url)

		# print('\nurlData %s' % (url))
		# print(urlData)
		
		# Restore host or protocol
		if len(urlData['host']) > 0:
			self._curHost = urlData['host']
			self._curProtocol = urlData['protocol']
		elif self._curHost is not None:
			urlData['host'] = self._curHost
			urlData['protocol'] = self._curProtocol
		# else: # something extraordinary! 
		# 	pass

		# Update cookie
		cookies = self.cm.getCookies(urlData['host'])
		# print('Send cookies %s' % cookies)
		self.headers['Host'] = urlData['host']

		if len(cookies) > 0:
			self.headers['Cookie'] = cookies	
			log['cookie'] = cookies			
		
		# print('[CALL fetch]: ' + url)
		# print(urlData)

		resp = directfetch(urlData, self.headers, 10.0, self.f_connectionHandler)
		self._lastResponse = resp

		if isinstance(resp, Exception):
			log['httpStatus'] = 0
			log['httpReason'] = str(resp)	
			self.last_location = None	
		else:
			log['httpStatus'] = resp.status
			log['httpReason'] = resp.reason

			if 'Location' in resp.headers:
				self.last_location = resp.headers['Location']
			elif 'location' in resp.headers:
				self.last_location = resp.headers['location']
			else: 
				self.last_location = None

			# ATTENTION: headers can contains several properties `set-cookie`
			logSetCookie = []
			for header_name, value in resp.headers.items():	
				header_name = header_name.lower()
				if header_name == 'set-cookie':
					self.cm.append(value)
					logSetCookie.append(value)
				elif header_name == 'content-type':
					log['contentType'] = value

			log['setCookie'] = logSetCookie
			log['setLocation'] = self.last_location

			if resp.status > 299 and resp.status < 400:
				redirected = True

		self.log.append(log) 
		return redirected
	def doRedirect(self, _url = None):
		url = _url or self.last_location
		res = None
		# print('\n\t[CALL doRedirect] url: %s' % url)
		if url is not None:
			res = self.fetch(url)
		return res
	def trace(self, maxRedirects = 10):
		rc = 0
		while self.doRedirect():
			if rc > maxRedirects:
				print('Redirect counter limit overhead')
				break
			else:
				rc += 1
		# maybe return content
	# def b_downloadContent(self, conn, resp):
