********************************
WaveWatch III® Command Processor
********************************

.. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Licensed under the Apache License, Version 2.0
.. image:: https://img.shields.io/badge/python-3.6+-blue.svg
    :target: https://docs.python.org/3.7/
    :alt: Python Version
.. image:: https://img.shields.io/badge/version%20control-hg-blue.svg
    :target: https://bitbucket.org/midoss/wwatch3-cmd/
    :alt: Mercurial on Bitbucket
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://black.readthedocs.io/en/stable/
    :alt: The uncompromising Python code formatter
.. image:: https://readthedocs.org/projects/wwatch3-cmd/badge/?version=latest
    :target: https://wwatch3-cmd.readthedocs.io/en/latest/
    :alt: Documentation Status
.. image:: https://img.shields.io/bitbucket/issues/midoss/wwatch3-cmd.svg
    :target: https://bitbucket.org/midoss/wwatch3-cmd/issues?status=new&status=open
    :alt: Issue Tracker

The WaveWatch III® command processor package, ``WWatch3-Cmd``, provides the ``wwatch3``
command-line tool for doing various operations associated with the Strait of Georgia
configuration of the WAVEWATCH III® model as it is used in the context of the `MIDOSS project`_.

.. _MIDOSS project: https://midoss-docs.readthedocs.io/en/latest/

Use ``wwatch3 --help`` to get a list of the sub-commands available for doing things
with and related to the Strait of Georgia WAVEWATCH III® model.
Use ``wwatch3 help <sub-command>`` to get a synopsis of what a sub-command does,
what its required arguments are,
and what options are available to control it.

Documentation for the package is in the ``docs/`` directory and is rendered at http://wwatch3-cmd.readthedocs.org/en/latest/.

.. image:: https://readthedocs.org/projects/wwatch3-cmd/badge/?version=latest
    :target: https://wwatch3-cmd.readthedocs.io/en/latest/
    :alt: Documentation Status

This an extensible tool built on the OpenStack ``cliff``
(`Command Line Interface Formulation Framework`_)
package.
It uses plug-ins from the `NEMO-Cmd`_ package to provide a command processor tool
that is specifically tailored to the Strait of Georgia WAVEWATCH III® model
as it is used in the MIDOSS project.

.. _Command Line Interface Formulation Framework: https://docs.openstack.org/cliff/latest/
.. _NEMO-Cmd: https://bitbucket.org/salishsea/nemo-cmd


License
=======

.. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Licensed under the Apache License, Version 2.0

The code and documentation of the WaveWatch III® Command Processor project
are copyright 2019-2020 the MIDOSS project contributors, The University of British Columbia,
and Dalhousie University.

They are licensed under the Apache License, Version 2.0.
https://www.apache.org/licenses/LICENSE-2.0
Please see the LICENSE file for details of the license.
