import subprocess
'''
Does neccessary checkouts for installer testing
'''

def checkout(repo,loc):
	''' Checkout from repo to loc '''
	try:
		cmd = 'svn co ' + repo + ' ' + loc
		#p = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
		subprocess.Popen(cmd,shell=True).communicate('')
	except Exception,err:
		print 'Error in subprocess '+cmd+': '+str(err)

checkout('https://svn.mantidproject.org/mantid/trunk/Code/Tools/InstallerTesting','InstallerTesting')
checkout('https://svn.mantidproject.org/mantid/trunk/Code/Tools/StressTestFramework','StressTestFramework')
checkout('https://svn.mantidproject.org/mantid/trunk/Test/Data','Data')
checkout('https://svn.mantidproject.org/mantid/Data','Data2')
checkout('https://svn.mantidproject.org/mantid/trunk/Test/SystemTests','SystemTests')
checkout('https://svn.mantidproject.org/mantid/trunk/Test/AutoTestData','AutoTestData')
