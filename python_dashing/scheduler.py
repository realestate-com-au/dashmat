from croniter import croniter
import datetime
import logging

log = logging.getLogger("python_dashing.scheduler")

class Scheduler(object):
    def __init__(self):
        self.check_times = {}
        self.checks = []

    def register(self, module, module_name):
        for cron, func in module.register_checks:
            self.checks.append((module_name, cron, func))

    def run(self, force=False):
        now = datetime.datetime.now()
        for module_name, cron, func in self.checks:
            key = "{0}_{1}".format(cron.replace(" ", "_").replace("/", "SLSH").replace("*", "STR"), func.__name__)
            iterable = croniter(cron, self.check_times.get(key, now))
            nxt = iterable.get_next(datetime.datetime)
            if nxt > now and not force:
                continue

            log.info("Triggering cron: {0}.{1} '{2}'".format(module_name, func.__name__, cron))
            try:
                func(now - self.check_times.get(key, now))
            except Exception:
                log.exception("Error running a check\tmodule={0}\tcheck={1}".format(module_name, func.__name__))
            finally:
                self.check_times[key] = now
