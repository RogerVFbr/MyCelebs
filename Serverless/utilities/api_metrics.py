import time


class ApiMetrics:

    __counters = {}

    @classmethod
    def start(cls, invocation_id, metric):
        if metric not in cls.__counters:
            if invocation_id not in cls.__counters:
                print(f'METRICS - Starting measurements on new invocation (Id: {invocation_id})')
                cls.__counters[invocation_id] = {}
            cls.__counters[invocation_id][metric] = {}
            cls.__counters[invocation_id][metric]['time'] = time.time()
            cls.__counters[invocation_id][metric]['counting'] = True

    @classmethod
    def stop(cls, invocation_id, metric):
        if invocation_id in cls.__counters and metric in cls.__counters[invocation_id]:
            cls.__counters[invocation_id][metric]['time'] = cls.__get_time_diff(
                cls.__counters[invocation_id][metric]['time'])
            cls.__counters[invocation_id][metric]['counting'] = False

    @classmethod
    def get(cls,  invocation_id):
        metrics = {}
        for k, v in cls.__counters[invocation_id].items():
            if v['counting']:
                metrics[k] = cls.__get_time_diff(v['time'])
            else:
                metrics[k] = v['time']
        del cls.__counters[invocation_id]
        return metrics

    @staticmethod
    def __get_time_diff(metric):
        return round(time.time() - metric, 3)
