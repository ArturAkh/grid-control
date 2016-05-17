#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import create_config, remove_files, run_test
from grid_control.parameters import ParameterInfo, ParameterSource
from grid_control.parameters.padapter import TrackedParameterAdapter
from grid_control.parameters.psource_meta import CrossParameterSource
from python_compat import lfilter, sorted

def s2ps(**kwargs):
	ps_list = []
	for key, values in sorted(kwargs.items()):
		value_list = []
		for value in values.split(' '):
			if value.startswith('!'):
				value_list.append({key: value.lstrip('!'), ParameterInfo.ACTIVE: False})
			else:
				value_list.append({key: value})
		ps_list.append(ParameterSource.createInstance('InternalParameterSource', value_list, [key]))
	return CrossParameterSource(*ps_list)

def testPAS(ps):
	config = create_config(configDict={'global': {'workdir': '.'}, 'state': {'#resync': True}})
	pa = TrackedParameterAdapter(config, ps)
	line_1 = '   '
	params = {}
	keys = []
	ps.fillParameterKeys(keys)
	keys = lfilter(lambda k: not k.untracked, keys)
	for key in keys:
		params[key] = '%s =' % key
	for entry in pa.iterJobs():
		if entry[ParameterInfo.ACTIVE]:
			line_1 += ' %02d' % entry['GC_JOB_ID']
		else:
			line_1 += ' --'
		for key in keys:
			params[key] += entry.get(key, '').rjust(3)
	result = [line_1] + sorted(params.values())
	print(str.join('\n', result))

class Test_ParameterAdapter:
	"""
	>>> remove_files(['params.dat.gz', 'params.map.gz'])

	>>> testPAS(s2ps(A = '1', B = 'X Y'))
	    00 01
	A =  1  1
	B =  X  Y

	>>> testPAS(s2ps(A = '1 2 3', B = 'X Y'))
	    00 01 02 03 04 05
	A =  1  1  2  3  2  3
	B =  X  Y  X  X  Y  Y

	>>> testPAS(s2ps(A = '1 2', B = 'X Y'))
	    00 01 02 -- 04 --
	A =  1  1  2  3  2  3
	B =  X  Y  X  X  Y  Y

	>>> testPAS(s2ps(A = '1 2 4', B = 'X Y'))
	    00 01 02 -- 04 -- 06 07
	A =  1  1  2  3  2  3  4  4
	B =  X  Y  X  X  Y  Y  X  Y

	>>> testPAS(s2ps(A = '1 2 3 4', B = 'X Y'))
	    00 01 02 03 04 05 06 07
	A =  1  1  2  3  2  3  4  4
	B =  X  Y  X  X  Y  Y  X  Y

	>>> testPAS(s2ps(A = '1 2 3 4', B = '!X Y'))
	    -- 01 -- -- 04 05 -- 07
	A =  1  1  2  3  2  3  4  4
	B =  X  Y  X  X  Y  Y  X  Y

	>>> testPAS(s2ps(A = '1 2 3 4', B = '!X Y', C = ' m'))
	    -- 01 -- -- 04 05 -- 07 -- -- -- -- 12 13 14 15
	A =  1  1  2  3  2  3  4  4  1  2  3  4  1  2  3  4
	B =  X  Y  X  X  Y  Y  X  Y  X  X  X  X  Y  Y  Y  Y
	C =                          m  m  m  m  m  m  m  m

	>>> testPAS(s2ps(A = '1 2 3 4', B = '!X Y'))
	    -- 01 -- -- 04 05 -- 07 -- -- -- -- -- -- -- --
	A =  1  1  2  3  2  3  4  4  1  2  3  4  1  2  3  4
	B =  X  Y  X  X  Y  Y  X  Y  X  X  X  X  Y  Y  Y  Y

	>>> testPAS(s2ps(A = '1 2 3 4', B = '!X Y', C = ' k'))
	    -- 01 -- -- 04 05 -- 07 -- -- -- -- -- -- -- -- -- -- -- -- 20 21 22 23
	A =  1  1  2  3  2  3  4  4  1  2  3  4  1  2  3  4  1  2  3  4  1  2  3  4
	B =  X  Y  X  X  Y  Y  X  Y  X  X  X  X  Y  Y  Y  Y  X  X  X  X  Y  Y  Y  Y
	C =                          m  m  m  m  m  m  m  m  k  k  k  k  k  k  k  k

	>>> testPAS(s2ps(A = '2 !3 4', B = '!X Y'))
	    -- -- -- -- 04 -- -- 07 -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	A =  1  1  2  3  2  3  4  4  1  2  3  4  1  2  3  4  1  2  3  4  1  2  3  4
	B =  X  Y  X  X  Y  Y  X  Y  X  X  X  X  Y  Y  Y  Y  X  X  X  X  Y  Y  Y  Y

	>>> testPAS(s2ps(A = '1 2', B = 'X Y'))
	    00 01 02 -- 04 -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	A =  1  1  2  3  2  3  4  4  1  2  3  4  1  2  3  4  1  2  3  4  1  2  3  4
	B =  X  Y  X  X  Y  Y  X  Y  X  X  X  X  Y  Y  Y  Y  X  X  X  X  Y  Y  Y  Y

	>>> remove_files(['params.dat.gz', 'params.map.gz'])
	"""

run_test()
