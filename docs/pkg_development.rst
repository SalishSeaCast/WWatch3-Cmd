.. Copyright 2019-2021, the MIDOSS project contributors, The University of British Columbia,
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


.. _WWatch3-CmdPackagedDevelopment:

**********************************************************
:kbd:`wwatch3_cmd` Package Development
**********************************************************


.. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Licensed under the Apache License, Version 2.0
.. image:: https://img.shields.io/badge/python-3.6+-blue.svg
    :target: https://docs.python.org/3.7/
    :alt: Python Version
.. image:: https://img.shields.io/badge/version%20control-git-blue.svg?logo=github
    :target: https://github.com/MIDOSS/WWatch3-Cmd
    :alt: Git on GitHub
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://black.readthedocs.io/en/stable/
    :alt: The uncompromising Python code formatter
.. image:: https://readthedocs.org/projects/wwatch3-cmd/badge/?version=latest
    :target: https://wwatch3-cmd.readthedocs.io/en/latest/
    :alt: Documentation Status
.. image:: https://github.com/MIDOSS/WWatch3-Cmd/workflows/CI/badge.svg
    :target: https://github.com/MIDOSS/WWatch3-Cmd/actions?query=workflow%3ACI
    :alt: GitHub Workflow Status
.. image:: https://codecov.io/gh/MIDOSS/WWatch3-Cmd/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/MIDOSS/WWatch3-Cmd
    :alt: Codecov Testing Coverage Report
.. image:: https://img.shields.io/github/issues/MIDOSS/WWatch3-Cmd?logo=github
    :target: https://github.com/MIDOSS/WWatch3-Cmd/issues
    :alt: Issue Tracker

The WaveWatch III® command processor package, ``WWatch3-Cmd``, provides the ``wwatch3``
command-line tool for doing various operations associated with the Strait of Georgia
configuration of the WAVEWATCH III® model as it is used in the context of the `MIDOSS project`_.

.. _MIDOSS project: https://midoss-docs.readthedocs.io/en/latest/

.. _WWatch3-CmdPythonVersions:

Python Versions
===============

.. image:: https://img.shields.io/badge/python-3.6+-blue.svg
    :target: https://docs.python.org/3.7/
    :alt: Python Version

The :kbd:`wwatch3_cmd` package is developed and tested using `Python`_ 3.7 or later.
The package uses some Python language features that are not available in versions prior to 3.6,
in particular:

* `formatted string literals`_
  (aka *f-strings*)
* the `file system path protocol`_

.. _Python: https://www.python.org/
.. _formatted string literals: https://docs.python.org/3/reference/lexical_analysis.html#f-strings
.. _file system path protocol: https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-pep519


.. _WWatch3-CmdGettingTheCode:

Getting the Code
================

.. image:: https://img.shields.io/badge/version%20control-git-blue.svg?logo=github
    :target: https://github.com/MIDOSS/WWatch3-Cmd
    :alt: Git on GitHub

Clone the code and documentation `repository`_ from GitHub with:

.. _repository: https://github.com/MIDOSS/WWatch3-Cmd

.. code-block:: bash

    $ git clone git@github.com:MIDOSS/WWatch3-Cmd.git

or copy the URI
(the stuff after :kbd:`git clone` above)
from the :guilabel:`Code` button on the `repository`_ page.

.. note::

    The :kbd:`git clone` command above assumes that your are `connecting to GitHub using SSH`_.
    If it fails,
    please follow the instructions in our :ref:`SecureRemoteAccess` docs to set up your SSH keys and :ref:`CopyYourPublicSshKeyToGitHub`.

    .. _connecting to GitHub using SSH: https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh


.. _WWatch3-CmdDevelopmentEnvironment:

Development Environment
=======================

The :kbd:`WWatch3-Cmd` package depends on the :kbd:`NEMO-Cmd` package,
so you need to clone the `NEMO-Cmd repo`_
beside your clone of the :kbd:`WWatch3-Cmd` `repository`_.

.. _NEMO-Cmd repo: https://bitbucket.org/salishsea/nemo-cmd

Setting up an isolated development environment using `Conda`_ is recommended.
Assuming that you have `Miniconda3`_ installed,
you can create and activate an environment called :kbd:`wwatch3-cmd` that will have all of the Python packages necessary for development,
testing,
and building the documentation with the commands below.

.. _Conda: https://conda.io/en/latest/
.. _Miniconda3:  https://docs.conda.io/en/latest/miniconda.html

.. code-block:: bash

    $ cd MIDOSS
    $ conda env create -f WWatch3-Cmd/envs/environment-dev.yaml
    $ conda activate wwatch3-cmd
    (wwatch3-cmd)$ python3 -m pip install --editable NEMO-Cmd/
    (wwatch3-cmd)$ python3 -m pip install --editable WWatch3-Cmd/

The :kbd:`--editable` option in the :command:`pip install` command above installs the packages from the cloned repos via symlinks so that the installed packages will be automatically updated as the repos evolve.

To deactivate the environment use:

.. code-block:: bash

    (wwatch3-cmd)$ conda deactivate


.. _WWatch3-CmdCodingStyle:

Coding Style
============

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://black.readthedocs.io/en/stable/
    :alt: The uncompromising Python code formatter

The :kbd:`WWatch3-Cmd` package uses the `black`_ code formatting tool to maintain a coding style that is very close to `PEP 8`_.

.. _black: https://black.readthedocs.io/en/stable/
.. _PEP 8: https://www.python.org/dev/peps/pep-0008/

:command:`black` is installed as part of the :ref:`WWatch3-CmdDevelopmentEnvironment` setup.

To run :command:`black` on the entire code-base use:

.. code-block:: bash

    $ cd WWatch3-Cmd
    $ conda activate wwatch3_cmd
    (wwatch3-cmd)$ black ./

in the repository root directory.
The output looks something like::

  reformatted /media/doug/warehouse/MIDOSS/WWatch3-Cmd/docs/conf.py
  All done! ✨ 🍰 ✨
  1 file reformatted, 3 files left unchanged.


.. _WWatch3-CmdBuildingTheDocumentation:

Building the Documentation
==========================

.. image:: https://readthedocs.org/projects/wwatch3-cmd/badge/?version=latest
    :target: https://wwatch3-cmd.readthedocs.io/en/latest/
    :alt: Documentation Status

The documentation for the :kbd:`WWatch3-Cmd` package is written in `reStructuredText`_ and converted to HTML using `Sphinx`_.

.. _reStructuredText: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _Sphinx: http://www.sphinx-doc.org/en/master/

If you have write access to the `repository`_ on GitHub,
whenever you push changes to GitHub the documentation is automatically re-built and rendered at https://wwatch3-cmd.readthedocs.io/en/latest/.

Additions,
improvements,
and corrections to these docs are *always* welcome.

The quickest way to fix typos, etc. on existing pages is to use the :guilabel:`Edit on GitHub` link in the upper right corner of the page to get to the online editor for the page on `GitHub`_.

.. _GitHub: https://github.com/MIDOSS/WWatch3-Cmd

For more substantial work,
and to add new pages,
follow the instructions in the :ref:`WWatch3-CmdDevelopmentEnvironment` section above.
In the development environment you can build the docs locally instead of having to push commits to GitHub to trigger a `build on readthedocs.org`_ and wait for it to complete.
Below are instructions that explain how to:

.. _build on readthedocs.org: https://readthedocs.org/projects/wwatch3-cmd/builds/

* build the docs with your changes,
  and preview them in Firefox

* check the docs for broken links


.. _WWatch3-CmdBuildingAndPreviewingTheDocumentation:

Building and Previewing the Documentation
-----------------------------------------

Building the documentation is driven by the :file:`docs/Makefile`.
With your :kbd:`wwatch3-cmd` environment activated,
use:

.. code-block:: bash

    (wwatch3-cmd)$ (cd docs && make clean html)

to do a clean build of the documentation.
The output looks something like::

  Removing everything under '_build'...
  Running Sphinx v2.2.0
  making output directory... done
  building [mo]: targets for 0 po files that are out of date
  building [html]: targets for 5 source files that are out of date
  updating environment: [new config] 5 added, 0 changed, 0 removed
  reading sources... [100%] subcommands
  looking for now-outdated files... none found
  pickling environment... done
  checking consistency... done
  preparing documents... done
  writing output... [100%] subcommands
  generating indices...  genindexdone
  writing additional pages...
  done
  copying static files... ... done
  copying extra files... done
  dumping search index in English (code: en)... done
  dumping object inventory... done
  build succeeded.

  The HTML pages are in _build/html.

The HTML rendering of the docs ends up in :file:`docs/_build/html/`.
You can open the :file:`index.html` file in that directory tree in your browser to preview the results of the build.

If you have write access to the `repository`_ on GitHub,
whenever you push changes to Bitbucket the documentation is automatically re-built and rendered at https://wwatch3-cmd.readthedocs.io/en/latest/.


.. _WWatch3-CmdLinkCheckingTheDocumentation:

Link Checking the Documentation
-------------------------------

Sphinx also provides a link checker utility which can be run to find broken or redirected links in the docs.
With your :kbd:`wwatch3-cmd)` environment activated,
use:

.. code-block:: bash

    (wwatch3-cmd))$ cd WWatch3-Cmd)/docs/
    (wwatch3-cmd)) docs$ make linkcheck

The output looks something like::

  loading pickled environment... done
  building [mo]: targets for 0 po files that are out of date
  building [linkcheck]: targets for 5 source files that are out of date
  updating environment: 0 added, 1 changed, 0 removed
  reading sources... [100%] run_description_file/index
  looking for now-outdated files... none found
  pickling environment... done
  checking consistency... done
  preparing documents... done
  writing output... [ 20%] index
  (line   27) ok        https://docs.openstack.org/cliff/latest/
  (line   55) ok        https://img.shields.io/badge/license-Apache%202-cb2533.svg
  (line   21) ok        https://midoss-docs.readthedocs.io/en/latest/
  (line   27) ok        https://bitbucket.org/salishsea/nemo-cmd
  (line   55) ok        https://www.apache.org/licenses/LICENSE-2.0
  (line   65) ok        https://www.apache.org/licenses/LICENSE-2.0
  writing output... [ 40%] pkg_development
  (line   21) ok        https://docs.python.org/3.7/
  (line   58) ok        https://www.python.org/
  (line   62) ok        https://docs.python.org/3/reference/lexical_analysis.html#f-strings
  (line   21) ok        https://bitbucket.org/midoss/wwatch3-cmd/
  (line   21) ok        https://black.readthedocs.io/en/stable/
  (line   64) ok        https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-pep519
  (line   94) ok        https://confluence.atlassian.com/bitbucket/set-up-an-ssh-key-728138079.html
  (line  148) ok        https://www.python.org/dev/peps/pep-0008/
  (line  180) ok        http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
  (line   21) ok        https://bitbucket.org/midoss/wwatch3-cmd/issues?status=new&status=open
  (line  112) ok        https://conda.io/en/latest/
  (line  180) ok        http://www.sphinx-doc.org/en/master/
  (line  294) ok        https://docs.pytest.org/en/latest/
  (line  317) ok        https://coverage.readthedocs.io/en/latest/
  (line  112) ok        https://docs.conda.io/en/latest/miniconda.html
  (line   21) ok        https://img.shields.io/badge/python-3.6+-blue.svg
  (line   21) ok        https://img.shields.io/badge/version%20control-hg-blue.svg
  (line   21) ok        https://img.shields.io/badge/code%20style-black-000000.svg
  (line   21) ok        https://img.shields.io/bitbucket/issues/midoss/wwatch3-cmd.svg
  (line  174) ok        https://readthedocs.org/projects/wwatch3-cmd/badge/?version=latest
  (line   21) ok        https://readthedocs.org/projects/wwatch3-cmd/badge/?version=latest
  (line  351) ok        https://www.mercurial-scm.org/
  (line  365) ok        https://bitbucket.org/midoss/wwatch3-cmd/issues
  writing output... [ 60%] run_description_file/index
  (line   23) ok        https://pyyaml.org/wiki/PyYAMLDocumentation
  writing output... [ 80%] run_description_file/yaml_file
  writing output... [100%] subcommands

  build finished.

Look for any errors in the above output or in _build/linkcheck/output.txt


.. _WWatch3-CmdRunningTheUnitTests:

Running the Unit Tests
======================

The test suite for the :kbd:`WWatch3-Cmd` package is in :file:`WWatch3-Cmd/tests/`.
The `pytest`_ tool is used for test parametrization and as the test runner for the suite.

.. _pytest: https://docs.pytest.org/en/latest/

With your :kbd:`wwatch3-cmd` development environment activated,
use:

.. code-block:: bash

    (wwatch3-cmd)$ cd WWatch3-Cmd/
    (wwatch3-cmd)$ py.test

to run the test suite.
The output looks something like::

  =========================== test session starts ===========================
  platform linux -- Python 3.7.3, pytest-5.1.2, py-1.8.0, pluggy-0.13.0
  rootdir: /media/doug/warehouse/MIDOSS/WWatch3-Cmd
  collected 10 items

  tests/test_prepare.py ..........                                     [100%]

  ============================ 10 passed in 0.17s ============================

You can monitor what lines of code the test suite exercises using the `coverage.py`_ and `pytest-cov`_ tools with the command:

.. _coverage.py: https://coverage.readthedocs.io/en/latest/
.. _pytest-cov: https://pytest-cov.readthedocs.io/en/latest/

.. code-block:: bash

    (wwatch3-cmd)$ cd WWatch3-Cmd/
    (wwatch3-cmd)$ pytest --cov=./

The test coverage report will be displayed below the test suite run output.

Alternatively,
you can use

.. code-block:: bash

    (wwatch3-cmd)$ pytest --cov=./ --cov-report html

to produce an HTML report that you can view in your browser by opening :file:`WWatch3-Cmd/htmlcov/index.html`.


.. _WWatch3-CmdContinuousIntegration:

Continuous Integration
----------------------

.. image:: https://github.com/MIDOSS/WWatch3-Cmd/workflows/CI/badge.svg
    :target: https://github.com/MIDOSS/WWatch3-Cmd/actions?query=workflow%3ACI
    :alt: GitHub Workflow Status
.. image:: https://codecov.io/gh/MIDOSS/WWatch3-Cmd/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/MIDOSS/WWatch3-Cmd
    :alt: Codecov Testing Coverage Report

The :kbd:`WWatch3-Cmd` package unit test suite is run and a coverage report is generated whenever changes are pushed to GitHub.
The results are visible on the `repo actions page`_,
from the green checkmarks beside commits on the `repo commits page`_,
or from the green checkmark to the left of the "Latest commit" message on the `repo code overview page`_ .
The testing coverage report is uploaded to `codecov.io`_

.. _repo actions page: https://github.com/MIDOSS/WWatch3-Cmd/actions
.. _repo commits page: https://github.com/MIDOSS/WWatch3-Cmd/commits/master
.. _repo code overview page: https://github.com/MIDOSS/WWatch3-Cmd
.. _codecov.io: https://codecov.io/gh/MIDOSS/WWatch3-Cmd

The `GitHub Actions`_ workflow configuration that defines the continuous integration tasks is in the :file:`.github/workflows/pytest-coverage.yaml` file.

.. _GitHub Actions: https://help.github.com/en/actions


.. _WWatch3-CmdVersionControlRepository:

Version Control Repository
==========================

.. image:: https://img.shields.io/badge/version%20control-git-blue.svg?logo=github
    :target: https://github.com/MIDOSS/WWatch3-Cmd
    :alt: Git on GitHub

The :kbd:`WWatch3-Cmd` package code and documentation source files are available as a `Git`_ repository at https://github.com/MIDOSS/WWatch3-Cmd.

.. _Git: https://git-scm.com/


.. _WWatch3-CmdIssueTracker:

Issue Tracker
=============

.. image:: https://img.shields.io/github/issues/MIDOSS/WWatch3-Cmd?logo=github
    :target: https://github.com/MIDOSS/WWatch3-Cmd/issues
    :alt: Issue Tracker

Development tasks,
bug reports,
and enhancement ideas are recorded and managed in the issue tracker at https://github.com/MIDOSS/WWatch3-Cmd/issues.


License
=======

.. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Licensed under the Apache License, Version 2.0

The code and documentation of the WaveWatch III® Command Processor project
are copyright 2019-2021 by the `MIDOSS project contributors`_, The University of British Columbia,
and Dalhousie University.

.. _MIDOSS project contributors: https://github.com/MIDOSS/docs/blob/master/CONTRIBUTORS.rst

They are licensed under the Apache License, Version 2.0.
https://www.apache.org/licenses/LICENSE-2.0
Please see the LICENSE file for details of the license.
