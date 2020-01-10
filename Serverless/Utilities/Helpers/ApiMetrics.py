import time


class ApiMetrics:

    def __init__(self):
        self.counters = {}

    def start_time(self, metric):
        if metric not in self.counters:
            self.counters[metric] = {}
            self.counters[metric]['time'] = time.time()
            self.counters[metric]['counting'] = True

    def stop_time(self, metric):
        if metric in self.counters:
            self.counters[metric]['time'] = self.__get_time_diff(self.counters[metric]['time'])
            self.counters[metric]['counting'] = False

    def get(self):
        metrics = {}
        for k, v in self.counters.items():
            if v['counting']:
                metrics[k] = self.__get_time_diff(v['time'])
            else:
                metrics[k] = v['time']
        return metrics

    @staticmethod
    def __get_time_diff(metric):
        return round(time.time() - metric, 3)
