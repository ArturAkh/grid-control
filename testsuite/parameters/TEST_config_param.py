#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import cmp_obj, create_config, run_test, try_catch
from grid_control.parameters.config_param import ParameterConfig, parseParameterOption, parseTuple

class Test_ParameterConfigParser:
	"""
	>>> parseTuple('()', ',')
	()
	>>> parseTuple('(,)', ',')
	('', '')
	>>> parseTuple('(, )', ',')
	('', '')
	>>> parseTuple('( ,)', ',')
	('', '')
	>>> parseTuple('( , )', ',')
	('', '')
	>>> parseTuple('(,,)', ',')
	('', '', '')

	>>> parseParameterOption('a')
	('a', None)
	>>> parseParameterOption('a1')
	('a1', None)
	>>> parseParameterOption('a b')
	('a', 'b')
	>>> parseParameterOption('a1 b1')
	('a1', 'b1')
	>>> parseParameterOption('a b c')
	('a', 'b c')
	>>> parseParameterOption('a1 b1 c1')
	('a1', 'b1 c1')
	>>> parseParameterOption('(a) b c')
	(('a',), 'b c')
	>>> parseParameterOption('(a1) b1 c1')
	(('a1',), 'b1 c1')
	>>> parseParameterOption('(a_b) b_c c_d')
	(('a_b',), 'b_c c_d')
	>>> parseParameterOption('(a_b b_c) c_d')
	(('a_b', 'b_c'), 'c_d')
	>>> parseParameterOption('(a b)')
	(('a', 'b'), None)
	>>> parseParameterOption('(a1 b1)')
	(('a1', 'b1'), None)
	>>> parseParameterOption('(a b) c')
	(('a', 'b'), 'c')
	>>> parseParameterOption('(a1 b1) c1')
	(('a1', 'b1'), 'c1')

	>>> parseParameterOption('a b c')
	('a', 'b c')
	>>> parseParameterOption('(a) b c')
	(('a',), 'b c')
	>>> parseParameterOption('(a b)')
	(('a', 'b'), None)
	>>> parseParameterOption('(a b) c')
	(('a', 'b'), 'c')
	"""

class Test_ParameterConfig:
	"""
	>>> pc = ParameterConfig(create_config(configFile='test.conf'), False)

	>>> pc.getParameter('a')
	['1', '2', '3', '4', '5 6', '7', '8', '9 0']
	>>> pc.getParameter('b')
	['a b c d', 'e f g h']
	>>> pc.getParameter('e')
	[2, 4, 6, 8]

	>>> pc.getParameter('ss')
	['a b c', 'd\\ne f', 'g h']

	>>> pc.getParameter('c') == ({('Y',): [987], None: [123], ('X',): [511]}, [('X',), ('Y',)])
	True
	>>> pc.getParameter('d') == ({('A',): ['511', '456'], ('B',): ['987', '823', '177']}, [('A',), ('B',)])
	True
	>>> pc.getParameter('g') == ({('A',): ['511', '456'], ('B',): ['987 823', '177'], None: ['124', '634']}, [('A',), ('B',)])
	True
	>>> pc.getParameter('h') == ({('A',): ['511', '456'], ('B',): ['987', '823', '177'], None: ['124', '634']}, [('A',), ('B',)])
	True

	>>> pc.getParameter('dd')
	['A => 511 456', 'B => 987 823 177']

	>>> pc.getParameter('x')
	[0, 3, 6, 11]
	>>> pc.getParameter('y')
	['2', '3', '4 1', '2']

	>>> pc.getParameter('x1')
	['1', '3']
	>>> pc.getParameter('y2')
	['2', '4']

	>>> pc.getParameter('t1')
	[1, 1, '1,']
	>>> pc.getParameter('t2')
	['"2"', '"2,3"', '","']
	>>> pc.getParameter('t3')
	[3, 4, '']

	>>> pc.getParameter('w')
	['1', '2', '3', '4', '5']
	>>> pc.getParameter('z')
	['2', '3', '4', '5', '6']

	>>> pc.getParameter('s')
	['1', '8']
	>>> pc.getParameter('j')
	['2,3', '2']
	>>> pc.getParameter('f')
	[4, 1]

	>>> pc.getParameter('t4')
	['', '', '1', '1', '', '', '1', '1']
	>>> pc.getParameter('t5')
	['', '1', '', '1', '', '1', '', '1']

	>>> pc.getParameter('TEST_1')
	[1, 8]
	>>> pc.getParameter('1_TEST')
	['2,3', '2']
	>>> pc.getParameter('TEST_TEST')
	['4', '1']

	>>> pm1 = pc.getParameter('m1')
	>>> cmp_obj(pm1, ({('J', 'K'): ['6', '7'], ('K', 'L'): ['1', '2', '3']}, [('K', 'L'), ('J', 'K')]))
	>>> pn1 = pc.getParameter('n1')
	>>> cmp_obj(pn1, ({('J', 'K'): ['7', '8'], ('K', 'L'): ['2', '3', '4']}, [('K', 'L'), ('J', 'K')]))

	>>> pm = pc.getParameter('m')
	>>> cmp_obj(pm, ({('J', 'K'): ['6 7'], ('K', 'L'): ['1 2 3', '6 7 1']}, [('K', 'L'), ('J', 'K')]))
	>>> pn = pc.getParameter('n')
	>>> cmp_obj(pn, ({('J', 'K'): ["'Y'"], ('K', 'L'): ["'X'", "'Z'"]}, [('K', 'L'), ('J', 'K')]))
	>>> try_catch(lambda: pc.getParameter('o'), 'ConfigError', 'expands to multiple variable entries')
	caught
	>>> try_catch(lambda: pc.getParameter('p'), 'ConfigError', 'Variable p is undefined')
	caught
	"""

run_test()
