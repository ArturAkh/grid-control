import copy, random
from grid_control import utils
from grid_control.datasets import DataProvider, DataSplitter
from python_compat import ifilter, imap, irange, izip, lmap, md5_hex, set, sorted

def mkmd5(x):
	return md5_hex(repr(x))

def getRandomDatasets(nDS = 9, nBlocks = 100, nFiles = 99, nEvents = 12500, nSE = 6, nSETotal = 10,
		nDirPrefixes = 4, nDirPrefixesTotal = 9, dsSeed = 0, blockSeedCounter = 1512, wildSeed = 0):

	random.seed(dsSeed)
	ds = lmap(lambda x: '/dataset/DS_%s' % mkmd5(random.random())[:16], irange(nDS))
	prefixes = lmap(lambda x: 'DIR_%s' % mkmd5(x)[:10], irange(nDirPrefixesTotal))
	SEs = lmap(lambda x: 'SE_%04d' % x, irange(nSETotal))

	for nBlock in irange(nBlocks):
		random.seed(nBlock + blockSeedCounter + dsSeed + random.randint(0, wildSeed))
		dsName = random.choice(ds)
		bName = mkmd5(random.random())[:8]
		pf = random.sample(prefixes, random.randint(1, nDirPrefixes))
		selist = random.sample(SEs, random.randint(0, nSE))
		if random.random() < 0.05:
			selist = None
		flist = lmap(lambda x: {
			DataProvider.URL: '/%s/FILE_%s' % (str.join('/', pf), mkmd5(random.random())),
			DataProvider.NEntries: random.randint(1, nEvents)
		}, irange(random.randint(1, nFiles)))
		yield {
			DataProvider.Dataset: dsName,
			DataProvider.BlockName: bName,
			DataProvider.Locations: selist,
			DataProvider.FileList: flist
		}

def printSplit(x, meta = False):
	head = [(10, 'x'), (DataSplitter.NEntries, 'SIZE'), (DataSplitter.Skipped, 'SKIP'), (DataSplitter.FileList, 'Files')]
	if meta:
		head.append((DataSplitter.Metadata, 'Metadata'))
		head.append((DataSplitter.Invalid, 'Invalid'))
	sinfo = lmap(lambda y : dict(list(x.getSplitInfo(y).items()) + [(10, y)]), irange(x.getMaxJobs()))
	utils.printTabular(head, sinfo, 'cccll')

def getLFNMap(src = None, blocks = None):
	result = {}
	if src:
		blocks = src.getBlocks()
	for b in blocks:
		for fi in b[DataProvider.FileList]:
			result[fi[DataProvider.URL]] = fi[DataProvider.NEntries]
	return result

def printSplitNice(sp, src, intro = True, printIdx = False, printComment = False, reuse = None, printLocation = False):
	last = 0
	charSrc = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
	allFiles = set()
	for x in irange(sp.getMaxJobs()):
		allFiles.update(sp.getSplitInfo(x)[DataSplitter.FileList])
	assert(len(allFiles) <= len(charSrc))
	if reuse is not None:
		allFiles = allFiles.difference(list(reuse.keys()))
		for char in reuse.values():
			charSrc = charSrc.replace(char, '')
		charMap = dict(reuse)
		charMap.update(dict(izip(sorted(allFiles), charSrc)))
	else:
		charMap = dict(izip(sorted(allFiles), charSrc))
	if not intro:
		for lfn in sorted(src):
			print('%s: %s' % (lfn, charMap[lfn]))
	fileoffset = {}
	for x in irange(sp.getMaxJobs()):
		si = sp.getSplitInfo(x)
		if printLocation:
			print('sites = %r' % si.get(DataSplitter.Locations))
		if not si[DataSplitter.FileList]:
			if si.get(DataSplitter.Invalid):
				msg = '<disabled partition without files>'
			else:
				msg = '<partition without files>'
			print(msg)
			continue
		fm = dict(imap(lambda x: (x, charMap[x]), si[DataSplitter.FileList]))
		seen = []
		for lfn in fm:
			if fm[lfn] in seen:
				fm[lfn] = fm[lfn].lower()
			seen.append(fm[lfn])
		allev = sum(imap(lambda fi: src.get(fi, 0), si[DataSplitter.FileList]))
		pos = 0
		value = ''
		if printIdx:
			if si.get(DataSplitter.Invalid):
				value += '%04d: ' % x
			else:
				value += '%4d: ' % x
		for lfn in si[DataSplitter.FileList]:
			if lfn not in fileoffset:
				fileoffset[lfn] = pos
			if lfn not in src:
				value += '!'
				pos += 1
				continue
			while pos < fileoffset[lfn]:
				value += ' '
				pos += 1
			value += fm[lfn] * src[lfn]
			pos += src[lfn]
		value += '  => %d' % allev

		if si.get(DataSplitter.Invalid):
			value += '    <disabled>'
		if si.get(DataSplitter.Comment) and printComment:
			value += ' [%s]' % si.get(DataSplitter.Comment)
		if intro:
			if printIdx:
				for fi in si[DataSplitter.FileList]:
					print('      %s: %s' % (fi, fm[fi]))
			else:
				print(str.join(', ', imap(lambda fi: '%s: %s' % (fi, fm[fi]), si[DataSplitter.FileList])))
		print(value)
		left = allev - si.get(DataSplitter.Skipped, 0) - si[DataSplitter.NEntries]
		firstFile = si[DataSplitter.FileList][0]
		msg = ''
		if printIdx:
			msg = '     '
		msg += ' ' * (fileoffset[firstFile] + si.get(DataSplitter.Skipped, 0))
		msg += '-' * si[DataSplitter.NEntries]
		msg += ' ' * left
		msg += '  => %d,%d' % (si.get(DataSplitter.Skipped, 0), si[DataSplitter.NEntries])
		print(msg)
	if reuse is not None:
		return charMap

def checkCoverage(splitting, datasrc):
	sizeMap = getLFNMap(blocks = datasrc)
	coverMap = {}
	for lfn in sizeMap:
		coverMap[lfn] = lmap(lambda x: [], irange(sizeMap[lfn]))

	try:
		for splitNum in irange(splitting.getMaxJobs()):
			try:
				si = splitting.getSplitInfo(splitNum)
				if si.get(DataSplitter.Invalid):
					continue

				posSplit = 0
				posLFN = si.get(DataSplitter.Skipped, 0)
				for lfn in si[DataSplitter.FileList]:
					while (posSplit < si[DataSplitter.NEntries]) and (posLFN < sizeMap[lfn]):
						coverMap[lfn][posLFN].append(splitNum)
						posSplit += 1
						posLFN += 1
					posLFN = 0
				assert(posSplit == si[DataSplitter.NEntries])
			except:
				msg = 'Invalid splitting!'
				msg += ' splitNum %d' % splitNum
				msg += ' posSplit %d' % posSplit
				msg += ' nEv %d' % si[DataSplitter.NEntries]
				msg += ' posLFN %s' % posLFN
				msg += ' %s' % si
				print(msg)
				raise

		failed = []
		for lfn in coverMap:
			try:
				splitCoverage = lmap(len, coverMap[lfn])
				assert(min(splitCoverage) == 1)
				assert(max(splitCoverage) == 1)
			except:
				failed.append((lfn, coverMap[lfn]))
		if failed:
			for lfn, m in failed:
				print('problem with %s %s' % (lfn, m))
			raise Exception()
	except Exception:
		print('Problem found!')
		printSplitNice(splitting, sizeMap, True, True, True)
		raise

def ss2bl(ss):
	files = set()
	for x in ss:
		if x.strip() != '-' and x.strip():
			files.add(x)
	block = {DataProvider.Dataset: 'Dataset', DataProvider.BlockName: 'Block'}
	block[DataProvider.FileList] = lmap(lambda lfn: {DataProvider.URL: lfn, DataProvider.NEntries: ss.count(lfn)}, sorted(files))
	return [block]

def modDS(ds, modstr):
	modDict = {}
	for mod in modstr.split():
		lfn, newSize = mod.split(':')
		modDict[lfn] = int(newSize)

	usedLFN = []
	newFileList = []
	ds = copy.deepcopy(ds)
	for fi in ds[0][DataProvider.FileList]:
		usedLFN.append(fi[DataProvider.URL])
		fi[DataProvider.NEntries] = modDict.get(fi[DataProvider.URL], fi[DataProvider.NEntries])
		if fi[DataProvider.NEntries]:
			newFileList.append(fi)

	for unusedLFN in ifilter(lambda lfn: lfn not in usedLFN, modDict):
		newFileList.append({DataProvider.URL: unusedLFN, DataProvider.NEntries: modDict[unusedLFN]})
	ds[0][DataProvider.FileList] = newFileList
	return ds
