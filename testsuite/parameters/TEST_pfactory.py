#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
import random
from testFwk import create_config, remove_files, run_test
from hpfwk import Plugin
from testINC import testPA
from python_compat import sorted

ParameterFactory = Plugin.getClass('ParameterFactory')
random.randint = lambda *args: 42 # 100% randomly choosen
noRNG = {'nseeds': 0}

def testPF(pf, config, details = False, manualKeys = None):
	every = 1
	if not details:
		every = 3
	testPA(pf.getSource(config), manualKeys = manualKeys, showJob = details, showPNum = details,
		showMetadata = details, showIV = details, showKeys = details,
		showUntracked = details,showJobPrefix = details, newlineEvery = every)

class Test_ParameterFactory:
	"""
	>>> random.seed(0)
	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])
	>>> config = create_config(configDict={'parameters': {'parameter adapter': 'BasicParameterAdapter'}})
	>>> pm = ParameterFactory.createInstance('ParameterFactory', config, 'parameters')
	>>> testPF(pm, config, True)
	None
	Keys = JOB_RANDOM, GC_JOB_ID, GC_PARAM
	1 {0: True, 2: [], '!JOB_RANDOM': 42, '!GC_JOB_ID': 1, '!GC_PARAM': 1}
	11 {0: True, 2: [], '!JOB_RANDOM': 42, '!GC_JOB_ID': 11, '!GC_PARAM': 11}
	redo: [] disable: [] size: False
	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])
	"""


class Test_BasicParameterFactory:
	"""
	>>> random.seed(0)
	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])
	>>> config = create_config(configDict={'parameters': {'parameter adapter': 'BasicParameterAdapter'}})
	>>> pm = config.getPlugin('parameter factory', 'BasicParameterFactory', cls = ParameterFactory)
	>>> testPF(pm, config, True)
	None
	Keys = JOB_RANDOM, SEED_0, SEED_1, SEED_2, SEED_3, SEED_4, SEED_5, SEED_6, SEED_7, SEED_8, SEED_9, GC_JOB_ID, GC_PARAM
	1 {0: True, 2: [], '!JOB_RANDOM': 42, '!SEED_0': 43, '!SEED_1': 43, '!SEED_2': 43, '!SEED_3': 43, '!SEED_4': 43, '!SEED_5': 43, '!SEED_6': 43, '!SEED_7': 43, '!SEED_8': 43, '!SEED_9': 43, '!GC_JOB_ID': 1, '!GC_PARAM': 1}
	11 {0: True, 2: [], '!JOB_RANDOM': 42, '!SEED_0': 53, '!SEED_1': 53, '!SEED_2': 53, '!SEED_3': 53, '!SEED_4': 53, '!SEED_5': 53, '!SEED_6': 53, '!SEED_7': 53, '!SEED_8': 53, '!SEED_9': 53, '!GC_JOB_ID': 11, '!GC_PARAM': 11}
	redo: [] disable: [] size: False
	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])

	>>> random.seed(0)
	>>> config = create_config(configDict={'jobs': {'seeds': '611'}, 'parameters': {'parameter adapter': 'BasicParameterAdapter'}})
	>>> pm = ParameterFactory.createInstance('BasicParameterFactory', config, 'parameters')
	>>> testPF(pm, config, True)
	None
	Keys = JOB_RANDOM, SEED_0, GC_JOB_ID, GC_PARAM
	1 {0: True, 2: [], '!JOB_RANDOM': 42, '!SEED_0': 612, '!GC_JOB_ID': 1, '!GC_PARAM': 1}
	11 {0: True, 2: [], '!JOB_RANDOM': 42, '!SEED_0': 622, '!GC_JOB_ID': 11, '!GC_PARAM': 11}
	redo: [] disable: [] size: False
	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])
	"""

def createMPM(pexpr, *args, **kwargs):
	kwargs['parameters'] = pexpr
	kwargs['parameter adapter'] = 'BasicParameterAdapter'
	jobCfg = dict(noRNG)
	for (opt, value) in args:
		kwargs[opt] = value
	for key in list(kwargs):
		kwargs[key.replace('_', ' ')] = kwargs.pop(key)
	config = create_config(configDict={'parameters': kwargs, 'jobs': jobCfg})
	pm = ParameterFactory.createInstance(kwargs.pop('factory', 'ModularParameterFactory'), config, 'parameters')
	return pm

def testMPM(pexpr, *args, **kwargs):
	factory = createMPM(pexpr, *args, **kwargs)
	if kwargs.pop('show_factory', False):
		print(factory.__class__.__name__)
	testPF(factory, create_config(configDict={}), kwargs.pop('details', False), manualKeys = sorted(kwargs.keys()))

class Test_LookupFactory:
	"""
	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])

	>>> A = 'a11 a12 a21 a22 a31 A00'
	>>> B = 'b11 b21 b22 b31 b41 B00'
	>>> LA = 'A! \\n a1 => A1 \\n a2 => A2 \\n a3 => A3'
	>>> LB = 'B! \\n b1 => B1 \\n b2 => B2 \\n b3 => B3'
	>>> LC = 'C! \\n (a1, b1) => C1 \\n (a2, b2) => C2 \\n (a3, b3) => C3'
	>>> PARAMS = {'A': A, 'B': B, 'LA': LA, 'LB': LB, 'LC': LC}
	>>> PARAMS.update({'LA matcher': 'regex', 'LB matcher': 'regex', 'LC matcher': 'regex'})
	>>> PARAMS.update({'details': True, 'show_factory': True})

	>>> EXPR = "zip(var('A'), lookup(key('LA'), key('A')))"
	>>> testMPM(EXPR, factory = 'ModularParameterFactory', **PARAMS)
	ModularParameterFactory
	6
	Keys = A [trk], JOB_RANDOM, LA [trk], GC_JOB_ID, GC_PARAM
	0 {'A': 'a11', 'LA': 'A1'}
	1 {'A': 'a12', 'LA': 'A1'}
	2 {'A': 'a21', 'LA': 'A2'}
	3 {'A': 'a22', 'LA': 'A2'}
	4 {'A': 'a31', 'LA': 'A3'}
	5 {'A': 'A00', 'LA': 'A!'}
	redo: [] disable: [] size: False

	>>> EXPR = 'A * LA[A]'
	>>> testMPM(EXPR, factory = 'SimpleParameterFactory', **PARAMS)
	SimpleParameterFactory
	6
	Keys = A [trk], JOB_RANDOM, LA [trk], GC_JOB_ID, GC_PARAM
	0 {'A': 'a11', 'LA': 'A1'}
	1 {'A': 'a12', 'LA': 'A1'}
	2 {'A': 'a21', 'LA': 'A2'}
	3 {'A': 'a22', 'LA': 'A2'}
	4 {'A': 'a31', 'LA': 'A3'}
	5 {'A': 'A00', 'LA': 'A!'}
	redo: [] disable: [] size: False

	>>> EXPR = 'A'
	>>> testMPM(EXPR, factory = 'SimpleParameterFactory', constants = 'LA', LA_lookup = 'A', **PARAMS)
	SimpleParameterFactory
	6
	Keys = A [trk], JOB_RANDOM, LA [trk], GC_JOB_ID, GC_PARAM
	0 {'A': 'a11', 'LA': 'A1'}
	1 {'A': 'a12', 'LA': 'A1'}
	2 {'A': 'a21', 'LA': 'A2'}
	3 {'A': 'a22', 'LA': 'A2'}
	4 {'A': 'a31', 'LA': 'A3'}
	5 {'A': 'A00', 'LA': 'A!'}
	redo: [] disable: [] size: False

	>>> EXPR = '(A, B) LA[A] LB[B] LC[(A, B)]'
	>>> testMPM(EXPR, factory = 'SimpleParameterFactory', **PARAMS)
	SimpleParameterFactory
	6
	Keys = A [trk], B [trk], JOB_RANDOM, LA [trk], LB [trk], LC [trk], GC_JOB_ID, GC_PARAM
	0 {'A': 'a11', 'B': 'b11', 'LA': 'A1', 'LB': 'B1', 'LC': 'C1'}
	1 {'A': 'a12', 'B': 'b21', 'LA': 'A1', 'LB': 'B2', 'LC': 'C!'}
	2 {'A': 'a21', 'B': 'b22', 'LA': 'A2', 'LB': 'B2', 'LC': 'C2'}
	3 {'A': 'a22', 'B': 'b31', 'LA': 'A2', 'LB': 'B3', 'LC': 'C!'}
	4 {'A': 'a31', 'B': 'b41', 'LA': 'A3', 'LB': 'B!', 'LC': 'C!'}
	5 {'A': 'A00', 'B': 'B00', 'LA': 'A!', 'LB': 'B!', 'LC': 'C!'}
	redo: [] disable: [] size: False

	>>> EXPR = '(A, B)'
	>>> testMPM(EXPR, factory = 'SimpleParameterFactory', constants = 'LA LB LC', LA_lookup = 'A', LB_lookup = 'B', LC_lookup = '(A,B)', **PARAMS)
	SimpleParameterFactory
	6
	Keys = A [trk], B [trk], JOB_RANDOM, LA [trk], LB [trk], LC [trk], GC_JOB_ID, GC_PARAM
	0 {'A': 'a11', 'B': 'b11', 'LA': 'A1', 'LB': 'B1', 'LC': 'C1'}
	1 {'A': 'a12', 'B': 'b21', 'LA': 'A1', 'LB': 'B2', 'LC': 'C!'}
	2 {'A': 'a21', 'B': 'b22', 'LA': 'A2', 'LB': 'B2', 'LC': 'C2'}
	3 {'A': 'a22', 'B': 'b31', 'LA': 'A2', 'LB': 'B3', 'LC': 'C!'}
	4 {'A': 'a31', 'B': 'b41', 'LA': 'A3', 'LB': 'B!', 'LC': 'C!'}
	5 {'A': 'A00', 'B': 'B00', 'LA': 'A!', 'LB': 'B!', 'LC': 'C!'}
	redo: [] disable: [] size: False

	>>> EXPR = "zip(var('A'), var('B'), lookup(key('LA'), key('A')), lookup(key('LB'), key('B')), lookup(key('LC'), key('A', 'B')))"
	>>> testMPM(EXPR, factory = 'ModularParameterFactory', **PARAMS)
	ModularParameterFactory
	6
	Keys = A [trk], B [trk], JOB_RANDOM, LA [trk], LB [trk], LC [trk], GC_JOB_ID, GC_PARAM
	0 {'A': 'a11', 'B': 'b11', 'LA': 'A1', 'LB': 'B1', 'LC': 'C1'}
	1 {'A': 'a12', 'B': 'b21', 'LA': 'A1', 'LB': 'B2', 'LC': 'C!'}
	2 {'A': 'a21', 'B': 'b22', 'LA': 'A2', 'LB': 'B2', 'LC': 'C2'}
	3 {'A': 'a22', 'B': 'b31', 'LA': 'A2', 'LB': 'B3', 'LC': 'C!'}
	4 {'A': 'a31', 'B': 'b41', 'LA': 'A3', 'LB': 'B!', 'LC': 'C!'}
	5 {'A': 'A00', 'B': 'B00', 'LA': 'A!', 'LB': 'B!', 'LC': 'C!'}
	redo: [] disable: [] size: False

	>>> EXPR = '(A, B) LA[A] LB[B] LC[(A, B)]'
	>>> testMPM(EXPR, factory = 'SimpleParameterFactory', **PARAMS)
	SimpleParameterFactory
	6
	Keys = A [trk], B [trk], JOB_RANDOM, LA [trk], LB [trk], LC [trk], GC_JOB_ID, GC_PARAM
	0 {'A': 'a11', 'B': 'b11', 'LA': 'A1', 'LB': 'B1', 'LC': 'C1'}
	1 {'A': 'a12', 'B': 'b21', 'LA': 'A1', 'LB': 'B2', 'LC': 'C!'}
	2 {'A': 'a21', 'B': 'b22', 'LA': 'A2', 'LB': 'B2', 'LC': 'C2'}
	3 {'A': 'a22', 'B': 'b31', 'LA': 'A2', 'LB': 'B3', 'LC': 'C!'}
	4 {'A': 'a31', 'B': 'b41', 'LA': 'A3', 'LB': 'B!', 'LC': 'C!'}
	5 {'A': 'A00', 'B': 'B00', 'LA': 'A!', 'LB': 'B!', 'LC': 'C!'}
	redo: [] disable: [] size: False

	>>> EXPR = '(A, B)'
	>>> testMPM(EXPR, factory = 'SimpleParameterFactory', constants = 'LA LB LC', LA_lookup = 'A', LB_lookup = 'B', LC_lookup = '(A,B)', **PARAMS)
	SimpleParameterFactory
	6
	Keys = A [trk], B [trk], JOB_RANDOM, LA [trk], LB [trk], LC [trk], GC_JOB_ID, GC_PARAM
	0 {'A': 'a11', 'B': 'b11', 'LA': 'A1', 'LB': 'B1', 'LC': 'C1'}
	1 {'A': 'a12', 'B': 'b21', 'LA': 'A1', 'LB': 'B2', 'LC': 'C!'}
	2 {'A': 'a21', 'B': 'b22', 'LA': 'A2', 'LB': 'B2', 'LC': 'C2'}
	3 {'A': 'a22', 'B': 'b31', 'LA': 'A2', 'LB': 'B3', 'LC': 'C!'}
	4 {'A': 'a31', 'B': 'b41', 'LA': 'A3', 'LB': 'B!', 'LC': 'C!'}
	5 {'A': 'A00', 'B': 'B00', 'LA': 'A!', 'LB': 'B!', 'LC': 'C!'}
	redo: [] disable: [] size: False

	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])
	"""

run_test()

class Test_ModularParameterFactory:
	"""
	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])
	>>> config = create_config(configDict={'parameters': {'parameter adapter': 'BasicParameterAdapter', 'parameters': "var('A')", 'A': '1 2 3'}, 'jobs': noRNG})
	>>> pm = ParameterFactory.createInstance('ModularParameterFactory', config, 'parameters')
	>>> testPF(pm, config)
	3
	{'A': '1'} {'A': '2'} {'A': '3'}
	>>> testMPM("var('A')", A = '1 2 3')
	3
	{'A': '1'} {'A': '2'} {'A': '3'}
	>>> testMPM("const('A')", A = '1 2 3')
	None
	{'A': '1 2 3'}
	{'A': '1 2 3'}
	>>> testMPM("var('a')", A = '1 2 3')
	3
	{'a': '1'} {'a': '2'} {'a': '3'}
	>>> testMPM("repeat(var('a'), 5)", A = '1 2 3')
	15
	{'a': '1'} {'a': '2'} {'a': '3'}
	{'a': '1'} {'a': '2'} {'a': '3'}
	{'a': '1'} {'a': '2'} {'a': '3'}
	{'a': '1'} {'a': '2'} {'a': '3'}
	{'a': '1'} {'a': '2'} {'a': '3'}
	>>> testMPM("zip(var('a'), var('b'))", A = '1 2 3', B = 'x y')
	3
	{'a': '1', 'b': 'x'} {'a': '2', 'b': 'y'} {'a': '3'}
	>>> testMPM("cross(var('a'), var('b'))", A = '1 2 3', B = 'x y')
	6
	{'a': '1', 'b': 'x'} {'a': '2', 'b': 'x'} {'a': '3', 'b': 'x'}
	{'a': '1', 'b': 'y'} {'a': '2', 'b': 'y'} {'a': '3', 'b': 'y'}
	>>> testMPM("cross(var('a'), var('b'), var('C'))", A = '1 2 3', B = 'x y', C = 'a b')
	12
	{'C': 'a', 'a': '1', 'b': 'x'} {'C': 'a', 'a': '2', 'b': 'x'} {'C': 'a', 'a': '3', 'b': 'x'}
	{'C': 'a', 'a': '1', 'b': 'y'} {'C': 'a', 'a': '2', 'b': 'y'} {'C': 'a', 'a': '3', 'b': 'y'}
	{'C': 'b', 'a': '1', 'b': 'x'} {'C': 'b', 'a': '2', 'b': 'x'} {'C': 'b', 'a': '3', 'b': 'x'}
	{'C': 'b', 'a': '1', 'b': 'y'} {'C': 'b', 'a': '2', 'b': 'y'} {'C': 'b', 'a': '3', 'b': 'y'}
	>>> testMPM("zip(var('a'), var('b'), var('C'))", A = '1 2 3', B = 'x y', C = 'a b')
	3
	{'C': 'a', 'a': '1', 'b': 'x'} {'C': 'b', 'a': '2', 'b': 'y'} {'a': '3'}
	>>> testMPM("chain(var('a'), var('b'), var('C'))", A = '1 2 3', B = 'x y', C = 'a b')
	7
	{'a': '1'} {'a': '2'} {'a': '3'}
	{'b': 'x'} {'b': 'y'} {'C': 'a'}
	{'C': 'b'}

	>>> random.seed(0)
	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])
	>>> testMPM("cross(rng(), var('a'), counter('b', 90), const('c', 'TEST'))",
	... A = '1 2 3', b = None, c = None)
	3
	{'a': '1', '!b': 90, 'c': 'TEST'} {'a': '2', '!b': 91, 'c': 'TEST'} {'a': '3', '!b': 92, 'c': 'TEST'}

	>>> testMPM("cross(cross(var('a'), var('b')), format('c', '%02d', 'a', 0))",
	... A = '1 2 3', b = 'x y z', c = None)
	9
	{'a': '1', 'b': 'x', '!c': '01'} {'a': '2', 'b': 'x', '!c': '02'} {'a': '3', 'b': 'x', '!c': '03'}
	{'a': '1', 'b': 'y', '!c': '01'} {'a': '2', 'b': 'y', '!c': '02'} {'a': '3', 'b': 'y', '!c': '03'}
	{'a': '1', 'b': 'z', '!c': '01'} {'a': '2', 'b': 'z', '!c': '02'} {'a': '3', 'b': 'z', '!c': '03'}
	>>> testMPM("zip(chain(var('va'), var('vb')), collect('t', 'v...'))",
	... VA = '1 2 3', Vb = 'x y z', t = None)
	6
	{'t': '1', 'va': '1'} {'t': '2', 'va': '2'} {'t': '3', 'va': '3'}
	{'t': 'x', 'vb': 'x'} {'t': 'y', 'vb': 'y'} {'t': 'z', 'vb': 'z'}
	>>> testMPM("range(var('a'), 5)", A = '1 2 3 4 5 6 7 8 9 10')
	5
	{'a': '6'} {'a': '7'} {'a': '8'}
	{'a': '9'} {'a': '10'}
	>>> testMPM("range(var('a'), 0, 2)", A = '1 2 3 4 5 6 7 8 9 10')
	3
	{'a': '1'} {'a': '2'} {'a': '3'}
	>>> testMPM("range(var('a'), None, 1)", A = '1 2 3 4 5 6 7 8 9 10')
	2
	{'a': '1'} {'a': '2'}
	>>> testMPM("range(var('a'), 3, 6)", A = '1 2 3 4 5 6 7 8 9 10')
	4
	{'a': '4'} {'a': '5'} {'a': '6'}
	{'a': '7'}
	>>> testMPM("variation(var('a'), var('b'), var('c'))", A = 'a0 a-1 a+1', B = 'b0 b-1 b-2 b+1', C = 'c0 c+1 c+2')
	8
	{'a': 'a0', 'b': 'b0', 'c': 'c0'} {'a': 'a-1', 'b': 'b0', 'c': 'c0'} {'a': 'a+1', 'b': 'b0', 'c': 'c0'}
	{'a': 'a0', 'b': 'b-1', 'c': 'c0'} {'a': 'a0', 'b': 'b-2', 'c': 'c0'} {'a': 'a0', 'b': 'b+1', 'c': 'c0'}
	{'a': 'a0', 'b': 'b0', 'c': 'c+1'} {'a': 'a0', 'b': 'b0', 'c': 'c+2'}

	>>> testMPM("cross(var('a'), lookup(key('d'), key('a')))", A = 'a1 a2 a3 a b1', D = '1 \\n a1 => 3 \\n b1 => x \\n a => 2')
	5
	{'a': 'a1', 'd': '3'} {'a': 'a2', 'd': '1'} {'a': 'a3', 'd': '1'}
	{'a': 'a', 'd': '2'} {'a': 'b1', 'd': 'x'}

	>>> testMPM("cross(var('a'), lookup(key('d'), key('a')))", ('D matcher', 'start'), A = 'a1 a2 a3 a b1', D = '1 \\n a1 => 3 \\n b1 => x \\n a => 2')
	5
	{'a': 'a1', 'd': '3'} {'a': 'a2', 'd': '2'} {'a': 'a3', 'd': '2'}
	{'a': 'a', 'd': '2'} {'a': 'b1', 'd': 'x'}

	>>> testMPM("cross(var('a'), var('b'), var('c'))", A = 'a1 a2 a3', B = 'b1 b2', C = 'c1 c2 c3')
	18
	{'a': 'a1', 'b': 'b1', 'c': 'c1'} {'a': 'a2', 'b': 'b1', 'c': 'c1'} {'a': 'a3', 'b': 'b1', 'c': 'c1'}
	{'a': 'a1', 'b': 'b2', 'c': 'c1'} {'a': 'a2', 'b': 'b2', 'c': 'c1'} {'a': 'a3', 'b': 'b2', 'c': 'c1'}
	{'a': 'a1', 'b': 'b1', 'c': 'c2'} {'a': 'a2', 'b': 'b1', 'c': 'c2'} {'a': 'a3', 'b': 'b1', 'c': 'c2'}
	{'a': 'a1', 'b': 'b2', 'c': 'c2'} {'a': 'a2', 'b': 'b2', 'c': 'c2'} {'a': 'a3', 'b': 'b2', 'c': 'c2'}
	{'a': 'a1', 'b': 'b1', 'c': 'c3'} {'a': 'a2', 'b': 'b1', 'c': 'c3'} {'a': 'a3', 'b': 'b1', 'c': 'c3'}
	{'a': 'a1', 'b': 'b2', 'c': 'c3'} {'a': 'a2', 'b': 'b2', 'c': 'c3'} {'a': 'a3', 'b': 'b2', 'c': 'c3'}

	>>> testMPM("cross(var('a'), var('b'), var('c'), lookup(key('d'), key('a')))", A = 'a1 a2 a3', B = 'b1 b2', C = 'c1 c2 c3', D = '1 \\n a1 => 3 \\n b1 => x \\n a => 2')
	18
	{'a': 'a1', 'b': 'b1', 'c': 'c1', 'd': '3'} {'a': 'a2', 'b': 'b1', 'c': 'c1', 'd': '1'} {'a': 'a3', 'b': 'b1', 'c': 'c1', 'd': '1'}
	{'a': 'a1', 'b': 'b2', 'c': 'c1', 'd': '3'} {'a': 'a2', 'b': 'b2', 'c': 'c1', 'd': '1'} {'a': 'a3', 'b': 'b2', 'c': 'c1', 'd': '1'}
	{'a': 'a1', 'b': 'b1', 'c': 'c2', 'd': '3'} {'a': 'a2', 'b': 'b1', 'c': 'c2', 'd': '1'} {'a': 'a3', 'b': 'b1', 'c': 'c2', 'd': '1'}
	{'a': 'a1', 'b': 'b2', 'c': 'c2', 'd': '3'} {'a': 'a2', 'b': 'b2', 'c': 'c2', 'd': '1'} {'a': 'a3', 'b': 'b2', 'c': 'c2', 'd': '1'}
	{'a': 'a1', 'b': 'b1', 'c': 'c3', 'd': '3'} {'a': 'a2', 'b': 'b1', 'c': 'c3', 'd': '1'} {'a': 'a3', 'b': 'b1', 'c': 'c3', 'd': '1'}
	{'a': 'a1', 'b': 'b2', 'c': 'c3', 'd': '3'} {'a': 'a2', 'b': 'b2', 'c': 'c3', 'd': '1'} {'a': 'a3', 'b': 'b2', 'c': 'c3', 'd': '1'}

	>>> testMPM("cross(var('a'), var('b'), var('c'), lookup(key('d'), key('a')))", ('D matcher', 'start'), A = 'a1 a2 a3', B = 'b1 b2', C = 'c1 c2 c3', D = '1 \\n a1 => 3 \\n b1 => x \\n a => 2')
	18
	{'a': 'a1', 'b': 'b1', 'c': 'c1', 'd': '3'} {'a': 'a2', 'b': 'b1', 'c': 'c1', 'd': '2'} {'a': 'a3', 'b': 'b1', 'c': 'c1', 'd': '2'}
	{'a': 'a1', 'b': 'b2', 'c': 'c1', 'd': '3'} {'a': 'a2', 'b': 'b2', 'c': 'c1', 'd': '2'} {'a': 'a3', 'b': 'b2', 'c': 'c1', 'd': '2'}
	{'a': 'a1', 'b': 'b1', 'c': 'c2', 'd': '3'} {'a': 'a2', 'b': 'b1', 'c': 'c2', 'd': '2'} {'a': 'a3', 'b': 'b1', 'c': 'c2', 'd': '2'}
	{'a': 'a1', 'b': 'b2', 'c': 'c2', 'd': '3'} {'a': 'a2', 'b': 'b2', 'c': 'c2', 'd': '2'} {'a': 'a3', 'b': 'b2', 'c': 'c2', 'd': '2'}
	{'a': 'a1', 'b': 'b1', 'c': 'c3', 'd': '3'} {'a': 'a2', 'b': 'b1', 'c': 'c3', 'd': '2'} {'a': 'a3', 'b': 'b1', 'c': 'c3', 'd': '2'}
	{'a': 'a1', 'b': 'b2', 'c': 'c3', 'd': '3'} {'a': 'a2', 'b': 'b2', 'c': 'c3', 'd': '2'} {'a': 'a3', 'b': 'b2', 'c': 'c3', 'd': '2'}

	>>> testMPM("switch(cross(var('a'), var('b'), var('c')), key('d'), key('a'))", A = 'a1 a2 a3 a4', B = 'b1 b2', C = 'c1 c2 c3', D = '\\n a1 => 31 32 33 \\n b1 => x y\\n a => 21')
	18
	{'a': 'a1', 'b': 'b1', 'c': 'c1', 'd': '31'} {'a': 'a1', 'b': 'b1', 'c': 'c1', 'd': '32'} {'a': 'a1', 'b': 'b1', 'c': 'c1', 'd': '33'}
	{'a': 'a1', 'b': 'b2', 'c': 'c1', 'd': '31'} {'a': 'a1', 'b': 'b2', 'c': 'c1', 'd': '32'} {'a': 'a1', 'b': 'b2', 'c': 'c1', 'd': '33'}
	{'a': 'a1', 'b': 'b1', 'c': 'c2', 'd': '31'} {'a': 'a1', 'b': 'b1', 'c': 'c2', 'd': '32'} {'a': 'a1', 'b': 'b1', 'c': 'c2', 'd': '33'}
	{'a': 'a1', 'b': 'b2', 'c': 'c2', 'd': '31'} {'a': 'a1', 'b': 'b2', 'c': 'c2', 'd': '32'} {'a': 'a1', 'b': 'b2', 'c': 'c2', 'd': '33'}
	{'a': 'a1', 'b': 'b1', 'c': 'c3', 'd': '31'} {'a': 'a1', 'b': 'b1', 'c': 'c3', 'd': '32'} {'a': 'a1', 'b': 'b1', 'c': 'c3', 'd': '33'}
	{'a': 'a1', 'b': 'b2', 'c': 'c3', 'd': '31'} {'a': 'a1', 'b': 'b2', 'c': 'c3', 'd': '32'} {'a': 'a1', 'b': 'b2', 'c': 'c3', 'd': '33'}

	>>> testMPM("switch(cross(var('a'), var('b'), var('c')), key('d'), key('a'))", A = 'a1 a2 a3 a4', B = 'b1 b2', C = 'c1 c2 c3', D = 'xx \\n a1 => 31 32 33 \\n b1 => x y\\n a => 21')
	36
	{'a': 'a1', 'b': 'b1', 'c': 'c1', 'd': '31'} {'a': 'a1', 'b': 'b1', 'c': 'c1', 'd': '32'} {'a': 'a1', 'b': 'b1', 'c': 'c1', 'd': '33'}
	{'a': 'a2', 'b': 'b1', 'c': 'c1', 'd': 'xx'} {'a': 'a3', 'b': 'b1', 'c': 'c1', 'd': 'xx'} {'a': 'a4', 'b': 'b1', 'c': 'c1', 'd': 'xx'}
	{'a': 'a1', 'b': 'b2', 'c': 'c1', 'd': '31'} {'a': 'a1', 'b': 'b2', 'c': 'c1', 'd': '32'} {'a': 'a1', 'b': 'b2', 'c': 'c1', 'd': '33'}
	{'a': 'a2', 'b': 'b2', 'c': 'c1', 'd': 'xx'} {'a': 'a3', 'b': 'b2', 'c': 'c1', 'd': 'xx'} {'a': 'a4', 'b': 'b2', 'c': 'c1', 'd': 'xx'}
	{'a': 'a1', 'b': 'b1', 'c': 'c2', 'd': '31'} {'a': 'a1', 'b': 'b1', 'c': 'c2', 'd': '32'} {'a': 'a1', 'b': 'b1', 'c': 'c2', 'd': '33'}
	{'a': 'a2', 'b': 'b1', 'c': 'c2', 'd': 'xx'} {'a': 'a3', 'b': 'b1', 'c': 'c2', 'd': 'xx'} {'a': 'a4', 'b': 'b1', 'c': 'c2', 'd': 'xx'}
	{'a': 'a1', 'b': 'b2', 'c': 'c2', 'd': '31'} {'a': 'a1', 'b': 'b2', 'c': 'c2', 'd': '32'} {'a': 'a1', 'b': 'b2', 'c': 'c2', 'd': '33'}
	{'a': 'a2', 'b': 'b2', 'c': 'c2', 'd': 'xx'} {'a': 'a3', 'b': 'b2', 'c': 'c2', 'd': 'xx'} {'a': 'a4', 'b': 'b2', 'c': 'c2', 'd': 'xx'}
	{'a': 'a1', 'b': 'b1', 'c': 'c3', 'd': '31'} {'a': 'a1', 'b': 'b1', 'c': 'c3', 'd': '32'} {'a': 'a1', 'b': 'b1', 'c': 'c3', 'd': '33'}
	{'a': 'a2', 'b': 'b1', 'c': 'c3', 'd': 'xx'} {'a': 'a3', 'b': 'b1', 'c': 'c3', 'd': 'xx'} {'a': 'a4', 'b': 'b1', 'c': 'c3', 'd': 'xx'}
	{'a': 'a1', 'b': 'b2', 'c': 'c3', 'd': '31'} {'a': 'a1', 'b': 'b2', 'c': 'c3', 'd': '32'} {'a': 'a1', 'b': 'b2', 'c': 'c3', 'd': '33'}
	{'a': 'a2', 'b': 'b2', 'c': 'c3', 'd': 'xx'} {'a': 'a3', 'b': 'b2', 'c': 'c3', 'd': 'xx'} {'a': 'a4', 'b': 'b2', 'c': 'c3', 'd': 'xx'}

	>>> testMPM("switch(cross(var('a'), var('b'), var('c')), key('d'), key('a'))", ('D matcher', 'start'), A = 'a1 a2 a3 a4', B = 'b1 b2', C = 'c1 c2 c3', D = '\\n a1 => 31 32 33 \\n b1 => x y\\n a => 21')
	36
	{'a': 'a1', 'b': 'b1', 'c': 'c1', 'd': '31'} {'a': 'a1', 'b': 'b1', 'c': 'c1', 'd': '32'} {'a': 'a1', 'b': 'b1', 'c': 'c1', 'd': '33'}
	{'a': 'a2', 'b': 'b1', 'c': 'c1', 'd': '21'} {'a': 'a3', 'b': 'b1', 'c': 'c1', 'd': '21'} {'a': 'a4', 'b': 'b1', 'c': 'c1', 'd': '21'}
	{'a': 'a1', 'b': 'b2', 'c': 'c1', 'd': '31'} {'a': 'a1', 'b': 'b2', 'c': 'c1', 'd': '32'} {'a': 'a1', 'b': 'b2', 'c': 'c1', 'd': '33'}
	{'a': 'a2', 'b': 'b2', 'c': 'c1', 'd': '21'} {'a': 'a3', 'b': 'b2', 'c': 'c1', 'd': '21'} {'a': 'a4', 'b': 'b2', 'c': 'c1', 'd': '21'}
	{'a': 'a1', 'b': 'b1', 'c': 'c2', 'd': '31'} {'a': 'a1', 'b': 'b1', 'c': 'c2', 'd': '32'} {'a': 'a1', 'b': 'b1', 'c': 'c2', 'd': '33'}
	{'a': 'a2', 'b': 'b1', 'c': 'c2', 'd': '21'} {'a': 'a3', 'b': 'b1', 'c': 'c2', 'd': '21'} {'a': 'a4', 'b': 'b1', 'c': 'c2', 'd': '21'}
	{'a': 'a1', 'b': 'b2', 'c': 'c2', 'd': '31'} {'a': 'a1', 'b': 'b2', 'c': 'c2', 'd': '32'} {'a': 'a1', 'b': 'b2', 'c': 'c2', 'd': '33'}
	{'a': 'a2', 'b': 'b2', 'c': 'c2', 'd': '21'} {'a': 'a3', 'b': 'b2', 'c': 'c2', 'd': '21'} {'a': 'a4', 'b': 'b2', 'c': 'c2', 'd': '21'}
	{'a': 'a1', 'b': 'b1', 'c': 'c3', 'd': '31'} {'a': 'a1', 'b': 'b1', 'c': 'c3', 'd': '32'} {'a': 'a1', 'b': 'b1', 'c': 'c3', 'd': '33'}
	{'a': 'a2', 'b': 'b1', 'c': 'c3', 'd': '21'} {'a': 'a3', 'b': 'b1', 'c': 'c3', 'd': '21'} {'a': 'a4', 'b': 'b1', 'c': 'c3', 'd': '21'}
	{'a': 'a1', 'b': 'b2', 'c': 'c3', 'd': '31'} {'a': 'a1', 'b': 'b2', 'c': 'c3', 'd': '32'} {'a': 'a1', 'b': 'b2', 'c': 'c3', 'd': '33'}
	{'a': 'a2', 'b': 'b2', 'c': 'c3', 'd': '21'} {'a': 'a3', 'b': 'b2', 'c': 'c3', 'd': '21'} {'a': 'a4', 'b': 'b2', 'c': 'c3', 'd': '21'}

	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])
	"""

def createSimplePF(pstr, raw = True):
	config = create_config(configDict={'parameters': {
		'A': 'test a b',
		'B': 'test a b',
		'C': 'test a b',
		'C1': 'a => test\n b => xxx',
		'X': 'a => test\n b => xxx',
		'D': 'test a b',
		'E': 'test a b',
		'F': 'test a b',
		'I': 'test a b',
		'(G,H)': 'a => (test, test1)\n b => (test2, test3)',
		'(G1,H1)': '(test, test1) (test2, test3)',
		'default lookup': 'A',
		'parameters': pstr,
		'parameter adapter': 'BasicParameterAdapter',
	}, 'jobs': {'nseeds': '4'}})
	pm = ParameterFactory.createInstance('SimpleParameterFactory', config, 'parameters')
	if raw:
		return pm._getUserSource(pstr, None)
	return pm.getSource(config)

class Test_SimpleParameterFactory:
	"""
	>>> random.seed(0)
	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])
	>>> testPA(createSimplePF('', raw = False))
	None
	Keys = JOB_RANDOM, SEED_0, SEED_1, SEED_2, SEED_3, GC_JOB_ID, GC_PARAM
	1 {0: True, 2: [], '!JOB_RANDOM': 42, '!SEED_0': 43, '!SEED_1': 43, '!SEED_2': 43, '!SEED_3': 43, '!GC_JOB_ID': 1, '!GC_PARAM': 1}
	11 {0: True, 2: [], '!JOB_RANDOM': 42, '!SEED_0': 53, '!SEED_1': 53, '!SEED_2': 53, '!SEED_3': 53, '!GC_JOB_ID': 11, '!GC_PARAM': 11}
	redo: [] disable: [] size: False

	>>> createSimplePF('A')
	var('A')
	>>> createSimplePF('A, B, C')
	zip(var('A'), var('B'), var('C'))
	>>> createSimplePF('A B C')
	cross(var('A'), var('B'), var('C'))
	>>> createSimplePF('A B * C')
	cross(var('A'), var('B'), var('C'))
	>>> createSimplePF('A B, 2*C')
	zip(cross(var('A'), var('B')), repeat(var('C'), 2))
	>>> createSimplePF('2 * (A B), C')
	zip(repeat(cross(var('A'), var('B')), 2), var('C'))

	>>> createSimplePF('A, (B+(C))*(((((D)))*E)+F), G1 (H1) * I')
	zip(var('A'), cross(chain(var('B'), var('C')), chain(cross(var('D'), var('E')), var('F'))), cross(var('G1'), var('H1'), var('I')))

	>>> createSimplePF('A B, C1[D]')
	zip(cross(var('A'), var('B')), lookup(key('C1'), key('D')))

	>>> createSimplePF('A B, C1[(D,E)]')
	zip(cross(var('A'), var('B')), lookup(key('C1'), key('D', 'E')))
	>>> createSimplePF('A B, (C1,X)[D]')
	zip(cross(var('A'), var('B')), lookup(key('C1'), key('D')), lookup(key('X'), key('D')))
	>>> createSimplePF('A B, (C,X)[(D,E)]')
	zip(cross(var('A'), var('B')), var('C'), lookup(key('X'), key('D', 'E')))
	>>> createSimplePF('A B, (C1,X)[(D,E)]')
	zip(cross(var('A'), var('B')), lookup(key('C1'), key('D', 'E')), lookup(key('X'), key('D', 'E')))
	>>> createSimplePF('A, 2 B+C D*E+F, (G,H)[A]')
	zip(var('A'), chain(repeat(var('B'), 2), cross(var('C'), var('D'), var('E')), var('F')), lookup(key('G'), key('A')), lookup(key('H'), key('A')))

	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])
	"""
