#!/usr/bin/env python3

import re
import sys
import os
import threading

def rtdir(directory):
	for root, dirs, files in os.walk(directory):
		yield root
		for file in files:
			yield os.path.join(root, file)

def core_exec(path, pattern, dotall, ignore_error):
	if os.path.isdir(path) == True:
		return
	try:
		f = open(path, "r")
		dat = f.read()
		f.close()
		for find in re.finditer(pattern, dat, re.DOTALL if dotall == True else 0):
			print("[" + path + "]:" + str(len(dat[0:find.start()].split("\n"))) + "," + str(len(dat[0:find.start()]) - dat[0:find.start()].rfind("\n") - 1))
	except UnicodeDecodeError as e:
		if ignore_error == False:
			print("[" + path + "] decode error, it might contains binary data")
	except:
		if ignore_error == False:
			print("[" + path + "] unknown error(binary?)")

class Thread(threading.Thread):
	def __init__(self, path, regex, dotall, ignore_error):
		self.path = path
		self.regex = regex
		self.dotall = dotall
		self.ignore_error = ignore_error
		threading.Thread.__init__(self)

	def run(self):
		core_exec(self.path, self.regex, self.dotall, self.ignore_error)

if __name__ == "__main__":
	path = ""
	regex = ""
	dotall = False
	exec_thread = True
	ignore_error = False
	if len(sys.argv) <= 4:
		print("-d directory -r regex [OPTION:--dotall --nothread --ignore_error]")
		sys.exit(0)
	else:
		n = 0
		for arg in sys.argv:
			if arg == "-d":
				path = sys.argv[n + 1]
			if arg == "-r":
				regex = sys.argv[n + 1]
			if arg == "--dotall":
				dotall = True
			if arg == "--nothread":
				exec_thread = False
			if arg == "--ignore_error":
				ignore_error = True
			n = n + 1
	if path == "" or regex == "":
		print("-d directory -r regex [OPTION:--dotall --nothread --ignore_error]")
		sys.exit(0)
	print("result of (" + regex + ") :")
	thread_list = []
	for f in rtdir(path):
		if exec_thread == True:
			thread = Thread(f, regex, dotall, ignore_error)
			thread.start()
			thread_list.append(thread)
		else:
			core_exec(f, regex, dotall, ignore_error)
	if exec_thread == True:
		for t in thread_list:
			t.join()
