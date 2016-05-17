#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
import time, random, logging
from testFwk import create_config, remove_files, setup_logging
from grid_control import utils
from grid_control.datasets import DataProvider, DataSplitter
from testDS import getRandomDatasets
from python_compat import irange

class RandomProvider(DataProvider):
	alias = ['rng']
	def __init__(self, config, datasetExpr, datasetNick, datasetID = 0):
		DataProvider.__init__(self, config, datasetExpr, datasetNick, datasetID)
		self.nBlocks = int(datasetExpr)
		print self.nBlocks
	def getBlocksInternal(self):
		return getRandomDatasets(10, self.nBlocks)

config = create_config(configDict = {
	'None': {
		'events per job': 25000,
		'files per job': 10,
		'nickname check collision': False,
		'splitter stack': 'BlockBoundarySplitter FileBoundarySplitter HybridSplitter',
	},
	'dummy': {
		'parameters': "cross(data(), var('A'))",
		'A': '1 2 3'
	},
	'dataset': {
		'resync interactive': False
	}
})

setup_logging()
logging.show = False
utils.ActivityLog = utils.ActivityLogOld

def display(info, t_start, total):
	diff = time.time() - start
	print(info + ' %f %f' % (diff, diff / float(total) * 1e3))

start = time.time()
provider = RandomProvider(config, '1000', None)
alldata = list(provider.getBlocks())
data1 = random.sample(alldata, int(len(alldata) * 0.8))
data2 = random.sample(alldata, int(len(alldata) * 0.8))
display ('t_get / 1kBlocks', start, len(alldata))

provider.saveToFile('data_large_all.dbs', alldata)
provider.saveToFile('data_large_1.dbs', data1)
provider.saveToFile('data_large_2.dbs', data2)

def checkSplitter(sc):
	start = time.time()
	splitFile = sc(config)
	splitFile.splitDataset('datamap-resync.tar', data1)
	display ('t_split / 1kJobs', start, splitFile.getMaxJobs())

	for x in irange(1):
		splitter = DataSplitter.loadPartitionsForScript('datamap-resync.tar')
		start = time.time()
		tmp = splitter.resyncMapping('datamap-resync1.tar', data1, data2)
		splitter = DataSplitter.loadPartitionsForScript('datamap-resync1.tar')
		display ('t_sync / 1kJobs', start, splitFile.getMaxJobs())

checkSplitter(DataSplitter.getClass('EventBoundarySplitter'))
#checkSplitter(DataSplitter.getClass('FLSplitStacker'))
remove_files(['data_large_all.dbs', 'data_large_1.dbs', 'data_large_2.dbs', 'datamap-resync.tar', 'datamap-resync1.tar'])
