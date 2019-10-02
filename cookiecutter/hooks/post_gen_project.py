#  Copyright 2019, the MIDOSS project contributors, The University of British Columbia,
#  and Dalhousie University.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""Post-rendering script to set up symlinks in temporary run directory
for Strait of Georgia WaveWatch III® run.
"""
import os
from pathlib import Path

Path("mod_def.ww3").symlink_to(
    os.path.expandvars(Path("{{ cookiecutter.mod_def_ww3_path }}").expanduser())
)
Path("wind").symlink_to(os.path.expandvars("{{ cookiecutter.wind_forcing_dir }}"))
Path("current").symlink_to(os.path.expandvars("{{ cookiecutter.current_forcing_dir }}"))
if "{{ cookiecutter.restart_path }}":
    Path("restart.ww3").symlink_to(
        os.path.expandvars(Path("{{ cookiecutter.restart_path }}").expanduser())
    )
