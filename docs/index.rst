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


*********************************************
WWatch3-Cmd Documentation
*********************************************

The WaveWatch III® command processor package, ``WWatch3-Cmd``, provides the ``wwatch3``
command-line tool for doing various operations associated with the Strait of Georgia
configuration of the WAVEWATCH III® model as it is used in the context of the `MIDOSS project`_.

.. _MIDOSS project: https://midoss-docs.readthedocs.io/en/latest/

This an extensible tool built on the OpenStack ``cliff``
(`Command Line Interface Formulation Framework`_)
package.
It uses plug-ins from the `NEMO-Cmd`_ package to provide a command processor tool
that is specifically tailored to the Strait of Georgia WAVEWATCH III® model
as it is used in the MIDOSS project.

.. _Command Line Interface Formulation Framework: https://docs.openstack.org/cliff/latest/
.. _NEMO-Cmd: https://github.com/SalishSeaCast/NEMO-Cmd


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   subcommands
   run_description_file/index
   pkg_development


Indices
=======

* :ref:`genindex`
* :ref:`modindex`


License
=======

.. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Licensed under the Apache License, Version 2.0

The code and documentation of the WaveWatch III® Command Processor project
are copyright 2019-2021 by the `MIDOSS project contributors`_, The University of British Columbia,
and Dalhousie University.

.. _MIDOSS project contributors: https://github.com/MIDOSS/docs/blob/main/CONTRIBUTORS.rst

They are licensed under the Apache License, Version 2.0.
https://www.apache.org/licenses/LICENSE-2.0
Please see the LICENSE file for details of the license.
