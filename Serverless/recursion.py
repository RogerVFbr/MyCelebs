def main():

    data = {
        'test1': 1,
        'test2': 2,
        'test3': {
            'test4': 4,
            'test5': 5
        },
        'test6': [
            {
                "test7": 7
            }
        ],
        'test8': [
            {
                'test9': (
                    {
                        "test10": 10
                    }
                )
            }
        ]
    }

    prop = 'test10'

    print(str(data))
    print(prop)
    print("")

    result = get_prop_value(data, prop)

    print("")
    print(result)


def get_prop_value(data, prop):

    if isinstance(data, dict):
        if prop in data:
            return data[prop]
        else:
            print('imin')
            for k, v in data.items():
                value = get_prop_value(v, prop)
                if value: return value

    elif isinstance(data, (list, tuple)):
        for v in data:
            value = get_prop_value(v, prop)
            if value: return value

    else:
        return None

if __name__ == "__main__":
    main()