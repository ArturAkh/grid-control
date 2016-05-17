#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), ''))
__import__('testFwk').setup(__file__)
# - prolog marker
import os
from testFwk import create_config, run_test, setPath, try_catch
from grid_control.backends.access import AccessToken, TimedAccessToken

config1 = create_config(configDict={'proxy': {'min lifetime': '0:02:00', 'ignore warnings': 'False'}})
config2 = create_config(configDict={'proxy': {'ignore warnings': 'True'}})

setPath('bin')

class TestTimedProxy(TimedAccessToken):
	def __init__(self, config, tmp):
		TimedAccessToken.__init__(self, config, 'myproxy')
		self.tmp = tmp

	def _getTimeleft(self, cached):
		return self.tmp

class Test_Proxy:
	"""
	>>> proxy1 = AccessToken.createInstance('TrivialProxy', config1, 'myproxy')
	>>> proxy1.getUsername() == os.environ['LOGNAME']
	True
	>>> proxy1.getGroup() == os.environ.get('GROUP', 'None')
	True
	>>> proxy1.getAuthFiles()
	[]
	>>> proxy1.canSubmit(None, None)
	True

	>>> proxy2 = AccessToken.createInstance('VomsProxy', config1, 'myproxy')
	>>> try_catch(lambda: proxy2.canSubmit(100, True), 'AccessTokenError', 'voms-proxy-info failed with return code')
	caught

	>>> proxy2 = AccessToken.createInstance('VomsProxy', config2, 'myproxy')
	>>> proxy2.getUsername()
	'Fred-Markus Stober'
	>>> proxy2.getGroup()
	'cms'
	>>> proxy2.getAuthFiles()
	['/usr/users/stober/.globus/proxy.grid']
	>>> proxy2.canSubmit(100, True)
	True

	>>> proxy3 = TestTimedProxy(config1, 120)
	>>> proxy3.canSubmit(60, True)
	log:Access token (myproxy) lifetime (0h 02min 00sec) does not meet the access and walltime (0h 03min 00sec) requirements!
	log:Disabling job submission
	False

	>>> proxy5 = TestTimedProxy(config1, 240)
	>>> proxy5.canSubmit(60, True)
	True
	"""

run_test()
