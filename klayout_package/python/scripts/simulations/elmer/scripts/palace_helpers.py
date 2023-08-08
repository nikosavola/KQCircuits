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


def write_palace_json(json_data, palace_json):

    shutil.copy(path.joinpath('sif/PalaceCapacitance.json'), palace_json)

    with open(palace_json, 'r') as fp:
        palace_json_data = json.load(fp)

    palace_json_data['Domains']['Materials'] = [
      {
        "Attributes": [vacuum],
        "Permittivity": 1.0
      },
      {
        "Attributes": [substrate],
        "Permittivity": 11.4
      }
    ]

    palace_json_data['Boundaries']['Ground'] = {'Attributes': [7]}
    palace_json_data['Boundaries']['Terminal'] = [
      {
        "Index": i,
        "Attributes": [port_mesh]
      } for i, port in enumerate(ports)
    ]
    palace_json_data['Boundaries']['Postprocessing']['Capacitance'] = palace_json_data['Boundaries']['Terminal']

    palace_json_data['Solver']['Order'] = json_data['p_element_order']


    with open(palace_json, 'w') as fp:
        json.dump(palace_json_data, fp)

    return palace_json