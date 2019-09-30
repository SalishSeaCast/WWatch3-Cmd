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
"""WWatch3-Cmd prepare sub-command plug-in unit tests
"""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

import wwatch3_cmd.prepare


@pytest.fixture
def prepare_cmd():
    return wwatch3_cmd.prepare.Prepare(Mock(spec=True), [])


class TestParser:
    """Unit tests for `wwatch3 prepare` sub-command command-line parser.
    """

    def test_get_parser(self, prepare_cmd):
        parser = prepare_cmd.get_parser("wwatch3 prepare")
        assert parser.prog == "wwatch3 prepare"

    def test_cmd_description(self, prepare_cmd):
        parser = prepare_cmd.get_parser("wwatch3 prepare")
        assert parser.description.startswith(
            "Set up the WaveWatch III® run described in DESC_FILE"
        )

    def test_desc_file_argument(self, prepare_cmd):
        parser = prepare_cmd.get_parser("wwatch3 prepare")
        assert parser._actions[1].dest == "desc_file"
        assert parser._actions[1].metavar == "DESC_FILE"
        assert parser._actions[1].type == Path
        assert parser._actions[1].help

    def test_quiet_argument(self, prepare_cmd):
        parser = prepare_cmd.get_parser("wwatch3 prepare")
        assert parser._actions[2].dest == "quiet"
        assert parser._actions[2].option_strings == ["-q", "--quiet"]
        assert parser._actions[2].const is True
        assert parser._actions[2].default is False
        assert parser._actions[2].help

    def test_parsed_args_defaults(self, prepare_cmd):
        parser = prepare_cmd.get_parser("wwatch3 prepare")
        parsed_args = parser.parse_args(["foo.yaml"])
        assert parsed_args.desc_file == Path("foo.yaml")
        assert not parsed_args.quiet

    @pytest.mark.parametrize("flag", ["-q", "--quiet"])
    def test_parsed_args_options(self, flag, prepare_cmd):
        parser = prepare_cmd.get_parser("wwatch3 prepare")
        parsed_args = parser.parse_args(["foo.yaml", flag])
        assert parsed_args.quiet is True


@patch("wwatch3_cmd.prepare.logger", autospec=True)
@patch(
    "wwatch3_cmd.prepare.prepare",
    return_value=Path("SoGwaves28sep19_2019-09-28T131343.123456-0800"),
    autospec=True,
)
class TestTakeAction:
    """Unit tests for `wwatch3 prepare` sub-command take_action() method.
    """

    def test_return_tmp_run_dir(self, m_prepare, m_logger, prepare_cmd):
        parsed_args = SimpleNamespace(desc_file="foo.yaml", quiet=False)
        tmp_run_dir = prepare_cmd.take_action(parsed_args)
        m_logger.info.assert_called_once_with(
            "Created temporary run directory: SoGwaves28sep19_2019-09-28T131343.123456-0800"
        )
        assert tmp_run_dir == Path("SoGwaves28sep19_2019-09-28T131343.123456-0800")

    def test_quiet(self, m_prepare, m_logger, prepare_cmd):
        parsed_args = SimpleNamespace(desc_file="foo.yaml", quiet=True)
        prepare_cmd.take_action(parsed_args)
        assert not m_logger.info.called


@patch("wwatch3_cmd.prepare.nemo_cmd.prepare.load_run_desc", autospec=True)
@patch(
    "wwatch3_cmd.prepare.nemo_cmd.prepare.get_run_desc_value",
    autospec=True,
    side_effect=("SoGwaves", "$SCRATCH/MIDOSS/wwatch3-runs/"),
)
@patch("wwatch3_cmd.prepare.cookiecutter.main.cookiecutter", spec=True)
class TestPrepare:
    """Unit tests for `wwatch3 prepare` prepare() function.
    """

    def test_prepare(self, m_cookiecutter, m_get_run_desc_val, m_ld_run_desc):
        tmp_run_dir = wwatch3_cmd.prepare.prepare(Path("foo.yaml"))
        m_ld_run_desc.assert_called_once_with(Path("foo.yaml"))
        assert tmp_run_dir == m_cookiecutter()
