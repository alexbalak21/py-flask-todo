from flask import jsonify


class User:
    def __init__(self, name, age) -> None:
        self.name = name
        self.age = age

    def __str__(self) -> str:
        return f'{{"name": {self.name}, "age": {self.age}}}'


u1 = User('Alex', 37)

d1 = u1.__dict__


print(d1)
