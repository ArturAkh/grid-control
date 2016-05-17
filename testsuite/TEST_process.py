#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), ''))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import run_test, try_catch
from grid_control.utils.process_base import LocalProcess
from python_compat import sorted

long_timeout = 10

class Test_Process:
	"""
	>>> try_catch(lambda: LocalProcess('sleep', '10').get_output(timeout = 0.1, raise_errors = True), 'ProcessTimeout', 'Process is still running')
	caught
	>>> LocalProcess('sleep', '1').stdout.wait(timeout = 0.1)
	False
	>>> LocalProcess('sleep', '1').stdout.wait(timeout = long_timeout)
	True

	>>> sorted(LocalProcess('find', '-name', 'test*.py').get_output(timeout = long_timeout).split())
	['./datasets/testResync.py', './parameters/testINC.py', './testDS.py', './testFwk.py']

	>>> p1 = LocalProcess('find', '-name', 'test*.py')
	>>> sorted(p1.get_output(timeout = long_timeout).splitlines())
	['./datasets/testResync.py', './parameters/testINC.py', './testDS.py', './testFwk.py']

	>>> p2 = LocalProcess('python', '-Ec', 'cs=__import__("code").InteractiveConsole();tmp=cs.raw_input;cs.raw_input=lambda*args:tmp();cs.interact("")')
	>>> p2.stdin.write('1+5\\n')
	>>> p2.stdout.wait(timeout = long_timeout)
	True
	>>> p2.stdin.close()
	>>> p2.status(timeout = long_timeout)
	0
	>>> p2.get_output(timeout = long_timeout)
	'6\\n'

	>>> p3 = LocalProcess('python', '-Ec', 'cs=__import__("code").InteractiveConsole();tmp=cs.raw_input;cs.raw_input=lambda*args:tmp();cs.interact("")')
	>>> p3.stdin.write('1+5\\n')
	>>> p3.stdin.write('6*7\\n')
	>>> p3.stdout.wait(timeout = long_timeout)
	True
	>>> p3.stdin.close()
	>>> p3.get_output(timeout = long_timeout)
	'6\\n42\\n'

	>>> p4 = LocalProcess('cat')
	>>> try_catch(lambda: p4.status_raise(timeout = 0.5), 'ProcessTimeout', 'Process is still running')
	caught

	>>> p5 = LocalProcess('find', '-name', 'test*.py')
	>>> for x in sorted(p5.stdout.iter(timeout = long_timeout)):
	...   print(x.strip())
	./datasets/testResync.py
	./parameters/testINC.py
	./testDS.py
	./testFwk.py

	"""

run_test()
