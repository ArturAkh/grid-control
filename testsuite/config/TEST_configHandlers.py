#!/usr/bin/env python
__import__('sys').path.append(__import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
__import__('testFwk').setup(__file__)
# - prolog marker
from testFwk import create_config, run_test
from grid_control.config import validNoVar

complex_string = '--disable-repo-versions --log-level info --log-files /net/scratch_cms/institut_3b/tmuller/artus/2016-04-13_10-51_analysis/output/${DATASETNICK}/${DATASETNICK}_job_${MY_JOBID}_log.txt --print-envvars ROOTSYS CMSSW_BASE DATASETNICK FILE_NAMES LD_LIBRARY_PATH -c artus_07761e3ef891bb2850d05339376aea03.json --nick $DATASETNICK -i $FILE_NAMES --ld-library-paths /.automount/net_rw/net__scratch_cms/institut_3b/tmuller/cms/htt/analysis/CMSSW_7_1_5/src/HiggsAnalysis/HiggsToTauTau/CombineHarvester/CombineTools/lib/ /.automount/net_rw/net__scratch_cms/institut_3b/tmuller/cms/htt/analysis/CMSSW_7_1_5/src/Kappa/lib/ /.automount/net_rw/net__scratch_cms/institut_3b/tmuller/cms/htt/analysis/CMSSW_7_1_5/src/KappaTools/lib/'

class Test_ConfigView:
	"""
	>>> config = create_config()
	>>> valid = validNoVar(config)
	>>> valid.check('TEST')
	False
	>>> valid.check('TEST @XYZ@')
	True
	>>> valid.check('TEST @XYZ@\\nTEST @ABC@')
	True
	>>> valid.check('TEST @XYZ\\nTEST @ABC')
	False
	>>> valid.check('TEST @XYZ\\nTEST @ABC __XYZ__')
	True
	>>> valid.check('TEST @XYZ @XXXX@\\nTEST @ABC __XYZ__')
	True

	>>> config = create_config(configDict = {'global': {'variable markers': '@'}})
	>>> valid1 = validNoVar(config)
	>>> valid1.check(complex_string)
	False
	>>> config = create_config(configDict = {'global': {'variable markers': '@ __'}})
	>>> valid1 = validNoVar(config)
	>>> valid1.check(complex_string)
	True
	"""

run_test()
