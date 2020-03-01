import json, threading, subprocess, time, os, ast
from collections import OrderedDict
from tests.test_logger import TestLogger as tl


class TestProcedure:
    """
    Testing procedure object class. Wraps logic around Serverless Framework CLI commands to run service integration
    tests following configurations contained in test_configs.json file. Requested tests are sent by parameter via
    constructor.
    """

    TEST_CONFIG_PATH = 'tests/test_configs.json'    # :str: Test configurations file location.
    REQUIRED_CONFIG_PROPERTIES = {                  # :set: Properties each test configuration must contain.
        'log_name',                                 # :str: Descriptive test name.
        'function_name',                            # :str: Main function name, trigger of the event chain.
        'params',                                   # :str: Path of the JSON file containing execution parameters.
        'expected'                                  # :str: Expected response objects.
    }
    REQUIRED_CONFIG_RESPONSE_PROPERTIES = {         # :set: Properties required on expected response.
        'function_name',                            # :str: Name of function that will generate this response via log.
        'execution_confirmation',                   # :str: Log must contain this string for execution to be confirmed.
        'pick_by',                                  # :str: Log must contain this string to be selected for analysis.
        'assert'                                    # :str: Additional assertions to be performed on log.
    }
    LOG_MONITORING_TIMEOUT = 30                     # :int: Maximum log monitoring time.
    LOG_START_IDENTIFIER = 'START RequestId:'       # :str: Function log start line contains this string.
    LOG_END_IDENTIFIER = 'XRAY TraceId:'            # :str: Function log end line contains this string.
    LOG_REPORT_IDENTIFIER = 'REPORT '               # :str: Function log report line contains this string.

    def __init__(self, required_tests: list, print_on_screen: bool):
        """
        Constructor of the Test Procedure object. Stores provided data, triggers configuration parsing, validation and
        test procedures.
        :param required_tests: List containing strings denoting which tests are to be executed.
        :param print_on_screen: Toggles function on screen log printing on or off.
        """

        self.required_tests = required_tests        # :list: Contains names of the tests requested to be executed.
        self.test_configs = None                    # :dict: Parsed test configurations from JSON file.
        self.test_name = None                       # :str: Name of currently executed test.
        self.log_name = None                        # :str: Descriptive name of currently executed test.
        self.function_name = None                   # :str: Name of main trigger function currently being tested.
        self.params = None                          # :str: Path of JSON parameters file currently being used.
        self.expected = []                          # :list: Current expected response objects.
        self.threads = []                           # :list: Current log monitoring threads.
        self.timeout_flag = False                   # :bool: Timeout flag, is True when execution time expired.
        self.test_results = OrderedDict()           # :OrderedDict: Stores test results (log diagnoses.)

        # Updates on screen log printing flag as per parameter sent.
        self.PRINT_FUNCTION_LOGS_ON_SCREEN = print_on_screen

        # Performs configuration parsing and validation, abort if impossible.
        if not self.__parse_test_configs(): return

        # Runs tests.
        self.__run_tests()

        # Test concluded, present test results.
        self.__present_test_results()

    def __parse_test_configs(self) -> bool:
        """
        Parses and validates test configurations JSON file located on path described at class property
        TEST_CONFIG_PATH.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Attempts to locate and read test_configs.json file.
        try:
            with open(self.TEST_CONFIG_PATH, 'r') as f:
                self.test_configs = json.load(f)
        except Exception as e:
            tl.log_error(f"Unable to locate or read test configuration JSON file at given path: "
                         f"'{self.TEST_CONFIG_PATH}'")
            return False

        # Checks each test configuration contained in test configs dictionary.
        available_tests = self.test_configs.keys()
        for test in self.required_tests:

            # If requested test configuration doesn't exist on test_configs file, alert and abort.
            if test not in available_tests:
                tl.log_error(f"Unable to find required test '{test}' specifications in configuration file.")
                return False

            # If requested test configuration doesn't contain required properties, alert and abort.
            test_keys = set(self.test_configs.get(test).keys())
            if self.REQUIRED_CONFIG_PROPERTIES != test_keys:
                tl.log_error(f"Missing or mistyped test property in test '{test}' - {test_keys}.")
                return False

            # If requested test configuration doesn't contain at least one response specification, alert and abort.
            test_config = self.test_configs.get(test)
            expected_responses = test_config.get('expected')
            if len(expected_responses) == 0:
                tl.log_error(f"At least one expected response must be specified on test '{test}'")
                return False

            # If requested test responses don't contain required properties, alert and abort.
            for i, expected_response in enumerate(expected_responses):
                expected_response_keys = set(expected_response.keys())
                if self.REQUIRED_CONFIG_RESPONSE_PROPERTIES != expected_response_keys:
                    tl.log_error(f"Missing os mistyped property on test '{test}'s expected response indexed "
                                 f"{i}: {expected_response_keys}")
                    return False

            # If no response is defined for main test function, alert and abort.
            expected_func_names = [x.get('function_name') for x in expected_responses]
            main_function_name = test_config.get('function_name')
            if main_function_name not in expected_func_names:
                tl.log_error(f"No expected response is defined for main function '{main_function_name}' on test "
                             f"'{test}'.")
                return False

            # Parsing and validation occurred successfully, return True.
            return True

    def __run_tests(self):
        """
        Executes required tests on standard test procedure, triggering results presentation after each iteration.
        :return: void.
        """

        # Apply procedure sequentially for every requested test.
        for test in self.required_tests:

            # Prepares data
            self.test_name = test
            self.log_name = self.test_configs.get(test, {}).get('log_name')
            self.function_name = self.test_configs.get(test, {}).get('function_name')
            self.params = self.test_configs.get(test, {}).get('params')
            self.expected = self.test_configs.get(test, {}).get('expected')
            self.test_results[self.test_name] = OrderedDict()
            self.timeout_flag = False

            # Informs developer a requested test is initiating.
            tl.log_alert(f"Initiating test '{self.test_name}'...")

            # Launches log monitoring threads, one for each of the observed functions.
            for expected in self.expected:
                if expected.get('function_name') == self.function_name: continue
                t = threading.Thread(target=self.__monitor_function_log, args=(expected,))
                t.daemon = True
                t.start()
                self.threads.append({
                    'function_name': expected.get('function_name'),
                    'thread': t
                })

            # Triggers main function invocation.
            t = threading.Thread(target=self.__invoke_main_function)
            t.daemon = True
            t.start()
            self.threads.append({
                'function_name': self.function_name,
                'thread': t
            })

            # Main thread now awaits log extraction, up to a maximum amount of time.
            for thread_entry in self.threads:
                thread_entry['thread'].join(self.LOG_MONITORING_TIMEOUT)

            # If any log extraction thread is still alive, it's timed out. Aborts it's execution.
            for thread_entry in self.threads:
                if thread_entry['thread'].is_alive():
                    tl.log_error(f"Function '{thread_entry['function_name']}' log monitoring has timed out. "
                                 f"({self.LOG_MONITORING_TIMEOUT}s)")
                    self.timeout_flag = True

    def __present_test_results(self):
        """
        Formats and presents acquired test results on screen.
        :return: void
        """

        # Prepares data
        test_result = self.test_results.get(self.test_name)

        # Informs developer testing has been concluded.
        tl.log_alert(f"Test '{self.test_name}' completed. Results:")
        tl.log('.')

        # Checks test results per function.
        # present_order = [x['function_name'] for x in self.expected]
        # tl.log(str(test_result.items()))
        for function_name, results in test_result.items():

            # Logs analyzed function name.
            tl.log(tl.underline(f"-> Function '{function_name}'"))

            # Explodes function execution logs.
            execution_confirmation = results.get('execution_confirmation')
            print_on_screen = self.PRINT_FUNCTION_LOGS_ON_SCREEN if execution_confirmation else True
            log_raw = results.get('log_raw')
            if log_raw:
                for log_line in log_raw:
                    tl.log(f"{log_line}", print_on_screen=print_on_screen)
                tl.log('.', print_on_screen=print_on_screen)
            else:
                tl.log(f"No log captured.", print_on_screen=print_on_screen)

            # Prepares and displays log report data such as duration and memory usage.
            log_report = results.get('log_report')
            if log_report:
                init_duration = log_report.get('init_duration', 'N.A.').replace(' ', '').replace('ms', '')
                duration = log_report.get('duration', 'N.A.').replace(' ', '').replace('ms', '')
                billed = log_report.get('billed_duration', 'N.A.')
                max_memory = log_report.get('max_memory_used', 'N.A.').replace(' ', '').replace('MB', '')
                memory_size = log_report.get('memory_size', 'N.A.')
                try:
                    billed_in_seconds = float(billed.replace('ms', '').strip())/1000
                    memory_size_in_gb = float(memory_size.replace('MB', '').strip())/1024
                    gbs = round(billed_in_seconds*memory_size_in_gb, 5)
                except:
                    gbs = 'N.A.'
                report_str = f"Time: {init_duration}/{duration}/{billed} | Memory: {max_memory}/{memory_size} | " \
                             f"GB-s: {gbs}"
                tl.log(report_str)

            # Exposes criteria by which the log has been selected.
            pick_by = results.get('pick_by')
            if pick_by:
                tl.log(f"Picked by '{pick_by}'.")

            # Initiates assertion counter.
            assertion_success = 0

            # Shows execution confirmation status
            tl.log(f"{tl.get_status_string(execution_confirmation)} Execution confirmation.")
            if execution_confirmation: assertion_success += 1

            # Shows individual function assertion statuses.
            assertion_list = list(results.items())[4:]
            for assertion, status in assertion_list:
                tl.log(f"{tl.get_status_string(status)} {assertion}")
                if status: assertion_success += 1

            # Shows final function assertion status.
            assertion_no = len(assertion_list)
            if assertion_no+1 == assertion_success:
                tl.log(tl.paint_status_bg(f"'{function_name}' assertion PASSED ({assertion_success}/{assertion_no+1} "
                                      f"checks).", True))
            else:
                tl.log(tl.paint_status_bg(f"'{function_name}' assertion FAILED ({assertion_success}/{assertion_no+1} "
                                    f"checks).", False))
            tl.log('.')

    def __monitor_function_log(self, expected: dict):
        """
        Monitors function logs in real-time, extracts individual acquired logs and passes to log parser method.
        :param expected: Dictionary containing expected response properties.
        :return: void.
        """

        # Prepares data
        function_name = expected.get('function_name')
        command = f"sls logs -f {function_name} -t"
        log_open = False
        log_raw = []

        # Runs log monitoring command line via subprocess.Popen
        p = subprocess.Popen(command, bufsize=1, stdin=open(os.devnull), shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        # Iterates on subprocess stdout to capture logs.
        for line in iter(p.stdout.readline, b''):
            if self.timeout_flag: return
            line = line.decode("utf-8").replace('\n', '')

            # Initiates a log capture if a 'log start identifier' has been detected.
            if self.LOG_START_IDENTIFIER in line and not log_open:
                log_open = True

            # Finishes a log capture if a 'log end identifier' has been detected.
            elif self.LOG_END_IDENTIFIER in line and log_open:
                log_raw.append(line)
                log_open = False
                if self.timeout_flag: return
                if self.__parse_log(log_raw, expected): return
                else: log_raw = []

            # If a log capture is ongoing, capture this line.
            if log_open:
                log_raw.append(line)

        p.stdout.close()
        p.wait()

    def __parse_log(self, log_raw: list, expected: dict) -> bool:
        """
        Parses and evaluates log data according to provided expectations, arranging extracted data into log diagnose
        dictionary.
        :param log_raw: List of string containing function execution log lines.
        :param expected: Dictionary containing expected function output characteristics.
        :return:
        """

        # Prepares data
        function_name = expected.get('function_name')
        pick_by = expected.get('pick_by')
        log_str = ''.join(log_raw)
        log_dicts = self.__parse_dicts_from_strings(log_str)
        log_report = self.__parse_report_from_raw_logs(log_raw)
        log_diagnose = OrderedDict({
            'execution_confirmation': False,
            'pick_by': pick_by,
            'log_raw': log_raw,
            'log_report': log_report
        })

        # Informs developer a log has been captured.
        tl.log(f"Log for '{function_name}' function captured.")

        # Declares error if execution is not confirmed.
        if expected.get('execution_confirmation') not in log_str:
            self.test_results[self.test_name][function_name] = log_diagnose
            return True
        else:
            log_diagnose['execution_confirmation'] = True

        # Checks if "pick_by" id is present, skip log if not.
        if pick_by.strip() and pick_by not in log_str:
            tl.log(f"Skipping log for '{function_name}': 'pickup_by' conditions not met.")
            return False

        # Checks asserts
        for assertion in expected.get('assert'):

            # If assert was sent in string form, checks existence in string version of log.
            if isinstance(assertion, str):
                msg = f"Contains '{assertion}'."
                if assertion in log_str:
                    log_diagnose[msg] = True
                else:
                    log_diagnose[msg] = False

            # If assert was sent in dictionary form, searches property and value in dictionaries extracted from log.
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

        # Saves log diagnose to main test results object
        self.test_results[self.test_name][function_name] = log_diagnose
        return True

    def __invoke_main_function(self):
        """
        Invokes main trigger function.
        :return: void.
        """

        # Await 100ms before invocation.
        time.sleep(0.1)

        # Build execution command with path if available.
        command = f'sls invoke -f {self.function_name} -l'
        if self.params.strip(): command += f' --path {self.params.strip()}'

        # Inform developer of invocation.
        tl.log(f"Invoking '{self.function_name}' @ params '{self.params}'...")

        # Run command using subprocess.Popen
        p = subprocess.Popen(command, bufsize=1, stdin=open(os.devnull), shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        # Iterates on subprocess stdout to capture logs.
        log_raw = []
        for line in iter(p.stdout.readline, b''):
            line = line.decode("utf-8").replace('\n', '')
            log_raw.append(line)
        p.stdout.close()
        p.wait()

        self.__parse_log(log_raw, next(x for x in self.expected if x['function_name'] == self.function_name))

    @staticmethod
    def __parse_dicts_from_strings(data: str) -> list:
        """
        Parses dictionaries of any form contained on provided string.
        :param data: String to be analyzed.
        :return: List of dictionaries parsed from provided string.
        """

        # Initialize memory
        dicts, current_check, open_braces = [], '', 0

        # Iterate on every character of provided string.
        for c in data:

            # If an opening curly brace has been found, increase it's count.
            if c == '{':
                open_braces += 1

            # If a closing curly brace has been found, decrease it's count.
            elif c == '}' and open_braces > 0:
                open_braces -= 1

                # If open braces count has zeroed out, a dictionary has been formed. Convert and save.
                if open_braces == 0:
                    current_check += c
                    try:
                        dicts.append(ast.literal_eval(current_check.replace('true', 'True').replace('false', 'False')))
                    except Exception as e:
                        tl.log_error(f'__parse_dicts_from_strings -> Unable to "eval" extracted dictionary: {str(e)}')
                    current_check = ''
                    continue

            # If there are open braces, a dictionary is being formed, save character.
            if open_braces > 0:
                current_check += c

        # Procedure completed, return extracted dictionaries.
        return dicts

    @classmethod
    def __parse_report_from_raw_logs(cls, log_raw: list) -> dict:
        """
        Parses metric reports from provided raw log lines.
        :param log_raw:
        :return:
        """

        # Attempts to locate line containing report identifier.
        report_raw = ''
        for line in log_raw:
            if cls.LOG_REPORT_IDENTIFIER in line:
                report_raw = line.replace(cls.LOG_REPORT_IDENTIFIER, '').strip()
                break

        # If report was not found, return empty dictionary.
        if not report_raw: return {}

        # Parse report line data into usable dictionary if possible.
        fragments, report_dict = report_raw.split('\t'), {}
        for x in fragments:
            try:
                key, value = tuple(x.split(': '))
                report_dict[key.lower().replace(' ', '_')] = value
            except Exception:
                pass

        # Return built report dictionary.
        return report_dict

    @classmethod
    def __get_prop_value(cls, data, prop):
        """
        Recursive method for extracting the value of the first property that matches a given name on an unknown data
        structure.
        :param data: Data structure to be traversed.
        :param prop: Property name to be located.
        :return: Found value.
        """

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
