class Helpers:

    @classmethod
    def convert_structure_to_dynamo_compatible(cls, data):
        # Método recursivo para converter floats em strings em um objeto de estrutura desconhecida
        if isinstance(data, dict):
            for k, v in data.items():
                data[k] = cls.convert_structure_to_dynamo_compatible(v)

        elif isinstance(data, list):
            for x in range(len(data)):
                data[x] = cls.convert_structure_to_dynamo_compatible(data[x])

        elif isinstance(data, tuple):
            data = list(data)
            data = cls.convert_structure_to_dynamo_compatible(data)

        if isinstance(data, float):
            return str(data)

        else:
            return data






