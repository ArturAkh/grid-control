#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
import random
from testFwk import create_config, run_test
from grid_control import utils
from grid_control.config import Matcher
from grid_control.datasets import DataProvider, DataSplitter, PartitionProcessor
from grid_control.parameters import ParameterMetadata, ParameterSource
from grid_control.parameters.padapter import ParameterAdapter
from grid_control.parameters.psource_file import GCDumpParameterSource
from testDS import ss2bl
from testINC import DataSplitProcessorTest, testPS, updateDS
from python_compat import lmap, lrange, set

def createMatcher(name):
	return Matcher.createInstance(name, create_config(), 'test')

random.randint = lambda *args: 42 # 100% randomly choosen

class Test_BasicParameterSource:
	"""
	>>> ps = ParameterSource.createInstance('InternalParameterSource', [{'KEY': 1}, {'KEY': 2}, {'KEY': 3}], lmap(ParameterMetadata, ['KEY']))
	>>> testPS(ps, True)
	3
	Keys = KEY [trk], GC_PARAM
	0 {0: True, 2: [], 'KEY': 1, '!GC_PARAM': 0}
	1 {0: True, 2: [], 'KEY': 2, '!GC_PARAM': 1}
	2 {0: True, 2: [], 'KEY': 3, '!GC_PARAM': 2}
	redo: [1] disable: [2] size: False

	>>> testPS(ParameterSource.createInstance('SimpleParameterSource', 'KEY', [1, 2, 3]), True)
	3
	Keys = KEY [trk], GC_PARAM
	0 {0: True, 2: [], 'KEY': 1, '!GC_PARAM': 0}
	1 {0: True, 2: [], 'KEY': 2, '!GC_PARAM': 1}
	2 {0: True, 2: [], 'KEY': 3, '!GC_PARAM': 2}
	redo: [1] disable: [2] size: False

	>>> testPS(ParameterSource.createInstance('SimpleParameterSource', '!KEY', [1, 2, 3]), True)
	3
	Keys = KEY, GC_PARAM
	0 {0: True, 2: [], '!KEY': 1, '!GC_PARAM': 0}
	1 {0: True, 2: [], '!KEY': 2, '!GC_PARAM': 1}
	2 {0: True, 2: [], '!KEY': 3, '!GC_PARAM': 2}
	redo: [1] disable: [2] size: False

	>>> testPS(ParameterSource.createInstance('ConstParameterSource', 'KEY', 'VALUE'), True)
	None
	Keys = KEY [trk], GC_PARAM
	1 {0: True, 2: [], 'KEY': 'VALUE', '!GC_PARAM': 1}
	11 {0: True, 2: [], 'KEY': 'VALUE', '!GC_PARAM': 11}
	redo: [1] disable: [2] size: False

	>>> testPS(ParameterSource.createInstance('ConstParameterSource', '!KEY', 'VALUE'), True)
	None
	Keys = KEY, GC_PARAM
	1 {0: True, 2: [], '!KEY': 'VALUE', '!GC_PARAM': 1}
	11 {0: True, 2: [], '!KEY': 'VALUE', '!GC_PARAM': 11}
	redo: [1] disable: [2] size: False

	>>> ps = ParameterSource.createInstance('SimpleLookupParameterSource', 'KEY', ('SRC',), None, ({}, []))
	>>> testPS(ps)
	None
	Keys = KEY [trk], GC_PARAM
	1 {0: True, 2: [], '!GC_PARAM': 1}
	11 {0: True, 2: [], '!GC_PARAM': 11}
	redo: [] disable: [] size: False

	>>> random.seed(0)
	>>> ps = ParameterSource.createInstance('RNGParameterSource', 'RNG', 1, 9)
	>>> testPS(ps)
	None
	Keys = RNG, GC_PARAM
	1 {0: True, 2: [], '!RNG': 42, '!GC_PARAM': 1}
	11 {0: True, 2: [], '!RNG': 42, '!GC_PARAM': 11}
	redo: [] disable: [] size: False

	>>> ps = ParameterSource.createInstance('CounterParameterSource', 'C', 1111)
	>>> testPS(ps)
	None
	Keys = C, GC_PARAM
	1 {0: True, 2: [], '!C': 1112, '!GC_PARAM': 1}
	11 {0: True, 2: [], '!C': 1122, '!GC_PARAM': 11}
	redo: [] disable: [] size: False

	>>> p1 = ParameterSource.createInstance('InternalParameterSource',
	... [{'CPUTIME': '10:00'}, {'MEMORY': '2000'}, {'WALLTIME': '0:00:10'}], [])
	>>> p1.resyncSetup(info = (set([1]), set([2]), False))
	>>> pr = ParameterSource.createInstance('RequirementParameterSource')
	>>> testPS(ParameterSource.createInstance('CombineParameterSource', p1, pr))
	3
	Keys = GC_PARAM
	0 {0: True, 2: [(1, 36000)], '!GC_PARAM': 0}
	1 {0: True, 2: [(2, 2000)], '!GC_PARAM': 1}
	2 {0: True, 2: [(0, 10)], '!GC_PARAM': 2}
	redo: [1] disable: [2] size: False
	"""

class Test_LookupParameterSources:
	"""
	>>> p1 = ParameterSource.createInstance('SimpleParameterSource', 'KEY1', ['AX', 'AY', 'AZ', 'BX', 'BY'])
	>>> p2 = ParameterSource.createInstance('SimpleParameterSource', 'KEY2', ['10', '15', '20', '25', '30'])

	>>> pl = ParameterSource.createInstance('SimpleLookupParameterSource', 'LOOKUP', ('KEY1',),
	... [createMatcher('equal')],
	... ({('AX',): ['511'], ('A',): ['811'], ('B',): ['987']}, [('AX',), ('A',), ('B',)]))
	>>> p1.resyncSetup(info = (set([1, 4]), set([2, 3]), False))
	>>> testPS(ParameterSource.createInstance('CombineParameterSource', p1, pl))
	5
	Keys = KEY1 [trk], LOOKUP [trk], GC_PARAM
	0 {0: True, 2: [], 'KEY1': 'AX', 'LOOKUP': '511', '!GC_PARAM': 0}
	1 {0: True, 2: [], 'KEY1': 'AY', '!GC_PARAM': 1}
	2 {0: True, 2: [], 'KEY1': 'AZ', '!GC_PARAM': 2}
	3 {0: True, 2: [], 'KEY1': 'BX', '!GC_PARAM': 3}
	4 {0: True, 2: [], 'KEY1': 'BY', '!GC_PARAM': 4}
	redo: [1, 4] disable: [2, 3] size: False

	>>> pl = ParameterSource.createInstance('SimpleLookupParameterSource', 'LOOKUP', ('KEY1',),
	... [createMatcher('start')],
	... ({('AX',): ['511'], ('A',): ['811'], ('B',): ['987']}, [('AX',), ('A',), ('B',)]))
	>>> p1.resyncSetup(info = (set([1, 4]), set([2, 3]), False))
	>>> testPS(ParameterSource.createInstance('CombineParameterSource', p1, pl))
	5
	Keys = KEY1 [trk], LOOKUP [trk], GC_PARAM
	0 {0: True, 2: [], 'KEY1': 'AX', 'LOOKUP': '511', '!GC_PARAM': 0}
	1 {0: True, 2: [], 'KEY1': 'AY', 'LOOKUP': '811', '!GC_PARAM': 1}
	2 {0: True, 2: [], 'KEY1': 'AZ', 'LOOKUP': '811', '!GC_PARAM': 2}
	3 {0: True, 2: [], 'KEY1': 'BX', 'LOOKUP': '987', '!GC_PARAM': 3}
	4 {0: True, 2: [], 'KEY1': 'BY', 'LOOKUP': '987', '!GC_PARAM': 4}
	redo: [1, 4] disable: [2, 3] size: False

	>>> pl = ParameterSource.createInstance('SimpleLookupParameterSource', 'LOOKUP', ('KEY1', 'KEY2'),
	... [createMatcher('start'), createMatcher('equal')],
	... ({('AX',): ['511'], ('A', '15'): ['811'], ('B', '25'): ['987']}, [('AX',), ('A', '15'), ('B', '25')]))
	>>> p1.resyncSetup(info = (set([1, 4]), set([2, 3]), False))
	>>> testPS(ParameterSource.createInstance('CombineParameterSource', p1, p2, pl))
	5
	Keys = KEY1 [trk], KEY2 [trk], LOOKUP [trk], GC_PARAM
	0 {0: True, 2: [], 'KEY1': 'AX', 'KEY2': '10', 'LOOKUP': '511', '!GC_PARAM': 0}
	1 {0: True, 2: [], 'KEY1': 'AY', 'KEY2': '15', 'LOOKUP': '811', '!GC_PARAM': 1}
	2 {0: True, 2: [], 'KEY1': 'AZ', 'KEY2': '20', '!GC_PARAM': 2}
	3 {0: True, 2: [], 'KEY1': 'BX', 'KEY2': '25', 'LOOKUP': '987', '!GC_PARAM': 3}
	4 {0: True, 2: [], 'KEY1': 'BY', 'KEY2': '30', '!GC_PARAM': 4}
	redo: [1, 4] disable: [2, 3] size: False

	>>> p1.resyncSetup(info = (set([1, 3]), set([2]), False))
	>>> p2.resyncSetup(info = (set([0]), set([1, 2]), False))
	>>> testPS(ParameterSource.createInstance('CrossParameterSource', p1, p2, pl))
	25
	Keys = KEY1 [trk], KEY2 [trk], LOOKUP [trk], GC_PARAM
	0 {0: True, 2: [], 'KEY1': 'AX', 'KEY2': '10', 'LOOKUP': '511', '!GC_PARAM': 0}
	1 {0: True, 2: [], 'KEY1': 'AY', 'KEY2': '10', '!GC_PARAM': 1}
	2 {0: True, 2: [], 'KEY1': 'AZ', 'KEY2': '10', '!GC_PARAM': 2}
	3 {0: True, 2: [], 'KEY1': 'BX', 'KEY2': '10', '!GC_PARAM': 3}
	4 {0: True, 2: [], 'KEY1': 'BY', 'KEY2': '10', '!GC_PARAM': 4}
	5 {0: True, 2: [], 'KEY1': 'AX', 'KEY2': '15', 'LOOKUP': '511', '!GC_PARAM': 5}
	6 {0: True, 2: [], 'KEY1': 'AY', 'KEY2': '15', 'LOOKUP': '811', '!GC_PARAM': 6}
	7 {0: True, 2: [], 'KEY1': 'AZ', 'KEY2': '15', 'LOOKUP': '811', '!GC_PARAM': 7}
	8 {0: True, 2: [], 'KEY1': 'BX', 'KEY2': '15', '!GC_PARAM': 8}
	9 {0: True, 2: [], 'KEY1': 'BY', 'KEY2': '15', '!GC_PARAM': 9}
	10 {0: True, 2: [], 'KEY1': 'AX', 'KEY2': '20', 'LOOKUP': '511', '!GC_PARAM': 10}
	11 {0: True, 2: [], 'KEY1': 'AY', 'KEY2': '20', '!GC_PARAM': 11}
	12 {0: True, 2: [], 'KEY1': 'AZ', 'KEY2': '20', '!GC_PARAM': 12}
	13 {0: True, 2: [], 'KEY1': 'BX', 'KEY2': '20', '!GC_PARAM': 13}
	14 {0: True, 2: [], 'KEY1': 'BY', 'KEY2': '20', '!GC_PARAM': 14}
	15 {0: True, 2: [], 'KEY1': 'AX', 'KEY2': '25', 'LOOKUP': '511', '!GC_PARAM': 15}
	16 {0: True, 2: [], 'KEY1': 'AY', 'KEY2': '25', '!GC_PARAM': 16}
	17 {0: True, 2: [], 'KEY1': 'AZ', 'KEY2': '25', '!GC_PARAM': 17}
	18 {0: True, 2: [], 'KEY1': 'BX', 'KEY2': '25', 'LOOKUP': '987', '!GC_PARAM': 18}
	19 {0: True, 2: [], 'KEY1': 'BY', 'KEY2': '25', 'LOOKUP': '987', '!GC_PARAM': 19}
	20 {0: True, 2: [], 'KEY1': 'AX', 'KEY2': '30', 'LOOKUP': '511', '!GC_PARAM': 20}
	21 {0: True, 2: [], 'KEY1': 'AY', 'KEY2': '30', '!GC_PARAM': 21}
	22 {0: True, 2: [], 'KEY1': 'AZ', 'KEY2': '30', '!GC_PARAM': 22}
	23 {0: True, 2: [], 'KEY1': 'BX', 'KEY2': '30', '!GC_PARAM': 23}
	24 {0: True, 2: [], 'KEY1': 'BY', 'KEY2': '30', '!GC_PARAM': 24}
	redo: [0, 1, 2, 3, 4, 6, 8, 11, 13, 16, 18, 21, 23] disable: [2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 22] size: False

	>>> pl = ParameterSource.createInstance('SwitchingLookupParameterSource', p1, 'LOOKUP', ('KEY1', 'KEY2'),
	... [createMatcher('start')],
	... ({('AX',): ['511', '235'], ('A',): ['811'], ('BY',): ['987', '634', '374']}, [('AX',), ('A',), ('BY',)]))
	>>> p1.resyncSetup(info = (set([1, 3]), set([2]), False))
	>>> testPS(pl)
	7
	Keys = KEY1 [trk], LOOKUP [trk], GC_PARAM
	0 {0: True, 2: [], 'KEY1': 'AX', 'LOOKUP': '511', '!GC_PARAM': 0}
	1 {0: True, 2: [], 'KEY1': 'AX', 'LOOKUP': '235', '!GC_PARAM': 1}
	2 {0: True, 2: [], 'KEY1': 'AY', 'LOOKUP': '811', '!GC_PARAM': 2}
	3 {0: True, 2: [], 'KEY1': 'AZ', 'LOOKUP': '811', '!GC_PARAM': 3}
	4 {0: True, 2: [], 'KEY1': 'BY', 'LOOKUP': '987', '!GC_PARAM': 4}
	5 {0: True, 2: [], 'KEY1': 'BY', 'LOOKUP': '634', '!GC_PARAM': 5}
	6 {0: True, 2: [], 'KEY1': 'BY', 'LOOKUP': '374', '!GC_PARAM': 6}
	redo: [2] disable: [3] size: False
	"""

class Test_MultiParameterSource:
	"""
	>>> p1 = ParameterSource.createInstance('SimpleParameterSource', 'A', [1, 2, 3])
	>>> p2 = ParameterSource.createInstance('SimpleParameterSource', 'B', ['M', 'N'])
	>>> p3 = ParameterSource.createInstance('SimpleParameterSource', 'C', ['x', 'y', 'z'])
	>>> p4 = ParameterSource.createInstance('CounterParameterSource', 'X', 100)
	>>> p5 = ParameterSource.createInstance('CounterParameterSource', 'Y', 900)

	>>> p1.resyncSetup(info = (set([1]), set([2]), False))
	>>> p2.resyncSetup(info = (set([0]), set([1]), False))
	>>> testPS(ParameterSource.createInstance('ZipShortParameterSource', p1, p2, p3))
	2
	Keys = A [trk], B [trk], C [trk], GC_PARAM
	0 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'x', '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'N', 'C': 'y', '!GC_PARAM': 1}
	redo: [0, 1] disable: [1, 2] size: False

	>>> p1.resyncSetup(info = (set([1]), set([2]), False))
	>>> p2.resyncSetup(info = (set([0]), set([1]), False))
	>>> testPS(ParameterSource.createInstance('ZipShortParameterSource', p1, p2, p3, p4, p5))
	2
	Keys = A [trk], B [trk], C [trk], X, Y, GC_PARAM
	0 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'x', '!X': 100, '!Y': 900, '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'N', 'C': 'y', '!X': 101, '!Y': 901, '!GC_PARAM': 1}
	redo: [0, 1] disable: [1, 2] size: False

	>>> p1.resyncSetup(info = (set([1]), set([2]), False))
	>>> p2.resyncSetup(info = (set([0]), set([1]), False))
	>>> testPS(ParameterSource.createInstance('ZipLongParameterSource', p1, p2, p3))
	3
	Keys = A [trk], B [trk], C [trk], GC_PARAM
	0 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'x', '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'N', 'C': 'y', '!GC_PARAM': 1}
	2 {0: True, 2: [], 'A': 3, 'C': 'z', '!GC_PARAM': 2}
	redo: [0, 1] disable: [1, 2] size: False

	>>> p1.resyncSetup(info = (set([1]), set([2]), False))
	>>> p2.resyncSetup(info = (set([0]), set([1]), False))
	>>> testPS(ParameterSource.createInstance('ChainParameterSource', p1, p2, p3))
	8
	Keys = A [trk], B [trk], C [trk], GC_PARAM
	0 {0: True, 2: [], 'A': 1, '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 2, '!GC_PARAM': 1}
	2 {0: True, 2: [], 'A': 3, '!GC_PARAM': 2}
	3 {0: True, 2: [], 'B': 'M', '!GC_PARAM': 3}
	4 {0: True, 2: [], 'B': 'N', '!GC_PARAM': 4}
	5 {0: True, 2: [], 'C': 'x', '!GC_PARAM': 5}
	6 {0: True, 2: [], 'C': 'y', '!GC_PARAM': 6}
	7 {0: True, 2: [], 'C': 'z', '!GC_PARAM': 7}
	redo: [1, 3] disable: [2, 4] size: False

	>>> p2.resyncSetup(info = (set([0]), set([1]), False))
	>>> testPS(ParameterSource.createInstance('RepeatParameterSource', p2, 3))
	6
	Keys = B [trk], GC_PARAM
	0 {0: True, 2: [], 'B': 'M', '!GC_PARAM': 0}
	1 {0: True, 2: [], 'B': 'N', '!GC_PARAM': 1}
	2 {0: True, 2: [], 'B': 'M', '!GC_PARAM': 2}
	3 {0: True, 2: [], 'B': 'N', '!GC_PARAM': 3}
	4 {0: True, 2: [], 'B': 'M', '!GC_PARAM': 4}
	5 {0: True, 2: [], 'B': 'N', '!GC_PARAM': 5}
	redo: [0, 2, 4] disable: [1, 3, 5] size: False

	>>> p1.resyncSetup(info = (set([1]), set([2]), False))
	>>> p2.resyncSetup(info = (set([0]), set([1]), False))
	>>> testPS(ParameterSource.createInstance('CrossParameterSource', p1, p2))
	6
	Keys = A [trk], B [trk], GC_PARAM
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', '!GC_PARAM': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', '!GC_PARAM': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', '!GC_PARAM': 3}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', '!GC_PARAM': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!GC_PARAM': 5}
	redo: [0, 1, 2, 4] disable: [2, 3, 4, 5] size: False

	>>> p1.resyncSetup(info = (set([1]), set([2]), False))
	>>> p2.resyncSetup(info = (set([0]), set([1]), False))
	>>> testPS(ParameterSource.createInstance('CrossParameterSource', p1, p2, p3))
	18
	Keys = A [trk], B [trk], C [trk], GC_PARAM
	0 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'x', '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', 'C': 'x', '!GC_PARAM': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', 'C': 'x', '!GC_PARAM': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', 'C': 'x', '!GC_PARAM': 3}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', 'C': 'x', '!GC_PARAM': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', 'C': 'x', '!GC_PARAM': 5}
	6 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'y', '!GC_PARAM': 6}
	7 {0: True, 2: [], 'A': 2, 'B': 'M', 'C': 'y', '!GC_PARAM': 7}
	8 {0: True, 2: [], 'A': 3, 'B': 'M', 'C': 'y', '!GC_PARAM': 8}
	9 {0: True, 2: [], 'A': 1, 'B': 'N', 'C': 'y', '!GC_PARAM': 9}
	10 {0: True, 2: [], 'A': 2, 'B': 'N', 'C': 'y', '!GC_PARAM': 10}
	11 {0: True, 2: [], 'A': 3, 'B': 'N', 'C': 'y', '!GC_PARAM': 11}
	12 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'z', '!GC_PARAM': 12}
	13 {0: True, 2: [], 'A': 2, 'B': 'M', 'C': 'z', '!GC_PARAM': 13}
	14 {0: True, 2: [], 'A': 3, 'B': 'M', 'C': 'z', '!GC_PARAM': 14}
	15 {0: True, 2: [], 'A': 1, 'B': 'N', 'C': 'z', '!GC_PARAM': 15}
	16 {0: True, 2: [], 'A': 2, 'B': 'N', 'C': 'z', '!GC_PARAM': 16}
	17 {0: True, 2: [], 'A': 3, 'B': 'N', 'C': 'z', '!GC_PARAM': 17}
	redo: [0, 1, 2, 4, 6, 7, 8, 10, 12, 13, 14, 16] disable: [2, 3, 4, 5, 8, 9, 10, 11, 14, 15, 16, 17] size: False

	>>> p1.resyncSetup(info = (set([1]), set([2]), False))
	>>> p2.resyncSetup(info = (set([0]), set([1]), False))
	>>> testPS(ParameterSource.createInstance('CrossParameterSource', p1, p5, p2))
	6
	Keys = A [trk], B [trk], Y, GC_PARAM
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!Y': 900, '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', '!Y': 901, '!GC_PARAM': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', '!Y': 902, '!GC_PARAM': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', '!Y': 903, '!GC_PARAM': 3}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', '!Y': 904, '!GC_PARAM': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!Y': 905, '!GC_PARAM': 5}
	redo: [0, 1, 2, 4] disable: [2, 3, 4, 5] size: False

	>>> p1.resyncSetup(info = (set([1]), set([2]), False))
	>>> p2.resyncSetup(info = (set([0]), set([1]), False))
	>>> testPS(ParameterSource.createInstance('CrossParameterSource', p5, p1, p2))
	6
	Keys = A [trk], B [trk], Y, GC_PARAM
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!Y': 900, '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', '!Y': 901, '!GC_PARAM': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', '!Y': 902, '!GC_PARAM': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', '!Y': 903, '!GC_PARAM': 3}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', '!Y': 904, '!GC_PARAM': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!Y': 905, '!GC_PARAM': 5}
	redo: [0, 1, 2, 4] disable: [2, 3, 4, 5] size: False

	>>> p6 = ParameterSource.createInstance('SimpleParameterSource', 'KEY1', lrange(10))
	>>> p6.resyncSetup(info = (set([1, 3]), set([2]), False))
	>>> testPS(ParameterSource.createInstance('RangeParameterSource', p6, 5))
	5
	Keys = KEY1 [trk], GC_PARAM
	0 {0: True, 2: [], 'KEY1': 5, '!GC_PARAM': 0}
	1 {0: True, 2: [], 'KEY1': 6, '!GC_PARAM': 1}
	2 {0: True, 2: [], 'KEY1': 7, '!GC_PARAM': 2}
	3 {0: True, 2: [], 'KEY1': 8, '!GC_PARAM': 3}
	4 {0: True, 2: [], 'KEY1': 9, '!GC_PARAM': 4}
	redo: [] disable: [] size: False

	>>> p6.resyncSetup(info = (set([1, 3]), set([2]), False))
	>>> testPS(ParameterSource.createInstance('RangeParameterSource', p6, None, 2))
	3
	Keys = KEY1 [trk], GC_PARAM
	0 {0: True, 2: [], 'KEY1': 0, '!GC_PARAM': 0}
	1 {0: True, 2: [], 'KEY1': 1, '!GC_PARAM': 1}
	2 {0: True, 2: [], 'KEY1': 2, '!GC_PARAM': 2}
	redo: [1] disable: [2] size: False

	>>> p6.resyncSetup(info = (set([1, 3]), set([0, 2]), False))
	>>> testPS(ParameterSource.createInstance('RangeParameterSource', p6, 1, 3))
	3
	Keys = KEY1 [trk], GC_PARAM
	0 {0: True, 2: [], 'KEY1': 1, '!GC_PARAM': 0}
	1 {0: True, 2: [], 'KEY1': 2, '!GC_PARAM': 1}
	2 {0: True, 2: [], 'KEY1': 3, '!GC_PARAM': 2}
	redo: [0, 2] disable: [1] size: False

	>>> px = ParameterSource.createInstance('SimpleParameterSource', 'A', [1, 2, 3])
	>>> px.resyncSetup(info = (set([1]), set([2]), False))
	>>> py = ParameterSource.createInstance('SimpleParameterSource', 'B', ['M', 'N'])
	>>> py.resyncSetup(info = (set([]), set([1]), False))
	>>> pz = ParameterSource.createInstance('SimpleParameterSource', 'C', ['x', 'y', 'z'])
	>>> pz.resyncSetup(info = (set([2]), set([1]), False))
	>>> eps = ParameterSource.createInstance('ErrorParameterSource', px, py, pz)
	>>> testPS(eps)
	6
	Keys = A [trk], B [trk], C [trk], GC_PARAM
	0 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'x', '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', 'C': 'x', '!GC_PARAM': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', 'C': 'x', '!GC_PARAM': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', 'C': 'x', '!GC_PARAM': 3}
	4 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'y', '!GC_PARAM': 4}
	5 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'z', '!GC_PARAM': 5}
	redo: [1, 5] disable: [2, 3, 4] size: False
	"""

class Test_FileParameterSources:
	"""
	>>> utils.removeFiles(['param.saved'])

	>>> p1 = ParameterSource.createInstance('SimpleParameterSource', 'A', [1, 2, 3])
	>>> p2 = ParameterSource.createInstance('SimpleParameterSource', 'B', ['M', 'N'])
	>>> p3 = ParameterSource.createInstance('CounterParameterSource', 'X', 100)

	>>> p1.resyncSetup(info = (set([1]), set([2]), False))
	>>> p2.resyncSetup(info = (set([0]), set([1]), False))
	>>> ps = ParameterSource.createInstance('CrossParameterSource', p1, p2, p3)
	>>> testPS(ps)
	6
	Keys = A [trk], B [trk], X, GC_PARAM
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!X': 100, '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', '!X': 101, '!GC_PARAM': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', '!X': 102, '!GC_PARAM': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', '!X': 103, '!GC_PARAM': 3}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', '!X': 104, '!GC_PARAM': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!X': 105, '!GC_PARAM': 5}
	redo: [0, 1, 2, 4] disable: [2, 3, 4, 5] size: False
	>>> GCDumpParameterSource.write('param.saved', ParameterAdapter(create_config(), ps))

	>>> pl = ParameterSource.createInstance('GCDumpParameterSource', 'param.saved')
	>>> testPS(pl)
	6
	Keys = A [trk], B [trk], GC_PARAM
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', '!GC_PARAM': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', '!GC_PARAM': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', '!GC_PARAM': 3}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', '!GC_PARAM': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!GC_PARAM': 5}
	redo: [] disable: [] size: False

	>>> utils.removeFiles(['param.saved'])
	"""

class Test_DataParameterSourceReal:
	"""
	>>> utils.removeFiles(['datasetcache.dat', 'datasetmap.tar'])
	>>> dataSource = DataProvider.createInstance('ListProvider', create_config(), '../datasets/dataE.dbs', None)
	>>> config = create_config(configDict = {'dataset': {'events per job': 10}})
	>>> dataSplit = DataSplitter.createInstance('EventBoundarySplitter', config)
	>>> pproc_basic = PartitionProcessor.createInstance('BasicPartitionProcessor', config)
	>>> pproc_se = PartitionProcessor.createInstance('LocationPartitionProcessor', config)
	>>> dataProc = PartitionProcessor.createInstance('MultiPartitionProcessor', config, [pproc_basic, pproc_se])
	>>> ps = ParameterSource.createInstance('DataParameterSource', '.', 'dataset', dataSource, dataSplit, dataProc, False)
	log:Block /MY/DATASET#easy3 is not available at any site!
	>>> ps.getNeededDataKeys()
	['FILE_NAMES', 'SKIP_EVENTS', 'MAX_EVENTS']
	>>> testPS(ps, True)
	log:Block /MY/DATASET#easy3 is not available at any site!
	log:Block /MY/DATASET#easy3 is not available at any site!
	9
	Keys = DATASETBLOCK, DATASETID, DATASETNICK, DATASETPATH, DATASETSPLIT [trk], FILE_NAMES, MAX_EVENTS, SKIP_EVENTS, GC_PARAM
	0 {0: True, 2: [(8, ['SE4'])], '!DATASETBLOCK': 'easy1', '!DATASETID': None, '!DATASETNICK': 'MY_DATASET', '!DATASETPATH': '/MY/DATASET', 'DATASETSPLIT': 0, '!FILE_NAMES': '/path/file0', '!MAX_EVENTS': 10, '!SKIP_EVENTS': 0, '!GC_PARAM': 0}
	1 {0: True, 2: [(8, ['SE4'])], '!DATASETBLOCK': 'easy1', '!DATASETID': None, '!DATASETNICK': 'MY_DATASET', '!DATASETPATH': '/MY/DATASET', 'DATASETSPLIT': 1, '!FILE_NAMES': '/path/file1 /path/file2', '!MAX_EVENTS': 10, '!SKIP_EVENTS': 0, '!GC_PARAM': 1}
	2 {0: True, 2: [(8, ['SE4'])], '!DATASETBLOCK': 'easy1', '!DATASETID': None, '!DATASETNICK': 'MY_DATASET', '!DATASETPATH': '/MY/DATASET', 'DATASETSPLIT': 2, '!FILE_NAMES': '/path/file2', '!MAX_EVENTS': 10, '!SKIP_EVENTS': 5, '!GC_PARAM': 2}
	3 {0: True, 2: [], '!DATASETBLOCK': 'easy2', '!DATASETID': None, '!DATASETNICK': 'MY_DATASET', '!DATASETPATH': '/MY/DATASET', 'DATASETSPLIT': 3, '!FILE_NAMES': '/path/file3', '!MAX_EVENTS': 10, '!SKIP_EVENTS': 0, '!GC_PARAM': 3}
	4 {0: True, 2: [], '!DATASETBLOCK': 'easy2', '!DATASETID': None, '!DATASETNICK': 'MY_DATASET', '!DATASETPATH': '/MY/DATASET', 'DATASETSPLIT': 4, '!FILE_NAMES': '/path/file5', '!MAX_EVENTS': 5, '!SKIP_EVENTS': 0, '!GC_PARAM': 4}
	5 {0: False, 2: [(8, [])], '!DATASETBLOCK': 'easy3', '!DATASETID': None, '!DATASETNICK': 'MY_DATASET', '!DATASETPATH': '/MY/DATASET', 'DATASETSPLIT': 5, '!FILE_NAMES': '/path/file6', '!MAX_EVENTS': 10, '!SKIP_EVENTS': 0, '!GC_PARAM': 5}
	6 {0: False, 2: [(8, [])], '!DATASETBLOCK': 'easy3', '!DATASETID': None, '!DATASETNICK': 'MY_DATASET', '!DATASETPATH': '/MY/DATASET', 'DATASETSPLIT': 6, '!FILE_NAMES': '/path/file7 /path/file8', '!MAX_EVENTS': 10, '!SKIP_EVENTS': 0, '!GC_PARAM': 6}
	7 {0: False, 2: [(8, [])], '!DATASETBLOCK': 'easy3', '!DATASETID': None, '!DATASETNICK': 'MY_DATASET', '!DATASETPATH': '/MY/DATASET', 'DATASETSPLIT': 7, '!FILE_NAMES': '/path/file8 /path/file9', '!MAX_EVENTS': 10, '!SKIP_EVENTS': 5, '!GC_PARAM': 7}
	8 {0: False, 2: [(8, [])], '!DATASETBLOCK': 'easy3', '!DATASETID': None, '!DATASETNICK': 'MY_DATASET', '!DATASETPATH': '/MY/DATASET', 'DATASETSPLIT': 8, '!FILE_NAMES': '/path/file9', '!MAX_EVENTS': 10, '!SKIP_EVENTS': 5, '!GC_PARAM': 8}
	redo: [1] disable: [2] size: False

	>>> utils.removeFiles(['datasetcache.dat', 'datasetmap.tar'])
	>>> config2 = create_config(configDict = {'dataset': {'files per job': 10}})
	>>> dataSplit = DataSplitter.createInstance('FileBoundarySplitter', config2)
	>>> ps2 = ParameterSource.createInstance('DataParameterSource', '.', 'dataset', dataSource, dataSplit, pproc_basic, False)
	>>> list(ps2.getNeededDataKeys())
	['FILE_NAMES']
	>>> utils.removeFiles(['datasetcache.dat', 'datasetmap.tar'])
	"""

class Test_DataParameterSource:
	"""
	>>> utils.removeFiles(['dummycache.dat', 'dummymap.tar', 'dataset.tmp'])
	>>> config = create_config(configDict = {'datasetx': {'events per job': 3}})
	>>> data_bl = ss2bl('AABBCCCD')
	>>> updateDS(data_bl, '')
	>>> dataSource = DataProvider.createInstance('ListProvider', config, 'dataset.tmp', 'nick')
	>>> dataSplit = DataSplitter.createInstance('EventBoundarySplitter', config)
	>>> dataProc = DataSplitProcessorTest(config)
	>>> pd = ParameterSource.createInstance('DataParameterSource', '.', 'dummy', dataSource, dataSplit, dataProc, False)
	>>> pd.getNeededDataKeys()
	[]

	>>> testPS(pd) # AAB BCC CD
	3
	Keys = EVT, FN, SID [trk], SKIP, GC_PARAM
	0 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, '!GC_PARAM': 0}
	1 {0: True, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, '!GC_PARAM': 1}
	2 {0: True, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, '!GC_PARAM': 2}
	redo: [] disable: [] size: False

	>>> updateDS(data_bl, 'D:2', pd)
	>>> pd.resync() == (set([]), set([]), True)
	True
	>>> testPS(pd) # AAB BCC CD D
	4
	Keys = EVT, FN, SID [trk], SKIP, GC_PARAM
	0 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, '!GC_PARAM': 0}
	1 {0: True, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, '!GC_PARAM': 1}
	2 {0: True, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, '!GC_PARAM': 2}
	3 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 3, '!SKIP': 1, '!GC_PARAM': 3}
	redo: [] disable: [] size: False

	>>> updateDS(data_bl, 'D:2 C:1', pd)
	>>> pd.resync() == (set([]), set([1, 2]), True)
	True
	>>> testPS(pd) # AAB BCc cD D BC D
	6
	Keys = EVT, FN, SID [trk], SKIP, GC_PARAM
	0 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, '!GC_PARAM': 0}
	1 {0: False, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, '!GC_PARAM': 1}
	2 {0: False, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, '!GC_PARAM': 2}
	3 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 3, '!SKIP': 1, '!GC_PARAM': 3}
	4 {0: True, 2: [], '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, '!GC_PARAM': 4}
	5 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, '!GC_PARAM': 5}
	redo: [] disable: [] size: False

	>>> updateDS(data_bl, 'C:1', pd)
	>>> pd.resync() == (set([]), set([3]), False)
	True
	>>> testPS(pd) # AAB BCc cD d BC D
	6
	Keys = EVT, FN, SID [trk], SKIP, GC_PARAM
	0 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, '!GC_PARAM': 0}
	1 {0: False, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, '!GC_PARAM': 1}
	2 {0: False, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, '!GC_PARAM': 2}
	3 {0: False, 2: [], '!EVT': 0, '!FN': 'D', 'SID': 3, '!SKIP': 1, '!GC_PARAM': 3}
	4 {0: True, 2: [], '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, '!GC_PARAM': 4}
	5 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, '!GC_PARAM': 5}
	redo: [] disable: [] size: False

	>>> updateDS(data_bl, '', pd)
	>>> pd.resync() == (set([]), set([]), True)
	True
	>>> testPS(pd) # AAB BCc cD d BC D CC
	7
	Keys = EVT, FN, SID [trk], SKIP, GC_PARAM
	0 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, '!GC_PARAM': 0}
	1 {0: False, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, '!GC_PARAM': 1}
	2 {0: False, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, '!GC_PARAM': 2}
	3 {0: False, 2: [], '!EVT': 0, '!FN': 'D', 'SID': 3, '!SKIP': 1, '!GC_PARAM': 3}
	4 {0: True, 2: [], '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, '!GC_PARAM': 4}
	5 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, '!GC_PARAM': 5}
	6 {0: True, 2: [], '!EVT': 2, '!FN': 'C', 'SID': 6, '!SKIP': 1, '!GC_PARAM': 6}
	redo: [] disable: [] size: False

	>>> utils.removeFiles(['dummycache.dat', 'dummymap.tar', 'dataset.tmp'])
	"""

run_test()
