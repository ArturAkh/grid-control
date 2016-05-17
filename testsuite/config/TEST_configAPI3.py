#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import TestStream, create_config, run_test, write_file
from grid_control.gc_plugin import NamedPlugin

class Task(NamedPlugin):
	tagName = 'tasktag'
	configSections = ['task']

class WMS(NamedPlugin):
	tagName = 'wmstag'
	configSections = ['wms', 'backend']
	def __init__(self, config, name):
		config = config.changeView(setSections = ['global', 'dataset'])
		self._proxy = config.get('proxy', 'defaultproxy')

	def __repr__(self):
		return '%s(%s)' % (self.__class__.__name__, self._proxy)

class Local(WMS):
	configSections = WMS.configSections + ['local']
	def __init__(self, config, name):
		WMS.__init__(self, config, name)

class PBS(Local):
	configSections = Local.configSections + ['mybatch']
	def __init__(self, config, name):
		Local.__init__(self, config, name)

write_file('configfile.conf', """
[global]                       wms = PBS:mypbs

[global]                       proxy = global
[global tasktag:mytag]         proxy = global tasktag:mytag
[dataset]                      proxy = dataset
[dataset invalid]              proxy = dataset invalid
[dataset tasktag:mytag]        proxy = dataset tasktag:mytag
[wms]                          proxy = wms
[wms invalidtag:invalid]       proxy = wms invalidtag:invalid
[wms tasktag:mytag]            proxy = wms tasktag:mytag
[wms tasktag:invalid]          proxy = wms tasktag:invalid
[wms tasktag:datasettask]      proxy = wms tasktag:datasettask
[wms tasktag:mytag tasktag:datasettask] proxy = wms tasktag:mytag tasktag:datasettask
[wms mypbs]                    proxy = wms mypbs
[wms tasktag:mytag mypbs]      proxy = wms mypbs tasktag:mytag
[backend]                      proxy = backend
[backend tasktag:mytag]        proxy = backend tasktag:mytag
[backend mypbs]                proxy = backend mypbs
[backend tasktag:mytag mypbs]  proxy = backend mypbs tasktag:mytag
[local]                        proxy = local
[local tasktag:mytag]          proxy = local tasktag:mytag
[local mypbs]                  proxy = local mypbs
[local tasktag:mytag mypbs]    proxy = local mypbs tasktag:mytag
[mybatch]                      proxy = mybatch
[mybatch tasktag:mytag]        proxy = mybatch tasktag:mytag
[mybatch tasktag:mytask]       proxy = mybatch tasktag:mytask
[mybatch mypbs]                proxy = mybatch mypbs
[mybatch tasktag:mytag mypbs]  proxy = mybatch mypbs tasktag:mytag
""")

class Test_ConfigWMS(object):
	"""
	>>> config = create_config(configFile = 'configfile.conf')
	>>> config = config.changeView(viewClass = 'TaggedConfigView', setSections = ['global'], setTags = [Task(config, 'datasettask')])
	>>> config.getPlugin('wms', cls = WMS)
	PBS(mybatch mypbs)
	>>> config.getPlugin('wms', cls = WMS, tags = [Task(config, 'mytag')])
	PBS(mybatch mypbs tasktag:mytag)
	>>> config = config.changeView(setSections = None)

	>>> config.write(TestStream(), printSource = True) # doctest:+ELLIPSIS
	[backend]
	proxy = backend                    ; .../configfile.conf:16
	-----
	[dataset]
	proxy = dataset                    ; .../configfile.conf:5
	-----
	[global]
	; source: configfile.conf
	plugin paths += ...
	proxy = global                     ; .../configfile.conf:3
	wms = PBS:mypbs                    ; .../configfile.conf:1
	-----
	[global!]
	config id ?= configfile            ; <default>
	; source: <default>
	plugin paths ?= ...
	; source: <default>
	workdir ?= .../work.configfile
	; source: <default>
	workdir base ?= ...
	-----
	[local]
	proxy = local                      ; .../configfile.conf:20
	-----
	[mybatch]
	proxy = mybatch                    ; .../configfile.conf:24
	-----
	[wms]
	proxy = wms                        ; .../configfile.conf:8
	-----
	[wms tasktag:datasettask]
	proxy = wms tasktag:datasettask    ; .../configfile.conf:12
	-----
	[wms tasktag:mytag tasktag:datasettask]
	; source: .../configfile.conf:13
	proxy = wms tasktag:mytag tasktag:datasettask
	-----
	[wms!]
	proxy ?= defaultproxy              ; <default>
	-----
	"""

run_test()
