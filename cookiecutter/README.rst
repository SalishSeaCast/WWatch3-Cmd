*****************************************************************
Strait of Georgia WaveWatch III® Temporary Run Directory Template
*****************************************************************

This directory is a `cookiecutter`_ template for the temporary run directories for runs of the Strait of Georgia configuration of the WaveWatch III® model.
It is used by the :ref:`wwatch3-prepare`.

The :file:`cookiecutter.json` file contains the template variables and their default values.
The defaults are (mostly) overridden by values calculated by the :ref:`wwatch3-prepare`.
Sadly,
comments are not allowed in JSON files,
so you will have to guess the meaning of the template variables from their names and values,
or read the cdoe in the :file:`wwatch3/prepare.py` module to learn more about them.

The :file:`{{cookiecutter.tmp_run_dir}}` directory is the temporary run directory template.
The rendered temporary run directory will have the name given by the :kbd:`tmp_run_dir` template variable.

Please see the `cookiecutter`_ docs for more details of the template structure,
template variables,
and how the template rendering process works.

.. _cookiecutter: https://cookiecutter.readthedocs.io/en/latest/index.html
