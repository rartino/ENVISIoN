import os,sys
import inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder+'/..'))
import re
import numpy as np
import h5py
from h5writer import _write_basis, _write_scaling_factor, _write_coordinates, _write_forces
from pathlib import Path
# Define coordinates regex.
coordinates_re = re.compile(r' +'.join([r'([+-]?[0-9]+\.[0-9]+)'] * 3))

def _find_line(rgx, f):
    match = None
    while not match:
        match = rgx.search(next(f))
    return match

def _parse_potcar(potcar_file):
    # Look for elements in POTCAR
    elements = []
    with open(potcar_file, "r") as f:
        element_re = re.compile('TITEL.*')
        match = None
        for line in f:
            match = element_re.search(line)
            if match:
                elements.append(match.group().split()[3].split('_')[0])
    return elements

def _parse_lattice(fileobj):
    # Read header.
    header = next(fileobj)

    # Read scaling factor
    scaling_factor = float(next(fileobj).split()[0])

    # Read lattice vectors
    basis = []
    basis.append([float(n) for n in next(fileobj).split()[:3]])
    basis.append([float(n) for n in next(fileobj).split()[:3]])
    basis.append([float(n) for n in next(fileobj).split()[:3]])

    return scaling_factor, np.array(basis)

def _cartesian(fileobj):
    # Cartesian or direct coordinates
    coord_re = re.compile(r'^[cCkKdD]')
    coord_type = _find_line(coord_re,fileobj)
    if (coord_type.group() == 'd') or (coord_type.group() == 'D'):
        return False
    else:
        return True


def _parse_coordinates(fileobj, count, transform=False, matrix=None):
    match = False
    try:
        coords_list = []
        match = _find_line(coordinates_re, fileobj)
        while match:
            coords = [float(coordinate) for coordinate in match.groups()]
            if transform:
                coords = np.dot(matrix, coords)
            coords_list.append(coords)
            match = coordinates_re.search(next(fileobj))
    except StopIteration:
        pass # if EOF is reached here

    if len(coords_list) != count:
        raise Exception('Incorrect number of coordinates.', len(coords_list))

    return coords_list

def _parse_forces(vasp_dir, get_vector_tips = False, coordinates = []):
    forces = []
    force_tips = []
    pos = 0
    amount = 0
    outcar_file_path = Path(vasp_dir).joinpath('OUTCAR')
    if not outcar_file_path.exists():
        raise FileNotFoundError('Cannot find the vasp file in directory %s'
                                % vasp_dir)
    with outcar_file_path.open('r') as f:

        lines = f.readlines()
        for n, line in enumerate(lines):
            if 'total drift' in line:
                pos = n - 2
        for i, line in enumerate(lines):
            if 'POSITION' in line:
                k = i + 1
                while k < pos:
                    force = (re.findall(r'-?[\d.]+', lines[k + 1])[3:])
                    force = [float(x) for x in force]
                    forces.append(force)
                    k += 1
    if get_vector_tips:
        for i in range(len(forces)):
            list = [x + y for x, y in zip(coordinates[i], forces[i])]
            for p in coordinates[i]:
                list.append(p)
            force_tips.append(list)
        return force_tips
    return forces

def _find_elements(fileobj, elements, vasp_dir):
    atomcount_re=re.compile('^ *(([0-9]+) *)+$')
    last_comment = None
    poscar_elements = []
    while True:
        atoms_per_species = next(fileobj)
        match = atomcount_re.match(atoms_per_species)
        if match:
            break
        last_comment = atoms_per_species
    if last_comment:
        poscar_elements = last_comment.split()
    # Number of atoms
    atoms = [int(n) for n in atoms_per_species.split()]

    # Parses number of atoms per species from POTCAR
    if not elements:
        try:
            elements = _parse_potcar(os.path.join(vasp_dir, 'POTCAR'))
        except FileNotFoundError:
            elements = poscar_elements

    if not elements:
        raise Exception('Element symbols not found.')

    if len(elements) != len(atoms):
        raise Exception('Incorrect number of elements.')

    return elements, atoms


def force_parser(h5file, vasp_dir, elements=None, poscar_equiv='POSCAR'):
    if os.path.isfile(h5file):
        with h5py.File(h5file, 'r') as h5:
            if "/UnitCell"  and "/Forces" in h5:
                print("Already parsed. Skipping.")
                return True

    try:
        # Parses lattice vectors and atom positions from POSCAR
        with open(os.path.join(vasp_dir,poscar_equiv), "r") as f:
            scaling_factor, basis = _parse_lattice(f)
            elements, atoms = _find_elements(f, elements, vasp_dir)
            coords_list = _parse_coordinates(
                f,
                sum(atoms),
                _cartesian(f),
                np.linalg.inv(basis)
            )
            force_list = _parse_forces(vasp_dir, True, coords_list)
            #_write_basis(h5file, basis)
            #_write_scaling_factor(h5file, scaling_factor)
            _write_coordinates(
                h5file,
                atoms,
                coords_list,
                elements,
                '/UnitCell'
            )
            _write_forces(h5file,
            atoms,
            force_list,
            '/Forces')

            return True
    except FileNotFoundError:
        print("POSCAR file not found.")
        return False
