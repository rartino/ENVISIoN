import os 
import sys
import itertools 
import h5py
import numpy as np 


#make module available 
PATH_TO_parser=os.path.expanduser("~/ENVISIoN/envision/envision/parser")
sys.path.append(os.path.abspath(PATH_TO_parser))

import h5writer 

#function called from script in inviwo 
def paircorrelation(h5file = 0, vasp_dir = 0):
	"""
	Reads PCDAT-file and stores the data in an HDF5-file. 

	Parameters 
	___________
	h5file : str 
		String that asserts which HDF5-file to write to. 
	vasp_dir : str 
		Path to directory containing volume file. 

	Returns 
	________ 
	bool
		True if PCDAT was parsed, false otherwise. 
	
	"""
	fileclass = h5py.File("Bajstest", "w") 
	grp = fileclass.create_group("subgroup1")
	dset = grp.create_dataset("blabla", (100,), dtype='i')


	#with h5py.File("mytestfile.hdf5", "w") as f:
	#	dset = f.create_dataset("mydataset", (100,), dtype='i')
	#	stringname = dset.name 
	#	fileobject = f.name 

	#print(str(20))
	#print(stringname)
	#print(fileobject)
	if "/subgroup1" in fileclass: 
		print("Yeas! kan lasa dataset")
		return fileclass 
	
	print("koko")
	return fileclass


	
	#is the file already parsed? 
	#if os.path.isfile(h5file): 
	#	with h5py.File(h5file, 'r') as h5: 
	#		if "" 
	
fileobj= paircorrelation() 
print(list(fileobj.keys())) 


