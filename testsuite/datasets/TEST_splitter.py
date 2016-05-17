#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import create_config, remove_files, run_test, try_catch
from grid_control.datasets import DataProvider, DataSplitter
from testDS import getLFNMap, printSplit, printSplitNice

remove_files(['datamap.tar', 'datamap-new.tar'])

config1 = create_config(configDict = {
	'somesection': {
		'resync interactive': 'False',
		'events per job': '10',
		'files per job': '2',
	},
})

config1a = create_config(configDict = {
	'somesection': {
		'resync interactive': 'False',
		'events per job': '10',
		'files per job': '2',
		'run range': 2,
	},
})

config2 = create_config(configDict = {
	'myexampletask': {
		'events per job': '15',
		'files per job': '2',
		'splitter stack': 'BlockBoundarySplitter FileBoundarySplitter EventBoundarySplitter',
	},
})

config3 = create_config(configDict = {
	'dataset0': {'resync interactive': 'False', 'events per job': '7'},
})

class Test_BlockBounarySplitter:
	"""
	>>> dataE = DataProvider.loadFromFile('dataE.dbs')
	>>> splitBlock = DataSplitter.createInstance('BlockBoundarySplitter', config1)
	>>> splitBlock.splitDataset('datamap.tar', dataE.getBlocks())
	log:Block /MY/DATASET#easy3 is not available at any site!
	>>> dataEmap = getLFNMap(dataE)
	>>> printSplitNice(splitBlock, dataEmap)
	/path/file0: A, /path/file1: B, /path/file2: C
	AAAAAAAAAABBBBBCCCCCCCCCCCCCCC  => 30
	------------------------------  => 0,30
	/path/file3: D, /path/file5: E
	DDDDDDDDDDEEEEE  => 15
	---------------  => 0,15
	/path/file6: F, /path/file7: G, /path/file8: H, /path/file9: I
	FFFFFFFFFFGGGGGHHHHHHHHHHIIIIIIIIIIIIIII  => 40
	----------------------------------------  => 0,40

	>>> DataSplitter.FileList in splitBlock.neededEnums()
	True
	>>> DataSplitter.NEntries in splitBlock.neededEnums()
	False
	>>> DataSplitter.Skipped in splitBlock.neededEnums()
	False

	>>> printSplit(DataSplitter.loadPartitionsForScript("datamap.tar"))
	 x | SIZE | SKIP |                            Files                             
	===+======+======+==============================================================
	 0 |  30  |      | ['/path/file0', '/path/file1', '/path/file2']                
	 1 |  15  |      | ['/path/file3', '/path/file5']                               
	 2 |  40  |      | ['/path/file6', '/path/file7', '/path/file8', '/path/file9'] 

	>>> dpFile1 = DataProvider.createInstance('FileProvider', config1, '/path/to/file | -1', None)
	>>> splitBlock.splitDataset('datamap.tar', dpFile1.getBlocks())
	>>> printSplit(DataSplitter.loadPartitionsForScript("datamap.tar"))
	 x | SIZE | SKIP |       Files       
	===+======+======+===================
	 0 |  -1  |      | ['/path/to/file'] 

	>>> remove_files(['datamap.tar'])
	"""

class Test_FileBounarySplitter:
	"""
	>>> dataE = DataProvider.loadFromFile('dataE.dbs')
	>>> splitFile = DataSplitter.createInstance('FileBoundarySplitter', config1)
	>>> splitFile.splitDataset('datamap.tar', dataE.getBlocks())
	log:Block /MY/DATASET#easy3 is not available at any site!

	>>> dataEmap = getLFNMap(dataE)
	>>> printSplitNice(splitFile, dataEmap)
	/path/file0: A, /path/file1: B
	AAAAAAAAAABBBBB  => 15
	---------------  => 0,15
	/path/file2: C
	CCCCCCCCCCCCCCC  => 15
	---------------  => 0,15
	/path/file3: D, /path/file5: E
	DDDDDDDDDDEEEEE  => 15
	---------------  => 0,15
	/path/file6: F, /path/file7: G
	FFFFFFFFFFGGGGG  => 15
	---------------  => 0,15
	/path/file8: H, /path/file9: I
	HHHHHHHHHHIIIIIIIIIIIIIII  => 25
	-------------------------  => 0,25

	>>> DataSplitter.FileList in splitFile.neededEnums()
	True
	>>> DataSplitter.NEntries in splitFile.neededEnums()
	False
	>>> DataSplitter.Skipped in splitFile.neededEnums()
	False

	>>> dpFile1 = DataProvider.createInstance('FileProvider', config1, '/path/to/file | -1', None)
	>>> splitFile.splitDataset('datamap.tar', dpFile1.getBlocks())
	>>> remove_files(['datamap.tar'])
	"""

class Test_FLSplitter:
	"""
	>>> dataE = DataProvider.loadFromFile('dataE.dbs')
	>>> splitFile = DataSplitter.createInstance('FLSplitStacker', config2)
	>>> splitFile.splitDataset('datamap.tar', dataE.getBlocks())
	log:Block /MY/DATASET#easy3 is not available at any site!
	>>> dataEmap = getLFNMap(dataE)
	>>> printSplitNice(splitFile, dataEmap)
	/path/file0: A, /path/file1: B
	AAAAAAAAAABBBBB  => 15
	---------------  => 0,15
	/path/file2: C
	CCCCCCCCCCCCCCC  => 15
	---------------  => 0,15
	/path/file3: D, /path/file5: E
	DDDDDDDDDDEEEEE  => 15
	---------------  => 0,15
	/path/file6: F, /path/file7: G
	FFFFFFFFFFGGGGG  => 15
	---------------  => 0,15
	/path/file8: H, /path/file9: I
	HHHHHHHHHHIIIIIIIIIIIIIII  => 25
	---------------            => 0,15
	/path/file9: I
	          IIIIIIIIIIIIIII  => 15
	               ----------  => 5,10

	>>> DataSplitter.FileList in splitFile.neededEnums()
	True
	>>> DataSplitter.NEntries in splitFile.neededEnums()
	False
	>>> DataSplitter.Skipped in splitFile.neededEnums()
	False
	"""

class Test_EventBounarySplitter:
	"""
	>>> dataE = DataProvider.loadFromFile('dataE.dbs')
	>>> splitEvent = DataSplitter.createInstance('EventBoundarySplitter', config1)
	>>> splitEvent.splitDataset('datamap.tar', dataE.getBlocks())
	log:Block /MY/DATASET#easy3 is not available at any site!

	>>> dataEmap = getLFNMap(dataE)
	>>> printSplitNice(splitEvent, dataEmap)
	/path/file0: A
	AAAAAAAAAA  => 10
	----------  => 0,10
	/path/file1: B, /path/file2: C
	BBBBBCCCCCCCCCCCCCCC  => 20
	----------            => 0,10
	/path/file2: C
	     CCCCCCCCCCCCCCC  => 15
	          ----------  => 5,10
	/path/file3: D
	DDDDDDDDDD  => 10
	----------  => 0,10
	/path/file5: E
	EEEEE  => 5
	-----  => 0,5
	/path/file6: F
	FFFFFFFFFF  => 10
	----------  => 0,10
	/path/file7: G, /path/file8: H
	GGGGGHHHHHHHHHH  => 15
	----------       => 0,10
	/path/file8: H, /path/file9: I
	     HHHHHHHHHHIIIIIIIIIIIIIII  => 25
	          ----------            => 5,10
	/path/file9: I
	               IIIIIIIIIIIIIII  => 15
	                    ----------  => 5,10

	>>> DataSplitter.FileList in splitEvent.neededEnums()
	True
	>>> DataSplitter.NEntries in splitEvent.neededEnums()
	True
	>>> DataSplitter.Skipped in splitEvent.neededEnums()
	True

	>>> dpFile1 = DataProvider.createInstance('FileProvider', config1, '/path/to/file | -1', None)
	>>> try_catch(lambda: splitEvent.splitDataset('datamap.tar', dpFile1.getBlocks()), 'DatasetError', 'does not support files with a negative number of events')
	caught
	>>> dataC = DataProvider.loadFromFile('dataC.dbs')
	>>> splitEvent = DataSplitter.createInstance('EventBoundarySplitter', config1)
	>>> splitEvent.splitDataset('datamap.tar', dataC.getBlocks())
	>>> dataCmap = getLFNMap(dataC)
	>>> printSplitNice(splitEvent, dataCmap)
	/path/to//file1: A, /path/to//file2: B
	AAAAABBBBBBBBBBBBBBB  => 20
	----------            => 0,10
	/path/to//file2: B
	     BBBBBBBBBBBBBBB  => 15
	          ----------  => 5,10

	>>> remove_files(['datamap.tar'])
	"""

class Test_HybridBounarySplitter:
	"""
	>>> dataE = DataProvider.loadFromFile('dataE.dbs')
	>>> splitHybrid = DataSplitter.createInstance('HybridSplitter', config1)
	>>> splitHybrid.splitDataset('datamap.tar', dataE.getBlocks())
	log:Block /MY/DATASET#easy3 is not available at any site!
	>>> dataEmap = getLFNMap(dataE)
	>>> printSplitNice(splitHybrid, dataEmap)
	/path/file0: A
	AAAAAAAAAA  => 10
	----------  => 0,10
	/path/file1: B
	BBBBB  => 5
	-----  => 0,5
	/path/file2: C
	CCCCCCCCCCCCCCC  => 15
	---------------  => 0,15
	/path/file3: D
	DDDDDDDDDD  => 10
	----------  => 0,10
	/path/file5: E
	EEEEE  => 5
	-----  => 0,5
	/path/file6: F
	FFFFFFFFFF  => 10
	----------  => 0,10
	/path/file7: G
	GGGGG  => 5
	-----  => 0,5
	/path/file8: H
	HHHHHHHHHH  => 10
	----------  => 0,10
	/path/file9: I
	IIIIIIIIIIIIIII  => 15
	---------------  => 0,15

	>>> DataSplitter.FileList in splitHybrid.neededEnums()
	True
	>>> DataSplitter.NEntries in splitHybrid.neededEnums()
	False
	>>> DataSplitter.Skipped in splitHybrid.neededEnums()
	False

	>>> dpFile1 = DataProvider.createInstance('FileProvider', config1, '/path/to/file | -1', None)
	>>> splitHybrid.splitDataset('datamap.tar', dpFile1.getBlocks())

	>>> dataC = DataProvider.loadFromFile('dataC.dbs')
	>>> splitHybrid = DataSplitter.createInstance('HybridSplitter', config1)
	>>> splitHybrid.splitDataset('datamap.tar', dataC.getBlocks())
	>>> dataCmap = getLFNMap(dataC)
	>>> printSplitNice(splitHybrid, dataCmap)
	/path/to//file1: A
	AAAAA  => 5
	-----  => 0,5
	/path/to//file2: B
	BBBBBBBBBBBBBBB  => 15
	---------------  => 0,15

	>>> try_catch(lambda: splitHybrid.getSplitInfo(10), 'PartitionError', 'Job 10 out of range for available dataset')
	caught
	>>> remove_files(['datamap.tar'])
	"""

class Test_RunSplitter:
	"""
	>>> dataG = DataProvider.loadFromFile('dataG.dbs')
	>>> splitRun = DataSplitter.createInstance('RunSplitter', config1)
	>>> splitRun.splitDataset('datamap.tar', dataG.getBlocks())
	>>> dataGmap = getLFNMap(dataG)
	>>> printSplitNice(splitRun, dataGmap)
	3240252F.root: D
	DDDDD  => 5
	-----  => 0,5
	FA648234.root: L
	LLLLLL  => 6
	------  => 0,6
	66690367.root: E
	EEEEEEEEE  => 9
	---------  => 0,9
	04F2FC24.root: B
	BBBBBBBB  => 8
	--------  => 0,8
	047B67E9.root: A
	AAAA  => 4
	----  => 0,4
	E62E1DFF.root: I
	II  => 2
	--  => 0,2
	880C71DC.root: H, F8D11ADA.root: J, 720D3ADD.root: F
	HHHHHHJJFFFF  => 12
	------------  => 0,12
	FA07400E.root: K, 7E81320A.root: G
	KKKKKKKKGGGGGGGGG  => 17
	-----------------  => 0,17
	2AE92A85.root: C
	CCCCCCCCC  => 9
	---------  => 0,9

	>>> remove_files(['datamap.tar'])

	>>> splitRun = DataSplitter.createInstance('RunSplitter', config1a)
	>>> splitRun.splitDataset('datamap.tar', dataG.getBlocks())
	>>> dataGmap = getLFNMap(dataG)
	>>> printSplitNice(splitRun, dataGmap)
	3240252F.root: D
	DDDDD  => 5
	-----  => 0,5
	FA648234.root: L
	LLLLLL  => 6
	------  => 0,6
	66690367.root: E
	EEEEEEEEE  => 9
	---------  => 0,9
	04F2FC24.root: B
	BBBBBBBB  => 8
	--------  => 0,8
	047B67E9.root: A
	AAAA  => 4
	----  => 0,4
	E62E1DFF.root: I
	II  => 2
	--  => 0,2
	880C71DC.root: H, F8D11ADA.root: J, 720D3ADD.root: F, FA07400E.root: K, 7E81320A.root: G
	HHHHHHJJFFFFKKKKKKKKGGGGGGGGG  => 29
	-----------------------------  => 0,29
	2AE92A85.root: C
	CCCCCCCCC  => 9
	---------  => 0,9

	>>> remove_files(['datamap.tar'])
	"""

class Test_SplitterResync:
	"""
	>>> dataA = DataProvider.loadFromFile('dataA.dbs')
	>>> dataB = DataProvider.loadFromFile('dataB.dbs')

	>>> splitA = DataSplitter.createInstance('EventBoundarySplitter', config1)
	>>> splitA.splitDataset('datamap.tar', dataA.getBlocks())

	>>> splitB = DataSplitter.loadPartitionsForScript('datamap.tar')
	>>> printSplit(splitB)
	 x  | SIZE | SKIP |           Files            
	====+======+======+============================
	 0  |  10  |  0   | ['/path/UC1']              
	 1  |  10  |  0   | ['/path/UC2', '/path/UC3'] 
	 2  |  10  |  5   | ['/path/UC3']              
	 3  |  10  |  0   | ['/path/MX1']              
	 4  |  10  |  10  | ['/path/MX1', '/path/MX2'] 
	 5  |  10  |  0   | ['/path/MX3']              
	 6  |  10  |  0   | ['/path/EX1', '/path/EX2'] 
	 7  |  10  |  5   | ['/path/EX2', '/path/EX3'] 
	 8  |  10  |  5   | ['/path/EX3']              
	 9  |  5   |  0   | ['/path/EX4']              
	 10 |  10  |  0   | ['/path/AD1']              
	 11 |  10  |  10  | ['/path/AD1', '/path/AD2'] 
	 12 |  10  |  0   | ['/path/AD3']              
	 13 |  10  |  0   | ['/path/RM1', '/path/RM2'] 
	 14 |  10  |  5   | ['/path/RM2', '/path/RM3'] 
	 15 |  10  |  5   | ['/path/RM3']              
	 16 |  10  |  0   | ['/path/RM4']              
	 17 |  10  |  0   | ['/path/SH1', '/path/SH2'] 
	 18 |  10  |  5   | ['/path/SH2']              
	 19 |  10  |  15  | ['/path/SH2', '/path/SH3'] 
	 20 |  10  |  5   | ['/path/SH3']              
	 21 |  10  |  0   | ['/path/SH4']              
	 22 |  10  |  10  | ['/path/SH4']              
	 23 |  10  |  0   | ['/path/SH0']              
	 24 |  10  |  0   | ['/path/RP1']              
	 25 |  10  |  10  | ['/path/RP1', '/path/RP2'] 
	 26 |  10  |  5   | ['/path/RP2', '/path/RP3'] 
	 27 |  10  |  0   | ['/path/BR1']              
	 28 |  10  |  0   | ['/path/SE1']              

	>>> dataAmap = getLFNMap(dataA)
	>>> charMap = {}
	>>> charMap = printSplitNice(splitA, dataAmap, reuse = charMap)
	/path/UC1: Y
	YYYYYYYYYY  => 10
	----------  => 0,10
	/path/UC2: Z, /path/UC3: 1
	ZZZZZ111111111111111  => 20
	----------            => 0,10
	/path/UC3: 1
	     111111111111111  => 15
	          ----------  => 5,10
	/path/MX1: I
	IIIIIIIIIIIIIII  => 15
	----------       => 0,10
	/path/MX1: I, /path/MX2: J
	IIIIIIIIIIIIIIIJJJJJ  => 20
	          ----------  => 10,10
	/path/MX3: K
	KKKKKKKKKK  => 10
	----------  => 0,10
	/path/EX1: E, /path/EX2: F
	EEEEEFFFFFFFFFF  => 15
	----------       => 0,10
	/path/EX2: F, /path/EX3: G
	     FFFFFFFFFFGGGGGGGGGGGGGGG  => 25
	          ----------            => 5,10
	/path/EX3: G
	               GGGGGGGGGGGGGGG  => 15
	                    ----------  => 5,10
	/path/EX4: H
	HHHHH  => 5
	-----  => 0,5
	/path/AD1: A
	AAAAAAAAAAAAAAA  => 15
	----------       => 0,10
	/path/AD1: A, /path/AD2: B
	AAAAAAAAAAAAAAABBBBB  => 20
	          ----------  => 10,10
	/path/AD3: C
	CCCCCCCCCC  => 10
	----------  => 0,10
	/path/RM1: L, /path/RM2: M
	LLLLLMMMMMMMMMM  => 15
	----------       => 0,10
	/path/RM2: M, /path/RM3: N
	     MMMMMMMMMMNNNNNNNNNNNNNNN  => 25
	          ----------            => 5,10
	/path/RM3: N
	               NNNNNNNNNNNNNNN  => 15
	                    ----------  => 5,10
	/path/RM4: O
	OOOOOOOOOO  => 10
	----------  => 0,10
	/path/SH1: U, /path/SH2: V
	UUUUUVVVVVVVVVVVVVVVVVVVV  => 25
	----------                 => 0,10
	/path/SH2: V
	     VVVVVVVVVVVVVVVVVVVV  => 20
	          ----------       => 5,10
	/path/SH2: V, /path/SH3: W
	     VVVVVVVVVVVVVVVVVVVVWWWWWWWWWWWWWWW  => 35
	                    ----------            => 15,10
	/path/SH3: W
	                         WWWWWWWWWWWWWWW  => 15
	                              ----------  => 5,10
	/path/SH4: X
	XXXXXXXXXXXXXXXXXXXX  => 20
	----------            => 0,10
	/path/SH4: X
	XXXXXXXXXXXXXXXXXXXX  => 20
	          ----------  => 10,10
	/path/SH0: T
	TTTTTTTTTT  => 10
	----------  => 0,10
	/path/RP1: P
	PPPPPPPPPPPPPPP  => 15
	----------       => 0,10
	/path/RP1: P, /path/RP2: Q
	PPPPPPPPPPPPPPPQQQQQQQQQQ  => 25
	          ----------       => 10,10
	/path/RP2: Q, /path/RP3: R
	               QQQQQQQQQQRRRRR  => 15
	                    ----------  => 5,10
	/path/BR1: D
	DDDDDDDDDD  => 10
	----------  => 0,10
	/path/SE1: S
	SSSSSSSSSS  => 10
	----------  => 0,10

	>>> splitB.resyncMapping('datamap-new.tar', dataA.getBlocks(), dataB.getBlocks()) # doctest: +ELLIPSIS
	([], [7, 13, 14, 16, 18, 19, 22, 23, 25, 26, 27])

	>>> splitB1 = DataSplitter.loadPartitionsForScript('datamap-new.tar')
	>>> dataAmap.update(getLFNMap(dataB))
	>>> charMap = printSplitNice(splitB1, dataAmap, reuse = charMap)
	/path/UC1: Y
	YYYYYYYYYY  => 10
	----------  => 0,10
	/path/UC2: Z, /path/UC3: 1
	ZZZZZ111111111111111  => 20
	----------            => 0,10
	/path/UC3: 1
	     111111111111111  => 15
	          ----------  => 5,10
	/path/MX1: I
	IIIIIIIIIIIIIII  => 15
	----------       => 0,10
	/path/MX1: I, /path/MX2: J
	IIIIIIIIIIIIIIIJJJJJ  => 20
	          ----------  => 10,10
	/path/MX3: K
	KKKKKKKKKK  => 10
	----------  => 0,10
	/path/EX1: E, /path/EX2: F
	EEEEEFFFFFFFFFFFFFFFFFFFF  => 25
	----------                 => 0,10
	/path/EX2: F, /path/EX3: G
	     FFFFFFFFFFFFFFFFFFFFGGGGGGGGGGGGGGG  => 35    <disabled>
	          ----------                      => 5,10
	/path/EX3: G
	                         GGGGGGGGGGGGGGG  => 15
	                              ----------  => 5,10
	/path/EX4: H
	HHHHHHHHHH  => 10
	-----       => 0,5
	/path/AD1: A
	AAAAAAAAAAAAAAA  => 15
	----------       => 0,10
	/path/AD1: A, /path/AD2: B
	AAAAAAAAAAAAAAABBBBB  => 20
	          ----------  => 10,10
	/path/AD3: C
	CCCCCCCCCC  => 10
	----------  => 0,10
	/path/RM1: L, /path/RM2: M
	LLLLLMMMMMMMMMM  => 15    <disabled>
	----------       => 0,10
	/path/RM2: M, /path/RM3: N
	     MMMMMMMMMMNNNNNNNNNNNNNNN  => 25    <disabled>
	          ----------            => 5,10
	/path/RM3: N
	               NNNNNNNNNNNNNNN  => 15
	                    ----------  => 5,10
	<disabled partition without files>
	/path/SH1: U, /path/SH2: V
	UUUUUVVVVVVVVVV  => 15
	----------       => 0,10
	/path/SH2: V
	     VVVVVVVVVV  => 10    <disabled>
	          ----------  => 5,10
	/path/SH2: V, /path/SH3: W
	     VVVVVVVVVVWWWWWWWWWWWWWWW  => 25    <disabled>
	                    ----------  => 15,10
	/path/SH3: W
	               WWWWWWWWWWWWWWW  => 15
	                    ----------  => 5,10
	/path/SH4: X
	XXXXXXXXXXXXXXX  => 15
	----------       => 0,10
	/path/SH4: X
	XXXXXXXXXXXXXXX  => 15    <disabled>
	          ----------  => 10,10
	/path/SH0: T
	TTTTT  => 5    <disabled>
	----------  => 0,10
	/path/RP1: P
	PPPPPPPPPPPPPPP  => 15
	----------       => 0,10
	/path/RP1: P, /path/RP2: Q
	PPPPPPPPPPPPPPPQQQQQQQQQQ  => 25    <disabled>
	          ----------       => 10,10
	/path/RP2: Q, /path/RP3: R
	               QQQQQQQQQQRRRRR  => 15    <disabled>
	                    ----------  => 5,10
	<disabled partition without files>
	/path/SE1: S
	SSSSSSSSSS  => 10
	----------  => 0,10
	/path/EX2: F, /path/EX3: G
	     FFFFFFFFFFFFFFFFFFFFGGGGGGGGGGGGGGG  => 35
	          --------------------            => 5,20
	/path/EX4: H
	HHHHHHHHHH  => 10
	     -----  => 5,5
	/path/RM1: L
	LLLLL  => 5
	-----  => 0,5
	/path/RM3: N
	               NNNNNNNNNNNNNNN  => 15
	               -----            => 0,5
	/path/SH2: V
	     VVVVVVVVVV  => 10
	          -----  => 5,5
	/path/SH3: W
	               WWWWWWWWWWWWWWW  => 15
	               -----            => 0,5
	/path/SH4: X
	XXXXXXXXXXXXXXX  => 15
	          -----  => 10,5
	/path/SH0: T
	TTTTT  => 5
	-----  => 0,5
	/path/RP1: P
	PPPPPPPPPPPPPPP  => 15
	          -----  => 10,5
	/path/RP3: R
	                         RRRRR  => 5
	                         -----  => 0,5
	/path/AD4: 2
	2222222222  => 10
	----------  => 0,10
	/path/AD5: 3
	3333333333  => 10
	----------  => 0,10
	/path/BN1: 4
	4444444444  => 10
	----------  => 0,10
	/path/RP4: 5
	55555555555555555555  => 20
	----------            => 0,10
	/path/RP4: 5
	55555555555555555555  => 20
	          ----------  => 10,10

	>>> splitC = DataSplitter.loadPartitionsForScript('datamap-new.tar')
	>>> splitC.resyncMapping('datamap-newer.tar', dataB.getBlocks(), dataB.getBlocks()) # doctest: +ELLIPSIS
	([], [])

	>>> remove_files(['datamap.tar', 'datamap-new.tar', 'datamap-newer.tar'])
	"""

run_test()
