import os, sys

class TestStream(object):
	def write(self, value):
		if value == '\n':
			sys.stdout.write('-----\n')
		else:
			sys.stdout.write(value)

def setPath(x):
	try:
		path = setPath.backup
	except:
		setPath.backup = os.environ['PATH']
		path = os.environ['PATH']
	os.environ['PATH'] = str.join(':', [os.path.abspath(x)] + path.split(':')[1:])

def try_catch(fun, catch, catch_value = '!!!'):
	try:
		fun()
	except Exception:
		exName = sys.exc_info()[0].__name__
		exMsg = str(sys.exc_info()[1].args[0])
		if exName.endswith(catch) and (catch_value in exMsg):
			print('caught')
		else:
			print('failed %s(%s)' % (exName, exMsg))

def cmp_obj(x, y, desc = ''):
	from python_compat import sorted, izip, set
	if type(x) != type(y):
		return desc + 'different types %s %s' % (type(x), type(y))
	if isinstance(x, (list, tuple, dict, set)):
		if len(x) != len(y):
			return desc + 'different number of elements len(%r)=%d len(%r)=%d' % (x, len(x), y, len(y))
		if isinstance(x, (dict, set)):
			item_iter = enumerate(izip(sorted(x, key = str), sorted(y, key = str)))
		else:
			item_iter = enumerate(izip(x, y))
		for idx, (xi, yi) in item_iter:
			result = cmp_obj(xi, yi, desc + 'items (#%d):' % idx)
			if result is not None:
				return result
		if isinstance(x, dict):
			for xi in sorted(x):
				result = cmp_obj(x[xi], y[xi], desc + 'values (key:%s):' % repr(xi))
				if result is not None:
					return result
	elif isinstance(x, (str, int, float)):
		if x != y:
			return desc + 'different objects %r %r' % (x, y)
	elif isinstance(x, type(None)):
		assert(x == y)
	else:
		return 'unknown type %s' % type(x)

def create_config(*args, **kwargs):
	from grid_control.config import createConfig
	kwargs.setdefault('useDefaultFiles', False)
	return createConfig(*args, **kwargs)

def remove_files(files):
	import glob
	from grid_control.utils import removeFiles
	files_list = []
	for fn in files:
		files_list.extend(glob.glob(fn))
	return removeFiles(files_list)

class DummyObj:
	def __init__(self, **struct):
		for x in struct:
			setattr(self, x, struct[x])

def str_dict(d, keys = None):
	if keys == None:
		keys = list(d.keys())
		keys.sort()
	dict_list = []
	for key in keys:
		if key in d:
			dict_list.append('%s: %s' % (repr(key), repr(d[key])))
	return '{%s}' % str.join(', ', dict_list)

def setup(fn):
	def add_path(dn):
		sys.path.append(os.path.abspath(dn))
	sys.path.pop()
	dn_fn = os.path.dirname(fn)
	if not dn_fn:
		dn_fn = os.curdir
	add_path(os.path.dirname(__file__)) # testsuite base dir
	add_path(dn_fn) # test dir
	add_path(os.path.join(os.path.dirname(__file__), '..', 'packages')) # gc dir
	os.chdir(dn_fn)
	setup_logging()

def setup_logging():
	from grid_control.utils.table import ConsoleTable
	ConsoleTable._write_line = lambda self, x: sys.stdout.write(x + '\n')
	import logging
	from hpfwk import ExceptionFormatter
	root_logger = logging.getLogger()
	root_logger.addFilter = lambda *args: None
	logging.getLogger = lambda *args: root_logger

	class TestHandler(logging.Handler):
		def handle(self, record):
			if logging.show:
				print('log:' + logging.Formatter().format(record))
			if record.exc_info is not None:
				sys.stderr.write((ExceptionFormatter(showCodeContext = 1, showVariables = 0, showFileStack = 1).format(record)))
	logging.show = True
	root_logger.handlers = []
	root_logger.addHandler(TestHandler())

	from grid_control import utils
	utils.ActivityLogOld = utils.ActivityLog
	utils.ActivityLog = lambda *args: DummyObj(finish = lambda: None)

def run_test():
	import doctest
	setup_logging()
	try:
		kwargs = {'optionflags': doctest.REPORT_UDIFF}
	except Exception:
		kwargs = {}
	result = doctest.testmod(**kwargs)
	sys.exit(result[0])

def write_file(fn, content):
	fp = open(fn, 'w')
	fp.write(content)
	fp.close()
