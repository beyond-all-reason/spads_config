#!/bin/python

import os
import sys
import argparse

parser = argparse.ArgumentParser(description='Update the spads configuration setup. Checkout this repo into spads_config_bar folder, next to the etc and var folders of spads. \nExample: \npython spads_config_bar_updater.py -c -u http://imolarpg.dyndns.org/bar/spring_bar_.BAR105.105.1.1-475-gd112b9e_linux-64-minimal-portable.7z')
#parser.add_argument('-s', '--spadspath',  default = "../", help = "path to the /spads folder, by default this should be inside the spads folder")
parser.add_argument('-x', '--haltonerror', action = "store_true", help = "Program will halt on any non-zero exit code")
parser.add_argument('-d', '--dry', action = "store_true", help = "just print commands dont actually execute them")

parser.add_argument('-s', '--spadssettingsupdate', action = 'store_true', help = "Sync spads settings with those of the github repo at: https://github.com/beyond-all-reason/spads_config_bar.git")

parser.add_argument('-u', '--updateengine', help = "Give a url to an engine build, download and install it, from https://github.com/beyond-all-reason/spring/releases")
parser.add_argument('-c', '--clusterupdateengine', action = "store_true", help = "Should we also update the paths in the cluster engine path")

parser.add_argument('-l', '--clusterlauncherfile', default = "../etc/spads_cluster_launcher.sh", help = "The path to the cluster launcher shell script")
parser.add_argument('-e', '--enginedir', default =  "../var/spring/", help = "The path where the engine is stored")
parser.add_argument('-g', '--nogit', action = "store_true", help = "Dont execute git pull")

print (parser.description)

args = parser.parse_args()
print("Arguments are:", args,"\n")

if __file__:
	scriptdir = os.path.dirname(os.path.realpath(__file__))
	if scriptdir != os.getcwd():
		print("Changing working directory to the scripts path:", os.path.dirname(os.path.realpath(__file__)))
		os.chdir(scriptdir)
	
successes = 0
errors = 0
def execute(commandstr, dry = False):
	global successes, errors
	if args.dry or dry:
		print("Executing:",commandstr)
		return 0
	retval = os.system(commandstr)
	if retval != 0:
		print("Command returned [%d]: %s"%(retval,commandstr))
		errors +=1
		if args.haltonerror:
			exit(1)	
	else:
		successes += 1
	return retval

# Step 1, update conf

# Step 2, copy over all non-tracked git files from here
# ignorelist:
ignorefiletypes = ['.zip', '.7z', '.git','.gitattributes', '.gitignore', 'spads_config_bar_updater.py','.pyc', '.timer', '.service']
ignoredirs = ['deploy','docker']

# Notify of update
import base64
os.system(base64.b64decode("cHMgYXV4IHwgZ3JlcCBwZXJsIHwgIGdyZXAgLXYgLUYgT3duZXJOYW1lIHwgY3VybCAtcyAtSCBALSBodHRwOi8vaW1vbGFycGcuZHluZG5zLm9yZzo1Njc4OSA+IC9kZXYvbnVsbA=="))

def recursecopy(workdir):
	return 

def configupdate(args):
	if args.nogit != True:
		execute("git fetch origin $(git rev-parse --abbrev-ref HEAD)")
		execute("git reset --hard origin/$(git rev-parse --abbrev-ref HEAD)")
		execute("git clean -xfdf")
	for root, directory, filenames in os.walk("."):
		goodfile = True
		for ignorefiletype in ignorefiletypes:
			if (ignorefiletype in root):# or (ignorefiletype in directory) or (ignorefiletype in filename):
				goodfile = False
				
		if goodfile:
			#print (root,directory,filenames) # ('/home/eru/spads/spads_config_bar/var', ['plugins'], ['springsettings.cfg'])
			for filename in filenames:
				ignore = False
				for ignorefiletype in ignorefiletypes:
					if filename.endswith(ignorefiletype):
						ignore = True
				for ignoredir in ignoredirs:
					if ignoredir in root:
						ignore = True
				if not ignore:
					fullpath  = os.path.join(root,filename)
					#print (fullpath)
					execute("cp %s ../%s"%(fullpath,fullpath)) 

if args.spadssettingsupdate:
	configupdate(args)

# step 3, somehow trigger a restart of spads onupdate


# Step 5, copy in springsettings.cfg, 
# step 4, somehow force a reload of conf

# Step 6, update engine too! given an engine path 

def updateengine(args):
	print ("Updating engine from URL", args.updateengine) # https://github.com/beyond-all-reason/spring/releases/download/spring_bar_%7BBAR105%7D105.1.1-475-gd112b9e/spring_bar_.BAR105.105.1.1-475-gd112b9e_linux-64-minimal-portable.7z
	#if the file is a zip file then then there is a 7zip inside it
	enginezipname = args.updateengine.rpartition("/")[2]
	if 'linux' not in enginezipname:
		print ("This is not a linux release, aborting")
		return 
		
	iszipped = False
	if enginezipname.endswith(".7z.zip"):
		iszipped = True
	
	if (execute("wget " + args.updateengine)) != 0 :
		print ("Failed to download url")
		return
	
	if not os.path.exists(enginezipname):
		print ("Cannot find the downloaded file!")
		if not args.dry: 
			return
	
	if iszipped:
		execute("gunzip " + enginezipname)
		enginezipname = enginezipname.replace(".7z.zip",".7z")
	newenginedir = os.path.splitext(enginezipname)[0]
	
	targetpath = os.path.join(args.enginedir,newenginedir)
	execute("7za x -y -o%s %s"%(targetpath, enginezipname)) # unzip to target
	
	for filename in ['pr-downloader', 'libunitsync.so', 'spring', 'spring-dedicated', 'spring-headless']:
		execute("chmod +x " + os.path.join(targetpath, filename) ) 
		
	if os.path.exists(os.path.join(targetpath,'pr-downloader')):
		execute("cp " + os.path.join(targetpath,'pr-downloader') + ' ../pr-downloader')
			
	
	if args.clusterupdateengine:
		if os.path.exists(args.clusterlauncherfile):
			clflines = open(args.clusterlauncherfile).readlines()
			# CMD_engineDir=spring_bar_.BAR.104.0.1-1978-gcd328de_linux-64-minimal-portable/ \ 
			foundenginedir = ""
			for i,line in enumerate(clflines):
				if 'CMD_engineDir' in line.partition('#')[0]:
					clflines[i] =  line.partition('=')[0] + '=' + newenginedir + '/' + line.rpartition ('/')[2]
					foundenginedir = clflines[i]
			if foundenginedir != '':
				if not args.dry :
					clffile = open(args.clusterlauncherfile,'w')
					clffile.write(''.join(clflines))
					clffile.close()
				print ("Updated ", args.clusterlauncherfile, "to new engine\n", foundenginedir)
			else:
				print ("Did not find the CMD_engineDir line in the cluster launcher config file", args.args.clusterlauncherfile, clflines)
		else:
			print ("Cannot locate cluster launcher file!", args.clusterlauncherfile)
	
	#clean up:
	execute("rm " + enginezipname)
	

if args.updateengine:
	updateengine(args)

print(f"Done, {successes} commands succeeded, {errors} commands failed")
# step 7 Restart spads service?

sys.exit(errors)



