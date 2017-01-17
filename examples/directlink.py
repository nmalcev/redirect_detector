#  Example of exploring web links

import os
import sys

# sys.path.insert(0, os.path.abspath('../'))
from redirect_detector import RedirectResolver

HEADERS1 = { 
	'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate, sdch, br',
	'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
	'Connection': 'keep-alive',
	'Upgrade-Insecure-Requests': '1',
}

rr = RedirectResolver(HEADERS1, 'https://goo.gl/CRn44U')
rr.trace()

# Explore redirects
for item in rr.log:
	print('\nRequest: ')
	# print(item)
	for key in item:
		print(str(key) + ': ' + str(item[key]))

if bool(rr.cm.domains): # if not empty cookie collection
	print('Cookie cash:')
	print(rr.cm.domains)