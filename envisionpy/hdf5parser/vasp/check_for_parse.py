##  ENVISIoN
##
##  Copyright (c) 2021 Gabriel Anderberg, Didrik Axén, Adam Engman,
##  Kristoffer Gubberud Maras, Joakim Stenborg
##  All rights reserved.
##
##  Redistribution and use in source and binary forms, with or without
##  modification, are permitted provided that the following conditions are met:
##
##  1. Redistributions of source code must retain the above copyright notice, this
##  list of conditions and the following disclaimer.
##  2. Redistributions in binary form must reproduce the above copyright notice,
##  this list of conditions and the following disclaimer in the documentation
##  and/or other materials provided with the distribution.
##
##  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
##  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
##  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
##  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
##  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
##  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
##  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
##  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
##  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
##  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##
## ##############################################################################################

import os, sys
import inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
def has_been_parsed(parse_name, h5file, vasp_dir):
    prior_h5 = True
    prior_vasp = True
    parse_file = open(path_to_current_folder + "/../priorparses.txt", 'r')
    lines = parse_file.readlines()
    for index, line in enumerate(lines):
        if line == parse_name + "\n":
            if h5file in lines[index + 1]:
                prior_h5 = True
            elif lines[index + 1] ==  "\n":
                lines[index + 1] = h5file + "\n"
            else:
                prior_h5 = False
                lines[index + 1] = h5file + "\n"
        if line == parse_name + "\n":
            if vasp_dir in lines[index + 2]:
                prior_vasp = True
            elif lines[index + 2] ==  "\n":
                lines[index + 2] = vasp_dir  + "\n"
            else:
                prior_vasp = False
                lines[index + 2] = vasp_dir  + "\n"
    with open(path_to_current_folder + "/../priorparses.txt", 'w') as file:
        file.writelines(lines)
    if prior_h5 and prior_vasp:
        return True
    if prior_h5 and not prior_vasp:
        try:
            os.remove(h5file)
            return False
        except:
            pass
    if not prior_h5 and not prior_vasp:
        return False
    if prior_vasp and not prior_h5:
        return False
