# simple example of downloading image 

import os
import sys
import struct

# sys.path.insert(0, os.path.abspath('../'))
from redirect_detector import RedirectResolver, parseUrl, directfetch

HEADERS1 = { 
	'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate, sdch, br',
	'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
	'Connection': 'keep-alive',
	'Upgrade-Insecure-Requests': '1',
}

# @param datastream = urllib2.urlopen(url)
# Attention: maybe detection size of JPEG are incorrect
def getImageSize(datastream):
	data = datastream.read(24)
	# print('Data: %s' % (datastream.read()))
	size = len(data)
	height = -1
	width = -1
	content_type = ''

	# handle GIFs
	if (size >= 10) and data[:6] in (b'GIF87a', b'GIF89a'):
		# Check to see if content_type is correct
		content_type = 'image/gif'
		w, h = struct.unpack("<HH", data[6:10])
		width = int(w)
		height = int(h)

	# See PNG 2. Edition spec (http://www.w3.org/TR/PNG/)
	# Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
	# and finally the 4-byte width, height
	elif ((size >= 24) and (data[:8] == b'\211PNG\r\n\032\n') and (data[12:16] == b'IHDR')):
		content_type = 'image/png'
		w, h = struct.unpack(">LL", data[16:24])
		width = int(w)
		height = int(h)

	# Maybe this is for an older PNG version.
	elif (size >= 16) and data[:8] == b'\211PNG\r\n\032\n':
		# Check to see if we have the right content type
		content_type = 'image/png'
		w, h = struct.unpack(">LL", data[8:16])
		width = int(w)
		height = int(h)

	# handle JPEGs
	elif (size >= 2) and (data[:2] == b'\377\330'):
		content_type = 'image/jpeg'
		datastream.read(2)
		b = datastream.read(1)
		try:
			while (b and ord(b) != 0xDA):
				while (ord(b) != 0xFF): b = datastream.read(1)
				while (ord(b) == 0xFF): b = datastream.read(1)
				if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
					datastream.read(3)
					h, w = struct.unpack(">HH", datastream.read(4))
					width = int(w)
					height = int(h)
					break
				else:
					datastream.read(int(struct.unpack(">H", datastream.read(2))[0])-2)
				b = datastream.read(1)
			# width = int(w)
			# height = int(h)
		except struct.error:
			pass
		except ValueError:
			pass

	return content_type, width, height

# get input argments
# urlData = parseUrl('https://img.tinychan.org/img/1413923269267753.gif')
urlData = parseUrl('https://ad.publicidees.com/promos/banners/916/59848.jpg')
def connHandler(conn, resp):
	imageData = getImageSize(resp)
	print('[Connection ready]')
	print(resp.headers)
	print(imageData)

# Create request
directfetch(urlData, HEADERS1, 10, connHandler)
