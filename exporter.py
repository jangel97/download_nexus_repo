#/usr/bin/python

'''
opciones script mejorar y  anadir user con password

ahora estoy con continuation toker

sacar un poco de factor comun

'''

import libxml2
import sys
import urllib
import urllib2
import base64
import json
import os

from optparse import OptionParser
import logging

args_options = OptionParser()

args_options.add_option("-r", "--repository", dest="repository", help="Nexus repository name", default="snapshots")
args_options.add_option("-u", "--user", dest="user", help="user")
args_options.add_option("-p", "--password", dest="password", help="password" )
args_options.add_option("-n", "--url", dest="url", help="nexus url")

(options, args) = args_options.parse_args()

if options.repository is "":
	print "Repositorio??"
	sys.exit(1)


#check if repo exists

urlRepo=options.url+"/service/rest/beta/repositories"
req=urllib2.Request(urlRepo)
base64string = base64.b64encode('%s:%s' % (options.user, options.password))	#anadir opciones user y contra
req.add_header("Authorization", "Basic %s" % base64string)
result = urllib2.urlopen(req)
data = json.load(result)


if filter(lambda x: x==str(options.repository), map(lambda y:y['name'],data ) )==[]:
	print "NO EXISTE EL REPOSITORIO"
	sys.exit(1)

#llegados a este punto ya tengo el repo, asi que ire a ver que hay dentro del repo

urlRepo = options.url+"/service/rest/beta/assets?repository=" + str(options.repository)
req=urllib2.Request(urlRepo)
base64string = base64.b64encode('%s:%s' % (options.user, options.password))   #anadir opciones user y contra
req.add_header("Authorization", "Basic %s" % base64string)
result = urllib2.urlopen(req)
data = json.load(result)

#primero coger el name del folder y crear carpeta

#do-while structure

while True:
	for x in data['items']:	#aqui ya hay asset por asset
		path=x['path'].split('/',100)
		path = path[:-1]
		path = filter(lambda x: x!='-' ,path)	
		fp=os.path.join(str(options.repository) ,* path )
		if not os.path.isdir(fp):
			os.makedirs (fp)	
	#directorios creados, proceder con descarga

		dir="".join(map(lambda x: x+'/',path))	#creo el path a partir de la lista de string
		dir=options.repository +  '/' + dir
		print dir + '\n'
		cwd=os.getcwd()
		os.chdir(str(dir))	#cambiamos al path del asset en cuestion
		os.system('wget --user ' + str(options.user)+ ' --password ' + str(options.password)+' ' + x['downloadUrl'])     #recordar parametrizar
		os.chdir(cwd)
	
	if data['continuationToken'] is None:
		break
	else:
		urlRepo = options.url+"/service/rest/beta/assets?continuationToken=" + data['continuationToken']+ "&repository=" + str(options.repository)
		req=urllib2.Request(urlRepo)
		base64string = base64.b64encode('%s:%s' % (options.user, options.password))   #anadir opciones user y contra
		req.add_header("Authorization", "Basic %s" % base64string)
		result = urllib2.urlopen(req)
		data = json.load(result)

print "REPO: " + options.repository  + " DOWNLOADED"

sys.exit(0)
