#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), ''))
__import__('testFwk').setup(__file__)
# - prolog marker
import os
from testFwk import remove_files, run_test
from grid_control import utils
from grid_control.utils.file_objects import SafeFile, ZipFile
from grid_control.utils.gc_itertools import ichain, lchain, tchain
from grid_control.utils.parsing import parseDict, parseTime
from python_compat import imap, irange, lrange, sorted

class Test_SafeFile:
	"""
	>>> f = SafeFile('test', 'w')
	>>> f.write('hallo')
	>>> f.close()
	>>> os.path.exists('test')
	True
	>>> remove_files(['test'])
	"""

class Test_Chain:
	"""
	>>> list(ichain([lrange(0,5), lrange(5,10)]))
	[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
	>>> list(lchain([lrange(0,5), lrange(5,10)]))
	[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
	>>> sorted(tchain([lrange(0,5), lrange(5,10)]))
	[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
	"""

class Test_FileObjects:
	"""
	>>> fw = ZipFile('test.gz', 'w')
	>>> fw.write('Hallo Welt')
	>>> fw.close()
	>>> fr = ZipFile('test.gz', 'r')
	>>> fr.readline()
	'Hallo Welt'
	>>> remove_files(['test.gz'])
	"""

qs1 = 'a "" "c" \'d b\' \'d "x" b\''
qr1 = ['a', ' ', '""', ' ', '"c"', ' ', "'d b'", ' ', '\'d "x" b\'']
qs2 = 'a b c "d e" f g h \'asd "b"\''
qr2 = ['a', ' ', 'b', ' ', 'c', ' ', '"d e"', ' ', 'f', ' ', 'g', ' ', 'h', ' ', '\'asd "b"\'']

class Test_Utils:
	"""
	>>> parseDict(' 1\\n1 => 5\\n2=>4', int) ==\
	({'1': 5, '2': 4, None: 1}, ['1', '2'])
	True
	>>> parseDict(' 1\\n1 => 5\\n2=>4', parserKey=int) ==\
	({1: '5', 2: '4', None: '1'}, [1, 2])
	True
	>>> parseDict(' 1 2 3\\n 4 5 6\\n1 => 5\\n2=>3 4\\n63 1') ==\
	({'1': '5', '2': '3 4\\n63 1', None: '1 2 3\\n4 5 6'}, ['1', '2'])
	True

	>>> parseTime('')
	-1
	>>> parseTime(None)
	-1
	>>> parseTime('1:00')
	3600
	>>> parseTime('1:00:00')
	3600

	>>> list(utils.split_quotes(qs1)) == qr1
	True
	>>> list(utils.split_quotes(qs2)) == qr2
	True

	>>> list(utils.split_brackets('a[-1]x'))
	['a', '[-1]', 'x']
	>>> list(utils.split_brackets('a[(-1)+(4)+[2]]x'))
	['a', '[(-1)+(4)+[2]]', 'x']
	>>> list(utils.split_brackets('()[]{}([])[({})]'))
	['()', '[]', '{}', '([])', '[({})]']

	>>> list(utils.split_advanced('', lambda t: t == ',', lambda t: False))
	[]
	>>> list(utils.split_advanced('a', lambda t: t == ',', lambda t: False))
	['a']
	>>> list(utils.split_advanced(' a ', lambda t: t == ',', lambda t: False))
	[' a ']
	>>> list(utils.split_advanced(' a , b ', lambda t: t == ',', lambda t: False))
	[' a ', ' b ']
	>>> list(utils.split_advanced(' (a) ', lambda t: t == ',', lambda t: False))
	[' (a) ']
	>>> list(utils.split_advanced(' ( a ) ', lambda t: t == ',', lambda t: False))
	[' ( a ) ']
	>>> list(utils.split_advanced(' ( a , b ) ', lambda t: t == ',', lambda t: False))
	[' ( a , b ) ']
	>>> list(utils.split_advanced(' ( a , b ) ', lambda t: t == '|', lambda t: False))
	[' ( a , b ) ']

	>>> list(utils.split_advanced('', lambda t: t == ' ', lambda t: True))
	[]
	>>> list(utils.split_advanced('a', lambda t: t == ' ', lambda t: True))
	['a']
	>>> list(utils.split_advanced('()', lambda t: t == ' ', lambda t: True))
	['()']
	>>> list(utils.split_advanced('(a)', lambda t: t == ' ', lambda t: True))
	['(a)']
	>>> list(utils.split_advanced('(a b (c))', lambda t: t == ' ', lambda t: True))
	['(a b (c))']
	>>> list(utils.split_advanced('(a b (c)) ((d))', lambda t: t == ' ', lambda t: True))
	['(a b (c))', ' ', '((d))']
	>>> list(utils.split_advanced(' (c d )  (f g) ()', lambda t: t == ' ', lambda t: True))
	['', ' ', '(c d )', ' ', '', ' ', '(f g)', ' ', '()']
	>>> list(utils.split_advanced('ac b (c d ) e (f g) h (i) (j k) () h', lambda t: t == ' ', lambda t: True))
	['ac', ' ', 'b', ' ', '(c d )', ' ', 'e', ' ', '(f g)', ' ', 'h', ' ', '(i)', ' ', '(j k)', ' ', '()', ' ', 'h']
	>>> list(utils.split_advanced('ac b (c d ) e (f g) h (i) (j k) () h', lambda t: t == ' ', lambda t: False))
	['ac', 'b', '(c d )', 'e', '(f g)', 'h', '(i)', '(j k)', '()', 'h']

	>>> acc5 = lambda x, buf: len(buf) == 5
	>>> list(utils.accumulate([], [], acc5, opAdd = lambda x, y: x + [y]))
	[]
	>>> list(utils.accumulate(lrange(1), [], acc5, opAdd = lambda x, y: x + [y]))
	[[0]]
	>>> list(utils.accumulate(lrange(4), [], acc5, opAdd = lambda x, y: x + [y]))
	[[0, 1, 2, 3]]
	>>> list(utils.accumulate(lrange(5), [], acc5, opAdd = lambda x, y: x + [y]))
	[[0, 1, 2, 3, 4]]
	>>> list(utils.accumulate(lrange(6), [], acc5, opAdd = lambda x, y: x + [y]))
	[[0, 1, 2, 3, 4], [5]]
	>>> list(utils.accumulate(lrange(24), [], acc5, opAdd = lambda x, y: x + [y]))
	[[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14], [15, 16, 17, 18, 19], [20, 21, 22, 23]]
	>>> list(utils.accumulate(lrange(25), [], acc5, opAdd = lambda x, y: x + [y]))
	[[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14], [15, 16, 17, 18, 19], [20, 21, 22, 23, 24]]
	>>> list(utils.accumulate(lrange(26), [], acc5, opAdd = lambda x, y: x + [y]))
	[[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14], [15, 16, 17, 18, 19], [20, 21, 22, 23, 24], [25]]

	>>> utils.wrapList(imap(str, irange(20)), 20)
	'0, 1, 2, 3, 4, 5, 6,\\n7, 8, 9, 10, 11, 12,\\n13, 14, 15, 16, 17,\\n18, 19'

	>>> utils.optSplit('abc # def:ghi', ['#', ':'])
	('abc', 'def', 'ghi')
	>>> utils.optSplit('abcghi#def', ['#', ':'])
	('abcghi', 'def', '')
	>>> utils.optSplit('abc: def#test :ghi', [':', '#', ':'])
	('abc', 'def', 'test', 'ghi')
	>>> utils.optSplit('abc', [':', ':'])
	('abc', '', '')
	"""

run_test()
