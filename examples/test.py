import os
import sys


if __name__ == "__main__":
	# sys.path.insert(0, os.path.abspath('../'))
	from redirect_detector import RedirectResolver, parseUrl, CookieManager

	HEADERS = { 
		'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, sdch, br',
		'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
		'Connection': 'keep-alive',
		'Upgrade-Insecure-Requests': '1',
	}

	if(True):
		print('\n[Url parse test]')
		links = [
			'https://dpm.demdex.net/ibs:dpid=269&dpuuid=3797584e-a342-4100-87fd-e0586e83a7e5&ddsuuid=21562828320067591043226765471413674852',
			'http://www.taobao.com'
		]

		for link in links:
			urlData = parseUrl(link)
			print('UrlData:')
			print(urlData)

	if(True): 
		print('\n[Cookie parse test]')
		testCookies = CookieManager()
		tests = [
			'uuid=da51584b-ad3e-4700-8327-299218c19c2e; domain=.mathtag.com; path=/; expires=Sat, 06-Jan-2018 13:10:22 GMT',
			'uuidc=CUqTghFNO/i9kTnBAu5zxSMLh7cEf3572Sar/pAPLDcS41OZer8SzbLPHgOKa8xB2iQJEDRj49CZNUYV8CUpCHXG7RmfXA92iX9QJng5azo=; Expires=Sat, 06-Jan-18 13:10:23 GMT; Domain=.mathtag.com; Path=/',
			'demdex=61149099283264484541222287149626318631;Path=/;Domain=.demdex.net;Expires=Wed, 07-Jun-2017 13:10:23 GMT',
			'dpm=61149099283264484541222287149626318631;Path=/;Domain=.dpm.demdex.net;Expires=Wed, 07-Jun-2017 13:10:23 GMT',
			'demdex=61149099283264484541222287149626318631;Path=/;Domain=.demdex.net;Expires=Wed, 07-Jun-2017 13:10:23 GMT'
		]
		for cookieLine in tests:
			print('\nTEST: ', cookieLine)
			testCookies.append(cookieLine)

		print('\nCollected domains:')
		print(testCookies.domains)		

		domains = [
			'demdex.net',
			'sync.mathtag.com',
			'mathtag.com',
			'www.google.com',
			''
		]
		for domain in domains:
			cookie = testCookies.getCookies(domain)
			print('\tFor `%s` cookie: `%s`' % (domain, cookie))

	if(True): 
		print('\n[Test redirects]')

		links = [
			'https://sync.mathtag.com/sync/img?mt_exid=10004&mt_exuid=21562828320067591043226765471413674852&redir=https%3A%2F%2Fdpm.demdex.net%2Fibs%3Adpid%3D269%26dpuuid%3D[MM_UUID]%26ddsuuid%3d21562828320067591043226765471413674852',
			'https://beacon.krxd.net/usermatch.gif?kuid_status=new&partner=google',
			'https://cm.g.doubleclick.net/pixel?google_ula=1293153&google_nid=ssc&google_push=AHNF13KWTaePaqHMDmlZDYOmseyO1-5_ouFmrvEIMVc&google_sc&google_hm=2XxFsI5JReGCbEFBlMkIYg'
		]

		rr = RedirectResolver(HEADERS, links[2])
		while rr.doRedirect():
			pass		

		print('\nCookie cash:')
		print(rr.cm.domains)
		print('\nRequest log:')

		for item in rr.log:
			print('\nRequest:')
			print(item)
