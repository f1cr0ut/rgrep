#!/usr/bin/env python3

import re
import sys
import os
import threading

DOTALL = 1
NOTHREAD = 1 << 1
IGNORE_ERROR = 1 << 2
ABSPATH = 1 << 3
PATHONLY = 1 << 4
LINEONLY = 1 << 5
MATCHEDONLY = 1 << 6

def rtdir(directory):
	for root, dirs, files in os.walk(directory):
		yield root
		for file in files:
			yield os.path.join(root, file)

def core_exec(path, pattern, flag):
	if os.path.isdir(path) == True:
		return
	try:
		f = open(path, "r")
		dat = f.read()
		f.close()
		for find in re.finditer(pattern, dat, re.DOTALL if (flag & DOTALL) != 0 else 0):
			s = find.start()
			e = find.end()
			if (flag & PATHONLY) != 0:
				print(path)
			elif (flag & LINEONLY) != 0:
				print(
					str(len(dat[0:s].split("\n"))) + "," + 
					str(len(dat[0:s]) - dat[0:s].rfind("\n"))
				)
			elif (flag & MATCHEDONLY) != 0:
				print(dat[s:e])
			else:
				print(
					path + ":" + 
					str(len(dat[0:s].split("\n"))) + "," + 
					str(len(dat[0:s]) - dat[0:s].rfind("\n")) + ">>>" +
					dat[s:e]
				)
	except UnicodeDecodeError as e:
		if (flag & IGNORE_ERROR) == 0:
			print("[" + path + "] decode error, it might contains binary data")
	except:
		if (flag & IGNORE_ERROR) == 0:
			print("[" + path + "] unknown error(binary?)")

class Thread(threading.Thread):
	def __init__(self, path, regex, flag):
		self.path = path
		self.regex = regex
		self.flag = flag
		threading.Thread.__init__(self)

	def run(self):
		core_exec(self.path, self.regex, self.flag)

def exit_with_usage():
	print("-d directory -r regex [OPTION:--dotall --nothread --ignore_error --abspath --pathonly --lineonly --matchedonly]")
	sys.exit(0)

if __name__ == "__main__":
	path = ""
	regex = ""
	flag = 0
	abs_path = os.path.dirname(os.path.abspath(__file__))
	abs_path = abs_path.replace("\\", "/")
	if len(sys.argv) <= 4:
		exit_with_usage()
	try:
		n = 0
		for arg in sys.argv:
			if arg == "-d":
				path = sys.argv[n + 1]
			if arg == "-r":
				regex = sys.argv[n + 1]
			if arg == "--dotall":
				flag |= DOTALL
			if arg == "--nothread":
				flag |= NOTHREAD
			if arg == "--ignore_error":
				flag |= IGNORE_ERROR
			if arg == "--abspath":
				flag |= ABSPATH
			if arg == "--pathonly":
				flag |= PATHONLY
			if arg == "--lineonly":
				flag |= LINEONLY
			if arg == "--matchedonly":
				flag |= MATCHEDONLY
			n = n + 1
	except:
		exit_with_usage()
	if path == "" or regex == "":
		exit_with_usage()
	path = path.replace("\\", "/")
	path = path.replace("./", "")
	if (flag & ABSPATH) != 0:
		if path[0] == "/":
			path = abs_path + path
		else:
			path = abs_path + "/" + path
	print("result of (" + regex + ") :")
	thread_list = []
	for f in rtdir(path):
		f = f.replace("\\", "/")
		if (flag & NOTHREAD) != 0:
			thread = Thread(f, regex, flag)
			thread.start()
			thread_list.append(thread)
		else:
			core_exec(f, regex, flag)
	if (flag & NOTHREAD) != 0:
		for t in thread_list:
			t.join()
