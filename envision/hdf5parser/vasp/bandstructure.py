#
#  ENVISIoN
#
#  Copyright (c) 2017 Fredrik Segerhammar
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##############################################################################################
#
#  Alterations to this file by Anton Hjert
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.



import os,sys
import inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder+'/..'))
import re
import h5py
import numpy as np
from h5writer import _write_bandstruct

line_reg_int = re.compile(r'^( *[+-]?[0-9]+){3} *$')
line_reg_float = re.compile(r'( *[+-]?[0-9]*\.[0-9]+(?:[eE][+-]?[0-9]+)? *){4}')


def bandstruct_parse(file_object):
	"""
	Parses band structure data from EIGENVAL

	Parameters
	----------
	file_object : file object
		File object containing data in EIGENVAL

	Returns
	-------
	band_data : list
		list containing all the band data
		kval_list : list
		list containing all the K-points

	"""
	data = None
	kval = None
	kval_list = []
	band_data = []
	i = 0

	for line in file_object:
		match_float = line_reg_float.match(line)
		match_int = line_reg_int.match(line)

		if match_int:
			data = [int(v) for v in line.split()]
			band_data = [[] for _ in range(data[2])]
		if data and match_float:
			kval = []
			for u in range(3):
				kval.append(float(line.split()[u]))
		elif kval and data:
			band_data[i].append(float(line.split()[1]))
			i += 1
		if i == len(band_data) and kval:
			kval_list.append(kval)
			kval = None
			i = 0
	return band_data, kval_list


def bandstructure(h5file, vasp_dir):
	"""
	Parses band structure data from EIGENVAL

	Parameters
	----------
	h5file : str
		String that asserts which HDF-file to write to
	vasp_dir : str
		Path to directory containing EIGENVAL file

	Returns
	-------
	bool
		Return True if EIGENVAL was parsed, False otherwise

	"""
	if os.path.isfile(h5file):
		with h5py.File(h5file, 'r') as h5:
			if '/Bandstructure' in h5:
				print('Band structure data already parsed. Skipping.')
				return False
	try:
		with open(os.path.join(vasp_dir, 'EIGENVAL'), 'r') as f:
			band_data, kval_list = bandstruct_parse(f)
			if not band_data:
				print('EIGENVAL does not contain any data for band structure. Skipping.')
				return False
	except OSError:
		print('EIGENVAL file not in directory. Skipping.')
		return False
	_write_bandstruct(h5file, band_data, kval_list)
	print('Band structure data was parsed successfully.')
	return True