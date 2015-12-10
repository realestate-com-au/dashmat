from input_algorithms.dictobj import dictobj
from croniter import croniter
import datetime
import logging

log = logging.getLogger("python_dashing.option_spec.cronned_checks")

class CronnedChecks(dictobj):
    fields = ['checks']

    def setup(self, *args, **kwargs):
        super(CronnedChecks, self).setup(*args, **kwargs)
        self.check_times = {}

    def run(self, force=False):
        now = datetime.datetime.now()
        for cron, func in self.checks:
            key = "{0}_{1}".format(cron.replace(" ", "_").replace("/", "SLSH").replace("*", "STR"), func.__name__)
            iterable = croniter(cron, self.check_times.get(key, now))
            nxt = iterable.get_next(datetime.datetime)
            if nxt > now and not force:
                continue

            log.info("Triggering cron: {0} ({1})".format(cron, func.__name__))
            try:
                func(now - self.check_times.get(key, now))
            except Exception as error:
                log.error("Failed to trigger a cron\tcron={0}\tfunc={1}".format(cron, func.__name__))
                log.exception(error)
            finally:
                self.check_times[key] = now
