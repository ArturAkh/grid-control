BASEDIR=$PWD/../..

echo "fixing imports"
echo "-----------------------------"

python imports_check.py
python imports_sort.py

echo "============================="
echo "fixing compat imports"
echo "-----------------------------"

cd $BASEDIR
python packages/python_compat.py 2>&1 | grep -v requests | grep -v xmpp
cd - > /dev/null

echo "============================="
echo "updating plugins"
echo "-----------------------------"

cd $BASEDIR/packages
python gcUpdatePlugins.py
cd - > /dev/null

echo "============================="
echo "updating headers"
echo "-----------------------------"

python header_copyright.py | grep changed

echo "============================="
echo "updating notice"
echo "-----------------------------"

python commit_stats.py
