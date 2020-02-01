import textwrap


class Tests:

    WRAPPER = textwrap.TextWrapper(width=250)

    def __init__(self, function_name, response, expected):
        self.tests_map = {
            'add-picture': self.add_picture
        }

        func = self.tests_map.get(function_name)
        if func:
            func(response, expected)
        else:
            print('Could not find function.')

    @classmethod
    def add_picture(cls, response, expected):
        dicts = cls.__parse_dicts_from_strings(''.join(response).replace('true', 'True').replace('false', 'False'))
        if len(dicts) > 0:
            response = dicts[0]
            wrap_list = cls.WRAPPER.wrap(text='Response: ' + str(response))
            for line in wrap_list:
                print(line)

            http_status_code = response.get('statusCode')
            if http_status_code == expected:
                print(f'Test status: \u001b[32mSUCCESS\u001b[0m (Http status code is {expected})')
            else:
                print(f'Test status: \u001b[31mFAILED\u001b[0m (Http status code is not {expected})')

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

