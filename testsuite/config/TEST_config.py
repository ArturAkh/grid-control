#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
import os
from testFwk import TestStream, create_config, run_test, try_catch

default_cfg = os.path.abspath('test_default.conf')
assert(os.path.exists(default_cfg))
os.environ['GC_CONFIG'] = default_cfg

class Test_Config:
	"""
	>>> try_catch(lambda: create_config('FAIL.conf', useDefaultFiles = False), 'ConfigError', 'Could not find file')
	caught
	>>> try_catch(lambda: create_config('FAIL1.conf', useDefaultFiles = False), 'ConfigError', 'Unable to interpolate')
	caught

	>>> config = create_config(useDefaultFiles = False)
	>>> config.getConfigName()
	'unnamed'

	>>> config = create_config('test.conf', {'dict': {'test': 'works'}}, useDefaultFiles = True)
	>>> config.getConfigName()
	'test'

	>>> config.get('key', 'default_key')
	'value'
	>>> try_catch(lambda: config.get('key', 'default'), 'APIError', 'Inconsistent default values')
	caught
	>>> config.get('key1', 'default_key1')
	'default_key1'
	>>> try_catch(lambda: config.get('key1', 'default'), 'APIError', 'Inconsistent default values')
	caught

	>>> config.write(TestStream(), printDefault = False, printUnused = False) # doctest:+ELLIPSIS
	[global]
	plugin paths += ...
	-----
	[testuser]
	key = value
	-----

	>>> config.get('test')
	'works'

	>>> config.write(TestStream(), printDefault = True, printUnused = False) # doctest:+ELLIPSIS
	[dict]
	test = works
	-----
	[global]
	plugin paths += ...
	-----
	[global!]
	config id ?= test
	key1 ?= default_key1
	plugin paths ?= ...
	workdir ?= ...
	workdir base ?= ...
	-----
	[testuser]
	key = value
	-----

	>>> config.getDict('dict1') == ({'key3': 'value3', 'key2': 'value2\\ndefault2', 'key1': 'value1\\nvalue4', None: 'default1'}, ['key1', 'key2', 'key3'])
	True
	>>> config.getDict('dict2', {'key1': 'val1'}) == ({'key1': 'val1'}, ['key1'])
	True
	>>> config.getDict('dict3', {})
	({}, [])

	>>> config.get('key')
	'value'
	>>> config.changeView(setSections = ['TEST', 'TESTnick']).get('key')
	'valueX'
	>>> config.changeView(setSections = ['TEST', 'TESTnicky']).get('key')
	'value'

	>>> config.get('keydef', 'default')
	'valuedef'

	>>> try_catch(lambda: config.get('doesntexist'), 'ConfigError', 'does not exist')
	caught
	>>> try_catch(lambda: config.get('test1'), 'ConfigError', 'does not exist')
	caught
	>>> config.get('test2', 'default')
	'default'

	>>> config.getInt('zahl')
	123
	>>> try_catch(lambda: config.getInt('zahl1', 555), 'ConfigError', 'Unable to parse int')
	caught
	>>> config.getInt('zahl2', 985)
	985

	>>> config.changeView(setSections = ['TEST']).getList('liste')
	['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

	>>> config.changeView(setSections = ['TEST', 'TESTnick']).getList('liste')
	['x', 'y', 'z']

	>>> l0 = [1, 2]
	>>> config1 = config.changeView(setSections = ['TEST'])
	>>> config1.getList('liste')
	['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
	>>> config1.getList('liste1', l0)
	['1', '2']
	>>> config1.getList('liste')
	['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
	>>> config1.getList('liste1', l0)
	['1', '2']

	>>> config.getList('liste1')
	['1', '2']
	>>> config.getList('liste2', [1,2,3])
	['1', '2', '3']
	>>> config.getList('liste3', []) == []
	True

	>>> config.getBool('boolean')
	False
	>>> config.getBool('boolean1', True)
	True

	>>> config.getPath('path1')
	'/bin/sh'
	>>> try_catch(lambda: config.getPath('path2'), 'ConfigError', 'Unable to parse path')
	caught
	>>> config.getPath('path3') # doctest:+ELLIPSIS
	'.../config/test.conf'
	>>> try_catch(lambda: config.getPath('path4', 'invalid'), 'ConfigError', 'Unable to parse path')
	caught

	>>> config.getPath('path5', 'test.conf') # doctest:+ELLIPSIS
	'.../config/test.conf'
	>>> config.getPaths('paths') # doctest:+ELLIPSIS
	['.../config/test.conf', '.../TEST_config.py', '/bin/sh']
	>>> config.getPaths('paths1', '')
	[]
	>>> config.getPaths('paths1', [])
	[]
	>>> config.getPaths('paths2', ['test.conf', '/bin/sh']) # doctest:+ELLIPSIS
	['.../config/test.conf', '/bin/sh']
	"""

class Test_ConfigIncludes:
	"""
	>>> config = create_config('inc.conf', useDefaultFiles = True)

	config = Config('inc.conf', {'global': {'workdir': '.'}}, configHostSpecific = False)

	>>> config.get('keyd', 'valued')
	'valued'

	>>> config.get('key')
	'value'
	>>> config.get('keyl1')
	'level1'
	>>> config.get('keyl2')
	'level2'

	Multiple config files can be specified
	>>> config.get('keyl1a')
	'level1a'

	Top level config file overrides settings
	>>> config.get('keyo')
	'value0'

	2nd level is not read ...
	>>> config.get('keyl1o')
	'level1'

	Options can append to lower level values
	>>> config.get('keyl1ap')
	'level2\\nlevel1'
	>>> config.get('keyl0ap')
	'level1\\nlevel0'
	>>> config.get('keydefap1')
	'level0'
	>>> config.get('keydefap2', 'DEFAULT')
	'DEFAULT\\nlevel0'
	>>> config.getList('keydefap3')
	['a', 'b', 'c', 'd']
	>>> config.getList('keydefap4', ['1', '2', '3'])
	['1', '2', '3', 'e', 'f', 'g', 'h']

	Last include file overrides previous settings on same level
	>>> config.get('same1', 'same')
	'level1'
	>>> config.get('same2', 'same')
	'level1a'
	>>> config.get('same3')
	'level1a'

	>>> config.get('samex')
	'level0'

	>>> config.get('settest1', 'blubb')
	'blubb'
	>>> config.set('settest1', 'foobar') is None
	False
	>>> config.get('settest1', 'blubb')
	'foobar'

	>>> config.get('settest2', 'blubb')
	'blubb'
	>>> config.set('settest2', 'foobar', '?=') is None
	False
	>>> config.get('settest2', 'blubb')
	'foobar'
	"""

class Test_ConfigScoped:
	"""
	>>> config = create_config('sections.conf', useDefaultFiles = False)

	>>> config_nt = config.changeView(setSections = ['section named', 'section test'])
	>>> config_nt.getOptions()
	['key2', 'key3']
	>>> config_nt.get('key1', 'fail')
	'fail'
	>>> config_nt.get('key2', 'fail')
	'valueX'
	>>> config_nt.get('key3', 'fail')
	'value3'

	>>> config_s = config.changeView(setSections = ['section'])
	>>> config_s.getOptions()
	['key1', 'key2']
	>>> config_s.get('key1', 'fail')
	'value1'
	>>> config_s.get('key2', 'fail')
	'value2'
	>>> config_s.get('key3', 'fail')
	'fail'

	>>> config_n = config.changeView(setSections = ['section named'])
	>>> config_n.get('key1', 'fail')
	'fail'
	>>> config_n.get('key2', 'fail')
	'valueX'
	>>> config_n.get('key3', 'fail')
	'fail'

	>>> config_t = config.changeView(setSections = ['section test'])
	>>> config_t.getOptions()
	['key3']
	>>> config_t.get('key1', 'fail')
	'fail'
	>>> config_t.get('key2', 'fail')
	'fail'
	>>> config_t.get('key3', 'fail')
	'value3'

	>>> config_st = config.changeView(setSections = ['section', 'section test'])
	>>> config_st.getOptions()
	['key1', 'key2', 'key3']

	>>> config_st.get('key1', 'fail')
	'value1'
	>>> config_st.get('key2', 'fail')
	'value2'
	>>> config_st.get('key3', 'fail')
	'value3'

	>>> config_sn = config.changeView(setSections = ['section', 'section named'])
	>>> config_sn.get('key1', 'fail')
	'value1'
	>>> config_sn.get('key2', 'fail')
	'valueX'
	>>> config_sn.get('key3', 'fail')
	'fail'

	>>> config_snt = config.changeView(setSections = ['section', 'section named', 'section test'])
	>>> config_snt.getOptions()
	['key1', 'key2', 'key3']
	>>> config_snt.get('key1', 'fail')
	'value1'
	>>> config_snt.get('key2', 'fail')
	'valueX'
	>>> config_snt.get('key3', 'fail')
	'value3'

	>>> config_nt = config.changeView(setSections = ['section named', 'section test'])
	>>> config_nt.getOptions()
	['key1', 'key2', 'key3']
	>>> config_nt.get('key1')
	'fail'
	>>> config_nt.get('key2')
	'valueX'
	>>> config_nt.get('key3')
	'value3'

	>>> config = create_config('sections.conf', useDefaultFiles = False)
	>>> config.changeView(setSections = ['section']).get('keyX', 'persistent1')
	'persistent1'
	>>> config.changeView(setSections = ['section named']).get('keyX', 'persistent2')
	'persistent2'
	>>> config.changeView(setSections = ['section named', 'section']).get('keyX')
	'persistent1'
	>>> config.changeView(setSections = ['section', 'section named']).get('keyX')
	'persistent2'
	"""

run_test()
