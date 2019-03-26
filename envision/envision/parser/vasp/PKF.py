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
	fileclass = h5py.File("namba", "w") 
	grp = fileclass.create_group("subgroup1")
	grp2 = fileclass.create_group("subgroup2")

	subgrp2 = grp2.create_group("subsubgroup2")
	subgrp3 = subgrp2.create_group("subsubsubgroup2")

	dset = grp.create_dataset("blabla", (100,), dtype='i')
	dset2 = subgrp3.create_dataset("a special dataset", (100,), dtype='i')


	#with h5py.File("mytestfile.hdf5", "w") as f:
	#	dset = f.create_dataset("mydataset", (100,), dtype='i')
	#	stringname = dset.name 
	#	fileobject = f.name 

	#print(str(20))
	#print(stringname)
	#print(fileobject)
	if "/subgroup2/subsubgroup2/subsubsubgroup2/a special dataset" in fileclass: #if in notation only looks after groups directly after fileclass 
		print("Yeas! kan lasa dataset")
		#print(list(fileclass.keys())) #lista keys = groups till HDFfil
		print(dset2.name)
		return fileclass 
	
	print("koko")
	print(grp2.name)
	return fileclass


	
	#is the file already parsed? 
	#if os.path.isfile(h5file): 
	#	with h5py.File(h5file, 'r') as h5: 
	#		if "" 
	
fileobj= paircorrelation() 
#print(list(fileobj.keys())) 


