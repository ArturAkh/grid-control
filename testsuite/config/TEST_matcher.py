#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import create_config, run_test
from grid_control.config.matcher_base import DictLookup, ListFilter, ListOrder, Matcher

def testMatch(m, selector, value):
	r1 = m.matcher(value, selector)
	r2 = m.matchWith(selector).match(value)
	assert(r1 == r2)
	print(r1)

def testListFilter(name, m, selector, value, order = ListOrder.source, key = None, negate = False):
	lf = ListFilter.createInstance(name, selector, m, order, key, negate)
	return lf.filterList(value)

class Test_Matcher:
	"""
	>>> config = create_config()

	>>> m1 = Matcher.createInstance('StartMatcher', config, 'prefix')
	>>> testMatch(m1, 'A', 'ABC')
	1
	>>> testMatch(m1, 'C', 'ABC')
	-1
	>>> testMatch(m1, 'ABC', 'ABC')
	1

	>>> m2 = Matcher.createInstance('EndMatcher', config, 'prefix')
	>>> testMatch(m2, 'A', 'ABC')
	-1
	>>> testMatch(m2, 'C', 'ABC')
	1
	>>> testMatch(m2, 'ABC', 'ABC')
	1

	>>> m3 = Matcher.createInstance('EqualMatcher', config, 'prefix')
	>>> testMatch(m3, 'A', 'ABC')
	-1
	>>> testMatch(m3, 'C', 'ABC')
	-1
	>>> testMatch(m3, 'ABC', 'ABC')
	1

	>>> m4 = Matcher.createInstance('ExprMatcher', config, 'prefix')
	>>> testMatch(m4, '"A" in value', 'ABC')
	1
	>>> testMatch(m4, '"X" in value', 'ABC')
	-1
	>>> testMatch(m4, '"ABC" in value', 'ABC')
	1

	>>> m5 = Matcher.createInstance('RegexMatcher', config, 'prefix')
	>>> testMatch(m5, 'A..', 'ABC')
	1
	>>> testMatch(m5, '.BA', 'ABC')
	-1
	>>> testMatch(m5, '..C', 'ABC')
	1

	>>> m6 = Matcher.createInstance('blackwhite', config, 'prefix')
	>>> testMatch(m6, '-A AB', 'ABC')
	2
	>>> testMatch(m6, '-A AC', 'ABC')
	-1
	>>> testMatch(m6, 'AB -ABC', 'A')
	0
	>>> testMatch(m6, 'ABC', 'ABC')
	1

	>>> m7 = Matcher.createInstance('ShellStyleMatcher', config, 'prefix')
	>>> testMatch(m7, 'A*', 'ABC')
	1
	>>> testMatch(m7, '*BA', 'ABC')
	-1
	>>> testMatch(m7, '*C', 'ABC')
	1
	"""

class Test_MatchList:
	"""
	>>> config = create_config()
	>>> m1 = Matcher.createInstance('StartMatcher', config, 'prefix')
	>>> m2 = Matcher.createInstance('blackwhite', config, 'prefix')

	>>> testListFilter('strict', m1, 'AB', ['A', 'AB', 'ABC', 'ABCD', 'XAB'])
	['AB', 'ABC', 'ABCD']
	>>> testListFilter('strict', m2, 'AB -ABC', ['A', 'AB', 'ABC', 'ABCD', 'XAB', 'ABX'])
	['AB', 'ABX']
	>>> testListFilter('strict', m2, 'AB -ABC', ['X', 'Y', 'Z'])
	[]

	>>> testListFilter('try_strict', m1, 'AB', ['A', 'AB', 'ABC', 'ABCD', 'XAB'])
	['AB', 'ABC', 'ABCD']
	>>> testListFilter('try_strict', m2, 'AB -ABC', ['A', 'AB', 'ABC', 'ABCD', 'XAB', 'ABX'])
	['AB', 'ABX']
	>>> testListFilter('try_strict', m2, 'AB -ABC', ['X', 'Y', 'Z'])
	['X', 'Y', 'Z']

	>>> testListFilter('weak', m1, 'AB', ['A', 'AB', 'ABC', 'ABCD', 'XAB'])
	['AB', 'ABC', 'ABCD']
	>>> testListFilter('weak', m2, 'AB -ABC', ['A', 'AB', 'ABC', 'ABCD', 'XAB', 'ABX'])
	['A', 'AB', 'XAB', 'ABX']
	>>> testListFilter('weak', m2, 'AB -ABC', ['X', 'Y', 'Z'])
	['X', 'Y', 'Z']

	>>> testListFilter('strict', m2, 'A -AB ABCD', ['AB', 'ABC', 'B', 'ABCD', 'A'])
	['ABCD', 'A']
	>>> testListFilter('strict', m2, 'A -AB ABCD', ['AB', 'ABC', 'B', 'ABCD', 'A'], ListOrder.matcher)
	['A', 'ABCD']
	>>> testListFilter('strict', m2, 'A -AB ABCD', ['AB', 'ABC', 'B', 'ABCD', 'A'], negate = True)
	['AB', 'ABC']

	>>> testListFilter('strict', m2, 'A -AB ABCD', [{'data': 'AB'}, {'data': 'ABC'}, {'data': 'B'}, {'data': 'ABCD'}, {'data': 'A'}], key = lambda x: x['data'])
	[{'data': 'ABCD'}, {'data': 'A'}]
	>>> testListFilter('strict', m2, 'A -AB ABCD', [{'data': 'AB'}, {'data': 'ABC'}, {'data': 'B'}, {'data': 'ABCD'}, {'data': 'A'}], key = lambda x: x['data'], order = ListOrder.matcher)
	[{'data': 'A'}, {'data': 'ABCD'}]
	>>> testListFilter('strict', m2, 'A -AB ABCD', [{'data': 'AB'}, {'data': 'ABC'}, {'data': 'B'}, {'data': 'ABCD'}, {'data': 'A'}], key = lambda x: x['data'], negate = True)
	[{'data': 'AB'}, {'data': 'ABC'}]
	"""

class Test_Lookup:
	"""
	>>> config = create_config()
	>>> m1 = Matcher.createInstance('StartMatcher', config, 'prefix')
	>>> d1 = {'A': 1, 'B': 2, 'AB': 3, 'ABC': 4, None: 5}
	>>> o1 = ['A', 'ABC', 'AB', 'B']
	>>> DictLookup(d1, o1, m1, only_first = True, always_default = False).lookup('A')
	1
	>>> DictLookup(d1, o1, m1, only_first = True, always_default = False).lookup('A', is_selector = False)
	1

	>>> DictLookup(d1, o1, m1, only_first = False, always_default = False).lookup('A')
	[1, 4, 3]
	>>> DictLookup(d1, o1, m1, only_first = False, always_default = False).lookup('A', is_selector = False)
	[1]

	>>> DictLookup(d1, o1, m1, only_first = False, always_default = True).lookup('A')
	[1, 4, 3, 5]
	>>> DictLookup(d1, o1, m1, only_first = False, always_default = True).lookup('A', is_selector = False)
	[1, 5]

	>>> DictLookup(d1, o1, m1, only_first = True, always_default = True).lookup('A')
	1
	>>> DictLookup(d1, o1, m1, only_first = True, always_default = True).lookup('A', is_selector = False)
	1

	>>> DictLookup(d1, o1, m1, only_first = True, always_default = False).lookup('AB')
	4
	>>> DictLookup(d1, o1, m1, only_first = True, always_default = False).lookup('AB', is_selector = False)
	1

	>>> DictLookup(d1, o1, m1, only_first = False, always_default = False).lookup('AB')
	[4, 3]
	>>> DictLookup(d1, o1, m1, only_first = False, always_default = False).lookup('AB', is_selector = False)
	[1, 3]

	>>> DictLookup(d1, o1, m1, only_first = False, always_default = True).lookup('AB')
	[4, 3, 5]
	>>> DictLookup(d1, o1, m1, only_first = False, always_default = True).lookup('AB', is_selector = False)
	[1, 3, 5]

	>>> DictLookup(d1, o1, m1, only_first = True, always_default = True).lookup('AB')
	4
	>>> DictLookup(d1, o1, m1, only_first = True, always_default = True).lookup('AB', is_selector = False)
	1

	"""

class Test_ConfigWrapper:
	"""
	>>> config = create_config()
	>>> f = config.getFilter('foo filter', 'A B -C', defaultMatcher = 'blackwhite', defaultFilter = 'weak')
	>>> f.filterList(None)
	['A', 'B']
	>>> f.filterList(['A', 'C'])
	['A']
	>>> f.filterList(['X', 'Y'])
	['X', 'Y']
	>>> l = config.getLookup('bar lookup', {'A': 1, 'BC': 4, 'B': 2, 'AB': 3})
	>>> l.lookup('A')
	'1'
	>>> l.lookup('AB')
	'3'
	>>> l.lookup('B') # dict is sorted by keys
	'2'
	>>> l = config.getLookup('bar lookup', {'A': 1, 'BC': 4, 'B': 2, 'AB': 3}, single = False)
	>>> l.lookup('A')
	['1', '3']
	>>> l.lookup('AB')
	['3']
	>>> l.lookup('B') # dict is sorted by keys
	['2', '4']
	>>> l = config.getLookup('bar lookup', {'A': 1, 'BC': 4, 'B': 2, 'AB': 3}, single = False)
	>>> l.lookup('A')
	['1', '3']
	>>> l.lookup('AB')
	['3']
	>>> l.lookup('B') # dict is sorted by keys
	['2', '4']
	>>> l = config.getLookup('foobar lookup', {None: 0, 'A': 1, 'BC': 4, 'B': 2, 'AB': 3}, single = False)
	>>> l.lookup(None)
	['0']
	>>> l.lookup(None, is_selector = False)
	['0']
	>>> l.lookup('A')
	['1', '3']
	>>> l.lookup('A', is_selector = False)
	['1']
	>>> l.lookup('B')
	['2', '4']
	>>> l.lookup('B', is_selector = False)
	['2']
	"""

run_test()
