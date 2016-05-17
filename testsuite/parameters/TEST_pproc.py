#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import create_config, run_test
from grid_control import utils
from grid_control.datasets import DataProvider, DataSplitter, PartitionProcessor
from grid_control.parameters import ParameterInfo, ParameterSource
from grid_control.parameters.padapter import ParameterAdapter
from python_compat import imap, irange, lmap

def get_config(settings = None):
	settings = settings or {}
	settings['events per job'] = 10
	return create_config(configDict = {'dataset': settings})

def testPP(dataProcNames, config = None, keys = [], dataset = 'dataE.dbs'):
	utils.removeFiles(['datasetcache.dat', 'datasetmap.tar'])
	if not config:
		config = get_config()
	dataProcList = lmap(lambda name: PartitionProcessor.createInstance(name, config), dataProcNames.split())
	assert(dataProcList)
	if len(dataProcList) > 1:
		dataProc = PartitionProcessor.createInstance('MultiPartitionProcessor', config, dataProcList)
	else:
		dataProc = dataProcList[0]
	dataSource = DataProvider.createInstance('ListProvider', create_config(), '../datasets/' + dataset, None)
	dataSplit = DataSplitter.createInstance('BlockBoundarySplitter', config)
	ps = ParameterSource.createInstance('DataParameterSource', '.', 'dataset', dataSource, dataSplit, dataProc, False)
	pa = ParameterAdapter(create_config(), ps)
	for jobNum in irange(pa.getMaxJobs()):
		jobInfo = pa.getJobInfo(jobNum)
		msg = [str(jobNum), str(jobInfo[ParameterInfo.ACTIVE]).rjust(5),
			str(jobInfo[ParameterInfo.REQS]).ljust(15), jobInfo.get('FILE_NAMES', '<missing>')]
		msg = msg + lmap(lambda k: jobInfo.get(k), keys)
		print(str.join(' ', imap(str, msg)).rstrip())
	utils.removeFiles(['datasetcache.dat', 'datasetmap.tar'])

class Test_LFNPartitionProcessor:
	"""
	>>> testPP('LFNPartitionProcessor BasicPartitionProcessor', get_config({'partition lfn modifier': '/'}))
	log:Block /MY/DATASET#easy3 is not available at any site!
	0  True []              /store//path/file0 /store//path/file1 /store//path/file2
	1  True []              /store//path/file3 /store//path/file5
	2  True []              /store//path/file6 /store//path/file7 /store//path/file8 /store//path/file9

	>>> testPP('LFNPartitionProcessor BasicPartitionProcessor', get_config({'partition lfn modifier': 'TEST'}))
	log:Block /MY/DATASET#easy3 is not available at any site!
	0  True []              TEST/store//path/file0 TEST/store//path/file1 TEST/store//path/file2
	1  True []              TEST/store//path/file3 TEST/store//path/file5
	2  True []              TEST/store//path/file6 TEST/store//path/file7 TEST/store//path/file8 TEST/store//path/file9

	>>> testPP('LFNPartitionProcessor BasicPartitionProcessor', get_config({'partition lfn modifier': 'TEST', 'partition lfn modifier dict': 'test => 123'}))
	log:Block /MY/DATASET#easy3 is not available at any site!
	0  True []              123/store//path/file0 123/store//path/file1 123/store//path/file2
	1  True []              123/store//path/file3 123/store//path/file5
	2  True []              123/store//path/file6 123/store//path/file7 123/store//path/file8 123/store//path/file9

	>>> testPP('LFNPartitionProcessor BasicPartitionProcessor', get_config({'partition lfn modifier': '<xrootd>'}))
	log:Block /MY/DATASET#easy3 is not available at any site!
	0  True []              root://cms-xrd-global.cern.ch//store//path/file0 root://cms-xrd-global.cern.ch//store//path/file1 root://cms-xrd-global.cern.ch//store//path/file2
	1  True []              root://cms-xrd-global.cern.ch//store//path/file3 root://cms-xrd-global.cern.ch//store//path/file5
	2  True []              root://cms-xrd-global.cern.ch//store//path/file6 root://cms-xrd-global.cern.ch//store//path/file7 root://cms-xrd-global.cern.ch//store//path/file8 root://cms-xrd-global.cern.ch//store//path/file9
	"""

class Test_MetaPartitionProcessor:
	"""
	>>> testPP('MetaPartitionProcessor BasicPartitionProcessor', keys = ['KEY1', 'KEY2', 'KEY3'], dataset = 'dataK.dbs')
	0  True []              file1 file2 file3 filex None None None

	>>> testPP('MetaPartitionProcessor BasicPartitionProcessor', keys = ['KEY1', 'KEY2', 'KEY3'], dataset = 'dataK.dbs',
	... config = get_config({'partition metadata': 'KEY1'}))
	0  True []              file1 file2 file3 filex Value1 None None

	>>> testPP('MetaPartitionProcessor BasicPartitionProcessor', keys = ['KEY1', 'KEY2', 'KEY3'], dataset = 'dataK.dbs',
	... config = get_config({'partition metadata': 'KEY1 KEY2 KEY3'}))
	0  True []              file1 file2 file3 filex Value1 None None
	"""

class Test_TFCPartitionProcessor:
	"""
	>>> testPP('TFCPartitionProcessor BasicPartitionProcessor LocationPartitionProcessor')
	log:Block /MY/DATASET#easy3 is not available at any site!
	0  True [(8, ['SE4'])]  /path/file0 /path/file1 /path/file2
	1  True []              /path/file3 /path/file5
	2 False [(8, [])]       /path/file6 /path/file7 /path/file8 /path/file9

	>>> testPP('TFCPartitionProcessor BasicPartitionProcessor LocationPartitionProcessor',
	... config = get_config({'partition tfc': 'prefix:'}))
	log:Block /MY/DATASET#easy3 is not available at any site!
	0  True [(8, ['SE4'])]  prefix:/path/file0 prefix:/path/file1 prefix:/path/file2
	1  True []              prefix:/path/file3 prefix:/path/file5
	2 False [(8, [])]       prefix:/path/file6 prefix:/path/file7 prefix:/path/file8 prefix:/path/file9

	>>> testPP('TFCPartitionProcessor BasicPartitionProcessor LocationPartitionProcessor',
	... config = get_config({'partition tfc': 'prefix:\\nSE4 => xrootd:'}))
	log:Block /MY/DATASET#easy3 is not available at any site!
	0  True [(8, ['SE4'])]  xrootd:/path/file0 xrootd:/path/file1 xrootd:/path/file2
	1  True []              prefix:/path/file3 prefix:/path/file5
	2 False [(8, [])]       prefix:/path/file6 prefix:/path/file7 prefix:/path/file8 prefix:/path/file9

	>>> testPP('TFCPartitionProcessor BasicPartitionProcessor LocationPartitionProcessor',
	... config = get_config({'partition tfc': 'prefix:\\nSE => local:\\nST => xrootd:'}))
	log:Block /MY/DATASET#easy3 is not available at any site!
	0  True [(8, ['SE4'])]  local:/path/file0 local:/path/file1 local:/path/file2
	1  True []              prefix:/path/file3 prefix:/path/file5
	2 False [(8, [])]       prefix:/path/file6 prefix:/path/file7 prefix:/path/file8 prefix:/path/file9
	"""

class Test_PartitionProcessor:
	"""
	>>> testPP('BasicPartitionProcessor')
	log:Block /MY/DATASET#easy3 is not available at any site!
	0  True []              /path/file0 /path/file1 /path/file2
	1  True []              /path/file3 /path/file5
	2  True []              /path/file6 /path/file7 /path/file8 /path/file9

	>>> testPP('CMSSWPartitionProcessor')
	log:Block /MY/DATASET#easy3 is not available at any site!
	0  True []              "/path/file0", "/path/file1", "/path/file2"
	1  True []              "/path/file3", "/path/file5"
	2  True []              "/path/file6", "/path/file7", "/path/file8", "/path/file9"

	>>> testPP('LocationPartitionProcessor')
	log:Block /MY/DATASET#easy3 is not available at any site!
	0  True [(8, ['SE4'])]  <missing>
	1  True []              <missing>
	2 False [(8, [])]       <missing>

	>>> testPP('BasicPartitionProcessor LocationPartitionProcessor')
	log:Block /MY/DATASET#easy3 is not available at any site!
	0  True [(8, ['SE4'])]  /path/file0 /path/file1 /path/file2
	1  True []              /path/file3 /path/file5
	2 False [(8, [])]       /path/file6 /path/file7 /path/file8 /path/file9
	"""

run_test()
