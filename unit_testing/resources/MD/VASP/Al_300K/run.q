#!/bin/bash

#SBATCH -J MDfccAl32 
#SBATCH -A SNIC2018-1-1
# Use n mpi-tasks, --ntasks-per-node per node
#SBATCH -n 16
#SBATCH --ntasks-per-node 16
#SBATCH --time=168:00:00
module add icc/2017.1.132-GCC-5.4.0-2.26 impi/2017.1.132
module add VASP/5.4.1-05Feb16-p02-hpc2n
mpirun vasp_std
