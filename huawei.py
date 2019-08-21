#!/usr/bin/python

import requests
import pyping
import time
from bs4 import BeautifulSoup

class config:
	host = '192.168.8.1'
	poling_interval = 60
	status = '3'
	max_rtt = '0'
	avg_rtt = '0'
	min_rtt = '0'
	sessionid = False
	tokenid = False
	rsrq  = 0
	rsrp = 0
	rssi = 0
	cur_con_time = 0


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
		sup = BeautifulSoup(req.text, 'lxml')
		config.rsrq = sup.response.rsrq.get_text(strip=True)
		config.rsrp = sup.response.rsrp.get_text(strip=True)
		config.rssi = sup.response.rssi.get_text(strip=True)
		if config.rsrq and config.rsrp and config.rssi > 0:
			return True
		else:
			return False

	@staticmethod
        def traffic_stat():
                url="http://"+config.host+"/api/monitoring/traffic-statistics"
                headers ={'Cookie':config.session,'__RequestVerificationToken':config.tokenid,'Content-Type':'text/xml'}
                req = requests.get(url, headers=headers)
                sup = BeautifulSoup(req.text, 'lxml')
                config.cur_con_time = (float(sup.response.currentconnecttime.get_text(strip=True))/60)/60
                print(config.cur_con_time)
		#config.rsrp = sup.response.rsrp.get_text(strip=True)
                #config.rssi = sup.response.rssi.get_text(strip=True)
                #if config.rsrq and config.rsrp and config.rssi > 0:
                #        return True
                #else:
                #        return False
	
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
			 	if pool.signal() is not False:
					print (time.ctime(),"RSRQ:",config.rsrq)
					print (time.ctime(),"RSRP:",config.rsrp)
					print (time.ctime(),"RSSI:",config.rssi)
				else:
					print ("Unable to get data from modem")
				pool.traffic_stat()
				print ('Current connection time: {:%H:%M:S}'.format(config.cur_con_time))
			else:
				print (time.ctime(),"Unauthorised")
		else:
			print (time.ctime(),"Modem HTTP is Down","Code:",pool.home())
	else:
		print (time.ctime(),"Host IP:",config.host,"Down")
	time.sleep(config.poling_interval)
