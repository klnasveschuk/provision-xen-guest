#!/usr/bin/python
###########
# Author: Kent L Nasveschuk
# Date: 03-2015
# Version: 1.0
##########
import sys
import paramiko
from subprocess import Popen, PIPE, STDOUT

PRIVKEY = '/root/.ssh/id_rsa'
NETMASK = '255.255.255.0'
# template ID: IP, template name-label, template UUID, storage UUID, storage name-label
# These are the locations I want to create VMs, VDIs, VDBs
TEMPLATES = {'xen1-1': [ '192.168.1.30','CentOS6_x64_20GB_1024MB','74ed08a6-71a6-8dec-854e-72131f9f5228' ],\
'xen1-2': [ '192.168.1.30','CentOS6_x64_50GB_2048MB_2CPU','c50f354c-393e-c623-d547-f8cbec83930a' ],\
'xen1-3': [ '192.168.1.30','CentOS7_x64_20GB_1024MB','930670e1-2c9b-1530-4e4c-e47d8cb0a103' ],\
'xen1-4': [ '192.168.1.30','CentOS7_x64_50GB_2048MB_2CPU','cca8ff4a-444c-4648-5ff0-81209c94ec92' ],\
'xen1-5': [ '192.168.1.30','Ubuntu14_x64_20GB_1024MB','2644175a-a114-af66-14e6-ebf72414cd98' ],\
'xen1-6': [ '192.168.1.30','Ubuntu14_x64_50GB_2048MB_2CPU','85ca91ec-8bb1-a274-84f9-d555b2eb40bf' ],\
'xen1-7': [ '192.168.1.30','Ubuntu16_x64_20GB_1024MB','1c884a08-c7df-efd6-9512-b27bd9082da9' ],\
'xen1-8': [ '192.168.1.30','Ubuntu16_x64_50GB_2048MB_2CPU','0e4c3f3c-ff08-f995-6e7a-859d540dee4c' ],\
'xen2-1': [ '192.168.1.31','CentOS6_x64_20GB_1024MB','18f4bbb4-96b0-9534-23dd-f13489043a0d' ],\
'xen2-2': [ '192.168.1.31','CentOS6_x64_50GB_2048MB_2CPU','4fccd8a0-a168-90d8-ebb1-28c6033922fb' ],\
'xen2-3': [ '192.168.1.31','CentOS7_x64_20GB_1024MB','8db74efd-0112-12f4-aab3-76509fab91b3' ],\
'xen2-4': [ '192.168.1.31','CentOS7_x64_50GB_2048MB_2CPU','5ec6fd3f-1266-4110-da2a-ac34203ed310' ],\
'xen2-5': [ '192.168.1.31','Ubuntu14_x64_20GB_1024MB','1f263170-c69c-9c3f-5061-cf3cc80e2ac9' ], \
'xen2-6': [ '192.168.1.31','Ubuntu14_x64_50GB_2048MB_2CPU','2a7c8de1-0637-cf6b-6f5c-4ff19ff392f2' ], \
'xen2-7': [ '192.168.1.31','Ubuntu16_x64_20GB_1024MB','3db18851-2fe6-8ec1-abea-92fbcb2ec641' ], \
'xen2-8': [ '192.168.1.31','Ubuntu16_x64_50GB_2048MB_2CPU','967b45b3-218c-5e94-7dd6-b6857eb11452' ]}
# Make
def get_profiles(cmd):
	try:
		plist = {}
		cb = Popen(cmd, shell=True, stdout=PIPE)
		out = cb.stdout.readlines()
		for idx,val in enumerate(out):
			plist[str(idx)] = val.strip()
		return plist
	except:
		sys.exit()

def make_vm(cmd):
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(TEMPLATES[TM][0],username='root',key_filename=PRIVKEY)
	except paramiko.AuthenticationException:
		print "Authentication failed when connecting to %s" % TEMPLATES[TM][1]
		sys.exit(1)
	try:
		stdin, stdout, stderr = ssh.exec_command(cmd)
		if stdout:
			x = stdout.readlines()
			return x
		if not stderr:
			print 'Error: ' + str(stderr.readlines())
		else:
			pass

		ssh.close()
	except:
		print 'Unexpected error: ' + cmd + sys.exc_info()[0]
		raise


# MAIN
# Show Xen templates configured
msg = 'Xen template ID:'
for key,value in TEMPLATES.iteritems():
	msg =  msg + '\n' + key + ' -> ' + value[1]
msg = msg + '\nEnter template ID: '

TM = raw_input(msg)

# Get hostname
msg = 'Enter hostname: '
HOST = raw_input(msg)

# Get/show  profiles available to Cobbler system
plist = get_profiles('/usr/bin/cobbler profile list')

msg = 'Cobbler profile ID:'
for key,val in plist.iteritems():
	msg = msg + '\n' + key + ' -> ' + val
msg = msg + '\nEnter profile ID: '
CB = raw_input(msg)

# Get IP for new system to use
msg = 'Enter new system IP: '
IP = raw_input(msg)
if not IP:
	sys.exit()
msg = 'Info entered: ' + CB + ',' + HOST + ',' + TM + ',' +IP
msg = msg + '\nContinue (yn) :'
yn = raw_input(msg)
if yn != 'y':
	sys.exit()
		
if TM in TEMPLATES.keys():
	cmd = 'xe vm-install new-name-label=' + HOST + ' template=' + TEMPLATES[TM][2]
else:
	sys.exit()

vm_uuid = make_vm(cmd)
cmd = 'xe vm-param-set uuid=' + vm_uuid[0].rstrip() + ' HVM-boot-params:order=ndc'
print 'CH BOOT ORDER: ' + cmd
make_vm(cmd)
print 'VM_UUID: ' + str(vm_uuid[0].rstrip())

cmd = 'xe vif-list vm-uuid=' + str(vm_uuid[0].rstrip()) + ''' |egrep ^uuid|cut -d : -f2|tr -d [:blank:]'''
print 'CREATE VM: ' + cmd
vif_uuid = make_vm(cmd)
if vif_uuid:
	cmd = 'xe vif-param-get uuid=' + vif_uuid[0].rstrip() + ' param-name=MAC'
	print 'GET MAC CMD: ' + cmd
	mac = make_vm(cmd)
	if mac:
		if CB in plist.keys():
			cmd = 'cobbler system add --name=' + HOST + ' --profile=' + plist[CB] + ' --ip-address=' + IP\
 + ' --mac=' + mac[0].strip() + ' --interface=eth0 --static=1 --netmask=' + NETMASK + ' --hostname=' + HOST + ' --gateway=192.168.1.1'
			print cmd
	else:
		print 'No mac returned'
		sys.exit()
else:
	print 'No vif_uuid'
	sys.exit()
try:
	result = Popen(cmd, shell=True, stdout=PIPE)
	out = result.stdout.readlines()
	if out:
		print out
		sys.exit()
	
except:
	sys.exit()
print 'Success'
