import os 
import sys
import itertools 
import h5py
import numpy as np 


#make module available 
PATH_TO_parser=os.path.expanduser("~/ENVISIoN/envision/envision/parser")
sys.path.append(os.path.abspath(PATH_TO_parser))

import h5writer 


#The function script from inviwo will call with envision.parser.vasp.paircorrelation(PATH_TO_HDF5, PATH_TO_VASP_CALC)
print("This should work!!!")

def paircorrelation(h5file, vasp_dir):

	"""
	The function is called from ENVISIoNs (alt.inviwo) environment to parse relevant information 		for visualization of the paircorrelation function.    

	Parameters
	__________
	h5file: str
		String that asserts which HDF5-file to write to. 

	vasp_dir: str
		Path to directory containing VASP-files, such as PCDAT.  


	
	Return
	_______
	bool 
		True if parsing is taking place, False otherwise.	

	""" 

	#Check if it's parsed, no need for parsing if it's already done. 
"""	if os.path.isfile(h5file): 
		with h5py.File(h5file, 'r') as h5: 
			if '/PairCorrelationFunc' in h5: 
				print('PCDAT already parsed. Skipping.')
				return False

	try: 
		with open(os.path.join(vasp_dir, 'PCDAT'), 'r') as vasp_fileobj:
			pcdat_data = _parse_pcdat(h5file, vasp_fileobj) #vasp_fileobj is a fileobject 
			

	except FileNotFoundError:
		print("PCDAT file not in directory. Skipping.")
		return False 

	_write_pcdat(h5file, pcdat_data)
	print('PCDAT data was parsed sucessfully.')
	return True 		"""	 
	

#_parse_pcdat(h5file, vasp_fileobj)
#_write_pcdat(h5file, pcdat_data) pcdat_data is a list for relevant atom n. 

	



