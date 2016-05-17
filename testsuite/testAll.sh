OLDPWD=$PWD

for EXE in `find | grep TEST | grep -v pyc | sort | grep -v svn | grep -v scale | grep -v fuzz`; do
	grep -q ${EXE#./} ../.travis.yml || echo -n "not tested: "
	echo $1 ${EXE#./}
	$1 $EXE
done
