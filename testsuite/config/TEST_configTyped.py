#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import create_config, run_test, str_dict, try_catch
from grid_control.config import noDefault
from grid_control.gc_plugin import NamedPlugin
from python_compat import lmap

def getDictDisplay(value):
	if None in value[0]:
		return str_dict(value[0], value[1] + [None])
	return str_dict(value[0], value[1])

def createConfig(value):
	return create_config(configDict = {'TEST': {'key': value}})

class TSBase(NamedPlugin):
	tagName = 'blubb'
	def __init__(self, config, name, msg):
		NamedPlugin.__init__(self, config, name)
		self._msg = msg

	def __repr__(self):
		return '%s(name = %s, msg = %s)' % (self.__class__.__name__, self._name, self._msg)

class TSMulti(TSBase):
	def __init__(self, config, name, cls_list, msg):
		TSBase.__init__(self, config, name, msg)
		self._cls_list = cls_list

	def __repr__(self):
		return '%s(name = %s, msg = %s, %r)' % (self.__class__.__name__, self._name, self._msg, self._cls_list)

class TSChild(TSBase):
	pass

class TSChild1(TSBase):
	pass

class TSChildA(TSChild1):
	pass

class Test_ConfigBase:
	r"""
	>>> config = createConfig('value')
	>>> config.get('key', 'default')
	'value'
	>>> config.get('key_def', 'default')
	'default'
	>>> config.set('key_set', 'eulav') is not None
	True
	>>> config.get('key_set', 'fail')
	'eulav'

	== getInt ==
	>>> createConfig('1').getInt('key', 0)
	1
	>>> createConfig('+1').getInt('key', 0)
	1
	>>> createConfig('-1').getInt('key', 0)
	-1
	>>> try_catch(lambda: createConfig('0').getInt('key_def', None), 'APIError', 'Unable to get string representation of default object: None')
	caught
	>>> try_catch(lambda: createConfig('').getInt('key', 0), 'ConfigError', 'Unable to parse int')
	caught

	== getBool ==
	>>> createConfig('1').getBool('key', False)
	True
	>>> createConfig('true').getBool('key', False)
	True
	>>> createConfig('0').getBool('key', True)
	False
	>>> createConfig('false').getBool('key', True)
	False
	>>> createConfig('false').getBool('key_def1', True)
	True
	>>> createConfig('false').getBool('key_def2', False)
	False
	>>> try_catch(lambda: createConfig('false').getBool('key_def3', None), 'APIError', 'Unable to get string representation of default object')
	caught
	>>> try_catch(lambda: createConfig('').getBool('key', False), 'ConfigError', 'Unable to parse bool')
	caught

	== getTime ==
	>>> createConfig('1').getTime('key', 0)
	3600
	>>> createConfig('1:01').getTime('key', 0)
	3660
	>>> createConfig('1:01:01').getTime('key', 0)
	3661
	>>> createConfig('').getTime('key', 0)
	-1
	>>> createConfig('').getTime('key', -1)
	-1
	>>> createConfig('').getTime('key', -100)
	-1
	>>> createConfig('').getTime('key_def', 0)
	0
	>>> createConfig('').getTime('key_def', -1)
	-1
	>>> createConfig('').getTime('key_def', -100)
	-1
	>>> createConfig('false').getTime('key_def', None)
	-1
	>>> try_catch(lambda: createConfig('abc').getTime('key', False), 'ConfigError', 'Unable to parse time')
	caught

	== getList ==
	>>> createConfig('').getList('key', ['X'])
	[]
	>>> createConfig('123').getList('key', ['X'])
	['123']
	>>> createConfig('1 2 3').getList('key', ['X'])
	['1', '2', '3']
	>>> createConfig('').getList('key_def', [])
	[]
	>>> createConfig('').getList('key_def', ['1'])
	['1']
	>>> createConfig('').getList('key_def', [1, 2])
	['1', '2']
	>>> try_catch(lambda: createConfig('false').getList('key_def', None), 'APIError', 'Unable to get string representation of default object')
	caught

	== getDict ==
	>>> getDictDisplay(createConfig('default').getDict('key', {'K': 'V'}))
	"{None: 'default'}"
	>>> getDictDisplay(createConfig('A => 1').getDict('key', {'K': 'V'}))
	"{'A': '1'}"
	>>> getDictDisplay(createConfig('A => 1\nB => 2').getDict('key', {'K': 'V'}))
	"{'A': '1', 'B': '2'}"
	>>> getDictDisplay(createConfig('A => 1\nB => 2').getDict('key', {'K': 5}, parser = int))
	"{'A': 1, 'B': 2}"
	>>> getDictDisplay(createConfig('=> 1\nB => 2').getDict('key', {'K': 'V'}))
	"{'B': '2', None: '1'}"
	>>> getDictDisplay(createConfig('=> 1B => 2').getDict('key', {'K': 'V'}))
	"{None: '1B => 2'}"
	>>> getDictDisplay(createConfig('default\nA => 1\nB => 2').getDict('key', {'K': 'V'}))
	"{'A': '1', 'B': '2', None: 'default'}"
	>>> getDictDisplay(createConfig('A => 1\nB => 2\ndefault').getDict('key', {'K': 'V'}))
	"{'A': '1', 'B': '2\\ndefault'}"
	>>> getDictDisplay(createConfig('').getDict('key_def', {'K': 'V'}))
	"{'K': 'V'}"
	>>> getDictDisplay(createConfig('').getDict('key_def', {}))
	'{}'
	>>> try_catch(lambda: getDictDisplay(createConfig('false').getDict('key_def', None)), 'APIError', 'Unable to convert default object: None')
	caught

	== getPath ==
	>>> showPath = lambda x: str.join('/', x.split('/')[-2:])
	>>> showPath(createConfig('test.conf').getPath('key', 'def'))
	'config/test.conf'
	>>> showPath(createConfig('test.conf').getPath('key', 'def', mustExist = False))
	'config/test.conf'
	>>> try_catch(lambda: showPath(createConfig('file').getPath('key', 'def')), 'ConfigError', 'Unable to parse path')
	caught
	>>> showPath(createConfig('file').getPath('key', 'def', mustExist = False))
	'file'
	>>> showPath(createConfig('').getPath('key', 'def'))
	''
	>>> showPath(createConfig('').getPath('key', 'def', mustExist = False))
	''
	>>> showPath(createConfig('').getPath('key_def', ''))
	''
	>>> showPath(createConfig('').getPath('key_def', '', mustExist = False))
	''
	>>> try_catch(lambda: showPath(createConfig('').getPath('key_def', 'def')), 'ConfigError', 'Unable to parse path')
	caught
	>>> showPath(createConfig('').getPath('key_def', 'def', mustExist = False))
	'def'
	>>> showPath(createConfig('').getPath('key_def', 'test.conf'))
	'config/test.conf'
	>>> showPath(createConfig('').getPath('key_def', 'test.conf', mustExist = False))
	'config/test.conf'
	>>> try_catch(lambda: showPath(createConfig('false').getPath('key_def', None)), 'APIError', 'Unable to get string representation of default object: None')
	caught

	== getPaths ==
	>>> lmap(showPath, createConfig('test.conf\ninc.conf').getPaths('key', ['def']))
	['config/test.conf', 'config/inc.conf']
	>>> lmap(showPath, createConfig('test.conf\ninc.conf').getPaths('key', ['def'], mustExist = False))
	['config/test.conf', 'config/inc.conf']
	>>> try_catch(lambda: lmap(showPath, createConfig('test.conf\nincx.conf').getPaths('key', ['def'])), 'ConfigError', 'Unable to parse paths')
	caught
	>>> lmap(showPath, createConfig('test.conf\nincx.conf').getPaths('key', ['def'], mustExist = False))
	['config/test.conf', 'incx.conf']
	>>> lmap(showPath, createConfig('').getPaths('key', ['def']))
	[]
	>>> lmap(showPath, createConfig('').getPaths('key', ['def'], mustExist = False))
	[]
	>>> try_catch(lambda: lmap(showPath, createConfig('').getPaths('key_def', ['def'])), 'ConfigError', 'Unable to parse paths')
	caught
	>>> lmap(showPath, createConfig('').getPaths('key_def', ['def'], mustExist = False))
	['def']

	== getPlugin ==
	>>> createConfig('TSChild').getPlugin('key', noDefault, cls = TSBase, pargs = ('Hello World',))
	TSChild(name = TSChild, msg = Hello World)
	>>> createConfig('TSChild1').getPlugin('key', noDefault, cls = TSBase, pargs = ('Hello World',))
	TSChild1(name = TSChild1, msg = Hello World)
	>>> createConfig('TSChildA').getPlugin('key', noDefault, cls = TSBase, pargs = ('Hello World',))
	TSChildA(name = TSChildA, msg = Hello World)
	>>> createConfig('TSChildA:Testobject').getPlugin('key', noDefault, cls = TSBase, pargs = ('Hello World',))
	TSChildA(name = Testobject, msg = Hello World)
	>>> createConfig('').getPlugin('key_def', 'TSChild', cls = TSBase, pargs = ('Hello World',))
	TSChild(name = TSChild, msg = Hello World)
	>>> createConfig('').getPlugin('key', requirePlugin = False, cls = TSBase, pargs = ('Hello World',)) is None
	True

	== getCompositePlugin ==
	>>> createConfig('TSChild').getCompositePlugin('key', noDefault, cls = TSBase, pargs = ('Hello World',))
	TSChild(name = TSChild, msg = Hello World)
	>>> createConfig('TSChildA').getCompositePlugin('key', noDefault, cls = TSBase, pargs = ('Hello World',))
	TSChildA(name = TSChildA, msg = Hello World)
	>>> createConfig('TSChildA:Testobject').getCompositePlugin('key', noDefault, cls = TSBase, pargs = ('Hello World',))
	TSChildA(name = Testobject, msg = Hello World)
	>>> createConfig('TSChildA:Testobject TSChild1').getCompositePlugin('key', noDefault, cls = TSBase, default_compositor = 'TSMulti', pargs = ('Hello World',))
	TSMulti(name = TSMulti, msg = Hello World, [TSChildA(name = Testobject, msg = Hello World), TSChild1(name = TSChild1, msg = Hello World)])
	>>> createConfig('').getCompositePlugin('key_def', 'TSChild TSChild1:HEY TSChildA', cls = TSBase, default_compositor = 'TSMulti', pargs = ('Hello World',))
	TSMulti(name = TSMulti, msg = Hello World, [TSChild(name = TSChild, msg = Hello World), TSChild1(name = HEY, msg = Hello World), TSChildA(name = TSChildA, msg = Hello World)])
	"""

run_test()
