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
    gather         Gather results from a NEMO run. (NEMO-Cmd)
    help           print detailed help for another command (cliff)
    run            Prepare, execute, and gather results from a WaveWatch III® model run.

For details of the arguments and options for a sub-command use
:command:`wwatch3 help <sub-command>`.
For example:

.. code-block:: bash

    $ wwatch3 help run

::

    usage: wwatch3 run [-h] [--no-submit] [-q] [--run-date RUN_DATE]
                       DESC_FILE RESULTS_DIR

    Prepare, execute, and gather the results from a WaveWatch III® run described
    in DESC_FILE. The results files from the run are gathered in RESULTS_DIR. If
    RESULTS_DIR does not exist it will be created.

    positional arguments:
      DESC_FILE            run description YAML file
      RESULTS_DIR          directory to store results into

    optional arguments:
      -h, --help           show this help message and exit
      --no-submit          Prepare the temporary run directory, and the bash
                           script to
                           execute the WaveWatch III® run, but don't submit the
                           run to the queue.
                           This is useful during development runs when you want to
                           hack on
                           the bash script and/or use the same temporary run
                           directory
                           more than once.
      -q, --quiet          don't show the run directory path or job submission
                           message
      --run-date RUN_DATE  Date to execute the run for. Use YYYY-MM-DD format.
                           Defaults to 2019-10-07.

If a sub-command prints an error message,
you can get a Python traceback containing more information about the error by re-running the command with the :kbd:`--debug` flag.


.. _wwatch3-run:

:kbd:`run` Sub-command
======================

The :command:`run` sub-command prepares,
executes,
and gathers the results from the WaveWatch III® run described in the run description YAML file provided on the command-line.
The results are gathered in the results directory that is also provided on the command-line.

::

  usage: wwatch3 run [-h] [--no-submit] [-q] [--run-date RUN_DATE]
                     DESC_FILE RESULTS_DIR

  Prepare, execute, and gather the results from a WaveWatch III® run described
  in DESC_FILE. The results files from the run are gathered in RESULTS_DIR. If
  RESULTS_DIR does not exist it will be created.

  positional arguments:
    DESC_FILE            run description YAML file
    RESULTS_DIR          directory to store results into

  optional arguments:
    -h, --help           show this help message and exit
    --no-submit          Prepare the temporary run directory, and the bash
                         script to
                         execute the WaveWatch III® run, but don't submit the
                         run to the queue.
                         This is useful during development runs when you want to
                         hack on
                         the bash script and/or use the same temporary run
                         directory
                         more than once.
    -q, --quiet          don't show the run directory path or job submission
                         message
    --run-date RUN_DATE  Date to execute the run for. Use YYYY-MM-DD format.
                         Defaults to 2019-10-07.

If the :command:`run` sub-command prints an error message,
you can get a Python traceback containing more information about the error by re-running the command with the :kbd:`--debug` flag.


.. _wwatch3-gather:

:kbd:`gather` Sub-command
=========================

The :command:`gather` sub-command moves results from a WaveWatch III® run into a results directory.
It is provided by the `NEMO-Cmd`_ package.
Please use:

.. code-block:: bash

    $ wwatch3 help gather

to see its usage,
and see :ref:`nemocmd:nemo-gather` for more details.

.. _NEMO-Cmd: https://bitbucket.org/salishsea/nemo-cmd

If the :command:`gather` sub-command prints an error message,
you can get a Python traceback containing more information about the error by re-running the command with the :kbd:`--debug` flag.
