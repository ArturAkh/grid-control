#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import create_config, remove_files, run_test
from grid_control.datasets import DataProvider, DataSplitter
from grid_control.parameters import ParameterSource
from grid_control.parameters.padapter import BasicParameterAdapter, ParameterAdapter, TrackedParameterAdapter
from grid_control.parameters.psource_meta import CrossParameterSource
from testDS import ss2bl
from testINC import DataSplitProcessorTest, testPA, testPS, updateDS
from python_compat import set

p1 = ParameterSource.createInstance('SimpleParameterSource', 'A', [1, 2, 3])
p2 = ParameterSource.createInstance('SimpleParameterSource', 'B', ['M', 'N'])
p3 = ParameterSource.createInstance('CounterParameterSource', 'X', 100)
p1.resyncSetup(info = (set([1]), set([2]), False)) # redo: 2, disable: 3
p2.resyncSetup(info = (set([0]), set([1]), False)) # redo: M, disable: N

class Test_ParameterAdapter:
	"""
	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])
	>>> p1.resync() == (set([1]), set([2]), False)
	True
	>>> p2.resync() == (set([0]), set([1]), False)
	True
	>>> p1.resync() == (set([1]), set([2]), False)
	True
	>>> p2.resync() == (set([0]), set([1]), False)
	True

	>>> ps1 = ParameterSource.createInstance('CrossParameterSource', p1, p2, p3)
	>>> testPS(ps1, showJob = True)
	6
	Keys = A [trk], B [trk], X, GC_JOB_ID, GC_PARAM
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!X': 100, '!GC_JOB_ID': 0, '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', '!X': 101, '!GC_JOB_ID': 1, '!GC_PARAM': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', '!X': 102, '!GC_JOB_ID': 2, '!GC_PARAM': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', '!X': 103, '!GC_JOB_ID': 3, '!GC_PARAM': 3}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', '!X': 104, '!GC_JOB_ID': 4, '!GC_PARAM': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!X': 105, '!GC_JOB_ID': 5, '!GC_PARAM': 5}
	redo: [0, 1, 2, 4] disable: [2, 3, 4, 5] size: False

	>>> pa1 = ParameterAdapter(create_config(), ps1)
	>>> pa1.canSubmit(2)
	True

	>>> pa2 = BasicParameterAdapter(create_config(configDict={'global': {'workdir': '.'}}), ps1)
	>>> pa2.canSubmit(2)
	True

	>>> ps2 = ParameterSource.createInstance('CrossParameterSource', p2, p3, p1)
	>>> testPS(ps2, showJob = True)
	6
	Keys = A [trk], B [trk], X, GC_JOB_ID, GC_PARAM
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!X': 100, '!GC_JOB_ID': 0, '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 1, 'B': 'N', '!X': 101, '!GC_JOB_ID': 1, '!GC_PARAM': 1}
	2 {0: True, 2: [], 'A': 2, 'B': 'M', '!X': 102, '!GC_JOB_ID': 2, '!GC_PARAM': 2}
	3 {0: True, 2: [], 'A': 2, 'B': 'N', '!X': 103, '!GC_JOB_ID': 3, '!GC_PARAM': 3}
	4 {0: True, 2: [], 'A': 3, 'B': 'M', '!X': 104, '!GC_JOB_ID': 4, '!GC_PARAM': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!X': 105, '!GC_JOB_ID': 5, '!GC_PARAM': 5}
	redo: [0, 2, 3, 4] disable: [1, 3, 4, 5] size: False

	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])
	"""

p0 = ParameterSource.createInstance('SimpleParameterSource', 'VAR', ['A', 'B'])
p4 = ParameterSource.createInstance('SimpleParameterSource', 'C', ['', 'X'])
p5 = ParameterSource.createInstance('SimpleParameterSource', 'C', ['', 'Y', 'X'])
p6 = ParameterSource.createInstance('SimpleParameterSource', 'C', ['Y', ''])
p7 = ParameterSource.createInstance('SimpleParameterSource', 'C', ['', '', 'Y'])
p8 = ParameterSource.createInstance('SimpleParameterSource', 'C', ['X', ''])
p9 = ParameterSource.createInstance('SimpleParameterSource', 'C', ['', 'X', ''])

class Test_TrackedParameterAdapterRepeat:
	"""
	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz', 'dummycache*.dat', 'dummymap*.tar', 'dataset.tmp'])
	>>> config = create_config(configDict={'global': {'workdir': '.'}, 'dataset': {'events per job': 3}})

	>>> data_bl = ss2bl('AABBCCCD')
	>>> updateDS(data_bl, '')

	>>> dataSource = DataProvider.createInstance('ListProvider', config, 'dataset.tmp', 'nick')
	>>> dataSplit = DataSplitter.createInstance('EventBoundarySplitter', config)
	>>> dataProc = DataSplitProcessorTest(config)

	>>> pd = ParameterSource.createInstance('DataParameterSource', '.', 'dummy', dataSource, dataSplit, dataProc, False)
	>>> ps = CrossParameterSource(pd, p0, p3)
	>>> pa = TrackedParameterAdapter(config, ps)
	>>> testPA(pa, showPNum = False, showJob = False)
	6
	Keys = EVT, FN, SID [trk], SKIP, VAR [trk], X
	0 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'A', '!X': 100}
	1 {0: True, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'A', '!X': 101}
	2 {0: True, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'A', '!X': 102}
	3 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'B', '!X': 103}
	4 {0: True, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'B', '!X': 104}
	5 {0: True, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'B', '!X': 105}
	None

	>>> updateDS(data_bl, 'D:2', pd) # AAB BCC CD D
	>>> testPA(pa, showPNum = False, showJob = False)
	8
	Keys = EVT, FN, SID [trk], SKIP, VAR [trk], X
	0 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'A', '!X': 100}
	1 {0: True, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'A', '!X': 101}
	2 {0: True, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'A', '!X': 102}
	3 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'B', '!X': 103}
	4 {0: True, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'B', '!X': 104}
	5 {0: True, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'B', '!X': 105}
	6 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'A', '!X': 106}
	7 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'B', '!X': 107}
	redo: [] disable: [] size: True

	>>> updateDS(data_bl, 'D:2', pd) # AAB BCC CD D
	>>> testPA(pa, showPNum = False, showJob = False)
	8
	Keys = EVT, FN, SID [trk], SKIP, VAR [trk], X
	0 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'A', '!X': 100}
	1 {0: True, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'A', '!X': 101}
	2 {0: True, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'A', '!X': 102}
	3 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'B', '!X': 103}
	4 {0: True, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'B', '!X': 104}
	5 {0: True, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'B', '!X': 105}
	6 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'A', '!X': 106}
	7 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'B', '!X': 107}
	None

	>>> updateDS(data_bl, 'D:2 C:1', pd) # AAB BCc cD D BC D
	>>> testPA(pa, showPNum = False, showJob = False)
	12
	Keys = EVT, FN, SID [trk], SKIP, VAR [trk], X
	0 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'A', '!X': 100}
	1 {0: False, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'A', '!X': 101}
	2 {0: False, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'A', '!X': 102}
	3 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'B', '!X': 103}
	4 {0: False, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'B', '!X': 104}
	5 {0: False, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'B', '!X': 105}
	6 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'A', '!X': 106}
	7 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'B', '!X': 107}
	8 {0: True, 2: [], '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, 'VAR': 'A', '!X': 108}
	9 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, 'VAR': 'A', '!X': 109}
	10 {0: True, 2: [], '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, 'VAR': 'B', '!X': 110}
	11 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, 'VAR': 'B', '!X': 111}
	redo: [] disable: [1, 2, 4, 5] size: True

	>>> updateDS(data_bl, 'C:1', pd)
	>>> testPA(pa, showPNum = False, showJob = False)
	12
	Keys = EVT, FN, SID [trk], SKIP, VAR [trk], X
	0 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'A', '!X': 100}
	1 {0: False, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'A', '!X': 101}
	2 {0: False, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'A', '!X': 102}
	3 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'B', '!X': 103}
	4 {0: False, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'B', '!X': 104}
	5 {0: False, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'B', '!X': 105}
	6 {0: False, 2: [], '!EVT': 0, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'A', '!X': 106}
	7 {0: False, 2: [], '!EVT': 0, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'B', '!X': 107}
	8 {0: True, 2: [], '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, 'VAR': 'A', '!X': 108}
	9 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, 'VAR': 'A', '!X': 109}
	10 {0: True, 2: [], '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, 'VAR': 'B', '!X': 110}
	11 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, 'VAR': 'B', '!X': 111}
	redo: [] disable: [6, 7] size: False

	>>> updateDS(data_bl, '', pd)
	>>> testPA(pa, showPNum = False, showJob = False)
	14
	Keys = EVT, FN, SID [trk], SKIP, VAR [trk], X
	0 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'A', '!X': 100}
	1 {0: False, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'A', '!X': 101}
	2 {0: False, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'A', '!X': 102}
	3 {0: True, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'B', '!X': 103}
	4 {0: False, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'B', '!X': 104}
	5 {0: False, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'B', '!X': 105}
	6 {0: False, 2: [], '!EVT': 0, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'A', '!X': 106}
	7 {0: False, 2: [], '!EVT': 0, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'B', '!X': 107}
	8 {0: True, 2: [], '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, 'VAR': 'A', '!X': 108}
	9 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, 'VAR': 'A', '!X': 109}
	10 {0: True, 2: [], '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, 'VAR': 'B', '!X': 110}
	11 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, 'VAR': 'B', '!X': 111}
	12 {0: True, 2: [], '!EVT': 2, '!FN': 'C', 'SID': 6, '!SKIP': 1, 'VAR': 'A', '!X': 112}
	13 {0: True, 2: [], '!EVT': 2, '!FN': 'C', 'SID': 6, '!SKIP': 1, 'VAR': 'B', '!X': 113}
	redo: [] disable: [] size: True

	>>> updateDS(data_bl, 'A:3', pd)
	>>> testPA(pa, showPNum = False, showJob = False)
	16
	Keys = EVT, FN, SID [trk], SKIP, VAR [trk], X
	0 {0: False, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'A', '!X': 100}
	1 {0: False, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'A', '!X': 101}
	2 {0: False, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'A', '!X': 102}
	3 {0: False, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'B', '!X': 103}
	4 {0: False, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'B', '!X': 104}
	5 {0: False, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'B', '!X': 105}
	6 {0: False, 2: [], '!EVT': 0, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'A', '!X': 106}
	7 {0: False, 2: [], '!EVT': 0, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'B', '!X': 107}
	8 {0: True, 2: [], '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, 'VAR': 'A', '!X': 108}
	9 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, 'VAR': 'A', '!X': 109}
	10 {0: True, 2: [], '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, 'VAR': 'B', '!X': 110}
	11 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, 'VAR': 'B', '!X': 111}
	12 {0: True, 2: [], '!EVT': 2, '!FN': 'C', 'SID': 6, '!SKIP': 1, 'VAR': 'A', '!X': 112}
	13 {0: True, 2: [], '!EVT': 2, '!FN': 'C', 'SID': 6, '!SKIP': 1, 'VAR': 'B', '!X': 113}
	14 {0: True, 2: [], '!EVT': 4, '!FN': 'A B', 'SID': 7, '!SKIP': 0, 'VAR': 'A', '!X': 114}
	15 {0: True, 2: [], '!EVT': 4, '!FN': 'A B', 'SID': 7, '!SKIP': 0, 'VAR': 'B', '!X': 115}
	redo: [] disable: [0, 3] size: True

	>>> ps = CrossParameterSource(pd, p0, p3, p8)
	>>> pa = TrackedParameterAdapter(config, ps)
	>>> testPA(pa, showPNum = False, showJob = False)
	32
	Keys = C [trk], EVT, FN, SID [trk], SKIP, VAR [trk], X
	0 {0: False, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'A', '!X': 100}
	1 {0: False, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'A', '!X': 101}
	2 {0: False, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'A', '!X': 102}
	3 {0: False, 2: [], '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'B', '!X': 103}
	4 {0: False, 2: [], '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'B', '!X': 104}
	5 {0: False, 2: [], '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'B', '!X': 105}
	6 {0: False, 2: [], '!EVT': 0, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'A', '!X': 106}
	7 {0: False, 2: [], '!EVT': 0, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'B', '!X': 107}
	8 {0: True, 2: [], '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, 'VAR': 'A', '!X': 108}
	9 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, 'VAR': 'A', '!X': 109}
	10 {0: True, 2: [], '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, 'VAR': 'B', '!X': 110}
	11 {0: True, 2: [], '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, 'VAR': 'B', '!X': 111}
	12 {0: True, 2: [], '!EVT': 2, '!FN': 'C', 'SID': 6, '!SKIP': 1, 'VAR': 'A', '!X': 112}
	13 {0: True, 2: [], '!EVT': 2, '!FN': 'C', 'SID': 6, '!SKIP': 1, 'VAR': 'B', '!X': 113}
	14 {0: True, 2: [], '!EVT': 4, '!FN': 'A B', 'SID': 7, '!SKIP': 0, 'VAR': 'A', '!X': 114}
	15 {0: True, 2: [], '!EVT': 4, '!FN': 'A B', 'SID': 7, '!SKIP': 0, 'VAR': 'B', '!X': 115}
	16 {0: False, 2: [], 'C': 'X', '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'A', '!X': 116}
	17 {0: False, 2: [], 'C': 'X', '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'A', '!X': 117}
	18 {0: False, 2: [], 'C': 'X', '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'A', '!X': 118}
	19 {0: False, 2: [], 'C': 'X', '!EVT': 0, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'A', '!X': 119}
	20 {0: True, 2: [], 'C': 'X', '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, 'VAR': 'A', '!X': 120}
	21 {0: True, 2: [], 'C': 'X', '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, 'VAR': 'A', '!X': 121}
	22 {0: True, 2: [], 'C': 'X', '!EVT': 2, '!FN': 'C', 'SID': 6, '!SKIP': 1, 'VAR': 'A', '!X': 122}
	23 {0: True, 2: [], 'C': 'X', '!EVT': 4, '!FN': 'A B', 'SID': 7, '!SKIP': 0, 'VAR': 'A', '!X': 123}
	24 {0: False, 2: [], 'C': 'X', '!EVT': 3, '!FN': 'A B', 'SID': 0, '!SKIP': 0, 'VAR': 'B', '!X': 124}
	25 {0: False, 2: [], 'C': 'X', '!EVT': 3, '!FN': 'B C', 'SID': 1, '!SKIP': 1, 'VAR': 'B', '!X': 125}
	26 {0: False, 2: [], 'C': 'X', '!EVT': 2, '!FN': 'C D', 'SID': 2, '!SKIP': 2, 'VAR': 'B', '!X': 126}
	27 {0: False, 2: [], 'C': 'X', '!EVT': 0, '!FN': 'D', 'SID': 3, '!SKIP': 1, 'VAR': 'B', '!X': 127}
	28 {0: True, 2: [], 'C': 'X', '!EVT': 2, '!FN': 'B C', 'SID': 4, '!SKIP': 1, 'VAR': 'B', '!X': 128}
	29 {0: True, 2: [], 'C': 'X', '!EVT': 1, '!FN': 'D', 'SID': 5, '!SKIP': 0, 'VAR': 'B', '!X': 129}
	30 {0: True, 2: [], 'C': 'X', '!EVT': 2, '!FN': 'C', 'SID': 6, '!SKIP': 1, 'VAR': 'B', '!X': 130}
	31 {0: True, 2: [], 'C': 'X', '!EVT': 4, '!FN': 'A B', 'SID': 7, '!SKIP': 0, 'VAR': 'B', '!X': 131}
	None

	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz', 'dummycache*.dat', 'dummymap*.tar', 'dataset.tmp'])
	"""

class Test_TrackedParameterAdapterSequential:
	"""
	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])
	>>> config = create_config(configDict={'global': {'workdir': '.'}})
	>>> testPA(TrackedParameterAdapter(config, CrossParameterSource(p1, p2, p3)))
	6
	Keys = A [trk], B [trk], X, GC_JOB_ID, GC_PARAM
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!X': 100, '!GC_JOB_ID': 0, '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', '!X': 101, '!GC_JOB_ID': 1, '!GC_PARAM': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', '!X': 102, '!GC_JOB_ID': 2, '!GC_PARAM': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', '!X': 103, '!GC_JOB_ID': 3, '!GC_PARAM': 3}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', '!X': 104, '!GC_JOB_ID': 4, '!GC_PARAM': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!X': 105, '!GC_JOB_ID': 5, '!GC_PARAM': 5}
	redo: [0, 1] disable: [2, 3, 4, 5] size: False

	>>> testPA(TrackedParameterAdapter(config, CrossParameterSource(p2, p3, p1)))
	6
	Keys = A [trk], B [trk], X, GC_JOB_ID, GC_PARAM
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!X': 100, '!GC_JOB_ID': 0, '!GC_PARAM': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', '!X': 101, '!GC_JOB_ID': 1, '!GC_PARAM': 2}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', '!X': 102, '!GC_JOB_ID': 2, '!GC_PARAM': 4}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', '!X': 103, '!GC_JOB_ID': 3, '!GC_PARAM': 1}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', '!X': 104, '!GC_JOB_ID': 4, '!GC_PARAM': 3}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!X': 105, '!GC_JOB_ID': 5, '!GC_PARAM': 5}
	redo: [0, 1] disable: [2, 3, 4, 5] size: False

	>>> testPA(TrackedParameterAdapter(config, CrossParameterSource(p3, p4, p1, p2)), showPNum = False)
	12
	Keys = A [trk], B [trk], C [trk], X, GC_JOB_ID
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!X': 100, '!GC_JOB_ID': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', '!X': 101, '!GC_JOB_ID': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', '!X': 102, '!GC_JOB_ID': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', '!X': 103, '!GC_JOB_ID': 3}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', '!X': 104, '!GC_JOB_ID': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!X': 105, '!GC_JOB_ID': 5}
	6 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'X', '!X': 106, '!GC_JOB_ID': 6}
	7 {0: True, 2: [], 'A': 2, 'B': 'M', 'C': 'X', '!X': 107, '!GC_JOB_ID': 7}
	8 {0: True, 2: [], 'A': 3, 'B': 'M', 'C': 'X', '!X': 108, '!GC_JOB_ID': 8}
	9 {0: True, 2: [], 'A': 1, 'B': 'N', 'C': 'X', '!X': 109, '!GC_JOB_ID': 9}
	10 {0: True, 2: [], 'A': 2, 'B': 'N', 'C': 'X', '!X': 110, '!GC_JOB_ID': 10}
	11 {0: True, 2: [], 'A': 3, 'B': 'N', 'C': 'X', '!X': 111, '!GC_JOB_ID': 11}
	redo: [0, 1, 6, 7] disable: [2, 3, 4, 5, 8, 9, 10, 11] size: False

	>>> testPA(TrackedParameterAdapter(config, CrossParameterSource(p3, p5, p1, p2)), showPNum = False)
	18
	Keys = A [trk], B [trk], C [trk], X, GC_JOB_ID
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!X': 100, '!GC_JOB_ID': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', '!X': 101, '!GC_JOB_ID': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', '!X': 102, '!GC_JOB_ID': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', '!X': 103, '!GC_JOB_ID': 3}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', '!X': 104, '!GC_JOB_ID': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!X': 105, '!GC_JOB_ID': 5}
	6 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'X', '!X': 106, '!GC_JOB_ID': 6}
	7 {0: True, 2: [], 'A': 2, 'B': 'M', 'C': 'X', '!X': 107, '!GC_JOB_ID': 7}
	8 {0: True, 2: [], 'A': 3, 'B': 'M', 'C': 'X', '!X': 108, '!GC_JOB_ID': 8}
	9 {0: True, 2: [], 'A': 1, 'B': 'N', 'C': 'X', '!X': 109, '!GC_JOB_ID': 9}
	10 {0: True, 2: [], 'A': 2, 'B': 'N', 'C': 'X', '!X': 110, '!GC_JOB_ID': 10}
	11 {0: True, 2: [], 'A': 3, 'B': 'N', 'C': 'X', '!X': 111, '!GC_JOB_ID': 11}
	12 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'Y', '!X': 112, '!GC_JOB_ID': 12}
	13 {0: True, 2: [], 'A': 2, 'B': 'M', 'C': 'Y', '!X': 113, '!GC_JOB_ID': 13}
	14 {0: True, 2: [], 'A': 3, 'B': 'M', 'C': 'Y', '!X': 114, '!GC_JOB_ID': 14}
	15 {0: True, 2: [], 'A': 1, 'B': 'N', 'C': 'Y', '!X': 115, '!GC_JOB_ID': 15}
	16 {0: True, 2: [], 'A': 2, 'B': 'N', 'C': 'Y', '!X': 116, '!GC_JOB_ID': 16}
	17 {0: True, 2: [], 'A': 3, 'B': 'N', 'C': 'Y', '!X': 117, '!GC_JOB_ID': 17}
	redo: [0, 1, 6, 7, 12, 13] disable: [2, 3, 4, 5, 8, 9, 10, 11, 14, 15, 16, 17] size: False

	>>> testPA(TrackedParameterAdapter(config, CrossParameterSource(p3, p6, p1, p2)), showPNum = False)
	18
	Keys = A [trk], B [trk], C [trk], X, GC_JOB_ID
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!X': 100, '!GC_JOB_ID': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', '!X': 101, '!GC_JOB_ID': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', '!X': 102, '!GC_JOB_ID': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', '!X': 103, '!GC_JOB_ID': 3}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', '!X': 104, '!GC_JOB_ID': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!X': 105, '!GC_JOB_ID': 5}
	6 {0: False, 2: [], 'A': 1, 'B': 'M', 'C': 'X', '!GC_JOB_ID': 6}
	7 {0: False, 2: [], 'A': 2, 'B': 'M', 'C': 'X', '!GC_JOB_ID': 7}
	8 {0: False, 2: [], 'A': 3, 'B': 'M', 'C': 'X', '!GC_JOB_ID': 8}
	9 {0: False, 2: [], 'A': 1, 'B': 'N', 'C': 'X', '!GC_JOB_ID': 9}
	10 {0: False, 2: [], 'A': 2, 'B': 'N', 'C': 'X', '!GC_JOB_ID': 10}
	11 {0: False, 2: [], 'A': 3, 'B': 'N', 'C': 'X', '!GC_JOB_ID': 11}
	12 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'Y', '!X': 112, '!GC_JOB_ID': 12}
	13 {0: True, 2: [], 'A': 2, 'B': 'M', 'C': 'Y', '!X': 113, '!GC_JOB_ID': 13}
	14 {0: True, 2: [], 'A': 3, 'B': 'M', 'C': 'Y', '!X': 114, '!GC_JOB_ID': 14}
	15 {0: True, 2: [], 'A': 1, 'B': 'N', 'C': 'Y', '!X': 115, '!GC_JOB_ID': 15}
	16 {0: True, 2: [], 'A': 2, 'B': 'N', 'C': 'Y', '!X': 116, '!GC_JOB_ID': 16}
	17 {0: True, 2: [], 'A': 3, 'B': 'N', 'C': 'Y', '!X': 117, '!GC_JOB_ID': 17}
	redo: [0, 1, 12, 13] disable: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 17] size: False

	>>> testPA(TrackedParameterAdapter(config, CrossParameterSource(p3, p7, p1, p2)), showPNum = False)
	24
	Keys = A [trk], B [trk], C [trk], X, GC_JOB_ID
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!X': 100, '!GC_JOB_ID': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', '!X': 101, '!GC_JOB_ID': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', '!X': 102, '!GC_JOB_ID': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', '!X': 103, '!GC_JOB_ID': 3}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', '!X': 104, '!GC_JOB_ID': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!X': 105, '!GC_JOB_ID': 5}
	6 {0: False, 2: [], 'A': 1, 'B': 'M', 'C': 'X', '!GC_JOB_ID': 6}
	7 {0: False, 2: [], 'A': 2, 'B': 'M', 'C': 'X', '!GC_JOB_ID': 7}
	8 {0: False, 2: [], 'A': 3, 'B': 'M', 'C': 'X', '!GC_JOB_ID': 8}
	9 {0: False, 2: [], 'A': 1, 'B': 'N', 'C': 'X', '!GC_JOB_ID': 9}
	10 {0: False, 2: [], 'A': 2, 'B': 'N', 'C': 'X', '!GC_JOB_ID': 10}
	11 {0: False, 2: [], 'A': 3, 'B': 'N', 'C': 'X', '!GC_JOB_ID': 11}
	12 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'Y', '!X': 112, '!GC_JOB_ID': 12}
	13 {0: True, 2: [], 'A': 2, 'B': 'M', 'C': 'Y', '!X': 113, '!GC_JOB_ID': 13}
	14 {0: True, 2: [], 'A': 3, 'B': 'M', 'C': 'Y', '!X': 114, '!GC_JOB_ID': 14}
	15 {0: True, 2: [], 'A': 1, 'B': 'N', 'C': 'Y', '!X': 115, '!GC_JOB_ID': 15}
	16 {0: True, 2: [], 'A': 2, 'B': 'N', 'C': 'Y', '!X': 116, '!GC_JOB_ID': 16}
	17 {0: True, 2: [], 'A': 3, 'B': 'N', 'C': 'Y', '!X': 117, '!GC_JOB_ID': 17}
	18 {0: True, 2: [], 'A': 1, 'B': 'M', '!X': 118, '!GC_JOB_ID': 18}
	19 {0: True, 2: [], 'A': 2, 'B': 'M', '!X': 119, '!GC_JOB_ID': 19}
	20 {0: True, 2: [], 'A': 3, 'B': 'M', '!X': 120, '!GC_JOB_ID': 20}
	21 {0: True, 2: [], 'A': 1, 'B': 'N', '!X': 121, '!GC_JOB_ID': 21}
	22 {0: True, 2: [], 'A': 2, 'B': 'N', '!X': 122, '!GC_JOB_ID': 22}
	23 {0: True, 2: [], 'A': 3, 'B': 'N', '!X': 123, '!GC_JOB_ID': 23}
	redo: [0, 1, 12, 13, 18, 19] disable: [2, 3, 4, 5, 14, 15, 16, 17, 20, 21, 22, 23] size: False

	>>> testPA(TrackedParameterAdapter(config, CrossParameterSource(p3, p8, p1, p2)), showPNum = False)
	24
	Keys = A [trk], B [trk], C [trk], X, GC_JOB_ID
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!X': 100, '!GC_JOB_ID': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', '!X': 101, '!GC_JOB_ID': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', '!X': 102, '!GC_JOB_ID': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', '!X': 103, '!GC_JOB_ID': 3}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', '!X': 104, '!GC_JOB_ID': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!X': 105, '!GC_JOB_ID': 5}
	6 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'X', '!X': 106, '!GC_JOB_ID': 6}
	7 {0: True, 2: [], 'A': 2, 'B': 'M', 'C': 'X', '!X': 107, '!GC_JOB_ID': 7}
	8 {0: True, 2: [], 'A': 3, 'B': 'M', 'C': 'X', '!X': 108, '!GC_JOB_ID': 8}
	9 {0: True, 2: [], 'A': 1, 'B': 'N', 'C': 'X', '!X': 109, '!GC_JOB_ID': 9}
	10 {0: True, 2: [], 'A': 2, 'B': 'N', 'C': 'X', '!X': 110, '!GC_JOB_ID': 10}
	11 {0: True, 2: [], 'A': 3, 'B': 'N', 'C': 'X', '!X': 111, '!GC_JOB_ID': 11}
	12 {0: False, 2: [], 'A': 1, 'B': 'M', 'C': 'Y', '!GC_JOB_ID': 12}
	13 {0: False, 2: [], 'A': 2, 'B': 'M', 'C': 'Y', '!GC_JOB_ID': 13}
	14 {0: False, 2: [], 'A': 3, 'B': 'M', 'C': 'Y', '!GC_JOB_ID': 14}
	15 {0: False, 2: [], 'A': 1, 'B': 'N', 'C': 'Y', '!GC_JOB_ID': 15}
	16 {0: False, 2: [], 'A': 2, 'B': 'N', 'C': 'Y', '!GC_JOB_ID': 16}
	17 {0: False, 2: [], 'A': 3, 'B': 'N', 'C': 'Y', '!GC_JOB_ID': 17}
	18 {0: False, 2: [], 'A': 1, 'B': 'M', '!GC_JOB_ID': 18}
	19 {0: False, 2: [], 'A': 2, 'B': 'M', '!GC_JOB_ID': 19}
	20 {0: False, 2: [], 'A': 3, 'B': 'M', '!GC_JOB_ID': 20}
	21 {0: False, 2: [], 'A': 1, 'B': 'N', '!GC_JOB_ID': 21}
	22 {0: False, 2: [], 'A': 2, 'B': 'N', '!GC_JOB_ID': 22}
	23 {0: False, 2: [], 'A': 3, 'B': 'N', '!GC_JOB_ID': 23}
	redo: [0, 1, 6, 7] disable: [2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23] size: False

	>>> testPA(TrackedParameterAdapter(config, CrossParameterSource(p3, p9, p1, p2)), showPNum = False)
	24
	Keys = A [trk], B [trk], C [trk], X, GC_JOB_ID
	0 {0: True, 2: [], 'A': 1, 'B': 'M', '!X': 100, '!GC_JOB_ID': 0}
	1 {0: True, 2: [], 'A': 2, 'B': 'M', '!X': 101, '!GC_JOB_ID': 1}
	2 {0: True, 2: [], 'A': 3, 'B': 'M', '!X': 102, '!GC_JOB_ID': 2}
	3 {0: True, 2: [], 'A': 1, 'B': 'N', '!X': 103, '!GC_JOB_ID': 3}
	4 {0: True, 2: [], 'A': 2, 'B': 'N', '!X': 104, '!GC_JOB_ID': 4}
	5 {0: True, 2: [], 'A': 3, 'B': 'N', '!X': 105, '!GC_JOB_ID': 5}
	6 {0: True, 2: [], 'A': 1, 'B': 'M', 'C': 'X', '!X': 106, '!GC_JOB_ID': 6}
	7 {0: True, 2: [], 'A': 2, 'B': 'M', 'C': 'X', '!X': 107, '!GC_JOB_ID': 7}
	8 {0: True, 2: [], 'A': 3, 'B': 'M', 'C': 'X', '!X': 108, '!GC_JOB_ID': 8}
	9 {0: True, 2: [], 'A': 1, 'B': 'N', 'C': 'X', '!X': 109, '!GC_JOB_ID': 9}
	10 {0: True, 2: [], 'A': 2, 'B': 'N', 'C': 'X', '!X': 110, '!GC_JOB_ID': 10}
	11 {0: True, 2: [], 'A': 3, 'B': 'N', 'C': 'X', '!X': 111, '!GC_JOB_ID': 11}
	12 {0: False, 2: [], 'A': 1, 'B': 'M', 'C': 'Y', '!GC_JOB_ID': 12}
	13 {0: False, 2: [], 'A': 2, 'B': 'M', 'C': 'Y', '!GC_JOB_ID': 13}
	14 {0: False, 2: [], 'A': 3, 'B': 'M', 'C': 'Y', '!GC_JOB_ID': 14}
	15 {0: False, 2: [], 'A': 1, 'B': 'N', 'C': 'Y', '!GC_JOB_ID': 15}
	16 {0: False, 2: [], 'A': 2, 'B': 'N', 'C': 'Y', '!GC_JOB_ID': 16}
	17 {0: False, 2: [], 'A': 3, 'B': 'N', 'C': 'Y', '!GC_JOB_ID': 17}
	18 {0: True, 2: [], 'A': 1, 'B': 'M', '!X': 118, '!GC_JOB_ID': 18}
	19 {0: True, 2: [], 'A': 2, 'B': 'M', '!X': 119, '!GC_JOB_ID': 19}
	20 {0: True, 2: [], 'A': 3, 'B': 'M', '!X': 120, '!GC_JOB_ID': 20}
	21 {0: True, 2: [], 'A': 1, 'B': 'N', '!X': 121, '!GC_JOB_ID': 21}
	22 {0: True, 2: [], 'A': 2, 'B': 'N', '!X': 122, '!GC_JOB_ID': 22}
	23 {0: True, 2: [], 'A': 3, 'B': 'N', '!X': 123, '!GC_JOB_ID': 23}
	redo: [0, 1, 6, 7, 18, 19] disable: [2, 3, 4, 5, 8, 9, 10, 11, 20, 21, 22, 23] size: False

	>>> remove_files(['task.dat', 'params.dat.gz', 'params.map.gz'])
	"""

run_test()
