#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), ''))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import DummyObj, run_test, try_catch
from grid_control import utils
from grid_control.job_db import Job
from grid_control.job_selector import JobSelector, VarSelector
from python_compat import ifilter, irange, lfilter, lmap, lrange

testMod = DummyObj(getJobConfig = lambda jobNum: {'TEST': jobNum})

#states = lmap(lambda x: random.randint(0, len(Job.enumNames) - 1), lrange(20))
random_states = [0, 1, 4, 1, 10, 0, 6, 3, 10, 1, 4, 4, 2, 0, 5, 1, 7, 0, 3, 5]  # 100% random ...

class Test_JobSelector:
	"""
	>>> allJobs = lrange(0, 10) + lrange(20, 30) + [14, 17]
	>>> allJobs.sort()
	>>> allJobs
	[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 17, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]

	>>> sites = [None, 'ce1.gridka.de/long', 'ce1.gridka.de/medium', 'ce2.gridka.de/test', \
		'ce1.fnal.gov/medium', 'ce2.fnal.gov']
	>>> sites = dict(enumerate(sites))
	>>> allJobObjs = lmap(lambda x: DummyObj(id = x, state = random_states[x], \
		get = lambda y, d = 'NOSITE': utils.QM(sites.get(x % len(sites)), sites.get(x % len(sites)), d)), irange(20))

	>>> idSel = JobSelector.createInstance('IDSelector', '7-10,10,-2,27-,23')
	>>> lfilter(lambda x: idSel(x, None), allJobs)
	[0, 1, 2, 7, 8, 9, 23, 27, 28, 29]

	>>> idSel = JobSelector.createInstance('IDSelector', '')
	>>> lfilter(lambda x: idSel(x, None), allJobs) == allJobs
	True

	>>> stateSel = JobSelector.createInstance('StateSelector', '')
	>>> getJobListNice = lambda jobs: lmap(lambda x: (x.id, Job.enumNames[x.state]), jobs)
	>>> getJobListNice(allJobObjs)
	[(0, 'INIT'), (1, 'SUBMITTED'), (2, 'WAITING'), (3, 'SUBMITTED'), (4, 'FAILED'), (5, 'INIT'), (6, 'ABORTED'), (7, 'READY'), (8, 'FAILED'), (9, 'SUBMITTED'), (10, 'WAITING'), (11, 'WAITING'), (12, 'DISABLED'), (13, 'INIT'), (14, 'QUEUED'), (15, 'SUBMITTED'), (16, 'RUNNING'), (17, 'INIT'), (18, 'READY'), (19, 'QUEUED')]
	>>> getJobListNice(ifilter(lambda x: stateSel(None, x), allJobObjs)) == getJobListNice(allJobObjs)
	True

	>>> stateSel = JobSelector.createInstance('StateSelector', 'R,Q')
	>>> getJobListNice(ifilter(lambda x: stateSel(None, x), allJobObjs))
	[(7, 'READY'), (14, 'QUEUED'), (16, 'RUNNING'), (18, 'READY'), (19, 'QUEUED')]

	>>> siteSel = JobSelector.createInstance('SiteSelector', 'gridka.de')
	>>> getJobListNice = lambda jobs: lmap(lambda x: (x.id, x.get('dest')), jobs)
	>>> getJobListNice(allJobObjs)
	[(0, 'NOSITE'), (1, 'ce1.gridka.de/long'), (2, 'ce1.gridka.de/medium'), (3, 'ce2.gridka.de/test'), (4, 'ce1.fnal.gov/medium'), (5, 'ce2.fnal.gov'), (6, 'NOSITE'), (7, 'ce1.gridka.de/long'), (8, 'ce1.gridka.de/medium'), (9, 'ce2.gridka.de/test'), (10, 'ce1.fnal.gov/medium'), (11, 'ce2.fnal.gov'), (12, 'NOSITE'), (13, 'ce1.gridka.de/long'), (14, 'ce1.gridka.de/medium'), (15, 'ce2.gridka.de/test'), (16, 'ce1.fnal.gov/medium'), (17, 'ce2.fnal.gov'), (18, 'NOSITE'), (19, 'ce1.gridka.de/long')]
	>>> getJobListNice(allJobObjs)
	[(0, 'NOSITE'), (1, 'ce1.gridka.de/long'), (2, 'ce1.gridka.de/medium'), (3, 'ce2.gridka.de/test'), (4, 'ce1.fnal.gov/medium'), (5, 'ce2.fnal.gov'), (6, 'NOSITE'), (7, 'ce1.gridka.de/long'), (8, 'ce1.gridka.de/medium'), (9, 'ce2.gridka.de/test'), (10, 'ce1.fnal.gov/medium'), (11, 'ce2.fnal.gov'), (12, 'NOSITE'), (13, 'ce1.gridka.de/long'), (14, 'ce1.gridka.de/medium'), (15, 'ce2.gridka.de/test'), (16, 'ce1.fnal.gov/medium'), (17, 'ce2.fnal.gov'), (18, 'NOSITE'), (19, 'ce1.gridka.de/long')]
	>>> getJobListNice(ifilter(lambda x: siteSel(None, x), allJobObjs))
	[(1, 'ce1.gridka.de/long'), (2, 'ce1.gridka.de/medium'), (3, 'ce2.gridka.de/test'), (7, 'ce1.gridka.de/long'), (8, 'ce1.gridka.de/medium'), (9, 'ce2.gridka.de/test'), (13, 'ce1.gridka.de/long'), (14, 'ce1.gridka.de/medium'), (15, 'ce2.gridka.de/test'), (19, 'ce1.gridka.de/long')]

	>>> queueSel = JobSelector.createInstance('QueueSelector', 'medium')
	>>> getJobListNice(ifilter(lambda x: queueSel(None, x), allJobObjs))
	[(2, 'ce1.gridka.de/medium'), (4, 'ce1.fnal.gov/medium'), (8, 'ce1.gridka.de/medium'), (10, 'ce1.fnal.gov/medium'), (14, 'ce1.gridka.de/medium'), (16, 'ce1.fnal.gov/medium')]

	>>> varSel = VarSelector.createInstance('VarSelector', 'TEST=4$', task=testMod)
	>>> lfilter(lambda x: varSel(x, None), allJobs)
	[4, 14, 24]

	>>> multiSel = JobSelector.createInstance('MultiJobSelector', '7-10,10,-2,27-,23')
	>>> lfilter(lambda x: multiSel(x, None), allJobs)
	[0, 1, 2, 7, 8, 9, 23, 27, 28, 29]

	>>> multiSel = JobSelector.createInstance('MultiJobSelector', '~7-10,10,-2,27-,23')
	>>> lfilter(lambda x: multiSel(x, None), allJobs)
	[3, 4, 5, 6, 14, 17, 20, 21, 22, 24, 25, 26]

	>>> multiSel = JobSelector.createInstance('MultiJobSelector', '~5-25 id:8-17+12-')
	>>> lfilter(lambda x: multiSel(x, None), allJobs)
	[0, 1, 2, 3, 4, 14, 17, 26, 27, 28, 29]

	>>> try_catch(lambda: JobSelector.__call__(idSel, 0, None), 'AbstractError', 'is an abstract function')
	caught
	"""

run_test()
