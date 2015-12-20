#!/usr/bin/env python
"""
This is where the mainline sits and is responsible for setting up the logging,
the argument parsing and for starting up python_dashing.
"""

from python_dashing.actions import available_actions
from python_dashing.collector import Collector
from python_dashing.errors import BadTask

from delfick_app import App as DelfickApp
import logging

log = logging.getLogger("python_dashing.executor")

class App(DelfickApp):
    cli_categories = ['python_dashing']
    cli_description = "Application that reads YAML and serves up pretty dashboards"
    cli_environment_defaults = {"PYTHON_DASHING_CONFIG": ("--config", 'python_dashing.yml')}
    cli_positional_replacements = [('--task', 'list_tasks'), ('--artifact', "")]

    def execute(self, args_obj, args_dict, extra_args, logging_handler, no_docker=False):
        args_dict["python_dashing"]["extra"] = extra_args
        args_dict["python_dashing"]["debug"] = args_obj.debug

        collector = Collector()
        collector.prepare(args_dict["python_dashing"]["config"], args_dict)
        if hasattr(collector, "configuration") and "term_colors" in collector.configuration:
            self.setup_logging_theme(logging_handler, colors=collector.configuration["term_colors"])

        task = args_obj.python_dashing_chosen_task
        if task not in available_actions:
            raise BadTask("Unknown task", available=list(available_actions.keys()), wanted=task)

        available_actions[task](collector)

    def setup_other_logging(self, args, verbose=False, silent=False, debug=False):
        logging.getLogger("requests").setLevel([logging.CRITICAL, logging.ERROR][verbose or debug])

    def specify_other_args(self, parser, defaults):
        parser.add_argument("--config"
            , help = "The config file to read"
            , dest = "python_dashing_config"
            , **defaults["--config"]
            )

        parser.add_argument("--no-dynamic-dashboard-js"
            , help = "Turn off transpiling the dashboard javascript at runtime"
            , dest = "python_dashing_dynamic_dashboard_js"
            , action = "store_false"
            )

        parser.add_argument("--redis-host"
            , help = "Redis host to store data in"
            , dest = "python_dashing_redis_host"
            , default = ""
            )

        parser.add_argument("--task"
            , help = "The task to run"
            , dest = "python_dashing_chosen_task"
            , **defaults["--task"]
            )

        parser.add_argument("--host"
            , help = "The host to serve the dashboards on"
            , dest = "python_dashing_host"
            , default = "localhost"
            )

        parser.add_argument("--port"
            , help = "The port to serve the dashboards on"
            , default = 7546
            , dest = "python_dashing_port"
            , type = int
            )

        parser.add_argument("--artifact"
            , help = "Extra argument to be used as decided by each task"
            , dest = "python_dashing_artifact"
            , **defaults['--artifact']
            )

        parser.add_argument("--without-checks"
            , help = "Don't run the cronned checks, useful for development"
            , dest = "python_dashing_without_checks"
            , action = "store_true"
            )

        return parser

main = App.main
if __name__ == '__main__':
    main()
