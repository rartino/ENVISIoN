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

import os
import itertools
import h5py
import re
import numpy as np
from ..h5writer import _write_volume
from ..h5writer import _write_basis
from .unitcell import _parse_lattice

line_reg_int = re.compile(r'^( *[+-]?[0-9]+){3} *$')
line_reg_float = re.compile(r'( *[+-]?[0-9]*\.[0-9]+(?:[eE][+-]?[0-9]+)? *)+')

def parse_volume(vasp_file, volume):
	"""Parse a volume.

	Keyword arguments:

	"""
	array = []
	datasize = None
	data = None

	for line in vasp_file:
		match_float = line_reg_float.match(line)
		match_int = line_reg_int.match(line)

		if match_int:
			data = ([int(v) for v in line.split()])
			datasize = data[0]*data[1]*data[2]

		elif data and match_float:
			for element in line.split():
				array.append(float(element))
				if len(array) == datasize:
					return array, data
		else:
			data = None
	return None, None

def volume(h5file, hdfgroup, vasp_dir, vasp_file):
	
	if not '/{}'.format('Basis') in h5file:
		try:
			with open(os.path.join(vasp_dir,'POSCAR'), 'r') as f:
				basis = _parse_lattice(f)
				_write_basis(h5file, basis)
				print('Basis was parsed successfully.')
		except FileNotFoundError:
			print("POSCAR file not found.")

	try:
		with open(os.path.join(vasp_dir, vasp_file), "r") as f:
			with h5py.File(h5file, 'a') as h5:
				if '/{}'.format(hdfgroup) in h5:
					print(hdfgroup + ' already parsed. Skipping.')
					return False
				for i in itertools.count():
					array, data = parse_volume(f, hdfgroup)
					if not array:
						break
					_write_volume(h5, i, array, data, hdfgroup)
				h5['{}/final'.format(hdfgroup)] = h5py.SoftLink('{}/{}'.format(hdfgroup,i-1))
	except FileNotFoundError:
		print(vaspfile + ' not in directory. Skipping.')
		return False
	print(vasp_file + ' was parsed successfully.')
	return True

def charge(h5file, vasp_dir):
	return volume(h5file, 'CHG', vasp_dir, 'CHG')

def elf(h5file, vasp_dir):
	return volume(h5file, 'ELF', vasp_dir, 'ELFCAR')