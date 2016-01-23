from croniter import croniter
from threading import Thread
import datetime
import logging

log = logging.getLogger("dashmat.scheduler")

class Scheduler(Thread):
    daemon = True

    def __init__(self, datastore):
        super(Scheduler, self).__init__()
        self.check_times = {}
        self.checks = []
        self.finisher = {"finished": False}
        self.datastore = datastore

    def run(self):
        self.twitch(force=True)

        while True:
            if self.finisher['finished']:
                break

            try:
                self.twitch()
            except Exception as error:
                log.error("Scheduler failed an iteration!")
                log.exception(error)

    def finish(self):
        self.finisher['finished'] = True

    def register(self, module, server, module_name):
        for cron, func in server.register_checks:
            self.checks.append((cron, func, module, module_name))

    def twitch(self, force=False):
        now = datetime.datetime.now()
        for cron, func, module, module_name in self.checks:
            cron_key = "{0}_{1}".format(cron.replace(" ", "_").replace("/", "SLSH").replace("*", "STR"), func.__name__)
            iterable = croniter(cron, self.check_times.get(cron_key, now))
            nxt = iterable.get_next(datetime.datetime)
            if not force:
                if nxt > now and cron_key in self.check_times:
                    continue

            log.info("Triggering cron: {0}.{1} '{2}'".format(module_name, func.__name__, cron))
            try:
                ds = self.datastore.prefixed("{0}-{1}".format(module.relative_to, module_name))
                for key, value in func(now - self.check_times.get(cron_key, now)):
                    ds.create(key, value)
            except Exception:
                log.exception("Error running a check\tmodule={0}\tcheck={1}".format(module_name, func.__name__))
            finally:
                self.check_times[cron_key] = now
