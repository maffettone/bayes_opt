"""
observers...
"""
from datetime import datetime
from .event import Events
import json
import os


class Observer:
    def update(self, event, instance):
        raise NotImplementedError


class _Tracker(object):
    def __init__(self):
        self._iterations = 0

        self._previous_max = None
        self._previous_max_params = None

        self._start_time = None
        self._previous_time = None

    def _update_tracker(self, event, instance):
        if event == Events.OPTMIZATION_STEP:
            self._iterations += 1

            current_max = instance.max
            if (self._previous_max is None or
                current_max["target"] > self._previous_max):
                self._previous_max = current_max["target"]
                self._previous_max_params = current_max["params"]

    def _time_metrics(self):
        now = datetime.now()
        if self._start_time is None:
            self._start_time = now
        if self._previous_time is None:
            self._previous_time = now

        time_elapsed = now - self._start_time
        time_delta = now - self._previous_time

        self._previous_time = now
        return (
            now.strftime("%Y-%m-%d %H:%M:%S"),
            time_elapsed.total_seconds(),
            time_delta.total_seconds()
        )

class JSONLogger(_Tracker):
    def __init__(self, path, reset=True):
        self._path = path if path[-5:] == ".json" else path + ".json"
        if reset:
            try:
                os.remove(self._path)
            except OSError:
                pass
        super(JSONLogger, self).__init__()

    def update(self, event, instance):
        if event == Events.OPTMIZATION_STEP:
            data = dict(instance.res[-1])

            now, time_elapsed, time_delta = self._time_metrics()
            data["datetime"] = {
                "datetime": now,
                "elapsed": time_elapsed,
                "delta": time_delta,
            }

            with open(self._path, "a") as f:
                f.write(json.dumps(data) + "\n")

        self._update_tracker(event, instance)
