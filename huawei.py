#!/usr/bin/python

import requests
import pyping
import time
from bs4 import BeautifulSoup

class config:
	host = '192.168.8.1'
	poling_interval = 60
	status = '3'
	sessionid = False
	tokenid = False
	# cur_con_time = 0
	# cur_up = 0
	# cur_down = 0
	# cur_down_speed = 0
	# cur_up_speed = 0
	# tot_up_data = 0
	# tot_down_data = 0
	# tot_con_time = 0
	month_up_data = 0
	month_down_data = 0

class data:
	class device:
		info = {
			"device_name" : "",
			"serialnumber" : "",
			"imei" : "",
			"imsi" : "",
			"iccid" : "",
			"hardwareversion" : "",
			"softwareversion" : "",
			"webuiversion" : "",
			"macaddress1" : "",
			"productfamily" : "",
			"classify" : "",
			"supportmode" : "",
			"workmode" : "",
		}
	class ping_stats():
		results = {
			"max_rtt" : "",
			"avg_rtt" : "",
			"min_rtt" : "",
		}
	class signal_stats():
		results = {
			"rsrq" : "",
			"rsrp" : "",
			"rssi" : "",		
		}
	class data_stats():
		results ={
			"cur_con_time" : "",
			"cur_up" : "",
			"cur_down" : "",
			"cur_down_speed" : "",
			"cur_up_speed" : "",
			"tot_up_data" : "",
			"tot_down_data" : "",
			"tot_con_time" : "",
			"month_up_data" : "",
			"month_down_data" : "",
		}
		

def ping(host):
	probe = pyping.ping(host)
	#print ("Host IP:",probe.destination)
	config.status = probe.ret_code
	#print ("Ping results:",probe.max_rtt,"max rtt",probe.avg_rtt,"avg rtt",probe.min_rtt,"min rtt")
	data.ping_stats.results["max_rtt"] = probe.max_rtt
	data.ping_stats.results["avg_rtt"] = probe.avg_rtt
	data.ping_stats.results["min_rtt"] = probe.min_rtt

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
				data.signal_stats.results["rsrq"] = sup.response.rsrq.get_text(strip=True)
				data.signal_stats.results["rsrp"] = sup.response.rsrp.get_text(strip=True)
				data.signal_stats.results["rssi"] = sup.response.rssi.get_text(strip=True)
				if len(data.signal_stats.results.items()) > 0:
					return True
				else:
					return False

	@staticmethod
        def traffic_stat():
				url="http://"+config.host+"/api/monitoring/traffic-statistics"
				headers ={'Cookie':config.session,'__RequestVerificationToken':config.tokenid,'Content-Type':'text/xml'}
				req = requests.get(url, headers=headers)
				sup = BeautifulSoup(req.text, 'lxml')
				data.data_stats.results["cur_con_time"] = (float(sup.response.currentconnecttime.get_text(strip=True))/60)/60
				data.data_stats.results["cur_up"] = ((float(sup.response.currentupload.get_text(strip=True))/1024)/1024)/1024
				data.data_stats.results["cur_down"] = ((float(sup.response.currentdownload.get_text(strip=True))/1024)/1024)/1024
				data.data_stats.results["cur_down_speed"] = ((float(sup.response.currentdownloadrate.get_text(strip=True))/1024)/1024)
				data.data_stats.results["cur_up_speed"] = ((float(sup.response.currentuploadrate.get_text(strip=True))/1024)/1024)
				data.data_stats.results["tot_up_data"] = (((float(sup.response.totalupload.get_text(strip=True))/1024)/1024)/1024)
				data.data_stats.results["tot_down_data"] = (((float(sup.response.totaldownload.get_text(strip=True))/1024)/1024)/1024)
				data.data_stats.results["tot_con_time"] = (float(sup.response.totalconnecttime.get_text(strip=True))/60)/60
				if len(data.data_stats.results.items()) > 0:
					return True
				else:
					return False
	@staticmethod
        def month_traffic_stat():
				url="http://"+config.host+"/api/monitoring/month_statistics"
				headers ={'Cookie':config.session,'__RequestVerificationToken':config.tokenid,'Content-Type':'text/xml'}
				req = requests.get(url, headers=headers)
				sup = BeautifulSoup(req.text, 'lxml')
				config.month_up_data = (((float(sup.response.currentmonthdownload.get_text(strip=True))/1024)/1024)/1024)
				config.month_down_data = (((float(sup.response.currentmonthupload.get_text(strip=True))/1024)/1024)/1024)
				if config.month_down_data and config.month_up_data >0:
					return True
				else:
					return False
	@staticmethod
        def dev_info():
				url="http://"+config.host+"/api/device/information"
				headers ={'Cookie':config.session,'__RequestVerificationToken':config.tokenid,'Content-Type':'text/xml'}
				req = requests.get(url, headers=headers)
				sup = BeautifulSoup(req.text, 'lxml')
				data.device.info["device_name"] = sup.response.devicename.get_text(strip=True)
				data.device.info["serialnumber"] = sup.response.serialnumber.get_text(strip=True)
				data.device.info["imei"] = sup.response.imei.get_text(strip=True)
				data.device.info["imsi"] = sup.response.imsi.get_text(strip=True)
				data.device.info["iccid"] = sup.response.iccid.get_text(strip=True)
				data.device.info["hardwareversion"] = sup.response.hardwareversion.get_text(strip=True)
				data.device.info["softwareversion"] = sup.response.softwareversion.get_text(strip=True)
				data.device.info["webuiversion"] = sup.response.webuiversion.get_text(strip=True)
				data.device.info["macaddress1"] = sup.response.macaddress1.get_text(strip=True)
				data.device.info["productfamily"] = sup.response.productfamily.get_text(strip=True)
				data.device.info["classify"] = sup.response.classify.get_text(strip=True)
				data.device.info["supportmode"] = sup.response.supportmode.get_text(strip=True)
				data.device.info["workmode"] = sup.response.workmode.get_text(strip=True)
				# for v in data.device.info.items():
				if len(data.device.info.items()) > 0:
					return True
				else:
					return False
					

while True:
	ping(config.host)
	if config.status == 0 :
		print ("-----Host Status:-----")
		print (time.ctime(),"Host IP:",config.host,"UP")
		print (time.ctime(),'Ping results:{0} max rtt, {1} avg rtt, {2} min rtt'.format(data.ping_stats.results["max_rtt"],data.ping_stats.results["avg_rtt"],data.ping_stats.results["min_rtt"]))
		if pool.home() == 200:
			print (time.ctime(),"Modem HTTP is UP","Code:",pool.home())
			if pool.auth() is not False:
				print (time.ctime(),"Authentication token:",config.tokenid)
				print (time.ctime(),"Sesion ID:",config.session)
			 	if pool.signal() is not False:
					print ("-----Signal Statistics:-----")
					print (time.ctime(),"RSRQ:",data.signal_stats.results["rsrq"])
					print (time.ctime(),"RSRP:",data.signal_stats.results["rsrp"])
					print (time.ctime(),"RSSI:",data.signal_stats.results["rssi"])
				else:
					print (time.ctime(),"Unable to get data from modem")
				if pool.traffic_stat() is not False:
					print ("-----Traffic Statistics:-----")
					print (time.ctime(),'Current connection time:{:6.2f}'.format(data.data_stats.results["cur_con_time"]))
					print (time.ctime(),'Total connection time:{:6.2f}'.format(data.data_stats.results["tot_con_time"]))
					print (time.ctime(),'Transmited data:{:6.2f}GB'.format(data.data_stats.results["cur_up"]))
					print (time.ctime(),'Received data:{:6.2f}GB'.format(data.data_stats.results["cur_down"]))
					print (time.ctime(),'Current Download speed:{:6.2f}Mbps'.format(data.data_stats.results["cur_down_speed"]))
					print (time.ctime(),'Current Upload speed:{:6.2f}Mbps'.format(data.data_stats.results["cur_up_speed"]))
					print (time.ctime(),'Total Upload data:{:6.2f}GB'.format(data.data_stats.results["tot_up_data"]))
					print (time.ctime(),'Total Download data:{:6.2f}GB'.format(data.data_stats.results["tot_down_data"]))
				else:
					print (time.ctime(),"Unable to get statisctics from modem")
				if pool.month_traffic_stat() is not False:
					print ("-----Monthly Statistics:-----")
					print (time.ctime(),'This month Download data:{:6.2f}GB'.format(config.month_down_data))
					print (time.ctime(),'This month UPload data:{:6.2f}GB'.format(config.month_up_data))
				else:
					print (time.ctime(),"Unable to get statisctics from modem")
				if pool.dev_info() is not False:
					print ("-----Device Information's:-----")
					print (time.ctime(),'Device name:{}'.format(data.device.info["device_name"]))
					print (time.ctime(),'Serial number:{}'.format(data.device.info["serialnumber"]))
					print (time.ctime(),'Imei:{}'.format(data.device.info["imei"]))
					print (time.ctime(),'Imsi:{}'.format(data.device.info["imsi"]))
					print (time.ctime(),'Iccid:{}'.format(data.device.info["iccid"]))
					print (time.ctime(),'Hardware version:{}'.format(data.device.info["hardwareversion"]))
					print (time.ctime(),'Software version:{}'.format(data.device.info["softwareversion"]))
					print (time.ctime(),'WebUi version :{}'.format(data.device.info["webuiversion"]))
					print (time.ctime(),'Mac address:{}'.format(data.device.info["macaddress1"]))
					print (time.ctime(),'Product family:{}'.format(data.device.info["productfamily"]))
					print (time.ctime(),'Procuct classification:{}'.format(data.device.info["classify"]))
					print (time.ctime(),'Supported mode:{}'.format(data.device.info["supportmode"]))
					print (time.ctime(),'Current working mode:{}'.format(data.device.info["workmode"]))
				else:
					print (time.ctime(),"Unable to get statisctics from modem")
			else:
				print (time.ctime(),"Unauthorised")
		else:
			print (time.ctime(),"Modem HTTP is Down","Code:",pool.home())
	else:
		print ("-----Host Status:-----")
		print (time.ctime(),"Host IP:",config.host,"Down")
	time.sleep(config.poling_interval)
