from testFwk import create_config, str_dict
from grid_control import utils
from grid_control.datasets import DataProvider, DataSplitter, PartitionProcessor
from grid_control.parameters import ParameterInfo, ParameterMetadata
from grid_control.parameters.padapter import ParameterAdapter
from testDS import modDS
from python_compat import ifilter, imap, irange, lfilter, lmap, set, sorted

def testPS(ps, setiv = False, showJob = False):
	pa = ParameterAdapter(create_config(), ps)
	if setiv:
		ps.resyncSetup(info = (set([1]), set([2]), False))
	testPA(pa, showJob = showJob)

def orderedKeys(keys, showJob = True, showPNum = True):
	result = lfilter(lambda k: k not in ['GC_JOB_ID', 'GC_PARAM'], sorted(keys))
	if showJob:
		result.extend(ifilter(lambda k: k in ['GC_JOB_ID'], sorted(keys)))
	if showPNum:
		result.extend(ifilter(lambda k: k in ['GC_PARAM'], sorted(keys)))
	return result

def printJobInfo(ps, idx, keys = None, showJobPrefix = True):
	msg = ''
	if showJobPrefix:
		msg = '%d ' % idx
	return msg + str_dict(ps.getJobInfo(idx), keys)

def testPA(pa, showJob = True, showPNum = True, showMetadata = True, showJobPrefix = True,
		showKeys = True, showUntracked = True, showIV = True, manualKeys = None, newlineEvery = 1):
	iv = pa.resync()
	print(pa.getMaxJobs())

	keys = orderedKeys(pa.getJobKeys(), showJob, showPNum)
	if showKeys:
		print('Keys = %s' % str.join(', ', imap(lambda key: '%s%s' % (key, utils.QM(key.untracked, '', ' [trk]')), keys)))
	if not showUntracked:
		keys = lfilter(lambda k: not k.untracked, keys)
	if showMetadata:
		keys = [ParameterInfo.ACTIVE, ParameterInfo.HASH, ParameterInfo.REQS] + keys
	if manualKeys != None:
		keys = sorted(ifilter(lambda k: k.lower() in imap(str.lower, manualKeys), pa.getJobKeys()))

	if pa.getMaxJobs() == None:
		print(printJobInfo(pa, 1, keys, showJobPrefix = showJobPrefix))
		print(printJobInfo(pa, 11, keys, showJobPrefix = showJobPrefix))
	else:
		msg = []
		for jobNum in irange(pa.getMaxJobs()):
			msg.append(printJobInfo(pa, jobNum, keys, showJobPrefix = showJobPrefix))
			if jobNum % newlineEvery == (newlineEvery - 1):
				msg.append('\n')
			else:
				msg.append(' ')
		print(str.join('', msg).rstrip())

	if showIV:
		if iv != None:
			print('redo: %s disable: %s size: %s' % (sorted(iv[0]), sorted(iv[1]), iv[2]))
		else:
			print(str(iv))

def updateDS(data_raw, modstr, pd = None):
	DataProvider.saveToFile('dataset.tmp', modDS(data_raw, modstr))

class DataSplitProcessorTest(PartitionProcessor):
	def getKeys(self):
		result = lmap(lambda k: ParameterMetadata(k, untracked=True), ['FN', 'EVT', 'SKIP'])
		result.append(ParameterMetadata('SID', untracked = False))
		return result
	def process(self, pNum, splitInfo, result):
		result.update({
			'FN': str.join(' ', splitInfo[DataSplitter.FileList]),
			'EVT': splitInfo[DataSplitter.NEntries],
			'SKIP': splitInfo.get(DataSplitter.Skipped, 0),
			'SID': pNum,
		})
		result[ParameterInfo.ACTIVE] = result[ParameterInfo.ACTIVE] and not splitInfo.get(DataSplitter.Invalid, False)
