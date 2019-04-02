import unittest

import os, sys
import PKF
#from PKF import paircorrelation 

#PATH_TO_parser=os.path.expanduser("~/ENVISIoN/envision/envision/parser")
#sys.path.append(os.path.abspath(PATH_TO_parser))

#import h5writer 

#inherit from unittest.TestCase
class TestPKFparser(unittest.TestCase):
	def setUp(self):
        	pass
	
	#def test_datasetname(self):
	#	fileobject = PKF.paircorrelation()
	#	self.assertNotEqual(fileobject.keys(), "myset")

	def test_pathway(self):
		self.assertEqual(1,1)




if __name__ == '__main__':
    unittest.main()

