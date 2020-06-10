#!/usr/bin/env python3
from queue import Queue
from threading import Thread
from sys import stdin,exit
from bs4 import BeautifulSoup
from optparse import OptionParser
from requests import packages,Session,adapters
q = Queue()
packages.urllib3.disable_warnings()
adapter = adapters.HTTPAdapter(
    pool_connections=100,
    pool_maxsize=100)
optp = OptionParser(add_help_option=False)
optp.add_option("--timeout",dest='timeout',type='int')
optp.add_option("--threads",dest='thr',type='int')
optp.add_option("--redirect",dest='redirect',action="store_true")
optp.add_option("-h","--help",dest='help',action='store_true')
opts, args = optp.parse_args()
helper= (r'''
 , __       _
/|/  \     | |
 |___/  _  | |
 | \   |/  |/_)
 |  \_/|__/| \_/

# Coded By : Khaled Nassar @knassar702

Options:
	-h,--help   | Show help message and exit
	--threads   | Max number of concurrent HTTP(s) requests (default: 10)
	--timeout   | Seconds to wait before timeout connection (default: 4)
    --redirect  | Allow Redirects

Examples:
	$ cat domains.txt | python3 Rek.py
	$ cat domains.txt | python3 Rek.py --timeout=1000
	$ cat domains.txt | python3 Rek.py --threads=60
	$ cat domains.txt | python3 Rek.py --redirect
	$ cat domains.txt | python3 -u Rek.py | tee data.txt
      ''')
if opts.help:
	print(helper)
	sys.exit()
if opts.timeout:
	timeout = opts.timeout
else:
	timeout = 4
if opts.thr:
	thr = opts.thr
else:
	thr = 10
if opts.redirect:
	redirect = True
else:
	redirect = False
def opener(domain,redirect=False,timeout=4):
		try:
			r = Session()
			if domain.startswith('http://'): r.mount('http://', adapter)
			elif domain.startswith('https://'): r.mount('http://', adapter)
			r.verify = False
			r.allow_redirects = False
			r = r.get(f'{domain}',timeout=timeout,verify=False,allow_redirects=redirect)
			try:
				server = f"[{r.headers['Server']}]"
			except:
				server = '[]'
			bs = BeautifulSoup(r.content,'lxml')
			title = bs.title.text
			print(f"{domain} | {r.status_code} | {title} | {server}")
		except:
			pass
def threader():
	while True:
		item = q.get()
		opener(item.rstrip(),redirect=redirect,timeout=timeout)
		q.task_done()

if __name__ == '__main__':
	for i in range(thr):
		p1 = Thread(target=threader)
		p1.daemon = True
		p1.start()
	for domain in stdin:
		q.put(domain)
	try:
		q.join()
	except KeyboardInterrupt:
		exit()
