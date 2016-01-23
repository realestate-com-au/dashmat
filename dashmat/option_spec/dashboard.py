from dashmat.option_spec.import_line import import_line_spec

from input_algorithms.spec_base import boolean, string_spec, formatted, listof, overridden, or_spec
from input_algorithms.dictobj import dictobj

from textwrap import dedent

class Dashboard(dictobj.Spec):
    description = dictobj.Field(
          string_spec
        , default = "{_key_name_1} Dashboard"
        , formatted = True
        , help = "Description to show up in the index"
        )

    path = dictobj.Field(
          overridden("{_key_name_1}")
        , formatted = True
        , help = "Url path to the dashboard"
        )

    es6 = dictobj.Field(
          string_spec
        , help = "Extra es6 javascript to add to the dashboard module"
        )

    is_index = dictobj.Field(
          boolean
        , formatted = True
        , help = "Whether this page is an index or not"
        )

    layout = dictobj.Field(
          string_spec
        , help = "Reactjs xml for the laytout of the dashboard"
        )

    imports = dictobj.Field(
          lambda: or_spec(listof(string_spec()), listof(import_line_spec()))
        , help = "es6 imports for the dashboard"
        )

    enabled_modules = dictobj.Field(
          string_spec
        , formatted = True
        , wrapper = listof
        , help = "The modules to enable for this dashboard"
        )

    def make_dashboard_module(self, modules):
        imports = []
        for imprt in self.imports:
            if hasattr(imprt, "import_line"):
                imports.append(imprt.import_line(modules))
            else:
                imports.append(imprt)

        return dedent("""
            import styles from "/modules/dashmat.server/Dashboard.css";
            import React, {{Component}} from 'react';
            import ReactDOM from 'react-dom';
            {imports}

            class Dashboard extends Component {{
                render() {{
                    return (
                        <div className={{styles.dashboard}}>
                            {layout}
                        </div>
                    )
                }};

                {es6}
            }}

            document.addEventListener("DOMContentLoaded", function(event) {{
                var element = React.createElement(Dashboard);
                ReactDOM.render(element, document.getElementById('page-content'));
            }});
        """).format(imports="\n".join(imports), layout=self.layout, es6=self.es6)

