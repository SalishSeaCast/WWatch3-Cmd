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
"""WWatch3-Cmd run sub-command plug-in unit and integration tests.
"""
import logging
import os
from pathlib import Path
import textwrap
from types import SimpleNamespace

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

    def test_walltime_argument(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        assert parser._actions[2].dest == "walltime"
        assert parser._actions[2].metavar == "WALLTIME"
        assert parser._actions[2].type == str
        assert parser._actions[2].help

    def test_results_dir_argument(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        assert parser._actions[3].dest == "results_dir"
        assert parser._actions[3].metavar == "RESULTS_DIR"
        assert parser._actions[3].type == Path
        assert parser._actions[3].help

    def test_no_submit_option(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        assert parser._actions[4].dest == "no_submit"
        assert parser._actions[4].option_strings == ["--no-submit"]
        assert parser._actions[4].const is True
        assert parser._actions[4].default is False
        assert parser._actions[4].help

    def test_quiet_option(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        assert parser._actions[5].dest == "quiet"
        assert parser._actions[5].option_strings == ["-q", "--quiet"]
        assert parser._actions[5].const is True
        assert parser._actions[5].default is False
        assert parser._actions[5].help

    def test_start_date_option(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        assert parser._actions[6].dest == "start_date"
        assert parser._actions[6].option_strings == ["--start-date"]
        assert parser._actions[6].type == wwatch3_cmd.run.Run._arrow_date
        assert parser._actions[6].default == arrow.now().floor("day")
        assert parser._actions[6].help

    def test_parsed_args_defaults(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        parsed_args = parser.parse_args(["foo.yaml", "00:20:00", "results/foo/"])
        assert parsed_args.desc_file == Path("foo.yaml")
        assert parsed_args.results_dir == Path("results/foo/")
        assert parsed_args.walltime == "00:20:00"
        assert not parsed_args.no_submit
        assert not parsed_args.quiet
        assert parsed_args.start_date == arrow.now().floor("day")

    @pytest.mark.parametrize("flag", ["-q", "--quiet"])
    def test_parsed_args_quiet_options(self, flag, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        parsed_args = parser.parse_args(["foo.yaml", "00:20:00", "results/foo/", flag])
        assert parsed_args.quiet is True

    def test_parsed_args_no_submit_option(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        parsed_args = parser.parse_args(
            ["foo.yaml", "00:20:00", "results/foo/", "--no-submit"]
        )
        assert parsed_args.no_submit is True

    def test_parsed_args_start_date_option(self, run_cmd):
        parser = run_cmd.get_parser("wwatch3 run")
        parsed_args = parser.parse_args(
            ["foo.yaml", "00:20:00", "results/foo/", "--start-date", "2019-10-09"]
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
            walltime="00:20:00",
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
            walltime="00:20:00",
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
            walltime="00:20:00",
            results_dir=Path("results dir"),
            no_submit=True,
            quiet=False,
            start_date=arrow.get("2019-10-07"),
        )
        caplog.set_level(logging.INFO)
        monkeypatch.setattr(wwatch3_cmd.run, "run", mock_run_no_submit_return)
        run_cmd.take_action(parsed_args)
        assert not caplog.messages


class TestRun:
    """Unit tests for `wwatch3 run` run() function.
    """

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
            walltime="00:20:00",
            no_submit=True,
        )
        assert submit_job_msg is None

    def test_submit(
        self,
        mock_load_run_desc_return,
        mock_write_tmp_run_dir_run_desc,
        mock_subprocess_stdout,
        run_desc,
        tmp_path,
    ):
        results_dir = tmp_path / "results_dir"
        submit_job_msg = wwatch3_cmd.run.run(
            tmp_path / "wwatch3.yaml",
            results_dir,
            start_date=arrow.get("2019-10-07"),
            walltime="00:20:00",
        )
        assert submit_job_msg == "submit_job_msg"


class TestSbatchDirectives:
    """Unit test for _sbatch_directives() function.
    """

    def test_sbatch_directives(self, run_desc, tmp_path):
        results_dir = tmp_path / "results_dir"
        sbatch_directives = wwatch3_cmd.run._sbatch_directives(
            run_desc, results_dir, "00:20:00"
        )
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


class TestTmpRunDir:
    """Integration tests for temporary run directory generated by `wwatch3 run` sub-command.
    """

    @staticmethod
    @pytest.fixture
    def tmp_run_dir(mock_subprocess_stdout, tmp_path, caplog):
        caplog.set_level(logging.INFO)
        results_dir = tmp_path / "results_dir"
        start_date = arrow.get("2019-10-13")
        wwatch3_cmd.run.run(
            tmp_path / "wwatch3.yaml", results_dir, start_date, "00:20:00"
        )
        tmp_run_dir = caplog.messages[0].split()[-1]
        return Path(tmp_run_dir)

    def test_tmp_run_dir_name(self, run_desc, tmp_run_dir):
        assert tmp_run_dir.name.startswith(
            f"{run_desc['run_id']}_{arrow.now().format('YYYY-MM-DD')}T"
        )

    def test_tmp_run_dir_files(self, run_desc, tmp_run_dir):
        template_dir = (
            Path(__file__).parent.parent
            / "cookiecutter"
            / "{{cookiecutter.tmp_run_dir}}"
        )
        template_files = {fp.name for fp in template_dir.iterdir()}
        tmp_run_dir_files = {
            fp.name
            for fp in tmp_run_dir.iterdir()
            if fp.is_file() and not fp.is_symlink()
        }
        assert tmp_run_dir_files.difference(template_files) == {"wwatch3.yaml"}

    def test_tmp_run_dir_symlinks(self, run_desc, tmp_run_dir):
        tmp_run_dir_links = {fp.name for fp in tmp_run_dir.iterdir() if fp.is_symlink()}
        assert tmp_run_dir_links == {"mod_def.ww3", "restart.ww3", "wind", "current"}

    def test_tmp_run_dir_symlinks_no_restart(
        self, run_desc, mock_subprocess_stdout, tmp_path, caplog, monkeypatch
    ):
        def mock_load_run_desc_return(*args):
            monkeypatch.delitem(run_desc, "restart")
            return run_desc

        monkeypatch.setattr(
            wwatch3_cmd.run.nemo_cmd.prepare, "load_run_desc", mock_load_run_desc_return
        )
        caplog.set_level(logging.INFO)
        results_dir = tmp_path / "results_dir"
        start_date = arrow.get("2019-10-13")
        wwatch3_cmd.run.run(
            tmp_path / "wwatch3.yaml", results_dir, start_date, "00:20:00"
        )
        tmp_run_dir = Path(caplog.messages[0].split()[-1])
        tmp_run_dir_links = {fp.name for fp in tmp_run_dir.iterdir() if fp.is_symlink()}
        assert tmp_run_dir_links == {"mod_def.ww3", "wind", "current"}

    def test_ww3_ounf_inp_file(self, run_desc, tmp_run_dir):
        run_start_date_yyyymmdd = arrow.get("2019-10-13").format("YYYYMMDD")
        expected = textwrap.dedent(
            f"""\
            $ WAVEWATCH III NETCDF Grid output post-processing
            $
            $ First output time (YYYYMMDD HHmmss), output increment (s), number of output times
              {run_start_date_yyyymmdd} 000000 1800 48
            $
            $ Fields
              N  by name
              HS LM WND CUR FP T02 DIR DP WCH WCC TWO FOC USS
            $
            $ netCDF4 output
            $ real numbers
            $ swell partitions
            $ one file
              4
              4
              0 1 2
              T
            $
            $ File prefix
            $ number of characters in date
            $ IX, IY range
            $
              SoG_ww3_fields_
              8
              1 1000000 1 1000000
            """
        )
        tmp_run_dir_lines = (tmp_run_dir / "ww3_ounf.inp").read_text().splitlines()
        assert tmp_run_dir_lines == expected.splitlines()

    def test_ww3_ounp_inp_file(self, run_desc, tmp_run_dir):
        run_start_date_yyyymmdd = arrow.get("2019-10-13").format("YYYYMMDD")
        expected = textwrap.dedent(
            f"""\
            $ WAVEWATCH III NETCDF Point output post-processing
            $
            $ First output time (YYYYMMDD HHmmss), output increment (s), number of output times
              {run_start_date_yyyymmdd} 000000 600 144
            $
            $ All points defined in ww3_shel.inp
              -1
            $ File prefix
            $ number of characters in date
            $ netCDF4 output
            $ one file, max number of points to process
            $ tables of mean parameters
            $ WW3 global attributes
            $ time,station dimension order
            $ WMO standard output
              SoG_ww3_points_
              8
              4
              T 100
              2
              0
              T
              6
            """
        )
        tmp_run_dir_lines = (tmp_run_dir / "ww3_ounp.inp").read_text().splitlines()
        assert tmp_run_dir_lines == expected.splitlines()

    def test_ww3_prnc_current_inp_file(self, run_desc, tmp_run_dir):
        run_start_date_yyyymmdd = arrow.get("2019-10-13").format("YYYYMMDD")
        expected = textwrap.dedent(
            f"""\
            $ WAVEWATCH III NETCDF Field preprocessor input ww3_prnc_current.inp
            $
            $ Forcing type, grid type, time in file, header
              'CUR' 'LL' T T
            $ Name of dimensions
            $
              x y
            $
            $ Sea water current component variable names
              u_current v_current
            $
            $ Forcing source file path/name
            $ File is produced by make_ww3_current_file worker
              'current/SoG_current_{run_start_date_yyyymmdd}.nc'
            """
        )
        tmp_run_dir_lines = (
            (tmp_run_dir / "ww3_prnc_current.inp").read_text().splitlines()
        )
        assert tmp_run_dir_lines == expected.splitlines()

    def test_ww3_prnc_wind_inp_file(self, run_desc, tmp_run_dir):
        run_start_date_yyyymmdd = arrow.get("2019-10-13").format("YYYYMMDD")
        expected = textwrap.dedent(
            f"""\
            $ WAVEWATCH III NETCDF Field preprocessor input ww3_prnc_wind.inp
            $
            $ Forcing type, grid type, time in file, header
               'WND' 'LL' T T
            $
            $ Dimension variable names
              x y
            $
            $ Wind component variable names
              u_wind v_wind
            $
            $ Forcing source file path/name
            $ File is produced by make_ww3_wind_file worker
              'wind/SoG_wind_{run_start_date_yyyymmdd}.nc'
            """
        )
        tmp_run_dir_lines = (tmp_run_dir / "ww3_prnc_wind.inp").read_text().splitlines()
        assert tmp_run_dir_lines == expected.splitlines()

    def test_ww3_shel_inp_file(self, run_desc, tmp_run_dir):
        run_start_date_yyyymmdd = arrow.get("2019-10-13").format("YYYYMMDD")
        run_end_date_yyyymmdd = (
            arrow.get("2019-10-13").shift(days=+1).format("YYYYMMDD")
        )
        expected = textwrap.dedent(
            f"""\
            $ WAVEWATCH III shell input file
            $
            $ Forcing/inputs to use
              F F  Water levels w/ homogeneous field data
              T F  Currents w/ homogeneous field data
              T F  Winds w/ homogeneous field data
              F    Ice concentration
              F    Assimilation data : Mean parameters
              F    Assimilation data : 1-D spectra
              F    Assimilation data : 2-D spectra.
            $
               {run_start_date_yyyymmdd} 000000  Start time (YYYYMMDD HHmmss)
               {run_end_date_yyyymmdd} 000000  End time (YYYYMMDD HHmmss)
            $
            $ Output server mode
              2  dedicated process
            $
            $ Field outputs
            $ Start time (YYYYMMDD HHmmss), Interval (s), End time (YYYYMMDD HHmmss)
              {run_start_date_yyyymmdd} 000000 1800 {run_end_date_yyyymmdd} 000000
            $ Fields
              N  by name
              HS LM WND CUR FP T02 DIR DP WCH WCC TWO FOC USS
            $
            $ Point outputs (required placeholder for unused feature)
            $ Start time (YYYYMMDD HHmmss), Interval (s), End time (YYYYMMDD HHmmss)
              {run_start_date_yyyymmdd} 000000 0 {run_end_date_yyyymmdd} 000000
            $
            $ Along-track output (required placeholder for unused feature)
            $ Start time (YYYYMMDD HHmmss), Interval (s), End time (YYYYMMDD HHmmss)
              {run_start_date_yyyymmdd} 000000 0 {run_end_date_yyyymmdd} 000000
            $
            $ Restart files
            $ Start time (YYYYMMDD HHmmss), Interval (s), End time (YYYYMMDD HHmmss)
              {run_end_date_yyyymmdd} 000000 3600 {run_end_date_yyyymmdd} 000000
            $
            $ Boundary data (required placeholder for unused feature)
            $ Start time (YYYYMMDD HHmmss), Interval (s), End time (YYYYMMDD HHmmss)
              {run_start_date_yyyymmdd} 000000 0 {run_end_date_yyyymmdd} 000000
            $
            $ Separated wave field data (required placeholder for unused feature)
            $ Start time (YYYYMMDD HHmmss), Interval (s), End time (YYYYMMDD HHmmss)
              {run_start_date_yyyymmdd} 000000 0 {run_end_date_yyyymmdd} 000000
            $
            $ Homogeneous field data (required placeholder for unused feature)
              ’STP’
            """
        )
        tmp_run_dir_lines = (tmp_run_dir / "ww3_shel.inp").read_text().splitlines()
        assert tmp_run_dir_lines == expected.splitlines()

    def test_SoGWW3_sh_file(self, run_desc, tmp_run_dir, tmp_path):
        run_start_date_yyyymmdd = arrow.get("2019-10-13").format("YYYYMMDD")
        expected = textwrap.dedent(
            f"""\
            #!/bin/bash
            
            {wwatch3_cmd.run._sbatch_directives(run_desc, tmp_path / "results_dir", "00:20:00")}
            set -e  # abort on first error
            set -u  # abort if undefinded variable is encountered
            
            module load netcdf-fortran-mpi/4.4.4
            
            RUN_ID="{run_desc['run_id']}"
            WORK_DIR="{tmp_run_dir}"
            RESULTS_DIR="{tmp_path/'results_dir'}"
            WW3_EXE="$PROJECT/$USER/MIDOSS/wwatch3-5.16/exe"
            MPIRUN="mpirun"
            GATHER="$HOME/.local/bin/wwatch3 gather"
            
            mkdir -p ${{RESULTS_DIR}}
            
            cd ${{WORK_DIR}}
            echo "working dir: $(pwd)"
            
            echo "Starting wind.nc file creation at $(date)"
            ln -s ww3_prnc_wind.inp ww3_prnc.inp && \\
            ${{WW3_EXE}}/ww3_prnc && \\
            rm -f ww3_prnc.inp
            echo "Ending wind.nc file creation at $(date)"
            
            echo "Starting current.nc file creation at $(date)"
            ln -s ww3_prnc_current.inp ww3_prnc.inp && \\
            ${{WW3_EXE}}/ww3_prnc && \\
            rm -f ww3_prnc.inp
            echo "Ending current.nc file creation at $(date)"
            
            echo "Starting run at $(date)"
            ${{MPIRUN}} -np 48 ${{WW3_EXE}}/ww3_shel && \\
            mv log.ww3 ww3_shel.log && \\
            rm current.ww3 wind.ww3 && \\
            echo "Ended run at $(date)"
            
            echo "Starting netCDF4 fields output at $(date)"
            ${{WW3_EXE}}/ww3_ounf && \\
            mv SoG_ww3_fields_{run_start_date_yyyymmdd}.nc \\
              SoG_ww3_fields_{run_start_date_yyyymmdd}_{run_start_date_yyyymmdd}.nc && \\
            rm out_grd.ww3
            echo "Ending netCDF4 fields output at $(date)"
            
            echo "Results gathering started at $(date)"
            ${{GATHER}} ${{RESULTS_DIR}} --debug
            echo "Results gathering ended at $(date)"
            
            echo "Deleting run directory"
            rmdir $(pwd)
            echo "Finished at $(date)"
            """
        )
        tmp_run_dir_lines = [
            line.strip()
            for line in (tmp_run_dir / "SoGWW3.sh").read_text().splitlines()
        ]
        assert tmp_run_dir_lines == [line.strip() for line in expected.splitlines()]

    def test_ww3_grid_inp_file(self, run_desc, tmp_run_dir):
        expected = textwrap.dedent(
            """\
            $ WAVEWATCH III Grid preprocessor input file
            $ ------------------------------------------
            $  Grid name (C*30, in quotes)
              'SoG_BCgrid_00500m             '
            $
            $         '
            $ Frequency increment factor and first frequency (Hz) number of frequencies (wavenumbers) and directions,
            $ relative offset of first direction in terms of the directional increment [-0.5,0.5].
            $ In versions 1.18 and 2.22 of the model this value was by definiton 0,
            $ it is added to mitigate the GSE for a first order scheme.
            $ Note that this factor is IGNORED in the print plots in ww3_outp.
            $   1.1  0.04  25  24  0.
               1.1  0.06665  25  24  0.
            $  1.1  0.04665  15  24  0.
            $  1.1  0.04665  15  24  0.5
            $
            $ Set model flags
            $ - FLDRY:  Dry run (input/output only, no calculation).
            $ - FLCX, FLCY: Activate X and Y component of propagation.
            $ - FLCTH, FLCK: Activate direction and wavenumber shifts.
            $ - FLSOU:  Activate source terms.
            $$   F T T T T T
            $$$    F F F F F T
                 F T T T T T
            $
            $ Set time steps
            $ - Time step information (this information is always read)
            $ maximum global time step, maximum CFL time step for x-y and
            $ k-theta, minimum source term time step (all in seconds).
            $
            $  3600.  1300.  1300.  25.
              200.  50.  100.  10.
            $$
            $
            $ Start of namelist input section ------------------------------------ $
            $ Starting with WAVEWATCH III version 2.00, the tunable parameters
            $ for source terms, propagation schemes, and numerics are read using
            $ namelists. Any namelist found in the folowing sections up to the
            $ end-of-section identifier string (see below) is temporarily written
            $ to ww3_grid.scratch, and read from there if necessary. Namelists
            $ not needed for the given switch settings will be skipped
            $ automatically, and the order of the namelists is immaterial.
            $  see manual section 4.2 for options (many!)
            $ Activated up to one line per namelist !!
            $
            $  &PRO2 DTIME= 0. /
            $ &PRO2 DTIME=172800. /
            $ &PRO2 DTIME=345600. /
            $ &PRO3 WDTHTH=0.00, WDTHCG=0.00 /
            $ &PRO3 WDTHTH=0.75, WDTHCG=0.75 /
            $ &PRO3 WDTHTH=1.50, WDTHCG=1.50 /
            $ &PRO3 WDTHTH=2.00, WDTHCG=2.00 /
            $ &PRO3 WDTHTH=0.00, WDTHCG=2.00 /
            $ &PRO3 WDTHTH=2.00, WDTHCG=0.00 /
            $
            $
            $ Mandatory string to identify end of namelist input section.
            $
            END OF NAMELISTS
            $
            $ Define grid -------------------------------------------------------- $
            $
            $ Five records containing :
            $
            $ 1 Type of grid, coordinate system and type of closure: GSTRG, FLAGLL,
            $ CSTRG. Grid closure can only be applied in spherical coordinates.
            $ GSTRG : String indicating type of grid :
            $ ’RECT’ : rectilinear
            $ ’CURV’ : curvilinear
            $ FLAGLL : Flag to indicate coordinate system :
            $ T : Spherical (lon/lat in degrees)
            $ F : Cartesian (meters)
            $ CSTRG : String indicating the type of grid index space closure :
            $ ’NONE’ : No closure is applied
            $ ’SMPL’ : Simple grid closure : Grid is periodic in the
            $ : i-index and wraps at i=NX+1. In other words,
            $ : (NX+1,J) => (1,J). A grid with simple closure
            $ : may be rectilinear or curvilinear.
            $ ’TRPL’ : Tripole grid closure : Grid is periodic in the
            $ : i-index and wraps at i=NX+1 and has closure at
            $ : j=NY+1. In other words, (NX+1,J<=NY) => (1,J)
            $ : and (I,NY+1) => (MOD(NX-I+1,NX)+1,NY). Tripole
            $ : grid closure requires that NX be even. A grid
            $ : with tripole closure must be curvilinear.
            $
            $ 2 NX, NY. As the outer grid lines are always defined as land
            $ points, the minimum size is 3x3.
            $
            $ Branch here based on grid type:
            $
            $ IF ( RECTILINEAR GRID ) THEN
            $
            $ 3 Grid increments SX, SY (degr.or m) and scaling (division) factor.
            $ If CSTRG=’SMPL’, then SX is set to 360/NX.
            $
            $ 4 Coordinates of (1,1) (degr.) and scaling (division) factor.
            $
            $ ELSE IF ( CURVILINEAR GRID ) THEN
            $  (see manual for settings for non-rctiliniar grids)
            $  (here we assume a rectiliniar grid)
            $
            $ END IF ( GRID TYPE )
            $
            $ 5 Limiting bottom depth (m) to discriminate between land and sea
            $ points, minimum water depth (m) as allowed in model, unit number
            $ of file with bottom depths, scale factor for bottom depths (mult.),
            $ IDLA, IDFM, format for formatted read, FROM and filename.
            $ IDLA : Layout indicator :
            $ 1 : Read line-by-line bottom to top.
            $ 2 : Like 1, single read statement.
            $ 3 : Read line-by-line top to bottom.
            $ 4 : Like 3, single read statement.
            $ IDFM : format indicator :
            $ 1 : Free format.
            $ 2 : Fixed format with above format descriptor.
            $ 3 : Unformatted.
            $
              'RECT' T 'NONE'
              572      661
              0.42     0.27   60.00
              234.0000          48.0000         1.00
              -0.10   2.50  20  0.001000  1  1 '(....)'  NAME  'grid/SoG_BCgrid_00500m.bot'
            $
            $ Sub-grid information
            $$   30  0.010000  1  1  '(....)'  NAME  'grid/SoG_BCgrid_00500m.obs'
               40  1  1  '(....)'  NAME  'grid/SoG_BCgrid_00500m.msk'
            $
            $
            $
            $$   0  0  F
            $$   0  0  F
            $$   0  0
            $
            $  Close list by defining line with 0 points (mandatory)
               0. 0. 0. 0.  0
            $ -------------------------------------------------------------------- $
            $ End of input file
            $
            $ -------------------------------------------------------------------- $
            """
        )
        tmp_run_dir_lines = (tmp_run_dir / "ww3_grid.inp").read_text().splitlines()
        assert tmp_run_dir_lines == expected.splitlines()
