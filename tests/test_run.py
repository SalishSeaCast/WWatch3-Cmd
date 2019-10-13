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
"""WWatch3-Cmd run sub-command plug-in unit tests.
"""
import logging
import os
from pathlib import Path
import subprocess
import textwrap
from types import SimpleNamespace
from unittest.mock import call, patch

import arrow
import pytest
import yaml

import wwatch3_cmd.main
import wwatch3_cmd.run


@pytest.fixture
def run_cmd():
    return wwatch3_cmd.run.Run(wwatch3_cmd.main.WWatch3App, [])


@pytest.fixture()
def run_desc(tmp_path):
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    scratch_ww3_runs = scratch / "wwatch3_runs"
    scratch_ww3_runs.mkdir()
    results_01jan15 = scratch_ww3_runs / "01jan15"
    results_01jan15.mkdir()
    current_dir = scratch / "current"
    current_dir.mkdir()
    wind_dir = scratch / "wind"
    wind_dir.mkdir()
    project = tmp_path / "project"
    project.mkdir()
    project_ww3_runs = project / "wwatch3_runs"
    project_ww3_runs.mkdir()
    mod_def_ww3 = project_ww3_runs / "mod_def.ww3"
    mod_def_ww3.write_bytes(b"")
    ww3_yaml = tmp_path / "wwatch3.yaml"
    ww3_yaml.write_text(
        textwrap.dedent(
            f"""\
            run_id: SoGwaves
            walltime: 00:20:00
            account: def-allen
            email: someone@eoas.ubc.ca
            
            paths:
              runs directory: {os.fspath(scratch_ww3_runs)}
              
            grid:
              mod_def.ww3 file: {os.fspath(mod_def_ww3)}
              
            forcing:
              current: {os.fspath(current_dir)}
              wind: {os.fspath(wind_dir)}
              
            restart:
              restart.ww3: {os.fspath(results_01jan15)}
            """
        )
    )
    with ww3_yaml.open("rt") as f:
        run_desc = yaml.safe_load(f)
    return run_desc


class TestParser:
    """Unit tests for `wwatch3 run` sub-command command-line parser.
    """

    def test_get_parser(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        assert parser.prog == "wwatch3 run"

    def test_cmd_description(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        assert parser.description.strip().startswith(
            "Prepare, execute, and gather the results from a WaveWatch III®"
        )

    def test_desc_file_argument(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        assert parser._actions[1].dest == "desc_file"
        assert parser._actions[1].metavar == "DESC_FILE"
        assert parser._actions[1].type == Path
        assert parser._actions[1].help

    def test_results_dir_argument(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        assert parser._actions[2].dest == "results_dir"
        assert parser._actions[2].metavar == "RESULTS_DIR"
        assert parser._actions[2].type == Path
        assert parser._actions[2].help

    def test_no_submit_option(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        assert parser._actions[3].dest == "no_submit"
        assert parser._actions[3].option_strings == ["--no-submit"]
        assert parser._actions[3].const is True
        assert parser._actions[3].default is False
        assert parser._actions[3].help

    def test_quiet_option(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        assert parser._actions[4].dest == "quiet"
        assert parser._actions[4].option_strings == ["-q", "--quiet"]
        assert parser._actions[4].const is True
        assert parser._actions[4].default is False
        assert parser._actions[4].help

    def test_start_date_option(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        assert parser._actions[5].dest == "start_date"
        assert parser._actions[5].option_strings == ["--start-date"]
        assert parser._actions[5].type == wwatch3_cmd.run.Run._arrow_date
        assert parser._actions[5].default == arrow.now().floor("day")
        assert parser._actions[5].help

    def test_parsed_args_defaults(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        parsed_args = parser.parse_args(["foo.yaml", "results/foo/"])
        assert parsed_args.desc_file == Path("foo.yaml")
        assert parsed_args.results_dir == Path("results/foo/")
        assert not parsed_args.no_submit
        assert not parsed_args.quiet
        assert parsed_args.start_date == arrow.now().floor("day")

    @pytest.mark.parametrize("flag", ["-q", "--quiet"])
    def test_parsed_args_quiet_options(self, flag, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        parsed_args = parser.parse_args(["foo.yaml", "results/foo/", flag])
        assert parsed_args.quiet is True

    def test_parsed_args_no_submit_option(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        parsed_args = parser.parse_args(["foo.yaml", "results/foo/", "--no-submit"])
        assert parsed_args.no_submit is True

    def test_parsed_args_start_date_option(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        parsed_args = parser.parse_args(
            ["foo.yaml", "results/foo/", "--start-date", "2019-10-09"]
        )
        assert parsed_args.start_date == arrow.get("2019-10-09")


class TestTakeAction:
    """Unit tests for `wwatch3 run` sub-command take_action() method.
    """

    @patch("wwatch3_cmd.run.run", return_value="submit job msg", autospec=True)
    def test_take_action(self, m_run, run_cmd, caplog):
        start_date = arrow.get("2019-10-07")
        parsed_args = SimpleNamespace(
            desc_file=Path("desc file"),
            results_dir=Path("results dir"),
            no_submit=False,
            quiet=False,
            start_date=start_date,
        )
        caplog.set_level(logging.INFO)
        run_cmd.take_action(parsed_args)
        m_run.assert_called_once_with(
            Path("desc file"),
            Path("results dir"),
            no_submit=False,
            quiet=False,
            start_date=start_date,
        )
        assert caplog.messages[0] == "submit job msg"

    @patch("wwatch3_cmd.run.run", return_value="submit job msg", autospec=True)
    def test_take_action_quiet(self, m_run, run_cmd, caplog):
        parsed_args = SimpleNamespace(
            desc_file=Path("desc file"),
            results_dir=Path("results dir"),
            no_submit=False,
            quiet=True,
            start_date=arrow.get("2019-10-07"),
        )
        caplog.set_level(logging.INFO)
        run_cmd.take_action(parsed_args)
        assert not caplog.messages

    @patch("wwatch3_cmd.run.run", return_value=None, autospec=True)
    def test_take_action_no_submit(self, m_run, run_cmd, caplog):
        parsed_args = SimpleNamespace(
            desc_file=Path("desc file"),
            results_dir=Path("results dir"),
            no_submit=True,
            quiet=True,
            start_date=arrow.get("2019-10-07"),
        )
        caplog.set_level(logging.INFO)
        run_cmd.take_action(parsed_args)
        assert not caplog.messages


@patch("wwatch3_cmd.run.subprocess.run", autospec=True)
@patch("wwatch3_cmd.run._resolve_results_dir", spec=True)
@patch("wwatch3_cmd.run._sbatch_directives", spec=True)
@patch(
    "wwatch3_cmd.run.cookiecutter.main.cookiecutter",
    return_value="tmp_run_dir",
    autospec=True,
)
@patch("wwatch3_cmd.run.Path.open", autospec=True)
class TestRun:
    """Unit tests for `wwatch3 run` run() function.
    """

    def test_no_submit(
        self,
        m_open,
        m_cookiecutter,
        m_sbatch_dir,
        m_rslv_results_dir,
        m_subproc_run,
        run_desc,
        tmp_path,
    ):
        results_dir = tmp_path / "results_dir"
        submit_job_msg = wwatch3_cmd.run.run(
            tmp_path / "wwatch3.yaml",
            results_dir,
            start_date=arrow.get("2019-10-07"),
            no_submit=True,
        )
        assert m_rslv_results_dir().mkdir.called
        assert not m_subproc_run.called
        assert submit_job_msg is None

    def test_submit(
        self,
        m_open,
        m_cookiecutter,
        m_sbatch_dir,
        m_rslv_results_dir,
        m_subproc_run,
        run_desc,
        tmp_path,
    ):
        results_dir = tmp_path / "results_dir"
        m_subproc_run().stdout = "submit_job_msg"
        submit_job_msg = wwatch3_cmd.run.run(
            tmp_path / "wwatch3.yaml", results_dir, start_date=arrow.get("2019-10-07")
        )
        assert m_rslv_results_dir().mkdir.called
        assert m_subproc_run.call_args_list[1] == call(
            ["sbatch", "tmp_run_dir/SoGWW3.sh"],
            check=True,
            universal_newlines=True,
            stdout=subprocess.PIPE,
        )
        assert submit_job_msg == "submit_job_msg"

    def test_cookiecutter(
        self,
        m_open,
        m_cookiecutter,
        m_sbatch_dir,
        m_rslv_results_dir,
        m_subproc_run,
        run_desc,
        tmp_path,
    ):
        results_dir = tmp_path / "results_dir"
        start_date = arrow.get("2019-10-07")
        wwatch3_cmd.run.run(tmp_path / "wwatch3.yaml", results_dir, start_date)
        m_cookiecutter.assert_called_once_with(
            os.fspath(Path(__file__).parent.parent / "cookiecutter"),
            no_input=True,
            output_dir=Path(run_desc["paths"]["runs directory"]),
            extra_context={
                "batch_directives": m_sbatch_dir(run_desc),
                "module_loads": "module load netcdf-fortran-mpi/4.4.4",
                "run_id": "SoGwaves",
                "runs_dir": Path(run_desc["paths"]["runs directory"]),
                "run_start_date_yyyymmdd": start_date.format("YYYYMMDD"),
                "run_end_date_yyyymmdd": start_date.shift(days=+1).format("YYYYMMDD"),
                "mod_def_ww3_path": Path(run_desc["grid"]["mod_def.ww3 file"]),
                "current_forcing_dir": Path(run_desc["forcing"]["current"]),
                "wind_forcing_dir": Path(run_desc["forcing"]["wind"]),
                "restart_path": Path(run_desc["restart"]["restart.ww3"]),
                "results_dir": m_rslv_results_dir(),
            },
        )

    def test_cookiecutter_no_restart(
        self,
        m_open,
        m_cookiecutter,
        m_sbatch_dir,
        m_rslv_results_dir,
        m_subproc_run,
        run_desc,
        tmp_path,
    ):
        results_dir = tmp_path / "results_dir"
        start_date = arrow.get("2019-10-07")
        with patch.dict(run_desc, {"restart": {"not restart.ww3": "whatever"}}):
            # **Must use open() here because Path.open() is patched**
            with open(tmp_path / "wwatch3.yaml", "wt") as f:
                yaml.safe_dump(run_desc, f)
            wwatch3_cmd.run.run(tmp_path / "wwatch3.yaml", results_dir, start_date)
        m_cookiecutter.assert_called_once_with(
            os.fspath(Path(__file__).parent.parent / "cookiecutter"),
            no_input=True,
            output_dir=Path(run_desc["paths"]["runs directory"]),
            extra_context={
                "batch_directives": m_sbatch_dir(run_desc),
                "module_loads": "module load netcdf-fortran-mpi/4.4.4",
                "run_id": "SoGwaves",
                "runs_dir": Path(run_desc["paths"]["runs directory"]),
                "run_start_date_yyyymmdd": start_date.format("YYYYMMDD"),
                "run_end_date_yyyymmdd": start_date.shift(days=+1).format("YYYYMMDD"),
                "mod_def_ww3_path": Path(run_desc["grid"]["mod_def.ww3 file"]),
                "current_forcing_dir": Path(run_desc["forcing"]["current"]),
                "wind_forcing_dir": Path(run_desc["forcing"]["wind"]),
                "restart_path": "",
                "results_dir": m_rslv_results_dir(),
            },
        )


class TestSbatchDirectives:
    """Unit tests for _sbatch_directives() function.
    """

    def test_sbatch_directives(self, run_desc, tmp_path):
        results_dir = tmp_path / "results_dir"
        sbatch_directives = wwatch3_cmd.run._sbatch_directives(run_desc, results_dir)
        expected = textwrap.dedent(
            f"""\
            #SBATCH --job-name={run_desc['run_id']}
            #SBATCH --mail-user=someone@eoas.ubc.ca
            #SBATCH --mail-type=ALL
            #SBATCH --account=def-allen
            #SBATCH --constraint=skylake
            #SBATCH --nodes=1
            #SBATCH --ntasks-per-node=48
            #SBATCH --mem=0
            #SBATCH --time=00:20:00
            # stdout and stderr file paths/names
            #SBATCH --output={results_dir/"stdout"}
            #SBATCH --error={results_dir/"stderr"}
            """
        )
        assert sbatch_directives == expected
