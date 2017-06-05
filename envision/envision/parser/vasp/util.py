#!/usr/bin/env python3

"""
TODO
"""

REGSTR_INT = r'[+-]?[0-9]+'
REGSTR_FLOAT = r'[+-]?[0-9]*\.[0-9]+(?:[eE][+-]?[0-9]+)?'
RESTR_BOOL = r'\.TRUE\.|\.FALSE\.'

def vasp_file_lines(vasp_file, line_continuation=False):
    """
	Parses one line of data in file

    Parameters
    ----------
    vasp_file : str
	String containing path to file
    line_continuation : bool
	True or False statement that asserts whether or not more lines should be read than one
		
		
    Returns
    -------
    line_nr : float
	Number that says which line is currently being parsed
    line : line object
	Object that says which line is being parsed
	
    """
    vasp_file_stripped = (line.rstrip("\n") for line in vasp_file)
    line_nr = 0
    for line in vasp_file_stripped:
        line_nr += 1
        while line_continuation and line.endswith("\\"):
            line = line[:-1] + next(vasp_file_stripped)
            line_nr += 1
        yield line_nr, line

def vasp_value_from_string(vasp_string):
    """
    TODO.
    """

    regstr_convfunc_list = [
            [REGSTR_INT, int],
            [REGSTR_FLOAT, float],
            [RESTR_BOOL, lambda s: { ".TRUE." : True, ".FALSE." : False }[s]],
        ]

    for regstr, convfunc in regstr_convfunc_list:
        match = re.search(regstr, r'(?<value>' + vasp_string + r')')
        if match:
            return convfunc(match.grous('value'))

    raise ValueError

