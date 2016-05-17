#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), ''))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import cmp_obj, run_test
from grid_control.utils.webservice import JSONRestClient, RestClient

def response_filter(response):
	response.pop('origin')
	header = response['headers']
	header.pop('Accept-Encoding')
	header.pop('User-Agent')
	return response


class Test_RestClient:
	"""
	>>> rc = RestClient()
	>>> 'UTF-8 encoding' in rc.get('https://httpbin.org/encoding/utf8')
	True
	"""

class Test_JSONRestClient:
	"""
	>>> jrc = JSONRestClient()
	>>> r1 = response_filter(jrc.get('https://httpbin.org/get'))
	>>> cmp_obj(r1, {'headers': {'Accept': 'application/json',
	...    'Host': 'httpbin.org', 'Content-Type': 'application/json'},
	...    'args': {}, 'url': 'https://httpbin.org/get'})
	>>> r2 = response_filter(jrc.get('https://httpbin.org', 'get', {'header': 'test'}, {'key': 'value'}))
	>>> cmp_obj(r2, {'headers': {'Accept': 'application/json',
	...    'Host': 'httpbin.org', 'Content-Type': 'application/json', 'Header': 'test'},
	...    'args': {'key': 'value'}, 'url': 'https://httpbin.org/get?key=value'})
	>>> r3 = response_filter(jrc.post('https://httpbin.org', 'post', data = {'test': 'value'}))
	>>> cmp_obj(r3, {'headers': {'Accept': 'application/json',
	...    'Host': 'httpbin.org', 'Content-Type': 'application/json', 'Content-Length': '17'},
	...    'files': {}, 'form': {}, 'url': 'https://httpbin.org/post', 'args': {},
	...    'json': {'test': 'value'}, 'data': '{"test": "value"}'})
	>>> r4 = response_filter(jrc.put('https://httpbin.org', 'put', data = {'test': 'value'}))
	>>> cmp_obj(r4, {'headers': {'Accept': 'application/json',
	...    'Host': 'httpbin.org', 'Content-Type': 'application/json', 'Content-Length': '17'},
	...    'files': {}, 'form': {}, 'url': 'https://httpbin.org/put', 'args': {},
	...    'json': {'test': 'value'}, 'data': '{"test": "value"}'})
	>>> r5 = response_filter(jrc.delete('https://httpbin.org', 'delete', params = {'key': 'value'}))
	>>> dummy = r5['headers'].pop('Content-Length', None)
	>>> cmp_obj(r5, {'headers': {'Accept': 'application/json',
	...    'Host': 'httpbin.org', 'Content-Type': 'application/json'},
	...    'files': {}, 'form': {}, 'url': 'https://httpbin.org/delete?key=value', 'args': {'key': 'value'},
	...    'json': None, 'data': ''})
	"""

run_test()
