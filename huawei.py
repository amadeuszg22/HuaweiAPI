#!/usr/bin/python
import requests
import pyping
import time
from bs4 import BeautifulSoup

class config:
	host = '192.168.8.1'
	status = '3'
	max_rtt = '0'
	avg_rtt = '0'
	min_rtt = '0'
	sessionid = False
	tokenid = False

def ping(host):
	probe = pyping.ping(host)
	#print ("Host IP:",probe.destination)
	config.status = probe.ret_code
	#print ("Ping results:",probe.max_rtt,"max rtt",probe.avg_rtt,"avg rtt",probe.min_rtt,"min rtt")
	config.max_rtt = probe.max_rtt
	config.avg_rtt = probe.avg_rtt
	config.min_rtt = probe.min_rtt

class pool:
	@staticmethod
	def home():
		url="http://"+config.host+"/html/home.html"
		req = requests.get(url)
		return req.status_code
	@staticmethod
	def auth():
		url="http://"+config.host+"/api/webserver/SesTokInfo"
		req = requests.get(url)
		#print (req.headres)
		#print (req.encoding)
		#print (req.text)
		sup = BeautifulSoup(req.text, 'lxml')
		config.session = sup.response.sesinfo.get_text(strip=True) #.replace("SessionID=","")
		config.tokenid = sup.response.tokinfo.get_text(strip=True)
		if config.session and config.tokenid is not False:
			return True
		else:
			return False
	@staticmethod
        def signal():
		url="http://"+config.host+"/api/device/signal"
		headers ={'Cookie':config.session,'__RequestVerificationToken':config.tokenid,'Content-Type':'text/xml'}
		#print (headers['Cookie'])
                req = requests.get(url, headers=headers)
		print (req.text)


while True:
	ping(config.host)
	if config.status == 0 :
		print (time.ctime(),"Host IP:",config.host,"UP")
		print (time.ctime(),"Ping results:",config.max_rtt,"max rtt",config.avg_rtt,"avg rtt",config.min_rtt,"min rtt")
		if pool.home() == 200:
			print (time.ctime(),"Modem HTTP is UP","Code:",pool.home())
			if pool.auth() is not False:
				print (time.ctime(),"Authentication token:",config.tokenid)
				print (time.ctime(),"Sesion ID:",config.session)
				pool.signal()
			else:
				print (time.ctime(),"Unauthorised")
		else:
			print (time.ctime(),"Modem HTTP is Down","Code:",pool.home())
	else:
		print (time.ctime(),"Host IP:",config.host,"Down")
	time.sleep(60)
