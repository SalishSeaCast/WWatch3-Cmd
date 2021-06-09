#  Copyright 2019-2021, the MIDOSS project contributors, The University of British Columbia,
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
from copy import deepcopy
from pathlib import Path
import shlex
import shutil
import subprocess
import textwrap

import arrow
import arrow.parser
import cliff.command
import cookiecutter.main
import nemo_cmd.prepare
import yaml

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
            "walltime",
            metavar="WALLTIME",
            type=str,
            help="HPC batch job walltime for the run; formatted as HH:MM:SS",
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
            "--start-date",
            type=self._arrow_date,
            default=arrow.now().floor("day"),
            help=f"""
                Date to start run execution on. Use YYYY-MM-DD format.
                Defaults to {arrow.now().floor('day').format('YYYY-MM-DD')}.
                """,
        )
        parser.add_argument(
            "--n-days",
            type=int,
            default=1,
            help="Number of days of runs to execute in the batch job. Defaults to 1.",
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
            parsed_args.start_date,
            parsed_args.walltime,
            n_days=parsed_args.n_days,
            no_submit=parsed_args.no_submit,
            quiet=parsed_args.quiet,
        )
        if submit_job_msg and not parsed_args.quiet:
            logger.info(submit_job_msg)


def run(
    desc_file, results_dir, start_date, walltime, n_days=1, no_submit=False, quiet=False
):
    """Create and populate a temporary run directory, and a run script,
    and submit the run to the queue manager.

    The run script is stored in :file:`SoGWW3.sh` in the temporary run directory.
    That script is submitted to the queue manager in a subprocess.

    :param desc_file: File path/name of the YAML run description file.
    :type desc_file: :py:class:`pathlib.Path`

    :param results_dir: Path of the directory in which to store the run results;
                        it will be created if it does not exist.
    :type results_dir: :py:class:`pathlib.Path`

    :param start_date: Date to start run execution on.
    :type :py:class:`arrow.Arrow`:

    :param str walltime: HPC batch job walltime to use for the run;
                         formatted as :kbd:`HH:MM:SS`.

    :param int n_days: Number of days of runs to execute in the batch job.

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
    days = list(arrow.Arrow.range("day", start_date, limit=n_days))
    run_start_dates_yyyymmdd = (
        [start_date.format("YYYYMMDD")]
        if n_days == 1
        else [day.format("YYYYMMDD") for day in days]
    )
    results_dirs = (
        [_resolve_results_dir(results_dir)]
        if n_days == 1
        else [
            _resolve_results_dir(results_dir) / (day.format("DDMMMYY").lower())
            for day in days
        ]
    )
    tmp_run_dir_timestamp = arrow.now().format("YYYY-MM-DDTHHmmss.SSSSSSZ")
    tmp_run_dirs = (
        [runs_dir / f"{run_id}_{tmp_run_dir_timestamp}"]
        if n_days == 1
        else [
            runs_dir
            / f"{run_id}_{day.format('DDMMMYY').lower()}_{tmp_run_dir_timestamp}"
            for day in days
        ]
    )
    for day, day_results_dir, tmp_run_dir in zip(days, results_dirs, tmp_run_dirs):
        day_run_id = run_id
        try:
            restart_path = nemo_cmd.prepare.get_run_desc_value(
                run_desc, ("restart", "restart.ww3"), resolve_path=True, fatal=False
            )
        except KeyError:
            restart_path = ""
        cookiecutter_context = {
            "tmp_run_dir": tmp_run_dir,
            "run_start_dates_yyyymmdd": "\n  ".join(run_start_dates_yyyymmdd),
            "results_dirs": "\n  ".join(map(os.fspath, results_dirs)),
            "work_dirs": "\n  ".join(map(os.fspath, tmp_run_dirs)),
            "batch_directives": _sbatch_directives(run_desc, day_results_dir, walltime),
            "module_loads": "module load netcdf-fortran-mpi/4.4.4",
            "run_id": run_id,
            "runs_dir": runs_dir,
            "run_start_date_yyyymmdd": start_date.format("YYYYMMDD"),
            "run_end_date_yyyymmdd": start_date.shift(days=+1).format("YYYYMMDD"),
            "mod_def_ww3_path": mod_def_ww3_path,
            "current_forcing_dir": current_forcing_dir,
            "wind_forcing_dir": wind_forcing_dir,
            "restart_path": restart_path,
            "results_dir": day_results_dir,
        }
        if n_days > 1:
            day_run_id = f"{run_id}_{day.format('DDMMMYY').lower()}"
            if restart_path:
                daym1_ddmmmyy = day.shift(days=-1).format("DDMMMYY").lower()
                restart_path = (
                    restart_path.parent.parent / daym1_ddmmmyy
                ) / restart_path.name
            else:
                logger.warning(
                    "You have requested a multi-day run with no restart file path. "
                    "Each day of the run will start from calm wave fields. "
                    "Is this really what you want?"
                )
            cookiecutter_context.update(
                {
                    "run_id": day_run_id,
                    "run_start_date_yyyymmdd": day.format("YYYYMMDD"),
                    "run_end_date_yyyymmdd": day.shift(days=+1).format("YYYYMMDD"),
                    "restart_path": restart_path,
                }
            )
        cookiecutter.main.cookiecutter(
            os.fspath(Path(__file__).parent.parent / "cookiecutter"),
            no_input=True,
            output_dir=runs_dir,
            extra_context=cookiecutter_context,
        )
        day_run_desc = deepcopy(run_desc)
        day_run_desc.update(
            {"run_id": day_run_id, "restart": {"restart.ww3": os.fspath(restart_path)}}
        )
        _write_tmp_run_dir_run_desc(day_run_desc, tmp_run_dir, desc_file, n_days)
        if not quiet:
            logger.info(f"Created temporary run directory {tmp_run_dir}")
        day_results_dir.mkdir(parents=True, exist_ok=True)
    try:
        for tmp_run_dir in tmp_run_dirs[1:]:
            (tmp_run_dir / "SoGWW3.sh").unlink()
    except IndexError:
        # len(tmp_run_dirs) == 1 for n_days == 1
        pass
    run_script_file = tmp_run_dirs[0] / "SoGWW3.sh"
    if not quiet:
        logger.info(f"Wrote job run script to {run_script_file}")
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


def _write_tmp_run_dir_run_desc(run_desc, tmp_run_dir, desc_file, n_days):
    """Write the run description to a YAML file in the temporary run directory
    so that it is preserved with the run results.

    Extracted into a separate function to improve testability of the run() function.

    :param dict run_desc: Contents of run description file parsed from YAML into a dict.

    :param tmp_run_dir: Temporary directory generated for the run.
    :type tmp_run_dir: :py:class:`pathlib.Path`

    :param desc_file: File path/name of the YAML run description file.
    :type desc_file: :py:class:`pathlib.Path`

    :param int n_days: Number of days of runs to execute in the batch job.
    """
    if n_days == 1:
        shutil.copy2(desc_file, tmp_run_dir)
        return
    with (tmp_run_dir / desc_file.name).open("wt") as f:
        yaml.safe_dump(run_desc, f, default_flow_style=False)


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


def _sbatch_directives(run_desc, results_dir, walltime):
    run_id = nemo_cmd.prepare.get_run_desc_value(run_desc, ("run_id",))
    sbatch_directives = textwrap.dedent(
        f"""\
        #SBATCH --job-name={run_id}
        #SBATCH --mail-user={nemo_cmd.prepare.get_run_desc_value(run_desc, ("email",))}
        #SBATCH --mail-type=ALL
        #SBATCH --account={nemo_cmd.prepare.get_run_desc_value(run_desc, ("account",))}
        #SBATCH --constraint=skylake
        #SBATCH --nodes=1
        #SBATCH --ntasks-per-node=20
        #SBATCH --mem=0
        #SBATCH --time={walltime}
        # stdout and stderr file paths/names
        #SBATCH --output={results_dir/"stdout"}
        #SBATCH --error={results_dir/"stderr"}
        """
    )
    return sbatch_directives
