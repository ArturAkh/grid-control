import os
from testFwk import create_config
from grid_control.datasets import DataProvider, DataSplitter
from testDS import getLFNMap, printSplitNice

def doInitSplit(doprint = True, nEvent = 3, srcFN = "data-old.dbs"):
	dsplit = DataSplitter.createInstance('EventBoundarySplitter', create_config(configDict={'dataset': {'events per job': nEvent}}))
	data_old = DataProvider.loadFromFile(srcFN)
	dsplit.splitDataset("datamap-resync.tar", data_old.getBlocks())
	if doprint:
		printSplitNice(DataSplitter.loadPartitionsForScript("datamap-resync.tar"), getLFNMap(blocks = data_old.getBlocks()), False)

def doResync(doprint = True, configDict = {}, srcFN = "data-old.dbs", modFN = "data-new.dbs", doRename = True):
	configDict.setdefault('dataset', {})['resync interactive'] = 'False'
	config = create_config(configDict = configDict)
	split_old = DataSplitter.loadPartitionsForScript("datamap-resync.tar", config)
	data_old = DataProvider.loadFromFile(srcFN)
	data_new = DataProvider.loadFromFile(modFN)
	tmp = split_old.resyncMapping("datamap-resync-new.tar", data_old.getBlocks(), data_new.getBlocks())
	os.rename("datamap-resync-new.tar", "datamap-resync.tar")
	if doRename:
		os.rename(modFN, srcFN)
	if doprint:
		split_new = DataSplitter.loadPartitionsForScript("datamap-resync.tar")
		print("(%s, %s, %s)" % (tmp[0], tmp[1], split_new.getMaxJobs() != split_old.getMaxJobs()))
		printSplitNice(split_new, getLFNMap(blocks = data_new.getBlocks()), False)
