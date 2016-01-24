DashMat
=======

This is a dashboard framework written in Python.

Documentation can be found at http://dashmat.readthedocs.org

Installation
------------

To install dashmat, just create a virtualenv somewhere and:

.. code-block:: sh

  $ pip install dashmat

Or if you're developing:

.. code-block:: sh

  $ pip install -e .
  $ pip install -e ".[tests]"

Then something like:

.. code-block:: sh

  $ export DASHMAT_CONFIG=dashmat.yml.example
  $ dashmat run_checks
  $ dashmat serve

