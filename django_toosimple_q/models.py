import datetime
import contextlib
import io
import traceback
from croniter import croniter

from picklefield.fields import PickledObjectField

from django.utils import timezone
from django.db import models

from .registry import tasks
from .logging import logger


class Task(models.Model):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"
    INVALID = "INVALID"

    state_choices = (
        (QUEUED, "QUEUED"),
        (PROCESSING, "PROCESSING"),
        (FAILED, "FAILED"),
        (SUCCEEDED, "SUCCEEDED"),
        (INVALID, "INVALID"),
    )

    function = models.CharField(max_length=1024)
    args = PickledObjectField(blank=True, default=list)
    kwargs = PickledObjectField(blank=True, default=dict)
    priority = models.IntegerField(default=0)

    created = models.DateTimeField(default=timezone.now)
    started = models.DateTimeField(blank=True, null=True)
    finished = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=32, choices=state_choices, default=QUEUED)
    result = PickledObjectField(blank=True, null=True)

    stdout = models.TextField(blank=True, default="")
    stderr = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Task {self.function} {self.icon}"

    @property
    def icon(self):
        if self.state == Task.QUEUED:
            return "⌚"
        elif self.state == Task.PROCESSING:
            return "🚧"
        elif self.state == Task.SUCCEEDED:
            return "✔️"
        elif self.state == Task.FAILED:
            return "❌"
        else:  # if self.state == Task.INVALID:
            return "❔"

    def execute(self):
        """Execute the task.

        A check is done to make sure the task is still queued.

        Returns True if at the task was executed, whether it failed or succeeded (so you can loop for testing).
        """

        self.refresh_from_db()
        if self.state != Task.QUEUED:
            # this task was executed from another worker in the mean time
            return False

        if self.function not in tasks.keys():
            # this task is not in the registry
            self.state = Task.INVALID
            self.save()
            return False

        logger.info(f"Executing {self}")

        self.started = timezone.now()
        self.state = Task.PROCESSING
        self.save()

        try:
            stdout = io.StringIO()
            stderr = io.StringIO()

            callable = tasks[self.function]

            # TODO : if callable is a string, load the callable using this pseudocode:
            # if is_string(callable):
            #     mod, call = self.function.rsplit(".", 1)
            #     callable = getattr(import_module(mod), call)

            with contextlib.redirect_stderr(stderr):
                with contextlib.redirect_stdout(stdout):
                    self.result = callable(*self.args, **self.kwargs)

            self.state = Task.SUCCEEDED
        except Exception:
            self.result = traceback.format_exc()
            self.state = Task.FAILED
        finally:
            self.finished = timezone.now()
            self.stdout = stdout.getvalue()
            self.stderr = stderr.getvalue()
            self.save()

        return True


class Schedule(models.Model):

    name = models.CharField(max_length=1024)
    function = models.CharField(max_length=1024)
    args = PickledObjectField(blank=True, default=list)
    kwargs = PickledObjectField(blank=True, default=dict)

    last_check = models.DateTimeField(null=True, default=timezone.now)
    catch_up = models.BooleanField(default=False)
    last_run = models.ForeignKey(Task, null=True, on_delete=models.SET_NULL)

    cron = models.CharField(max_length=1024)

    def execute(self):
        """Execute the schedule.

        A check is done to make sure the schedule wasn't checked by another worker in the mean time.

        The task may be added several times if catch_up is True.

        Returns True if at least one task was queued (so you can loop for testing).
        """
        did_something = False

        last_check = self.last_check
        self.refresh_from_db()
        if last_check != self.last_check:
            # this schedule was executed from another worker in the mean time
            return False

        # we update last_check already to reduce race condition chance
        self.last_check = timezone.now()
        self.save()

        next_due = croniter(self.cron, last_check or timezone.now()).get_next(datetime.datetime)
        while last_check is None or next_due <= timezone.now():

            logger.info(f"{self} is due")

            t = tasks[self.function].queue(*self.args, **self.kwargs)
            if t:
                self.last_run = t
                self.save()

            did_something = True

            if self.catch_up:
                last_check = next_due
            else:
                last_check = timezone.now()

            next_due = croniter(self.cron, last_check).get_next(datetime.datetime)

        return did_something

    def __str__(self):
        return f"Schedule {self.function} [{self.cron}]"
