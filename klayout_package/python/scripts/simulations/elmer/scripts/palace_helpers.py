# This code is part of KQCircuits
# Copyright (C) 2023 IQM Finland Oy
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
import json
import shutil
from pathlib import Path
from typing import Any, Mapping, Union

import gmsh


def write_palace_json(json_data: Mapping[str, Any], palace_json: Union[Path, str], msh_file: str):

    with open('sif/PalaceCapacitance.json', 'r') as fp:
        palace_json_data = json.load(fp)

    palace_json_data['Model']['Mesh'] = msh_file
    palace_json_data['Domains']['Materials'] = [
      {
          "Attributes": [{v: k for k, v in json_data['model_data']['body_materials'].items()}['vacuum'][-1]],
        "Permittivity": 1.0
      },
      {
          "Attributes": [{v: k for k, v in json_data['model_data']['body_materials'].items()}['dielectric'][-1]],
        "Permittivity": json_data['model_data']['substrate_permittivity']
      }
    ]


    gmsh.initialize()
    gmsh.merge(msh_file)
    surface_to_tag = {
        gmsh.model.getPhysicalName(dim, tag): tag
        for dim, tag in gmsh.model.getPhysicalGroups(dim = 2)
    }
    gmsh.finalize()


    ports = [surface_to_tag[e] for e in json_data['model_data']['port_signal_names']]
    ground = [surface_to_tag[e] for e in json_data['model_data']['ground_names']]
    palace_json_data['Boundaries']['Ground'] = {'Attributes': ground}
    palace_json_data['Boundaries']['Terminal'] = [
      {
        "Index": i,
        "Attributes": [port_tag]
      } for i, port_tag in enumerate(ports, 1)
    ]
    palace_json_data['Boundaries']['Postprocessing']['Capacitance'] = palace_json_data['Boundaries']['Terminal']

    palace_json_data['Solver']['Order'] = json_data['p_element_order']
    palace_json_data['Solver']['Electrostatic']['Save'] = len(ports)

    # TODO better naming for arg
    if json_data.get('palace_linear_solver', None) is not None:
        palace_json_data["Solver"]["Linear"] = {**palace_json_data["Solver"]["Linear"], **json_data['palace_linear_solver']}

    with open(palace_json, 'w') as fp:
        fp.write(json.dumps(palace_json_data))

    return palace_json
