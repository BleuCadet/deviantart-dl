#!/usr/bin/python
"""
	BY: BleuCadet
	email: jesset513@gmail.com
	"""

from __future__ import print_function
from urllib import urlopen, urlretrieve
import mechanize
import pickle
import random
import sys
import re
import os

PAGES = []
ARTIST = ""
IMG_BUFF = []
TITLES = []
LOGGED_IN = False

class Page:
	def __init__(self, link=None, search=False):
		global TITLES
		if (search):
			phrase = ""
			while (phrase != '~q'):	
				phrase = raw_input("Search ~q to quit: ")
				try:
					source = "http://"+ARTIST+".deviantart.com/gallery/?catpath=%2F&q=" +\
							 '+'.join(phrase.split())
					print("Searching for:", source)
					gallery = open_page(source)
					if (re.findall("no deviations yet\!", gallery)):
						print("No Results")
						continue
					print("Results Found")
					break
				except:
					print("Bad phrase")
					continue
		else:
			self.__index = int(int(link[link.find('?offset=')+8:])/24)+1
			gallery = open_page(link)
		self.__images = []
		blocks = get_blocks(gallery)
		for block in blocks:
			title = re.findall('title="(.*?) by '+ARTIST, block)[0]
			self.__title = title
			TITLES.append(self.__title)
			self.__images.append( Image(self, self.__title, block) )

	def get_images(self):
		return self.__images
	def get_index(self):
		return self.__index


class Image:
	def __init__(self, page, title, block):
		self.__artist = ARTIST
		self.__page = page
		self.__title = title
		self.__date  = re.findall(ARTIST+', (.*?) in', block)[0]
		self.__mature = False
		self.__gif = False
		found = re.findall('data-super-(?:full-)?img="(.*?)"', block) +\
			  [ re.findall('src="(.*?)"', block)[0] ]
		if (len(found) == 3):
			self.__quality = 3
			self.__link = found[1]
		elif (len(found) == 2):
			self.__quality = 2
			self.__link = found[0]
		elif (len(found) == 1):
			self.__quality = 1
			if ('gif' in found[0]):
				self.__gif = True
		if (re.findall('ismature', block)):
			self.__mature = True
		self.__link = found[0]
		self.__ext = self.__link[len(self.__link)-4:]

	def dl_image(self):
		if (self.__gif) or (self.__mature):
			status = '      ! '
		else:
			status = '\t'
		status += str(self.__quality)+" [.] "
		status += self.__title
		print(status, end='\r')
		mod = 1
		while (self.__title+str(mod)+self.__ext in os.listdir('.')):
			mod += 1
		urlretrieve(self.__link, self.__title.replace('/', '')+str(mod)+self.__ext)
		print(status.replace('.', '+'))

	def get_title(self):
		return self.__title

	def is_mat(self):
		return self.__mature

class NoHistory(object):
	def add(self, *a, **k):
		pass
	def clear(self):
		pass
                
def daSetBrowser():
	useragents= (
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.202 Safari/535.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
    'Opera/9.99 (Windows NT 5.1; U; pl) Presto/9.9.9',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-US) AppleWebKit/530.5 (KHTML, like Gecko) Chrome/ Safari/530.5',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.2 (KHTML, like Gecko) Chrome/6.0',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; pl; rv:1.9.1) Gecko/20090624 Firefox/3.5 (.NET CLR 3.5.30729)'
    )
	global BROWSER
	BROWSER = mechanize.Browser(history=NoHistory())
	BROWSER.set_handle_redirect(True)
	BROWSER.set_handle_robots(False)
	BROWSER.addheaders = [('Referer', 'http://www.deviantart.com/')]
	BROWSER.addheaders = [('User-Agent', random.choice(useragents))]

def daLogin(username,password):
	data = ""
	try:
		BROWSER.open('https://www.deviantart.com/users/login', "ref=http%3A%2F%2Fwww.deviantart.com%2F&remember_me=1")
		BROWSER.select_form(nr=1)
		BROWSER.form['username'] = username
		BROWSER.form['password'] = password
		BROWSER.submit()
		data = BROWSER.response().read()
	except HTTPError, e:
		print("HTTP Error:",e.code)
		sys.exit()
	except URLError, e:
		print("URL Error:",e.reason)
		sys.exit()
	if re.search("The password you entered was incorrect",data):
		print("Wrong password or username. Attempting to download anyway.")
	elif re.search("\"loggedIn\":true",data):
		print("Logged in!")
		global LOGGED_IN
		LOGGED_IN = True
	else:
		print("Login unsuccessful. Attempting to download anyway.")

def startup():
	print("\ngetdeviantart 1.0")
	while True:
		artist = raw_input("Enter artist: ").lower()
		try: 
			source = "http://"+artist+".deviantart.com/gallery/?offset=0"
			gallery = open_page(source)
			artist = re.findall('<title>(.*?)&#', gallery)[0]
			print("Found", artist)
			if (re.findall("no deviations yet\!", gallery)):
				print(artist,"has no art.")
				continue
			try:
				os.mkdir(artist)
			except:
				pass
			os.chdir(artist)
			gallery = open_page(source)
			break
		except:
			print("User not found, try again.")
			continue
	global ARTIST
	ARTIST = artist
	return gallery, source

def count_pages(text, source):
	found = re.findall('(\d+)</a></li><li class="next"', text)[0]
	pages = []
	for i in range(0, int(found)*24, 24):
		pages.append(source[:-1]+str(i))
	return pages

def menu():
	print("\n1) Download all pages\
		   \n2) Select pages\
		   \n3) Select images page by page\
		   \n4) Search for image\
		   \n5) Choose different artist\
		   \n6) Quit")
	choice = 0
	while (choice<1) or (choice>6):
		try:
			choice = int(input("Choice> "))
		except ValueError:
			continue
	return choice		

def execute(choice, all_pages, source):
	global PAGES
	global ARTIST
	global IMG_BUFF
	global TITLES

	if (choice == 1): 
		download(range(1,len(all_pages)+1), source)

	elif (choice == 2): 
		sel_pages = input_vals(pg=True, last=len(all_pages))
		download(sel_pages, source)

	elif (choice == 3):
		sel_pages = input_vals(pg=True, last=len(all_pages))
		download(sel_pages, source, sel_imgs=True)

	elif (choice == 4):
		search()

	elif (choice == 5):
		PAGES = []
		ARTIST = ""
		IMG_BUFF = []
		TITLES = []		

def download(pages, source, sel_imgs=False):
	global PAGES
	page_nums = pages
	source = source[:-1]
	page_links = []
	for var in page_nums:
		page_links.append(source+str((int(var)-1)*24))

	for link in page_links:
		PAGES.append(Page(link))
		page = PAGES[-1]
		print("\nPage #", page.get_index())
		buff_down(page, sel_imgs)

def buff_down(page, sel_imgs):
	global IMG_BUFF
	index = 1
	for image in page.get_images():
		if (sel_imgs):
			if (image.is_mat()):
				s = '      ! '
			else:
				s = '\t'
			print(s+str(index)+')', image.get_title())
			IMG_BUFF.append(image)
			index += 1
		else:
			image.dl_image()
	if (sel_imgs):
		for img in input_vals(img=True, last=len(IMG_BUFF)):
			IMG_BUFF[int(img)-1].dl_image()
	IMG_BUFF = []	


def search():
	page = Page(search=True)
	buff_down(page, True)

def input_vals(pg=False, img=False, last=0):
	output = []
	while True:
		try:
			if (pg):	
				in_vals = raw_input("Pages to get/search (1-3,5,6-8 etc): ")
				in_vals = in_vals.replace(' ', '').split(',')
			elif (img):
				in_vals = raw_input("Images to download (1-3,5,6-8 etc): ")
				in_vals = in_vals.replace(' ', '').split(',')
			for val in in_vals:
				if (val.isdigit()):
						output.append(int(val))
				elif ('-' in val):
					if not((val.replace('-', '').isdigit())):
						raise ValueError
					else:
						left = int(val[:val.find('-')])
						right = int(val[val.find('-')+1:])+1
						if (left > right):
							raise ValueError
						else:	
							output += [int(var) for var in range(left,right)]
				elif (int(val) <= 0):
					raise ValueError
				else:
					raise ValueError

			output = [ int(a) for a in output ]
			if (max(output) > last):
				raise ValueError
			if (output.sort()) != None:
				output = output.sort()
			output = [ str(a) for a in output ]
			return output

		except ValueError:
			print("Bad format, Try again.")
			output = []
			continue

def get_blocks(text):
	return [ re.findall('</smoothie>.*</div>', text)[0] ] \
			+re.findall('</span></small><!-- TTT\$ --></span></div> <div.*', text)

def open_page(url):
	if (LOGGED_IN):
		return BROWSER.open(url).read()
	else:
		return urlopen(url).read().decode("utf-8")

def get_account():
	fil = '.DeVaCtinfo.p'
	choice = ''
	while (choice != 'y') and (choice != 'n'):
		choice = raw_input("Log in? (y/n): ").lower()
	if (choice == 'n'):
		return [None, None, 0]
	choice = ''	
	while (choice != 'y') and (choice != 'n'):
		choice = raw_input("New Account? (y/n): ").lower()
	if (choice == 'y'):
		print("Use throwaway account..")
		uname = raw_input("Enter account username: ")
		passwd = raw_input("Enter account password: ")
		pickle.dump('\n'.join([uname, passwd]), open(fil, 'wb'))
		return [uname, passwd, 0]
	else:
		try:
			uname, passwd = pickle.load(open(fil, 'rb')).split()
			return [uname, passwd, 0]
		except:
			print("Bad account info or no user on file.")
			return [None, None, 1]


def main():
	global PAGES
	global IMG_BUFF
	global TITLES
	choice = 5
	acl = [None, None, 1]
	while (acl[2] != 0):
		acl = get_account()
	if (acl[0] and acl[1]):
		daSetBrowser()
		daLogin(acl[0], acl[1])
	while (choice != 6):
		if (choice == 5):
			gallery, source = startup()
			all_pages = count_pages(gallery, source)
			print(ARTIST, "has", len(all_pages), "pages of art.")
		choice = menu()
		if (choice == 6):
			break
		else:
			execute(choice, all_pages, source)
			PAGES = []
			IMG_BUFF = []
			TITLES = []
	print("Quitting..")

main()