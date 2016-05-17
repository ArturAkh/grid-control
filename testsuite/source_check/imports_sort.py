def sortImports(fn):
	replacements = []
	raw = open(fn).read()
	for import_line in filter(lambda line: line.startswith('import '), raw.splitlines()):
		imports = sorted(map(str.strip, import_line.replace('import ', '').split(',')), key = lambda x: (len(x), x))
		replacements.append((import_line, 'import %s' % str.join(', ', imports)))
	for (old, new) in replacements:
		raw = raw.replace(old, new)
	open(fn, 'w').write(raw)

	replacements = []
	raw = open(fn).read()
	for import_line in filter(lambda line: line.startswith('from '), raw.splitlines()):
		try:
			_from, _source, _import, _what = import_line.split(None, 3)
			imports = sorted(map(str.strip, _what.split(',')))
			replacements.append((import_line, 'from %s import %s' % (_source, str.join(', ', imports))))
		except:
			print fn, import_line
			raise
	for (old, new) in replacements:
		raw = raw.replace(old, new)
	open(fn, 'w').write(raw)

	output = []
	output_import = set()
	importSection = False
	for line in open(fn).readlines():
		if line.startswith('from') or line.startswith('import'):
			importSection = True
		elif line.strip():
			if importSection:
				output_import = list(filter(lambda x: x.strip() != '', output_import))
				output_import.sort(key = lambda l: (not l.startswith('import'),
					('python_compat' in l), 'testFwk' not in l, map(lambda x: x.split('.'), l.split())))
				for x in output_import:
					output.append(x)
				output.append('\n')
				output_import = set()
			importSection = False
		if not importSection:
			output.append(line)
		else:
			output_import.add(line)
	if importSection:
		output_import = list(filter(lambda x: x.strip() != '', output_import))
		output_import.sort(key = lambda l: (not l.startswith('import'),
			'python_compat' not in l, map(lambda x: x.split('.'), l.split())))
		for x in output_import:
			output.append(x)

	fp = open(fn, 'w')
	for x in output:
		fp.write(x)

if __name__ == '__main__':
	import os, sys, getFiles
	for (fn, fnrel) in getFiles.getFiles(showTypes = ['py'], showExternal = False, showAux = False):
		sortImports(fn)
