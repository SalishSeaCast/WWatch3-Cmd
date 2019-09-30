.. Copyright 2019, the MIDOSS project contributors, The University of British Columbia,
.. and Dalhousie University.
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..    https://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.


.. _WWatch3-CmdSubcommands:

*******************************
:command:`wwatch3` Sub-Commands
*******************************

The command :kbd:`wwatch3 help` produces a list of the available :program:`wwatch3` options and sub-commands::

  usage: wwatch3 [--version] [-v | -q] [--log-file LOG_FILE] [-h] [--debug]

  WaveWatch III® Command Processor

  optional arguments:
    --version            show program's version number and exit
    -v, --verbose        Increase verbosity of output. Can be repeated.
    -q, --quiet          Suppress output except warnings and errors.
    --log-file LOG_FILE  Specify a file to log output. Disabled by default.
    -h, --help           Show help message and exit.
    --debug              Show tracebacks on errors.

  Commands:
    complete       print bash completion command (cliff)
    help           print detailed help for another command (cliff)
    prepare        Set up the WaveWatch III® run described in DESC_FILE and print the path of the temporary run directory.


For details of the arguments and options for a sub-command use
:command:`wwatch3 help <sub-command>`.
For example:


.. code-block:: bash

    $ wwatch3 help prepare

::

    usage: wwatch3 prepare [-h] [-q] DESC_FILE

    Set up the WaveWatch III® run described in DESC_FILE and print the path of the
    temporary run directory.

    positional arguments:
      DESC_FILE    run description YAML file

    optional arguments:
      -h, --help   show this help message and exit
      -q, --quiet  don't show the run directory path on completion


.. _wwatch3-prepare:

:kbd:`prepare` Sub-command
==========================

The :command:`prepare` sub-command sets up a temporary run directory from which to execute the WaveWatch III® run described in the run description YAML file provided on the command-line::

  usage: wwatch3 prepare [-h] [-q] DESC_FILE

  Set up the WaveWatch III® run described in DESC_FILE and print the path of the
  temporary run directory.

  positional arguments:
    DESC_FILE    run description YAML file

  optional arguments:
    -h, --help   show this help message and exit
    -q, --quiet  don't show the run directory path on completion
