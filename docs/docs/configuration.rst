.. _configuration:

Configuration
=============

Dashmat is configured via a yaml file.

There are two main sections that are necessary for telling dashmat what to show.

Modules section
---------------

The modules section is used to specify what python modules to load and what
options to give them.

.. code-block:: yaml

  ---

  modules:
    <friendly_name>:
      import_path: <package:kls>
      server_options: <options>

For example:

.. code-block:: yaml

  ---

  modules:
    components:
      import_path: dashmat.core_modules.components.main:Components

This tells dashmat that we have a module called ``components`` that loads the
``Components`` core module from dashmat.

You can have multiple friendly names for the same component and the data from
that module will be namespaced by the friendly name:
``/data/<friendly_name>/<route>``. This means you can instantiate the same
module with different ``server_options``.

Dashboards section
------------------

The dashboards section tells dashmat what dashboards there are, the path to the
dashboard, and what to show:

.. code-block:: yaml

  ---

  modules:
    components:
      import_path: dashmat.core_modules.components.main:Components

  dashboards:
    /number:
      description: A number!
      imports:
        - [[Number], 'components']
      layout:
        <Number title="test" data={this.datasource("/data/components/number")} />

In this example, when we go to ``localhost:7546/number`` we'll get a dashboard
containing an instance of the ``Number`` widget from the ``Component`` module.

This widget is using ``/data/components/number`` as a datasource, which means
it will hit that endpoint periodically to get a new value.

The dashboard has a few options:

is_index
  This will override all other options and tells dashmat to display an index
  page of all the available dashboards. By default the ``/`` route will be one
  of these.

description
  This is the text that is displayed for this dashboard in the index page.

imports
  Either a string or a list, specifying what es6 imports to include in the
  generated javascript for this dashboard.

  The example above is equivalent to saying:

  .. code-block:: yaml

    ---

    dashboards:
      /number:
        imports:
          - "import {Number} from '/modules/dashmat.core_modules.components/main.jsx'"
        enabled_moduels:
          - components

  Note that by specifying the import as an array, we are auto filling out the
  ``enabled_modules`` option.

layout
  This is jsx that is injected into the generated javascript for this dashboard.

  Note that in our example we are using the ``this.datasource`` function on the
  ``Dashboard`` to register a url as a source of data. The dashboard is then
  responsible for periodically polling this url and setting the data on the
  ``Number`` widget to the result of that call.

