import json


class ExampleMessage():
    def __init__(self, string="Hello world!"):
        self.id = self.__class__.__name__
        self.str = string

    def __str__(self):
        return json.dumps(self.__dict__)
