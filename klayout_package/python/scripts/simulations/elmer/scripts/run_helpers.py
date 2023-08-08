# This code is part of KQCircuits
# Copyright (C) 2022 IQM Finland Oy
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see
# https://www.gnu.org/licenses/gpl-3.0.html.
#
# The software distribution should follow IQM trademark policy for open-source software
# (meetiqm.com/developers/osstmpolicy). IQM welcomes contributions to the code. Please see our contribution agreements
# for individuals (meetiqm.com/developers/clas/individual) and organizations (meetiqm.com/developers/clas/organization).


import logging
import shutil
import subprocess
import sys
import platform
import json
from pathlib import Path

def write_simulation_machine_versions_file(path, name):
    """
    Writes file SIMULATION_MACHINE_VERSIONS into given file path.
    """
    versions = {}
    versions['platform'] = platform.platform()
    versions['python'] = sys.version_info

    gmsh_versions_list = []
    with open(path.joinpath(name+'.json_Gmsh.log')) as f:
        gmsh_log = f.readlines()
        gmsh_versions_list = [line.replace('\n', '') for line in gmsh_log if 'ersion' in line]

    elmer_versions_list = []
    with open(path.joinpath(name+'.json_Elmer.log')) as f:
        elmer_log = f.readlines()
        elmer_versions_list = [line.replace('\n', '') for line in elmer_log if 'ersion' in line]

    versions['gmsh'] = gmsh_versions_list
    versions['elmer'] = elmer_versions_list

    mpi_command = 'mpirun' if shutil.which('mpirun') is not None else 'mpiexec'
    if shutil.which(mpi_command) is not None:
        if mpi_command == 'mpiexec':
            output = subprocess.check_output([mpi_command])
        else:
            output = subprocess.check_output([mpi_command, '--version'])
        versions['mpi'] = output.decode('ascii').split('\n', maxsplit=1)[0]

    paraview_command = 'paraview'
    if shutil.which(paraview_command) is not None:
        output = subprocess.check_output([paraview_command, '--version'])
        versions['paraview'] = output.decode('ascii').split('\n', maxsplit=1)[0]

    with open('SIMULATION_MACHINE_VERSIONS.json', 'w') as file:
        json.dump(versions, file)

def run_elmer_grid(msh_path, n_processes, exec_path_override=None):
    elmergrid_executable = shutil.which('ElmerGrid')
    if elmergrid_executable is not None:
        subprocess.check_call([elmergrid_executable, '14', '2', msh_path], cwd=exec_path_override)
        if n_processes > 1:
            subprocess.check_call([elmergrid_executable, '2', '2', Path(msh_path).stem + '/', '-metis',
                                   str(n_processes), '4', '-removeunused'], cwd=exec_path_override)
    else:
        logging.warning("ElmerGrid was not found! Make sure you have ElmerFEM installed: "
                        "https://github.com/ElmerCSC/elmerfem")
        sys.exit()


def run_elmer_solver(sif_path, n_processes, exec_path_override=None):
    elmersolver_executable = shutil.which('ElmerSolver')
    elmersolver_mpi_executable = shutil.which('ElmerSolver_mpi')
    if n_processes > 1 and elmersolver_mpi_executable is not None:
        mpi_command = 'mpirun' if shutil.which('mpirun') is not None else 'mpiexec'
        subprocess.check_call([mpi_command, '-np', str(n_processes), elmersolver_mpi_executable,
                               sif_path], cwd=exec_path_override)
    elif elmersolver_executable is not None:
        subprocess.check_call([elmersolver_executable, sif_path], cwd=exec_path_override)
    else:
        logging.warning("ElmerSolver was not found! Make sure you have ElmerFEM installed: "
                        "https://github.com/ElmerCSC/elmerfem")
        sys.exit()


def run_paraview(result_path, n_processes, exec_path_override=None):
    paraview_executable = shutil.which('paraview')
    if paraview_executable is not None:
        if n_processes > 1:
            subprocess.check_call([paraview_executable, '{}_t0001.pvtu'.format(result_path)], cwd=exec_path_override)
        else:
            subprocess.check_call([paraview_executable, '{}_t0001.vtu'.format(result_path)], cwd=exec_path_override)
    else:
        logging.warning("Paraview was not found! Make sure you have it installed: https://www.paraview.org/")
        sys.exit()


def run_palace(config_json, n_processes, exec_path_override=None):
    palace_executable = shutil.which('palace')
    if palace_executable:
        subprocess.check_call([palace_executable, '-np', str(n_processes), config_json], cwd=exec_path_override)
    else:
        logging.warning("Palace was not found! Make sure you have it installed in your PATH. "
                        "https://awslabs.github.io/palace")
        sys.exit()
