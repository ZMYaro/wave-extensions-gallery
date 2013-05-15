def parseInt(string,default=None):
	try:
		return int(string)
	except:
		return default
