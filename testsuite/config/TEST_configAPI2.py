#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import TestStream, create_config, run_test, write_file
from grid_control.gc_plugin import NamedPlugin
from python_compat import imap

class MyTask(NamedPlugin):
	tagName = 'tasktag'
	configSections = ['task']

class MyWMS(NamedPlugin):
	configSections = ['wms', 'backend']
	tagName = 'wmstag'
	def __init__(self, config, name):
		self._proxy = config.get('proxy', 'defaultproxy')
		self._input = config.get('input', 'defaultinput')

	def __repr__(self):
		return '%s(%r, %r)' % (self.__class__.__name__, self._proxy.replace('\n', ' '), self._input.replace('\n', ' '))

class MyMultiWMS(MyWMS):
	def __init__(self, config, name, cls_list):
		MyWMS.__init__(self, config, name)
		self._cls_list = cls_list

	def __repr__(self):
		return MyWMS.__repr__(self) + '\n - ' + str.join('\n - ', imap(repr, self._cls_list))

class MyLocal(MyWMS):
	configSections = MyWMS.configSections + ['local']
	def __init__(self, config, name):
		config.set('proxy', 'localproxy', '=')
		config.set('input', 'localinput', '+=')
		MyWMS.__init__(self, config, name)

class MyPBS(MyLocal):
	configSections = MyLocal.configSections + ['mybatch']
	def __init__(self, config, name):
		config.set('proxy', 'pbsproxy', '=')
		config.set('input', 'pbsinput', '+=')
		MyLocal.__init__(self, config, name)

class MyGrid(MyWMS):
	configSections = MyWMS.configSections + ['grid']
	def __init__(self, config, name):
		config.set('proxy', 'gridproxy', '=')
		MyWMS.__init__(self, config, name)

write_file('configfile.conf', """
[global]  wms = MyPBS:mypbs MyGrid:mygrid MyLocal:mylocal
[wms]     proxy += user_wms
[local]   proxy += user_local
[pbs]     proxy += user_pbs
[mybatch] proxy += user_mybatch
[grid]    proxy += user_grid
""")

class Test_PluginDefaults(object):
	"""
	>>> config = create_config(configFile = 'configfile.conf')
	>>> config.getCompositePlugin('wms', cls = MyWMS, default_compositor = 'MyMultiWMS', tags = [MyTask(config, 'mytask')])
	MyMultiWMS('defaultproxy user_wms', 'defaultinput')
	 - MyPBS('pbsproxy user_wms user_local user_mybatch', 'defaultinput localinput pbsinput')
	 - MyGrid('gridproxy user_wms user_grid', 'defaultinput')
	 - MyLocal('localproxy user_wms user_local', 'defaultinput localinput')
	>>> config.write(TestStream(), printSource = True) # doctest:+ELLIPSIS
	[global]
	; source: configfile.conf
	plugin paths += ...
	wms =                              ; .../configfile.conf:1
	...MyPBS:mypbs
	...MyGrid:mygrid
	...MyLocal:mylocal
	-----
	[global!]
	config id ?= configfile            ; <default>
	; source: <default>
	plugin paths ?= ...
	wms manager ?= MyMultiWMS          ; <default>
	; source: <default>
	workdir ?= .../work.configfile
	; source: <default>
	workdir base ?= ...
	-----
	[grid]
	proxy += user_grid                 ; .../configfile.conf:6
	-----
	[grid mygrid tasktag:mytask!]
	proxy = gridproxy                  ; <string by mygrid::__init__>
	-----
	[local]
	proxy += user_local                ; .../configfile.conf:3
	-----
	[local mylocal tasktag:mytask!]
	input += localinput                ; <string by mylocal::__init__>
	proxy = localproxy                 ; <string by mylocal::__init__>
	-----
	[mybatch]
	proxy += user_mybatch              ; .../configfile.conf:5
	-----
	[mybatch mypbs tasktag:mytask!]
	input += pbsinput                  ; <string by mypbs::__init__>
	input += localinput                ; <string by mypbs::__init__>
	proxy = pbsproxy                   ; <string by mypbs::__init__>
	proxy = localproxy                 ; <string by mypbs::__init__>
	-----
	[pbs]
	proxy += user_pbs                  ; .../configfile.conf:4
	-----
	[wms]
	proxy += user_wms                  ; .../configfile.conf:2
	-----
	[wms!]
	input ?= defaultinput              ; <default>
	proxy ?= defaultproxy              ; <default>
	-----
	"""

def test():
	config = create_config(configFile = 'configfile.conf')
	wms = config.getCompositePlugin('wms', cls = MyWMS, default_compositor = 'MyMultiWMS', tags = [MyTask(config, 'mytask')])
	config.write(TestStream(), printSource = True)

run_test()
