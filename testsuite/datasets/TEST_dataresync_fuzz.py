#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
import copy, random, logging
from testFwk import setup_logging
from grid_control import utils
from hpfwk import Plugin
from testDS import checkCoverage, getRandomDatasets
from testResync import doInitSplit, doResync
from python_compat import irange, lmap, md5_hex

setup_logging()
logging.show = False
DataSplitter = Plugin.getClass('DataSplitter')
DataProvider = Plugin.getClass('DataProvider')

def modifyBlock(block, seed = 0):
	block = copy.deepcopy(block)
	random.seed(seed)
	rng = lambda x: random.random() < x
	fl = block[DataProvider.FileList]
	if rng(0.05):
		fl = list(random.sample(fl, max(1, len(fl) - random.randint(0, 4))))
	avgEvents = 0
	for fi in fl:
		if rng(0.1):
			if rng(0.5):
				fi[DataProvider.NEntries] += random.randint(0, 5)
			else:
				fi[DataProvider.NEntries] -= random.randint(0, 5)
			fi[DataProvider.NEntries] = max(1, fi[DataProvider.NEntries])
		avgEvents += fi[DataProvider.NEntries]
	avgEvents = avgEvents / len(fl)
	if rng(0.05):
		for x in irange(random.randint(0, 4)):
			lfn = fl[0][DataProvider.URL].split('FILE')[0]
			lfn += 'FILE_%s' % md5_hex(str(random.random()))
			nev = random.randint(max(1, avgEvents - 5), max(1, avgEvents + 5))
			fl.append({DataProvider.URL: lfn, DataProvider.NEntries: nev})
	if rng(0.1):
		random.shuffle(fl)
	block[DataProvider.FileList] = fl
	return block

def cascade_lb(nDS = 2, nMod = 2, nEvents = 2000):
	# Check large
	print("multiple blocks - Cascaded resyncs...")
	log = None
	for t in irange(nDS):
		initialData = list(getRandomDatasets(nDS = 5, nBlocks = 10, nFiles = 50, nEvents = nEvents, nSE = 3, dsSeed = t + 123))

		# Check for cascaded resyncs
		DataProvider.saveToFile('data-old.dbs', initialData)
		doInitSplit(False, 200)
		checkCoverage(DataSplitter.loadPartitionsForScript("datamap-resync.tar"), initialData)

		modified = initialData
		for x in irange(nMod):
			del log
			log = utils.ActivityLogOld('Sync test %s/%s %s/%s' % (t, nDS, x, nMod))
			modified = lmap(lambda b: modifyBlock(b, x + 1000*t), modified)
			DataProvider.saveToFile('data-new.dbs', modified)
#			DataProvider.saveToFile('data-new.dbs.tmp', modified)
			doResync(False)
			try:
				checkCoverage(DataSplitter.loadPartitionsForScript("datamap-resync.tar"), modified)
			except:
				print("Resync id %d %d" % (t, x))
				raise

def cascade_1b(nTests = 1000, nEvents = 15):
	initialData = list(getRandomDatasets(nDS = 1, nBlocks = 1, nFiles = 50, nEvents = nEvents, nSE = 1, dsSeed = 1))

	# Check for cascaded resyncs
#	DataProvider.saveToFile('data-ori.dbs', initialData)
	DataProvider.saveToFile('data-old.dbs', initialData)
	doInitSplit(False, 5)
	checkCoverage(DataSplitter.loadPartitionsForScript("datamap-resync.tar"), initialData)

#	print "1 block - Cascaded resyncs..."
	log = None
	modified = initialData
	for x in irange(nTests):
		del log
		log = utils.ActivityLogOld('Sync test %s/%s' % (x, nTests))
		modified = lmap(lambda b: modifyBlock(b, x), modified)
		DataProvider.saveToFile('data-new.dbs', modified)
#		DataProvider.saveToFile('data-new.dbs.%d' % x, modified)
		doResync(False)
		try:
			checkCoverage(DataSplitter.loadPartitionsForScript("datamap-resync.tar"), modified)
		except:
			print("Resync id %d" % x)
			raise

def single_1b(nTests = 1000, nEvents = 15):
	initialData = list(getRandomDatasets(nDS = 1, nBlocks = 1, nFiles = 50, nEvents = nEvents, nSE = 1, dsSeed = 1))

	# Check for single resyncs
	print("1 block - Single resyncs...")
	log = None
	for x in irange(nTests):
		del log
		log = utils.ActivityLogOld('Sync test %s/%s' % (x, nTests))
		DataProvider.saveToFile('data-old.dbs', initialData)
		DataProvider.saveToFile('data-ori.dbs', initialData)
		doInitSplit(False, 5)
		checkCoverage(DataSplitter.loadPartitionsForScript("datamap-resync.tar"), initialData)

		modified = lmap(lambda b: modifyBlock(b, x), initialData)
		DataProvider.saveToFile('data-new.dbs', modified)
#		DataProvider.saveToFile('data-new.dbs.%d' % x, modified)
		doResync(False)
		try:
			checkCoverage(DataSplitter.loadPartitionsForScript("datamap-resync.tar"), modified)
		except:
			print("Resync seed %d" % x)
			print(initialData)
			print(modified)
			raise

cascade_1b(20, 1)
single_1b(100, 1)
cascade_lb(nDS = 5, nMod = 20, nEvents = 1)

single_1b(100)
cascade_1b(20)
cascade_lb(nDS = 2, nMod = 20)

single_1b(5)
cascade_1b(2)
cascade_lb(nDS = 2, nMod = 10, nEvents = 10)
