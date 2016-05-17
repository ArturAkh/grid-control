#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import create_config, remove_files, run_test
from grid_control.datasets import DataProvider, DataSplitter, PartitionProcessor
from grid_control.parameters import ParameterSource
from grid_control.parameters.padapter import ParameterAdapter
from python_compat import irange

def getDS(userDict, fn = 'dataA.dbs'):
	configDict = {'dataset': {'dataset processor': 'LumiDataProcessor'}}
	configDict['dataset'].update(userDict or {})
	config = create_config(configDict = configDict)
	dsrc = DataProvider.createInstance('ListProvider', config, fn)
	return dsrc

def checkLDP(userDict = None, fn = 'dataA.dbs'):
	dsrc = getDS(userDict, fn)
	for b in dsrc.getBlocks():
		print('%s#%s meta:%s' % (b[DataProvider.Dataset], b[DataProvider.BlockName], b[DataProvider.Metadata]))
		for fi in b[DataProvider.FileList]:
			print('  %s:%d %s' % (fi[DataProvider.URL], fi[DataProvider.NEntries], fi[DataProvider.Metadata]))

def checkLPP(userDict = None, fn = 'dataA.dbs'):
	dsrc = getDS(userDict, fn)
	config = create_config(configDict = {'dataset': userDict})
	dsplit = DataSplitter.createInstance('FileBoundarySplitter', config)
	pproc_basic = PartitionProcessor.createInstance('BasicPartitionProcessor', config)
	pproc_se = PartitionProcessor.createInstance('LocationPartitionProcessor', config)
	pproc_lumi = PartitionProcessor.createInstance('LumiPartitionProcessor', config)
	pp = PartitionProcessor.createInstance('MultiPartitionProcessor', config, [pproc_basic, pproc_se, pproc_lumi])
	remove_files(['dummycache.dat', 'dummymap.tar'])
	ps = ParameterSource.createInstance('DataParameterSource', '.', 'dummy', dsrc, dsplit, pp, False)
	pa = ParameterAdapter(config, ps)
	for jobNum in irange(pa.getMaxJobs()):
		ji = pa.getJobInfo(jobNum)
		print('%s:%d %s' % (ji['FILE_NAMES'], ji['MAX_EVENTS'], ji['LUMI_RANGE']))

class Test_LumiProc:
	"""
	>>> remove_files(['dummycache.dat', 'dummymap.tar'])
	>>> checkLDP()
	/SingleMuon/Run2015E-PromptReco-v1/MINIAOD#17df3a8a-8e3d-11e5-9687-001e67abf228 meta:[]
	  /store/422/00000/A0C10611-438E-E511-93BE-02163E013522.root:3 []
	  /store/402/00000/44A8DF36-418E-E511-AECD-02163E013522.root:7576 []
	  /store/401/00000/3E4C8AD5-408E-E511-B6E5-02163E0134DB.root:13073 []
	  /store/399/00000/00AC9572-3F8E-E511-AE17-02163E014602.root:78409 []
	  /store/398/00000/4C3D439E-3D8E-E511-A01D-02163E0119C2.root:16788 []
	  /store/397/00000/CAAB76A3-3B8E-E511-9482-02163E0134F1.root:95082 []
	  /store/397/00000/A8DA65A7-3B8E-E511-8C33-02163E013745.root:56118 []

	>>> checkLDP({'lumi filter': '-'})
	/SingleMuon/Run2015E-PromptReco-v1/MINIAOD#17df3a8a-8e3d-11e5-9687-001e67abf228 meta:['Runs']
	  /store/422/00000/A0C10611-438E-E511-93BE-02163E013522.root:3 [[261422]]
	  /store/402/00000/44A8DF36-418E-E511-AECD-02163E013522.root:7576 [[261402]]
	  /store/401/00000/3E4C8AD5-408E-E511-B6E5-02163E0134DB.root:13073 [[261401]]
	  /store/399/00000/00AC9572-3F8E-E511-AE17-02163E014602.root:78409 [[261399]]
	  /store/398/00000/4C3D439E-3D8E-E511-A01D-02163E0119C2.root:16788 [[261398]]
	  /store/397/00000/CAAB76A3-3B8E-E511-9482-02163E0134F1.root:95082 [[261397]]
	  /store/397/00000/A8DA65A7-3B8E-E511-8C33-02163E013745.root:56118 [[261397]]

	>>> checkLDP({'lumi filter': '261400-'})
	/SingleMuon/Run2015E-PromptReco-v1/MINIAOD#17df3a8a-8e3d-11e5-9687-001e67abf228 meta:['Runs']
	  /store/422/00000/A0C10611-438E-E511-93BE-02163E013522.root:3 [[261422]]
	  /store/402/00000/44A8DF36-418E-E511-AECD-02163E013522.root:7576 [[261402]]
	  /store/401/00000/3E4C8AD5-408E-E511-B6E5-02163E0134DB.root:13073 [[261401]]

	>>> checkLDP({'lumi filter': '-261400'})
	/SingleMuon/Run2015E-PromptReco-v1/MINIAOD#17df3a8a-8e3d-11e5-9687-001e67abf228 meta:['Runs']
	  /store/399/00000/00AC9572-3F8E-E511-AE17-02163E014602.root:78409 [[261399]]
	  /store/398/00000/4C3D439E-3D8E-E511-A01D-02163E0119C2.root:16788 [[261398]]
	  /store/397/00000/CAAB76A3-3B8E-E511-9482-02163E0134F1.root:95082 [[261397]]
	  /store/397/00000/A8DA65A7-3B8E-E511-8C33-02163E013745.root:56118 [[261397]]

	>>> checkLDP({'lumi filter': '261399-261401'})
	/SingleMuon/Run2015E-PromptReco-v1/MINIAOD#17df3a8a-8e3d-11e5-9687-001e67abf228 meta:['Runs']
	  /store/401/00000/3E4C8AD5-408E-E511-B6E5-02163E0134DB.root:13073 [[261401]]
	  /store/399/00000/00AC9572-3F8E-E511-AE17-02163E014602.root:78409 [[261399]]

	>>> checkLDP({'lumi filter': '261399-261401', 'lumi keep': 'RunLumi'})
	/SingleMuon/Run2015E-PromptReco-v1/MINIAOD#17df3a8a-8e3d-11e5-9687-001e67abf228 meta:['Lumi', 'Runs']
	  /store/401/00000/3E4C8AD5-408E-E511-B6E5-02163E0134DB.root:13073 [[7, 12, 13, 6, 3, 4, 5, 8, 9, 10, 2, 11, 14, 1], [261401, 261401, 261401, 261401, 261401, 261401, 261401, 261401, 261401, 261401, 261401, 261401, 261401, 261401]]
	  /store/399/00000/00AC9572-3F8E-E511-AE17-02163E014602.root:78409 [[14, 3, 7, 8, 9, 4, 5, 16, 1, 6, 11, 13, 12, 10, 15, 2], [261399, 261399, 261399, 261399, 261399, 261399, 261399, 261399, 261399, 261399, 261399, 261399, 261399, 261399, 261399, 261399]]

	>>> checkLDP({'lumi filter': '261399-261401', 'lumi keep': 'none'})
	/SingleMuon/Run2015E-PromptReco-v1/MINIAOD#17df3a8a-8e3d-11e5-9687-001e67abf228 meta:[]
	  /store/401/00000/3E4C8AD5-408E-E511-B6E5-02163E0134DB.root:13073 []
	  /store/399/00000/00AC9572-3F8E-E511-AE17-02163E014602.root:78409 []

	>>> checkLPP({'lumi filter': '261399-261401', 'files per job': 1})
	/store/401/00000/3E4C8AD5-408E-E511-B6E5-02163E0134DB.root:13073 "261399:MIN-261401:MAX"
	/store/399/00000/00AC9572-3F8E-E511-AE17-02163E014602.root:78409 "261399:MIN-261401:MAX"

	>>> checkLPP({'lumi filter': '-', 'files per job': 1})
	/store/422/00000/A0C10611-438E-E511-93BE-02163E013522.root:3 "1:MIN-9999999:MAX"
	/store/402/00000/44A8DF36-418E-E511-AECD-02163E013522.root:7576 "1:MIN-9999999:MAX"
	/store/401/00000/3E4C8AD5-408E-E511-B6E5-02163E0134DB.root:13073 "1:MIN-9999999:MAX"
	/store/399/00000/00AC9572-3F8E-E511-AE17-02163E014602.root:78409 "1:MIN-9999999:MAX"
	/store/398/00000/4C3D439E-3D8E-E511-A01D-02163E0119C2.root:16788 "1:MIN-9999999:MAX"
	/store/397/00000/CAAB76A3-3B8E-E511-9482-02163E0134F1.root:95082 "1:MIN-9999999:MAX"
	/store/397/00000/A8DA65A7-3B8E-E511-8C33-02163E013745.root:56118 "1:MIN-9999999:MAX"

	>>> checkLPP({'lumi filter': '261399-261400,261401,261402', 'files per job': 1})
	/store/402/00000/44A8DF36-418E-E511-AECD-02163E013522.root:7576 "261402:MIN-261402:MAX"
	/store/401/00000/3E4C8AD5-408E-E511-B6E5-02163E0134DB.root:13073 "261401:MIN-261401:MAX"
	/store/399/00000/00AC9572-3F8E-E511-AE17-02163E014602.root:78409 "261399:MIN-261400:MAX"

	>>> checkLPP({'lumi filter': '261399-261400,261401,261402', 'files per job': 2})
	/store/402/00000/44A8DF36-418E-E511-AECD-02163E013522.root /store/401/00000/3E4C8AD5-408E-E511-B6E5-02163E0134DB.root:20649 "261401:MIN-261401:MAX","261402:MIN-261402:MAX"
	/store/399/00000/00AC9572-3F8E-E511-AE17-02163E014602.root:78409 "261399:MIN-261400:MAX"

	>>> checkLPP({'lumi filter': '261401:10-261402:3,261422', 'files per job': 1})
	/store/422/00000/A0C10611-438E-E511-93BE-02163E013522.root:3 "261422:MIN-261422:MAX"
	/store/402/00000/44A8DF36-418E-E511-AECD-02163E013522.root:7576 "261401:10-261402:3"
	/store/401/00000/3E4C8AD5-408E-E511-B6E5-02163E0134DB.root:13073 "261401:10-261402:3"

	>>> checkLPP({'lumi filter': '1000-2000', 'files per job': 1}, fn = 'dataB.dbs')
	/store/1000.root:123 "1000:MIN-2000:MAX"
	/store/1001.root:234 "1000:MIN-2000:MAX"
	/store/100x.root:345 "1000:MIN-2000:MAX"
	/store/1003.root:456 "1000:MIN-2000:MAX"
	/store/1004.root:567 "1000:MIN-2000:MAX"
	/store/1005.root:678 "1000:MIN-2000:MAX"
	/store/x1000.root:789 "1000:MIN-2000:MAX"
	/store/x2000.root:890 "1000:MIN-2000:MAX"

	>>> checkLPP({'lumi filter': '1000,2000\\ndataset_A => -1001\\ndataset_B => 1004-', 'files per job': 1}, fn = 'dataB.dbs')
	/store/1000.root:123 "1:MIN-1001:MAX"
	/store/1001.root:234 "1:MIN-1001:MAX"
	/store/1004.root:567 "1004:MIN-9999999:MAX"
	/store/1005.root:678 "1004:MIN-9999999:MAX"
	/store/x1000.root:789 "1000:MIN-1000:MAX"
	/store/x2000.root:890 "2000:MIN-2000:MAX"

	>>> remove_files(['dummycache.dat', 'dummymap.tar'])
	"""

run_test()
