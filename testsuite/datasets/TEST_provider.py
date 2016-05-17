#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import cmp_obj, create_config, remove_files, run_test, try_catch
from grid_control import utils
from hpfwk import Plugin
from python_compat import imap, lmap

config1 = create_config(configDict = {
	'datasetexample': {
		'dataset location filter': 'SE1 SE2 SE3 -SE4',
	},
}).changeView(setSections = ['datasetexample'])
config2 = create_config()
config3 = create_config(configDict = {
	'datasetfoo': {
		'dataset limit events': '21',
		'nickname check collision': 'False',
	},
})

DP = Plugin.getClass('DataProvider')
NP = Plugin.getClass('NickNameProducer')
BlockBoundarySplitter = Plugin.getClass('BlockBoundarySplitter')
EventBoundarySplitter = Plugin.getClass('EventBoundarySplitter')

def create_multi(value, defaultProvider):
	config = create_config(configDict = {'section': {'dataset provider': defaultProvider}})
	dp_list = []
	for x in DP.bind(value, config = config):
		dp_list.append(x.getBoundInstance())
	return DP.getClass('MultiDatasetProvider')(config, None, None, None, dp_list)

class Test_NicknameProducer:
	"""
	>>> np1 = NP.createInstance('NickNameProducer', config1)
	>>> try_catch(lambda: np1.getName('', '/PRIVATE/TESTDS#TESTBLOCK', None), 'AbstractError', 'is an abstract function')
	caught
	>>> np2 = NP.createInstance('SimpleNickNameProducer', config1)
	>>> np2.getName('', '/PRIVATE/TESTDS#TESTBLOCK', None)
	'TESTDS'
	>>> np2.getName('', '/LEVEL1/TESTDS#TESTBLOCK', None)
	'LEVEL1_TESTDS'
	>>> np2.getName('nick1', '/PRIVATE/TESTDS#TESTBLOCK', None)
	'nick1'
	"""

class Test_FileProvider:
	"""
	>>> dpFile1 = DP.createInstance('FileProvider', config1, '/path/ to /file | 123 @ SE1, SE2, SE4', None)
	>>> bf1 = list(dpFile1.getBlocks())
	>>> cmp_obj(bf1, [{DP.NEntries: 123, DP.BlockName: '0', DP.Dataset: '/path/ to /file', DP.Locations: ['SE1', 'SE2'], DP.Nickname: 'path_to_file', DP.FileList: [{DP.NEntries: 123, DP.URL: '/path/ to /file'}], DP.Provider: 'FileProvider'}])
	>>> try_catch(lambda: DP.createInstance('FileProvider', config1, '/path/ to /file @ SE1, SE2, SE4', None), 'PluginError', 'Error while creating instance of type FileProvider')
	caught

	>>> dpFile3 = DP.createInstance('FileProvider', config1, '/path/ to /file | 123 @ SE4, SE5', None)
	>>> bf3 = list(dpFile3.getBlocks())
	log:Block /path/ to /file#0 is not available at any selected site!
	>>> cmp_obj(bf3, [{DP.NEntries: 123, DP.BlockName: '0', DP.Dataset: '/path/ to /file', DP.Locations: [], DP.Nickname: 'path_to_file', DP.FileList: [{DP.NEntries: 123, DP.URL: '/path/ to /file'}], DP.Provider: 'FileProvider'}])

	>>> dpFile4 = DP.createInstance('FileProvider', config1, '/path/ to /file | 123 @ ', None)
	>>> bf4 = list(dpFile4.getBlocks())
	>>> cmp_obj(bf4, [{DP.NEntries: 123, DP.BlockName: '0', DP.Dataset: '/path/ to /file', DP.Locations: None, DP.Nickname: 'path_to_file', DP.FileList: [{DP.NEntries: 123, DP.URL: '/path/ to /file'}], DP.Provider: 'FileProvider'}])
	"""

class Test_ListProvider:
	"""
	>>> dpList1 = DP.createInstance('ListProvider', config1, 'dataA.dbs % unchanged', None)
	>>> bl1 = list(dpList1.getBlocks())
	>>> cmp_obj(bl1, [{DP.NEntries: 30, DP.BlockName: 'unchanged', DP.Dataset: '/MY/DATASET', DP.Locations: None, DP.Nickname: 'MY_DATASET', DP.FileList: [{DP.NEntries: 10, DP.URL: '/path/UC1'}, {DP.NEntries: 5, DP.URL: '/path/UC2'}, {DP.NEntries: 15, DP.URL: '/path/UC3'}], DP.Provider: 'ListProvider'}])
	>>> sum(imap(lambda x: x[DP.NEntries], bl1))
	30

	>>> dpList2 = DP.createInstance('ListProvider', config3, 'dataA.dbs', None)
	>>> sum(imap(lambda x: x[DP.NEntries], dpList2.getBlocks())) <= 21
	True

	>>> dpList3 = DP.createInstance('ListProvider', config1, 'dataC.dbs @ /enforced', None)
	>>> bl3 = list(dpList3.getBlocks())
	>>> bl3 == [{DP.NEntries: 20, DP.BlockName: 'test', DP.Dataset: '/MY/DATASET', DP.Locations: ['SE1', 'SE2'], \
		DP.Nickname: 'TESTNICK', DP.DatasetID: 423, DP.Metadata: ['KEY1', 'KEY2'], \
		DP.FileList: [\
			{DP.NEntries: 5, DP.URL: '/enforced/file1', DP.Metadata: [[1,2,3], 'Test1']},\
			{DP.NEntries: 15, DP.URL: '/enforced/file2', DP.Metadata: [[9,8,7], 'Test2']}],\
		DP.Provider: 'ListProvider'}]
	True

	>>> dpList4 = DP.createInstance('ListProvider', config1, 'dataD.dbs', None)
	>>> try_catch(lambda: list(dpList4.getBlocks()), 'DatasetError', 'Unable to retrieve dataset')
	caught

	>>> dpList5 = DP.createInstance('ListProvider', config1, 'dataF.dbs', None)
	>>> bl5 = list(dpList5.getBlocks())
	log:Inconsistency in block /MY/DATASET#fail: Number of events doesn't match (b:200 != f:30)

	>>> lmap(lambda x: x[DP.Locations], DP.createInstance('ListProvider', config1, 'dataE.dbs', None).getBlocks())
	log:Block /MY/DATASET#easy1 is not available at any selected site!
	log:Block /MY/DATASET#easy3 is not available at any site!
	[[], None, []]

	>>> lmap(lambda x: x[DP.Locations], DP.createInstance('ListProvider', config2, 'dataE.dbs', None).getBlocks())
	log:Block /MY/DATASET#easy3 is not available at any site!
	[['SE4'], None, []]

	>>> dpRL1 = DP.createInstance('ListProvider', config1, 'dataRL.dbs').getBlocks()
	log:Block /MinimumBias/Commissioning10-SD_Mu-Jun14thSkim_v1/RECO#f95a8d7e-f710-458d-8d0f-0d58a7667256 is not available at any selected site!
	log:Block /MinimumBias/Commissioning10-SD_Mu-Jun14thSkim_v1/RECO#b97fa5ba-925c-4bdb-98c9-bd92340f7440 is not available at any selected site!
	log:Block /MinimumBias/Commissioning10-SD_Mu-Jun14thSkim_v1/RECO#7bbb3050-fc83-4310-9944-e27821493fb6 is not available at any selected site!
	log:Block /MinimumBias/Commissioning10-SD_Mu-Jun14thSkim_v1/RECO#3bd6f9d3-aae2-4e94-ac5b-4eedd0a57a97 is not available at any selected site!
	log:Block /MinimumBias/Commissioning10-SD_Mu-Jun14thSkim_v1/RECO#343bb143-2385-4f11-9641-3b53743c2ccf is not available at any selected site!
	log:Block /MinimumBias/Commissioning10-SD_Mu-Jun14thSkim_v1/RECO#23c131a1-0fd2-4a77-9435-179f71c00b0e is not available at any selected site!
	log:Block /MinimumBias/Commissioning10-SD_Mu-Jun14thSkim_v1/RECO#1ce21f58-dd02-478e-866f-b208d5e450ab is not available at any selected site!
	log:Block /MinimumBias/Commissioning10-SD_Mu-Jun14thSkim_v1/RECO#07f7f674-dd7d-4508-9e49-9879f61b7c3e is not available at any selected site!

	>>> dpRL2 = DP.createInstance('ListProvider', config2, 'dataRL.dbs')
	>>> DP.saveToFile('dataRL1.dbs', dpRL2.getBlocks())
	>>> DP.loadFromFile('dataRL1.dbs').getBlocks() == dpRL2.getBlocks()
	True
	>>> remove_files(['dataRL1.dbs'])

	"""

class Test_Provider:
	"""
	>>> try_catch(lambda: DP(config1, 'DUMMY', 'NICK', 123).getBlocks(), 'DatasetError', 'Unable to retrieve dataset')
	caught
	"""

class Test_MultiProvider:
	"""
	>>> dpMulti1 = create_multi('nick : /path/file1|123\\n/path/file2|987', 'FileProvider')
	>>> dpMulti1.checkSplitter(EventBoundarySplitter).__name__
	'EventBoundarySplitter'
	
	>>> def confuser(splitClass):
	...   if splitClass == EventBoundarySplitter:
	...      return BlockBoundarySplitter
	...   return EventBoundarySplitter
	>>> dpMulti1._providerList[0].checkSplitter = confuser
	>>> try_catch(lambda: dpMulti1.checkSplitter(EventBoundarySplitter), 'DatasetError', 'Dataset providers could not agree on valid dataset splitter')
	caught
	>>> dpMulti1.queryLimit()
	60

	>>> bm1 = list(dpMulti1.getBlocks())
	>>> cmp_obj(bm1, [\
{DP.NEntries: 123, DP.BlockName: '0', DP.Dataset: '/path/file1', DP.Locations: None, DP.FileList: [{DP.NEntries: 123, DP.URL: '/path/file1'}], DP.Nickname: 'nick', DP.Provider: 'FileProvider'}, \
{DP.NEntries: 987, DP.BlockName: '0', DP.Dataset: '/path/file2', DP.Locations: None, DP.FileList: [{DP.NEntries: 987, DP.URL: '/path/file2'}], DP.Nickname: 'path_file2', DP.DatasetID: 1, DP.Provider: 'FileProvider'}\
])

	>>> dpMulti2 = create_multi('dataA.dbs\\ndataD.dbs', 'ListProvider')
	>>> try_catch(lambda: dpMulti2.getBlocks(), 'DatasetError', 'Could not retrieve all datasets')
	caught
	>>> dpMulti3 = create_multi('/path/file1|123\\n/path/file2|123', 'FileProvider')
	>>> utils.abort(True)
	True
	>>> try_catch(lambda: list(dpMulti3.getBlocks()), 'DatasetError', 'Could not retrieve all datasets')
	caught
	"""

run_test()
