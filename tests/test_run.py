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
import textwrap
from types import SimpleNamespace
from unittest.mock import patch

import arrow
import attr
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

    @staticmethod
    @pytest.fixture
    def mock_run_submit_return(monkeypatch):
        def mock_run_return(*args, **kwargs):
            return "submit job msg"

        monkeypatch.setattr(wwatch3_cmd.run, "run", mock_run_return)

    def test_take_action(self, mock_run_submit_return, run_cmd, caplog):
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
        assert caplog.messages[0] == "submit job msg"

    def test_take_action_quiet(self, mock_run_submit_return, run_cmd, caplog):
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

    def test_take_action_no_submit(self, run_cmd, caplog, monkeypatch):
        def mock_run_no_submit_return(*args, **kwargs):
            return None

        parsed_args = SimpleNamespace(
            desc_file=Path("desc file"),
            results_dir=Path("results dir"),
            no_submit=True,
            quiet=False,
            start_date=arrow.get("2019-10-07"),
        )
        caplog.set_level(logging.INFO)
        monkeypatch.setattr(wwatch3_cmd.run, "run", mock_run_no_submit_return)
        run_cmd.take_action(parsed_args)
        assert not caplog.messages


@patch(
    "wwatch3_cmd.run.cookiecutter.main.cookiecutter",
    return_value="tmp_run_dir",
    autospec=True,
)
class TestRun:
    """Unit tests for `wwatch3 run` run() function.
    """

    @staticmethod
    @pytest.fixture
    def mock_subprocess_stdout(monkeypatch):
        @attr.s
        class MockCompletedProcess:
            stdout = attr.ib(default="submit_job_msg")

        def mock_completed_process_stdout(*args, **kwargs):
            return MockCompletedProcess()

        monkeypatch.setattr(
            wwatch3_cmd.run.subprocess, "run", mock_completed_process_stdout
        )

    @staticmethod
    @pytest.fixture
    def mock_load_run_desc_return(run_desc, monkeypatch):
        def mock_return(*args):
            return run_desc

        monkeypatch.setattr(
            wwatch3_cmd.run.nemo_cmd.prepare, "load_run_desc", mock_return
        )

    @staticmethod
    @pytest.fixture
    def mock_write_tmp_run_dir_run_desc(monkeypatch):
        def mock_write(*args):
            pass

        monkeypatch.setattr(wwatch3_cmd.run, "_write_tmp_run_dir_run_desc", mock_write)

    def test_no_submit(
        self,
        m_cookiecutter,
        mock_load_run_desc_return,
        mock_write_tmp_run_dir_run_desc,
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
        assert submit_job_msg is None

    def test_submit(
        self,
        m_cookiecutter,
        mock_load_run_desc_return,
        mock_write_tmp_run_dir_run_desc,
        mock_subprocess_stdout,
        run_desc,
        tmp_path,
    ):
        results_dir = tmp_path / "results_dir"
        submit_job_msg = wwatch3_cmd.run.run(
            tmp_path / "wwatch3.yaml", results_dir, start_date=arrow.get("2019-10-07")
        )
        assert submit_job_msg == "submit_job_msg"

    def test_cookiecutter(
        self,
        m_cookiecutter,
        mock_load_run_desc_return,
        mock_write_tmp_run_dir_run_desc,
        mock_subprocess_stdout,
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
                "batch_directives": wwatch3_cmd.run._sbatch_directives(
                    run_desc, results_dir
                ),
                "module_loads": "module load netcdf-fortran-mpi/4.4.4",
                "run_id": "SoGwaves",
                "runs_dir": Path(run_desc["paths"]["runs directory"]),
                "run_start_date_yyyymmdd": start_date.format("YYYYMMDD"),
                "run_end_date_yyyymmdd": start_date.shift(days=+1).format("YYYYMMDD"),
                "mod_def_ww3_path": Path(run_desc["grid"]["mod_def.ww3 file"]),
                "current_forcing_dir": Path(run_desc["forcing"]["current"]),
                "wind_forcing_dir": Path(run_desc["forcing"]["wind"]),
                "restart_path": Path(run_desc["restart"]["restart.ww3"]),
                "results_dir": results_dir,
            },
        )

    def test_cookiecutter_no_restart(
        self,
        m_cookiecutter,
        mock_write_tmp_run_dir_run_desc,
        mock_subprocess_stdout,
        run_desc,
        tmp_path,
        monkeypatch,
    ):
        def mock_load_run_desc_return(*args):
            monkeypatch.delitem(run_desc, "restart")
            return run_desc

        monkeypatch.setattr(
            wwatch3_cmd.run.nemo_cmd.prepare, "load_run_desc", mock_load_run_desc_return
        )

        results_dir = tmp_path / "results_dir"
        start_date = arrow.get("2019-10-07")
        wwatch3_cmd.run.run(tmp_path / "wwatch3.yaml", results_dir, start_date)
        m_cookiecutter.assert_called_once_with(
            os.fspath(Path(__file__).parent.parent / "cookiecutter"),
            no_input=True,
            output_dir=Path(run_desc["paths"]["runs directory"]),
            extra_context={
                "batch_directives": wwatch3_cmd.run._sbatch_directives(
                    run_desc, results_dir
                ),
                "module_loads": "module load netcdf-fortran-mpi/4.4.4",
                "run_id": "SoGwaves",
                "runs_dir": Path(run_desc["paths"]["runs directory"]),
                "run_start_date_yyyymmdd": start_date.format("YYYYMMDD"),
                "run_end_date_yyyymmdd": start_date.shift(days=+1).format("YYYYMMDD"),
                "mod_def_ww3_path": Path(run_desc["grid"]["mod_def.ww3 file"]),
                "current_forcing_dir": Path(run_desc["forcing"]["current"]),
                "wind_forcing_dir": Path(run_desc["forcing"]["wind"]),
                "restart_path": "",
                "results_dir": results_dir,
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
