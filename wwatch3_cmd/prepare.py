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
"""WWatch3-Cmd command plug-in for prepare sub-command.

Sets up a temporary run directory for the WaveWatch III® run described
in a YAML run description file.
"""
import logging
import os
from pathlib import Path

import cliff.command
import cookiecutter.main
import nemo_cmd.prepare

logger = logging.getLogger(__name__)


class Prepare(cliff.command.Command):
    """Set up the WaveWatch III® run described in DESC_FILE and print the path of the temporary run directory.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "desc_file",
            metavar="DESC_FILE",
            type=Path,
            help="run description YAML file",
        )
        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="don't show the run directory path on completion",
        )
        return parser

    def take_action(self, parsed_args):
        """Execute the `wwatch3 prepare` sub-command.

        A uniquely named temporary run directory is created.
        Symbolic links and file copies are created in that directory based on the files and
        directories specified in the run description YAML file for a WaveWatch III® run.
        The path to the temporary run directory is logged to the console on completion
        of the set-up.
        """
        tmp_run_dir = prepare(parsed_args.desc_file)
        if not parsed_args.quiet:
            logger.info(f"Created temporary run directory: {tmp_run_dir}")
        return tmp_run_dir


def prepare(desc_file):
    """Create and prepare the temporary run directory.

    The temporary run directory is created with a unique name composed of the run id
    and an ISO-format date/time stamp;
    e.g. :file:`SoGwaves28sep19_2019-09-28T131343.123456-0800`.
    Symbolic links and file copies are created in that directory based on the files and
    directories specified in the run description YAML file for a WaveWatch III® run.
    The path to the temporary run directory is returned.

    :param desc_file: File path/name of the YAML run description file.
    :type desc_file: :py:class:`pathlib.Path`

    :returns: Path of the temporary run directory
    :rtype: :py:class:`pathlib.Path`
    """
    run_desc = nemo_cmd.prepare.load_run_desc(desc_file)
    run_id = nemo_cmd.prepare.get_run_desc_value(run_desc, ("run_id",))
    runs_dir = nemo_cmd.prepare.get_run_desc_value(
        run_desc, ("paths", "runs directory"), resolve_path=True
    )
    mod_def_ww3_path = nemo_cmd.prepare.get_run_desc_value(
        run_desc, ("grid", "mod_def.ww3 file"), resolve_path=True
    )
    current_forcing_dir = nemo_cmd.prepare.get_run_desc_value(
        run_desc, ("forcing", "current"), resolve_path=True
    )
    wind_forcing_dir = nemo_cmd.prepare.get_run_desc_value(
        run_desc, ("forcing", "wind"), resolve_path=True
    )
    tmp_run_dir = cookiecutter.main.cookiecutter(
        os.fspath(Path(__file__).parent.parent / "cookiecutter"),
        no_input=True,
        output_dir=runs_dir,
        extra_context={
            "run_id": run_id,
            "runs_dir": runs_dir,
            "mod_def_ww3_path": mod_def_ww3_path,
            "current_forcing_dir": current_forcing_dir,
            "wind_forcing_dir": wind_forcing_dir,
        },
    )
    return tmp_run_dir
