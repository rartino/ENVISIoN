
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
        os.remove(h5file)
        return False
    if not prior_h5 and not prior_vasp:
        return False
    if prior_vasp and not prior_h5:
        return False
