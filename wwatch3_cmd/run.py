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
"""WWatch3-Cmd command plug-in for run sub-command.

Prepare for, execute, and gather the results of a run of the WaveWatch III® model.
"""
import argparse
import logging
import os
from pathlib import Path
import shlex
import subprocess

import arrow
import arrow.parser
import cliff.command
import cookiecutter.main
import nemo_cmd.prepare

logger = logging.getLogger(__name__)


class Run(cliff.command.Command):
    """Prepare, execute, and gather results from a WaveWatch III® model run.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.description = """
            Prepare, execute, and gather the results from a WaveWatch III®
            run described in DESC_FILE.
            The results files from the run are gathered in RESULTS_DIR.

            If RESULTS_DIR does not exist it will be created.
        """
        parser.add_argument(
            "desc_file",
            metavar="DESC_FILE",
            type=Path,
            help="run description YAML file",
        )
        parser.add_argument(
            "results_dir",
            metavar="RESULTS_DIR",
            type=Path,
            help="directory to store results into",
        )
        parser.add_argument(
            "--no-submit",
            dest="no_submit",
            action="store_true",
            help="""
            Prepare the temporary run directory, and the bash script to 
            execute the WaveWatch III® run, but don't submit the run to the queue.
            This is useful during development runs when you want to hack on 
            the bash script and/or use the same temporary run directory 
            more than once.
            """,
        )
        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="don't show the run directory path or job submission message",
        )
        parser.add_argument(
            "--run-date",
            type=self._arrow_date,
            default=arrow.now().floor("day"),
            help=(
                f"Date to execute the run for. Use YYYY-MM-DD format. "
                f"Defaults to {arrow.now().floor('day').format('YYYY-MM-DD')}."
            ),
        )
        return parser

    @staticmethod
    def _arrow_date(string):
        """Convert a YYYY-MM-DD string to a UTC arrow object or raise
        :py:exc:`argparse.ArgumentTypeError`.

        The time part of the resulting arrow object is set to 00:00:00.

        :arg str string: YYYY-MM-DD string to convert.

        :returns: Date string converted to a UTC :py:class:`arrow.Arrow` object.

        :raises: :py:exc:`argparse.ArgumentTypeError`
        """
        try:
            return arrow.get(string, "YYYY-MM-DD")
        except arrow.parser.ParserError:
            msg = f"unrecognized date format: {string} - please use YYYY-MM-DD"
            raise argparse.ArgumentTypeError(msg)

    def take_action(self, parsed_args):
        """Execute the `wwatch3 run` sub-coomand.

        The message generated upon submission of the run to the queue
        manager is logged to the console.

        :param parsed_args: Arguments and options parsed from the command-line.
        :type parsed_args: :class:`argparse.Namespace` instance
        """
        submit_job_msg = run(
            parsed_args.desc_file,
            parsed_args.results_dir,
            parsed_args.run_date,
            no_submit=parsed_args.no_submit,
            quiet=parsed_args.quiet,
        )
        if submit_job_msg and not parsed_args.quiet:
            logger.info(submit_job_msg)


def run(desc_file, results_dir, run_date, no_submit=False, quiet=False):
    """Create and populate a temporary run directory, and a run script,
    and submit the run to the queue manager.

    The run script is stored in :file:`SoGWW3.sh` in the temporary run directory.
    That script is submitted to the queue manager in a subprocess.

    :param desc_file: File path/name of the YAML run description file.
    :type desc_file: :py:class:`pathlib.Path`

    :param results_dir: Path of the directory in which to store the run results;
                        it will be created if it does not exist.
    :type results_dir: :py:class:`pathlib.Path`

    :param run_date: Date to execute run for.
    :type :py:class:`arrow.Arrow`:

    :param boolean no_submit: Prepare the temporary run directory,
                              and the run script to execute the WaveWatch III® run,
                              but don't submit the run to the queue.

    :param boolean quiet: Don't show the run directory path message;
                          the default is to show the temporary run directory
                          path.

    :returns: Message generated by queue manager upon submission of the
              run script.
    :rtype: str
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
    results_dir = _resolve_results_dir(results_dir)
    tmp_run_dir = cookiecutter.main.cookiecutter(
        os.fspath(Path(__file__).parent.parent / "cookiecutter"),
        no_input=True,
        output_dir=runs_dir,
        extra_context={
            "run_id": run_id,
            "runs_dir": runs_dir,
            "run_start_date_yyyymmdd": run_date.format("YYYY-MM-DD"),
            "run_end_date_yyyymmdd": run_date.shift(days=+1).format("YYYY-MM-DD"),
            "mod_def_ww3_path": mod_def_ww3_path,
            "current_forcing_dir": current_forcing_dir,
            "wind_forcing_dir": wind_forcing_dir,
            "results_dir": results_dir,
        },
    )
    run_script_file = Path(tmp_run_dir) / "SoGWW3.sh"
    if not quiet:
        logger.info(f"Created temporary run directory {tmp_run_dir}")
        logger.info(f"Wrote job run script to {run_script_file}")
    results_dir.mkdir(parents=True, exist_ok=True)
    if no_submit:
        return
    sbatch_cmd = f"sbatch {run_script_file}"
    submit_job_msg = subprocess.run(
        shlex.split(sbatch_cmd),
        check=True,
        universal_newlines=True,
        stdout=subprocess.PIPE,
    ).stdout
    return submit_job_msg


def _resolve_results_dir(results_dir):
    """Expand environment variables and :file:`~` in :kbd:`results_dir`
    and resolve it to an absolute path.

    :param results_dir: Path of the directory in which to store the run results;
                        it will be created if it does not exist.
    :type results_dir: :py:class:`pathlib.Path`

    :return: :py:class:`pathlib.Path`
    """
    results_dir = Path(os.path.expandvars(results_dir)).expanduser().resolve()
    return results_dir
