class Tests:

    @classmethod
    def test(cls, function_name, response, expected):
        tests_map = {
            'add-picture': cls.add_picture
        }

        func = tests_map.get(function_name)
        if func:
            return func(response, expected)
        else:
            print('Could not find function.')
            return False, []

    @classmethod
    def add_picture(cls, response, expected):
        dicts = cls.__parse_dicts_from_strings(''.join(response).replace('true', 'True').replace('false', 'False'))
        logs = []
        if len(dicts) > 0:
            response = dicts[0]
            logs.append(str(response))
            http_status_code = response.get('statusCode')
            if http_status_code == expected:
                logs.append(f'Test status: \u001b[32mSUCCESS\u001b[0m (Http status code is {expected})')
                return True, logs
            else:
                logs.append(f'Test status: \u001b[31mFAILED\u001b[0m (Http status code is not {expected})')
                return False, logs

        logs.append(f'Test status: \u001b[31mFAILED\u001b[0m (Unable to extract response dictionary)')
        return False, logs

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

