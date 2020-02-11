import json, threading, subprocess, time, os
from collections import OrderedDict

from tests.test_logger import TestLogger as tl


class TestProcedure:

    TEST_CONFIG_PATH = 'tests/test_configs.json'
    REQUIRED_TEST_PROPERTIES = {'log_name', 'function_name', 'params', 'expected'}
    REQUIRED_EXPECTED_RESPONSE_PROPERTIES = {'function_name', 'execution_confirmation', 'pick_by', 'assert'}
    LOG_MONITORING_TIMEOUT = 30
    LOG_START_IDENTIFIER = 'START RequestId:'
    LOG_END_IDENTIFIER = 'XRAY TraceId:'
    TEST_PASSED_STR = 'PASSED'
    TEST_FAILED_STR = 'FAILED'

    def __init__(self, required_tests, print_on_screen):
        self.required_tests = required_tests
        self.test_configs = None
        self.test_name = None
        self.log_name = None
        self.function_name = None
        self.params = None
        self.expected = []
        self.threads = []
        self.timeout_flag = False
        self.test_results = OrderedDict()

        self.PRINT_FUNCTION_LOGS_ON_SCREEN = print_on_screen

        if not self.__parse_test_configs(): return
        self.__run_tests()

    def __parse_test_configs(self):
        try:
            with open(self.TEST_CONFIG_PATH, 'r') as f:
                self.test_configs = json.load(f)
        except Exception as e:
            tl.log_error(f"Unable to locate or read test configuration JSON file at given path: "
                         f"'{self.TEST_CONFIG_PATH}'")
            return False

        available_tests = self.test_configs.keys()

        for test in self.required_tests:

            if test not in available_tests:
                tl.log_error(f"Unable to find required test '{test}' specifications in configuration file.")
                return False

            test_keys = set(self.test_configs.get(test).keys())
            if self.REQUIRED_TEST_PROPERTIES != test_keys:
                tl.log_error(f"Missing or mistyped test property in test '{test}' - {test_keys}.")
                return False

            test_config = self.test_configs.get(test)
            expected_responses = test_config.get('expected')

            if len(expected_responses) == 0:
                tl.log_error(f"At least one expected response must be specified on test '{test}'")
                return False

            for i, expected_response in enumerate(expected_responses):
                expected_response_keys = set(expected_response.keys())
                if self.REQUIRED_EXPECTED_RESPONSE_PROPERTIES != expected_response_keys:
                    tl.log_error(f"Missing os mistyped property on test '{test}'s expected response indexed "
                                 f"{i}: {expected_response_keys}")
                    return False

            tl.log_alert(f"Successfully parsed test configurations for: {self.required_tests}")
            return True

    def __run_tests(self):
        for test in self.required_tests:

            self.test_name = test
            self.log_name = self.test_configs.get(test, {}).get('log_name')
            self.function_name = self.test_configs.get(test, {}).get('function_name')
            self.params = self.test_configs.get(test, {}).get('params')
            self.expected = self.test_configs.get(test, {}).get('expected')

            self.test_results[self.test_name] = OrderedDict()
            self.timeout_flag = False

            tl.log_alert(f"Initiating test '{self.test_name}'...")

            for expected in self.expected:
                self.test_results[self.test_name][expected.get('function_name')] = OrderedDict()
                t = threading.Thread(target=self.__monitor_function_log, args=(expected,))
                t.daemon = True
                t.start()
                self.threads.append({
                    'function_name': expected.get('function_name'),
                    'thread': t
                })

            self.__invoke_main_function()

            for thread_entry in self.threads:
                thread_entry['thread'].join(self.LOG_MONITORING_TIMEOUT)

            for thread_entry in self.threads:
                if thread_entry['thread'].is_alive():
                    tl.log_error(f"Function '{thread_entry['function_name']}' log monitoring has timed out. "
                                 f"({self.LOG_MONITORING_TIMEOUT}s)")
                    self.timeout_flag = True
                    # thread_entry['thread'].join()

            # tl.log(str(self.test_results))

            self.__present_test_results()

    def __present_test_results(self):
        tl.log_alert(f"Test '{self.test_name}' completed. Results:")
        tl.log('.')
        test_result = self.test_results.get(self.test_name)
        log_indent_title = ""
        log_indent_test = ""
        for function_name, results in test_result.items():
            tl.log(tl.underline(f"{log_indent_title}-> Function '{function_name}'"))
            log_raw = results.get('log_raw')

            execution_confirmation = results.get('execution_confirmation')
            print_on_screen = self.PRINT_FUNCTION_LOGS_ON_SCREEN if execution_confirmation else True

            if log_raw:
                for log_line in log_raw:
                    tl.log(f"{log_indent_test}{log_line}", print_on_screen=print_on_screen)
                tl.log('.', print_on_screen=print_on_screen)
            else:
                tl.log(f"{log_indent_test}No log captured.", print_on_screen=print_on_screen)

            pick_by = results.get('pick_by')
            if pick_by:
                tl.log(f"Picked by '{pick_by}'.")

            assertion_success = 0

            tl.log(f"{log_indent_test}Execution confirmation. {self.__get_status_string(execution_confirmation)}")
            if execution_confirmation: assertion_success += 1

            assertion_list = list(results.items())[3:]
            for assertion, status in assertion_list:
                tl.log(f"{log_indent_test}{assertion} {self.__get_status_string(status)}")
                if status: assertion_success += 1

            assertion_no = len(assertion_list)
            if assertion_no+1 == assertion_success:
                tl.log(tl.paint_status_bg(f"'{function_name}' assertion PASSED ({assertion_success}/{assertion_no + 1} "
                                      f"checks).", True))
            else:
                tl.log(tl.paint_status_bg(f"'{function_name}' assertion FAILED ({assertion_success}/{assertion_no + 1} "
                                    f"checks).", False))

            tl.log('.')

    def __get_status_string(self, status):
        if status:
            return tl.paint_status(self.TEST_PASSED_STR, True)
        else:
            return tl.paint_status(self.TEST_FAILED_STR, False)

    def __monitor_function_log(self, expected):
        function_name = expected.get('function_name')
        command = f"sls logs -f {function_name} -t"
        log_open = False
        log_raw = []
        p = subprocess.Popen(command, bufsize=1, stdin=open(os.devnull), shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        for line in iter(p.stdout.readline, b''):
            line = line.decode("utf-8").replace('\n', '')

            if self.LOG_START_IDENTIFIER in line and not log_open:
                log_open = True
            elif self.LOG_END_IDENTIFIER in line and log_open:
                log_raw.append(line)
                log_open = False
                if self.timeout_flag: return
                if self.__parse_log(log_raw, self.test_name, expected): return
                else:
                    log_raw = []
                    continue

            if log_open:
                log_raw.append(line)

        p.stdout.close()
        p.wait()

    def __parse_log(self, log_raw, test_name, expected) -> bool:

        # Prepare data
        function_name = expected.get('function_name')
        execution_confirmation = expected.get('execution_confirmation')
        pick_by = expected.get('pick_by')
        asserts = expected.get('assert')
        log_str = ''.join(log_raw)
        log_dicts = self.__parse_dicts_from_strings(log_str)
        log_diagnose = OrderedDict({
            'execution_confirmation': False,
            'pick_by': pick_by,
            'log_raw': log_raw
        })

        tl.log(f"Log for '{function_name}' function captured.")

        # Declare error if execution confirmation is not found
        if execution_confirmation not in log_str:
            self.test_results[test_name][function_name] = log_diagnose
            return True
        else:
            log_diagnose['execution_confirmation'] = True

        # Check if "pick_by" id is present, discard if not
        if pick_by.strip() and pick_by not in log_str:
            # self.test_results[test_name] = log_diagnose
            tl.log(f"Skipping log for '{function_name}': 'pickup_by' conditions not met.")
            return False

        # Check asserts
        for assertion in asserts:

            if isinstance(assertion, str):
                msg = f"Contains '{assertion}'."
                if assertion in log_str:
                    log_diagnose[msg] = True
                else:
                    log_diagnose[msg] = False

            elif isinstance(assertion, dict):
                props = assertion.keys()
                msg = "'{}': {} => {}."
                msg_not_found = "'{}' : {} => Property not found."
                for prop in props:
                    prop_value = self.__get_prop_value(log_dicts, prop)
                    if prop_value and prop_value == assertion[prop]:
                        log_diagnose[msg.format(prop, assertion[prop], prop_value)] = True
                    elif prop_value and prop_value != assertion[prop]:
                        log_diagnose[msg.format(prop, assertion[prop], prop_value)] = False
                    elif not prop_value:
                        log_diagnose[msg_not_found.format(prop, assertion[prop])] = False



                    # prop_found = False
                    # for log_dict in log_dicts:
                    #     if prop in log_dict:
                    #         if log_dict[prop] == assertion[prop]:
                    #             log_diagnose[msg.format(prop, assertion[prop], log_dict[prop])] = True
                    #         else:
                    #             log_diagnose[msg.format(prop, assertion[prop], log_dict[prop])] = False
                    #         prop_found = True
                    #         break
                    # if not prop_found:
                    #     log_diagnose[msg_not_found.format(prop, assertion[prop])] = False

        self.test_results[test_name][function_name] = log_diagnose
        return True

    def __invoke_main_function(self):
        time.sleep(0.1)
        command = f'sls invoke -f {self.function_name} -l'
        if self.params.strip(): command += f' --path {self.params.strip()}'
        tl.log(f"Invoking '{self.function_name}' @ params '{self.params}'...")
        p = subprocess.Popen(command, bufsize=1, stdin=open(os.devnull), shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

    @staticmethod
    def __parse_dicts_from_strings(value):
        dicts = []
        current_check = ''
        open_bracers = 0
        for x in value:
            if x == '{':
                open_bracers += 1
            elif x == '}' and open_bracers > 0:
                open_bracers -= 1
                if open_bracers == 0:
                    current_check += x
                    dicts.append(eval(current_check))
                    current_check = ''
                    continue
            if open_bracers > 0:
                current_check += x
        return dicts

    @classmethod
    def __get_prop_value(cls, data, prop):

        if isinstance(data, dict):
            if prop in data:
                return data[prop]
            else:
                for k, v in data.items():
                    value = cls.__get_prop_value(v, prop)
                    if value: return value

        elif isinstance(data, (list, tuple)):
            for v in data:
                value = cls.__get_prop_value(v, prop)
                if value: return value

        else:
            return None







