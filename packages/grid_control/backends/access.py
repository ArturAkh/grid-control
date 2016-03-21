#-#  Copyright 2007-2016 Karlsruhe Institute of Technology
#-#
#-#  Licensed under the Apache License, Version 2.0 (the "License");
#-#  you may not use this file except in compliance with the License.
#-#  You may obtain a copy of the License at
#-#
#-#      http://www.apache.org/licenses/LICENSE-2.0
#-#
#-#  Unless required by applicable law or agreed to in writing, software
#-#  distributed under the License is distributed on an "AS IS" BASIS,
#-#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#-#  See the License for the specific language governing permissions and
#-#  limitations under the License.

# Generic base class for authentication proxies GCSCF:

import time, logging
from grid_control import utils
from grid_control.gc_exceptions import UserError
from grid_control.utils.file_objects import VirtualFile
from hpfwk import AbstractError, NamedPlugin, NestedException
from python_compat import rsplit

class AccessTokenError(NestedException):
	pass

class AccessToken(NamedPlugin):
	configSections = NamedPlugin.configSections + ['proxy', 'access']
	tagName = 'access'
	def __init__(self, config, name, oslayer):
		NamedPlugin.__init__(self, config, name)
		self._oslayer = oslayer

	def getUsername(self):
		raise AbstractError

	def getFQUsername(self):
		return self.getUsername()

	def getGroup(self):
		raise AbstractError

	def getAuthFiles(self):
		raise AbstractError

	def canSubmit(self, neededTime, canCurrentlySubmit):
		raise AbstractError


class MultiAccessToken(AccessToken):
	def __init__(self, config, name, oslayer, subtokenBuilder):
		AccessToken.__init__(self, config, name, oslayer)
		self._subtokenList = map(lambda tbuilder: tbuilder.getInstance(), subtokenBuilder)

	def getUsername(self):
		return self._subtokenList[0].getUsername()

	def getFQUsername(self):
		return self._subtokenList[0].getFQUsername()

	def getGroup(self):
		return self._subtokenList[0].getGroup()

	def getAuthFiles(self):
		return self._subtokenList[0].getAuthFiles()

	def canSubmit(self, neededTime, canCurrentlySubmit):
		for subtoken in self._subtokenList:
			canCurrentlySubmit = canCurrentlySubmit and subtoken.canSubmit(neededTime, canCurrentlySubmit)
		return canCurrentlySubmit


class TrivialAccessToken(AccessToken):
	alias = ['TrivialProxy']

	def getUsername(self):
		for var in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
			result = self._oslayer.environ.get(var)
			if result:
				return result
		raise AccessTokenError('Unable to determine username!')

	def getGroup(self):
		return self._oslayer.environ.get('GROUP', 'None')

	def getAuthFiles(self):
		return []

	def canSubmit(self, neededTime, canCurrentlySubmit):
		return True


class TimedAccessToken(AccessToken):
	def __init__(self, config, name, oslayer):
		AccessToken.__init__(self, config, name, oslayer)
		self._lowerLimit = config.getTime('min lifetime', 300, onChange = None)
		self._maxQueryTime = config.getTime('max query time',  5 * 60, onChange = None)
		self._minQueryTime = config.getTime('min query time', 30 * 60, onChange = None)
		self._ignoreTime = config.getBool('ignore walltime', False, onChange = None)
		self._lastUpdate = 0
		self._logUser = logging.getLogger('user.time')

	def canSubmit(self, neededTime, canCurrentlySubmit):
		if not self._checkTimeleft(self._lowerLimit):
			raise UserError('Your access token (%s) only has %d seconds left! (Required are %s)' %
				(self.getObjectName(), self._getTimeleft(cached = True), utils.strTime(self._lowerLimit)))
		if self._ignoreTime:
			return True
		if not self._checkTimeleft(self._lowerLimit + neededTime) and canCurrentlySubmit:
			self._logUser.warning('Access token (%s) lifetime (%s) does not meet the access and walltime (%s) requirements!' %
				(self.getObjectName(), utils.strTime(self._getTimeleft(cached = False)), utils.strTime(self._lowerLimit + neededTime)))
			self._logUser.warning('Disabling job submission')
			return False
		return True

	def _getTimeleft(self, cached):
		raise AbstractError

	def _checkTimeleft(self, neededTime): # check for time left
		delta = time.time() - self._lastUpdate
		timeleft = max(0, self._getTimeleft(cached = True) - delta)
		# recheck token => after > 30min have passed or when time is running out (max every 5 minutes)
		if (delta > self._minQueryTime) or (timeleft < neededTime and delta > self._maxQueryTime):
			self._lastUpdate = time.time()
			timeleft = self._getTimeleft(cached = False)
			verbosity = utils.QM(timeleft < neededTime, -1, 0)
			self._logUser.info('Time left for access token "%s": %s' % (self.getObjectName(), utils.strTime(timeleft)))
		return timeleft >= neededTime


class VomsProxy(TimedAccessToken):
	def __init__(self, config, name, oslayer):
		TimedAccessToken.__init__(self, config, name, oslayer)
		self._infoExec = oslayer.findExecutable('voms-proxy-info')
		self._ignoreWarning = config.getBool('ignore warnings', False, onChange = None)
		self._cache = None

	def getUsername(self):
		return self._getProxyInfo('identity').split('CN=')[1].strip()

	def getFQUsername(self):
		return self._getProxyInfo('identity')

	def getGroup(self):
		return self._getProxyInfo('vo')

	def getAuthFiles(self):
		return [self._getProxyInfo('path')]

	def _getTimeleft(self, cached):
		return self._getProxyInfo('timeleft', utils.parseTime, cached)

	def _parseProxy(self, cached = True):
		# Return cached results if requested
		if cached and self._cache:
			return self._cache
		# Call voms-proxy-info and parse results
		(retCode, stdout, stderr) = self._oslayer.call(self._infoExec, '--all').finish(None)
		if (retCode != 0) and not self._ignoreWarning:
			msg = ('voms-proxy-info output:\n%s\n%s\n' % (stdout, stderr)).replace('\n\n', '\n')
			msg += 'If job submission is still possible, you can set [access] ignore warnings = True\n'
			raise AccessTokenError(msg + 'voms-proxy-info failed with return code %d' % retCode)
		self._cache = utils.DictFormat(':').parse(stdout)
		return self._cache

	def _getProxyInfo(self, key, parse = lambda x: x, cached = True):
		info = self._parseProxy(cached)
		try:
			return parse(info[key])
		except Exception:
			raise AccessTokenError("Can't access %s in proxy information:\n%s" % (key, info))


class RefreshableAccessToken(TimedAccessToken):
	def __init__(self, config, name, oslayer):
		TimedAccessToken.__init__(self, config, name, oslayer)
		self._refresh = config.getTime('access refresh', 60*60, onChange = None)

	def _refreshAccessToken(self):
		raise AbstractError

	def _checkTimeleft(self, neededTime): # check for time left
		if self._getTimeleft(True) < self._refresh:
			self._refreshAccessToken()
			self._getTimeleft(False)
		return TimedAccessToken._checkTimeleft(self, neededTime)


class AFSAccessToken(RefreshableAccessToken):
	alias = ['AFSProxy']

	def __init__(self, config, name, oslayer):
		assert(oslayer._standalone) # FIXME: Setting up environment for future calls is not yet supported!
		RefreshableAccessToken.__init__(self, config, name, oslayer)
		execDict = oslayer.findExecutables(['kinit', 'klist'], first = True)
		self._kinitExec = execDict['kinit']
		self._klistExec = execDict['klist']
		self._cache = None
		self._authFiles = dict(map(lambda name: (name, config.getWorkPath('proxy.%s' % name)), ['KRB5CCNAME', 'KRBTKFILE']))
		self._backupTickets(config)
		self._tickets = config.getList('tickets', [], onChange = None)

	def _backupTickets(self, config):
		import os, stat
		assert(self._oslayer.standalone) # FIXME: Setting up environment for future calls is not yet supported!
		for name in self._authFiles: # store kerberos files in work directory for persistency
			if name in os.environ:
				fn = os.environ[name].replace('FILE:', '')
				if fn != self._authFiles[name]:
					self._oslayer.writeFile(self._authFiles[name], VirtualFile(name, self._oslayer.readFile(fn)))
				os.chmod(self._authFiles[name], stat.S_IRUSR | stat.S_IWUSR)
				os.environ[name] = self._authFiles[name]

	def _refreshAccessToken(self):
		return self._oslayer.call(self._kinitExec, '-R').finish(None)

	def _parseTickets(self, cached = True):
		# Return cached results if requested
		if cached and self._cache:
			return self._cache
		# Call klist and parse results
		self._cache = {}
		try:
			for line in self._oslayer.call(self._klistExec).iter_stdout(None):
				if line.count('@') and (line.count(':') > 1):
					issued_expires, principal = rsplit(line, '  ', 1)
					issued_expires = issued_expires.replace('/', ' ').split()
					assert(len(issued_expires) % 2 == 0)
					issued_str = str.join(' ', issued_expires[:len(issued_expires) / 2])
					expires_str = str.join(' ', issued_expires[len(issued_expires) / 2:])
					parseDate = lambda value, format: time.mktime(time.strptime(value, format))
					if expires_str.count(' ') == 3:
						if len(expires_str.split()[2]) == 2:
							expires = parseDate(expires_str, '%m %d %y %H:%M:%S')
						else:
							expires = parseDate(expires_str, '%m %d %Y %H:%M:%S')
					elif expires_str.count(' ') == 2: # year information is missing
						currentYear = int(time.strftime('%Y'))
						expires = parseDate(expires_str + ' %d' % currentYear, '%b %d %H:%M:%S %Y')
						issued = parseDate(issued_str + ' %d' % currentYear, '%b %d %H:%M:%S %Y')
						if expires < issued: # wraparound at new year
							expires = parseDate(expires_str + ' %d' % (currentYear + 1), '%b %d %H:%M:%S %Y')
					self._cache.setdefault('tickets', {})[principal] = expires
				elif line.count(':') == 1:
					key, value = map(str.strip, line.split(':', 1))
					self._cache[key.lower()] = value
		except:
			raise AccessTokenError('Unable to parse kerberos ticket information!')
		return self._cache

	def _getTimeleft(self, cached):
		info = self._parseTickets(cached)['tickets']
		time_current = time.time()
		time_end = time_current
		for ticket in info:
			if (self._tickets and (ticket not in self._tickets)) or not ticket:
				continue
			time_end = max(info[ticket], time_end)
		return time_end - time_current

	def _getPrincipal(self):
		info = self._parseTickets()
		return info.get('default principal', info.get('principal'))

	def getUsername(self):
		return self._getPrincipal().split('@')[0]

	def getFQUsername(self):
		return self._getPrincipal()

	def getGroup(self):
		return self._getPrincipal().split('@')[1]

	def getAuthFiles(self):
		return self._authFiles.values()
