import copy
import time


class ApiMetrics:
    """
    Metrics API. Stores, calculates and exposes execution time metrics for efficiency evaluation.
    """

    __counters = {}                     # :dict: Main measurements storage.

    @classmethod
    def start(cls, invocation_id, procedure):
        """
        Starts time measurement on a new procedure of a particular cloud function invocation.
        :param invocation_id: string. Cloud function invocation Id.
        :param procedure: string. Particular procedure name to be measured.
        :return: void.
        """

        # If no metrics have been measured for this particular invocation, start a new register for it.
        if invocation_id not in cls.__counters:
            cls.__counters[invocation_id] = {}

        # If this particular procedure measurement hasn't yet been initiated, start it.
        if procedure not in cls.__counters[invocation_id]:
            cls.__counters[invocation_id][procedure] = {}
            cls.__counters[invocation_id][procedure]['time'] = time.time()
            cls.__counters[invocation_id][procedure]['counting'] = True

    @classmethod
    def stop(cls, invocation_id, procedure) -> float:
        """
        Stops time measurement of a procedure on a particular cloud function invocation.
        :param invocation_id: string. Cloud function invocation Id.
        :param procedure: string. Particular procedure whose time measurement is to be stopped.
        :return: float. Procedure final time measurement.
        """

        # If measurement has been initiated on this invocation and procedure, stop and calculate it.
        proc = cls.__counters.get(invocation_id, {}).get(procedure)
        if proc:
            proc['time'] = cls.__get_time_diff(proc['time'])
            proc['counting'] = False

        # Return final time measurement.
        return proc['time']

    @classmethod
    def get(cls,  invocation_id):
        """
        Finalizes all measurements and returns a finished metrics dictionary of a particular cloud function invocation.
        :param invocation_id: string. Cloud function invocation Id.
        :return: dictionary. Summary of all invocation measurements.
        """

        # Iterates on measurement dictionary stopping time counters and flagging measurements as done.
        metrics = {}
        if invocation_id not in cls.__counters: return metrics
        for k, v in cls.__counters[invocation_id].items():
            if v['counting']:
                metrics[k] = cls.__get_time_diff(v['time'])
            else:
                metrics[k] = v['time']
        del cls.__counters[invocation_id]
        return metrics

    @classmethod
    def get_snapshot(cls,  invocation_id):
        """
        Returns a finished metrics dictionary of a particular cloud function invocation containing only finalized
        measurements. Ongoing ones will be ignored.
        :param invocation_id: string. Cloud function invocation Id.
        :return: dictionary. Summary of all invocation measurements.
        """

        # Iterates on measurement dictionary selecting finalized entries.
        source = copy.copy(cls.__counters[invocation_id])
        return {k: v.get('time') for k, v in source.items() if not v.get('counting')}

    @staticmethod
    def __get_time_diff(ref):
        """
        Calculates time difference between current and reference time.
        :param ref: integer. Reference time.
        :return: integer. 3 digits rounded time difference in seconds.
        """

        return round(time.time() - ref, 3)
