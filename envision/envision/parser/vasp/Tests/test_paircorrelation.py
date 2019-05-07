#This file is created for the purpose of testing the parser system for
#visualisation of the pair-correlation function. The file uses the unittest python module.
#It can be called from the terminal with command: "python3 test_paircorrelation"


import unittest
import sys
import os
import h5py
import numpy
sys.path.insert(0, os.path.expanduser("~/ENVISIoN/envision/envision/parser"))
sys.path.insert(0, os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp"))

from PKF import _parse_pcdat, paircorrelation
from h5writer import _write_pcdat_onecol, _write_pcdat_multicol

# Test parsing correct line from file.
# Test that it is 256 values long.
# Test that it is t_0 and t_1
# Comment on new tests
# Write copyright on every file and push + merge it with master.

class except_n_error(unittest.TestCase):
	# Tests - for exception thrown for empty PCDAT-file
	def test_empty_file(self):
		dir_testfiles = os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp/Tests")
		vasp_dir = os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp/Tests/testdata")
		h5file_path = os.path.join(dir_testfiles, "testh5file.hdf5")
		empty_file = os.path.join(vasp_dir, "PCDAT_empty")

		with self.assertRaises(Exception) as ex:
			_parse_pcdat(h5file_path, empty_file, vasp_dir)
		self.assertEqual("PCDAT-file is empty.", str(ex.exception))

	# Tests - to skip parsing if it's already done
	def test_is_parsed(self):
		dir_testfiles = os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp/Tests")
		h5file_path = os.path.join(dir_testfiles, "testh5file.hdf5")

		testh5 = h5py.File(h5file_path, 'w')
		testh5.create_dataset('PairCorrelationFunc/test', (10,))
		testh5.close()
		self.assertFalse(paircorrelation(h5file_path, ''))
		os.remove(h5file_path)

	# Tests - for exception to be thrown when PCDAT file is not found
	def test_pcdat_file(self):
		dir_testfiles = os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp/Tests")
		vasp_dir = os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp/Tests/testdata")
		h5file_path = os.path.join(dir_testfiles, "testh5file.hdf5")

		with self.assertRaises(Exception) as ex:
			paircorrelation(h5file_path, vasp_dir)
		self.assertEqual("PCDAT-file not found.", str(ex.exception))

class parse_multitimes(unittest.TestCase):

	def test_write_pcdat_multicol(self):
		dir_testfiles = os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp/Tests")
		dir_Cu = os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp/Tests/testdata/Cu")
		file_Cu_t0nt1 = os.path.join(dir_Cu, "PCDAT")
		h5file_path = os.path.join(dir_testfiles, "testh5file.hdf5")

		pcdat_data = _parse_pcdat(h5file_path, file_Cu_t0nt1, dir_Cu)
		key0 = list(pcdat_data)[0]
		list0 = pcdat_data[key0]

		# Tests - to control pcdat_data's format
		# expected format is {'Cu':[0.00, 0.00,... 0.206,..]}
		self.assertIsInstance(pcdat_data, dict)
		self.assertEqual(str(key0), "Cu")
		self.assertIsInstance(list0, list)

		# Tests - to control pcdat_data has correct data
		# expected 513 values from 256*2 (t_0, and t_1) plus 1 other value
		self.assertEqual(len(list0), 513)
		self.assertEqual(list0[0], 0.000)
		self.assertEqual(list0[34], 0.206)
		self.assertEqual(list0[36], 1.469)
		self.assertEqual(list0[257], 0.000)
		self.assertEqual(list0[291], 0.411)
		self.assertEqual(list0[293], 1.286)


		# Create empty HDF5-file
		testh5 = h5py.File(h5file_path, 'w')
		group = list(testh5.keys())
		# Test - to show HDF5-file is empty.
		self.assertEqual(len(group), 0)
		testh5.close()

		# _write_pcdat_multicol is called for systems of one element, or multiple elements with no
		# average pair-correlation function.
		_write_pcdat_multicol(h5file_path, pcdat_data, 16, 256) #default APACO = 16, NPACO = 256

		testh5 = h5py.File(h5file_path, 'r')
		group = list(testh5.keys())

		# Test - to show HDF5-file is written to.
		self.assertNotEqual(len(group), 0)

		distance = testh5["PairCorrelationFunc/Iterations"]
		timeframes = list(testh5["PairCorrelationFunc/Elements/Cu"].keys())
		dataset_obj1 = testh5["PairCorrelationFunc/Elements/Cu/t_0"]
		dataset_obj2 = testh5["PairCorrelationFunc/Elements/Cu/t_1"]


		# Tests - to control the writing to HDF5-file
		self.assertIn("PairCorrelationFunc", testh5)
		self.assertIn("PairCorrelationFunc/Iterations", testh5)
		self.assertIn("PairCorrelationFunc/Elements", testh5)
		self.assertIn("PairCorrelationFunc/Elements/Cu", testh5)
		self.assertIn("PairCorrelationFunc/Elements/Cu/t_0", testh5)
		self.assertIn("PairCorrelationFunc/Elements/Cu/t_1", testh5)

		self.assertEqual(timeframes, ["t_0", "t_1"])
		self.assertIsInstance(dataset_obj1[()], numpy.ndarray)
		self.assertIsInstance(dataset_obj2[()], numpy.ndarray)
		self.assertEqual(dataset_obj1.shape, (256,))
		self.assertEqual(dataset_obj2.shape, (256,))
		self.assertEqual(dataset_obj1.attrs["element"], "Cu")
		self.assertEqual(dataset_obj2.attrs["element"], "Cu")

		self.assertIsInstance(distance[()], numpy.ndarray)
		self.assertEqual(distance.shape, (256,))
		# Tests - to control HDF5-file has correct data
		self.assertEqual(dataset_obj1[0], 0.000)
		self.assertEqual(dataset_obj1[34], 0.206)
		self.assertEqual(dataset_obj1[36], 1.469)

		self.assertEqual(dataset_obj2[0], 0.000)
		self.assertEqual(dataset_obj2[34], 0.411)
		self.assertEqual(dataset_obj2[36], 1.286)

		testh5.close()
		os.remove(h5file_path)


	#This class make sure that the whole parsing system works.
	def test_parsing(self):
		dir_testfiles = os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp/Tests")
		dir_Cu = os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp/Tests/testdata/Cu")
		h5file_path = os.path.join(dir_testfiles, "testh5file.hdf5")

		# Create empty HDF5-file
		testh5 = h5py.File(h5file_path, 'w')
		group = list(testh5.keys())
		# Test - to show HDF5-file is empty.
		self.assertEqual(len(group), 0)
		testh5.close()

		#Is the function calls other parsing functions such as _parse_pcdat, _write_pcdat_onecol or _write_pcdat_multicol
		paircorrelation(h5file_path, dir_Cu)

		testh5 = h5py.File(h5file_path, 'r')
		group = list(testh5.keys())

		# Test - to show HDF5-file is written to.
		self.assertNotEqual(len(group), 0)

		distance = testh5["PairCorrelationFunc/Iterations"]
		timeframes = list(testh5["PairCorrelationFunc/Elements/Cu"].keys())
		dataset_obj1 = testh5["PairCorrelationFunc/Elements/Cu/t_0"]
		dataset_obj2 = testh5["PairCorrelationFunc/Elements/Cu/t_1"]

		# Tests - to control the writing to HDF5-file
		self.assertIn("PairCorrelationFunc", testh5)
		self.assertIn("PairCorrelationFunc/Iterations", testh5)
		self.assertIn("PairCorrelationFunc/Elements", testh5)
		self.assertIn("PairCorrelationFunc/Elements/Cu", testh5)
		self.assertIn("PairCorrelationFunc/Elements/Cu/t_0", testh5)
		self.assertIn("PairCorrelationFunc/Elements/Cu/t_1", testh5)

		self.assertEqual(timeframes, ["t_0", "t_1"])
		self.assertIsInstance(dataset_obj1[()], numpy.ndarray)
		self.assertIsInstance(dataset_obj2[()], numpy.ndarray)
		self.assertEqual(dataset_obj1.shape, (256,))
		self.assertEqual(dataset_obj2.shape, (256,))
		self.assertEqual(dataset_obj1.attrs["element"], "Cu")
		self.assertEqual(dataset_obj2.attrs["element"], "Cu")

		self.assertIsInstance(distance[()], numpy.ndarray)
		self.assertEqual(distance.shape, (256,))
		# Tests - to control HDF5-file has correct data
		self.assertEqual(dataset_obj1[0], 0.000)
		self.assertEqual(dataset_obj1[34], 0.206)
		self.assertEqual(dataset_obj1[36], 1.469)

		self.assertEqual(dataset_obj2[0], 0.000)
		self.assertEqual(dataset_obj2[34], 0.411)
		self.assertEqual(dataset_obj2[36], 1.286)

		testh5.close()
		os.remove(h5file_path)



class parse_average_PKF(unittest.TestCase):
		def test_write_pcdat_onecol(self):
			dir_testfiles = os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp/Tests")
			dir_generalPKF = os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp/Tests/testdata/LiC")
			file_general = os.path.join(dir_generalPKF, "PCDAT")
			h5file_path = os.path.join(dir_testfiles, "testh5file.hdf5")

			pcdat_data = _parse_pcdat("testh5file.hdf5", file_general, dir_generalPKF)
			key0 = list(pcdat_data)[0]
			list0 = pcdat_data[key0]

			# Tests - to control pcdat_data's format
			# expected format is {'general paircorr':[0.00, 0.00,... 3.660,..]}
			self.assertIsInstance(pcdat_data, dict)
			self.assertEqual(str(key0), "general paircorr")
			self.assertIsInstance(list0, list)

			# Tests - to control pcdat_data has correct data
			# expected 256 values from t_0
			self.assertEqual(len(list0), 256)
			self.assertEqual(list0[0], 0.000)
			self.assertEqual(list0[20], 3.660)
			self.assertEqual(list0[32], 0.861)


			# Create empty HDF5-file
			testh5 = h5py.File(h5file_path, 'w')
			group = list(testh5.keys())
			# Test - to show HDF5-file is empty.
			self.assertEqual(len(group), 0)
			testh5.close()

			# _write_pcdat_onecol is called, for systems of multiple elements with an
			# average pair-correlation function.
			_write_pcdat_onecol(h5file_path, pcdat_data, 16, 256)  # default APACO = 16, NPACO = 256

			testh5 = h5py.File(h5file_path, 'r')
			group = list(testh5.keys())
			timeframes = list(testh5["PairCorrelationFunc"].keys())
			dataset_obj = testh5["PairCorrelationFunc/t_0"]
			distance = testh5["PairCorrelationFunc/Iterations"]

			# Test - to show HDF5-file is written to.
			self.assertNotEqual(len(group), 0)

			# Tests - to control the writing to HDF5-file
			self.assertIn("PairCorrelationFunc", testh5)
			self.assertIn("PairCorrelationFunc/Iterations", testh5)
			self.assertIn("PairCorrelationFunc/t_0", testh5)
			self.assertEqual(timeframes, ["Iterations", "t_0"])
			self.assertIsInstance(dataset_obj[()], numpy.ndarray)
			self.assertEqual(dataset_obj.shape, (256,))

			self.assertIsInstance(distance[()], numpy.ndarray)
			self.assertEqual(distance.shape, (256,))

			#Tests - to control HDF5-file has correct data
			self.assertEqual(dataset_obj[0], 0.000)
			self.assertEqual(dataset_obj[32], 0.861)
			self.assertEqual(dataset_obj[20], 3.660)
			testh5.close()
			os.remove(h5file_path)

		#This class make sure that the whole parsing system works.
		def test_parsing(self):
			dir_testfiles = os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp/Tests")
			dir_generalPKF = os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp/Tests/testdata/LiC")
			h5file_path = os.path.join(dir_testfiles, "testh5file.hdf5")

			# Create empty HDF5-file
			testh5 = h5py.File(h5file_path, 'w')
			group = list(testh5.keys())
			# Test - to show HDF5-file is empty.
			self.assertEqual(len(group), 0)
			testh5.close()

			#Is the function calls other parsing functions such as _parse_pcdat, _write_pcdat_onecol or _write_pcdat_multicol
			paircorrelation(h5file_path, dir_generalPKF)

			testh5 = h5py.File(h5file_path, 'r')
			group = list(testh5.keys())
			timeframes = list(testh5["PairCorrelationFunc"].keys())
			dataset_obj = testh5["PairCorrelationFunc/t_0"]
			distance = testh5["PairCorrelationFunc/Iterations"]

			# Test - to show HDF5-file is written to.
			self.assertNotEqual(len(group), 0)

			# Tests - to control the writing to HDF5-file
			self.assertIn("PairCorrelationFunc", testh5)
			self.assertIn("PairCorrelationFunc/Iterations", testh5)
			self.assertIn("PairCorrelationFunc/Iterations", testh5)
			self.assertEqual(timeframes, ["Iterations", "t_0"])
			self.assertIsInstance(dataset_obj[()], numpy.ndarray)
			self.assertEqual(dataset_obj.shape, (256,))

			self.assertIsInstance(distance[()], numpy.ndarray)
			self.assertEqual(distance.shape, (256,))

			#Tests - for contents
			self.assertEqual(dataset_obj[28], 0.003)
			self.assertEqual(dataset_obj[19], 1.371)
			testh5.close()
			os.remove(h5file_path)


if __name__ == '__main__':
	unittest.main()










