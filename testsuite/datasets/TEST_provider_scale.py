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

setup_logging()
logging.show = False
utils.ActivityLog = utils.ActivityLogOld

class RandomProvider(DataProvider):
	alias = ['rng']
	def __init__(self, config, datasetExpr, datasetNick, datasetID = 0):
		DataProvider.__init__(self, config, datasetExpr, datasetNick, datasetID)
		self.nBlocks = int(datasetExpr)
	def getBlocksInternal(self):
		return getRandomDatasets(self.nBlocks)

config = create_config(configDict = {
	'foosection': {
		'events per job': 25000,
		'files per job': 10,
		'splitter stack': 'BlockBoundarySplitter FileBoundarySplitter HybridSplitter',
		'nickname check collision': False,
		'resync interactive': False
	}
})

def display(info, t_start, total):
	diff = time.time() - start
	print(info + ' %f %f' % (diff, diff / float(total) * 1e3))

start = time.time()
provider = RandomProvider(config, 1000000, None)
allData = provider.getBlocks()
display('t_get / 1kBlocks', start, len(allData))

data1 = random.sample(allData, int(len(allData) * 0.9))
data2 = random.sample(allData, int(len(allData) * 0.9))

start = time.time()
provider.saveToFile('datacache-1.dat', data1)
display('t_dsave1 / 1kBlocks', start, len(data1))

start = time.time()
provider.saveToFile('datacache-2.dat', data2)
display('t_dsave2 / 1kBlocks', start, len(data2))

start = time.time()
splitFile = DataSplitter.createInstance('FLSplitStacker', config)
splitFile.splitDataset('datamap-large.tar', data1)
display('t_split / 1kJobs', start, splitFile.getMaxJobs())

start = time.time()
for jobNum in irange(splitFile.getMaxJobs()):
	splitFile.getSplitInfo(jobNum)
display('t_iter / 1kJobs', start, splitFile.getMaxJobs())

start = time.time()
jobChanges = splitFile.resyncMapping('datamap-resync.tar', data1, data2)
display('t_sync / 1kJobs', start, splitFile.getMaxJobs())

remove_files(['datacache-1.dat', 'datacache-2.dat', 'datamap-large.tar', 'datamap-resync.tar'])
