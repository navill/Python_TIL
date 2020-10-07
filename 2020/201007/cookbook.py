# class Person:
#     def __init__(self, name, age):
#         self._name = name
#         self._age = age
#
#     @property
#     def name(self):
#         return self._name
#
#     @name.setter
#     def name(self, name):
#         if not isinstance(name, str):
#             raise TypeError('must be a string')
#         self._name = name
#
#     @property
#     def age(self):
#         return self._age
#
#     @age.setter
#     def age(self, age):
#         if not isinstance(age, int):
#             raise TypeError('must be a integer')
#         self._age = age

# ...
from functools import partial


def typed_property(name, expected_type):
    storage_name = '_' + name

    @property
    def prop(self):
        return getattr(self, storage_name)

    @prop.setter
    def prop(self, value):
        if not isinstance(value, expected_type):
            raise TypeError('{} must be a {}'.format(name, expected_type))
        setattr(self, storage_name, value)

    return prop


String = partial(typed_property, expected_type=str)
Integer = partial(typed_property, expected_type=int)


class Person:
    name = typed_property('name', str)
    age = typed_property('age', int)
    str_name = String('str_name')
    int_age = Integer('int_age')

    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.str_name = name
        self.int_age = age


if __name__ == '__main__':
    p = Person('jihoon', 33)
    p.name = 'jihoon lee'
    p.str_name = 1
    # try:
    #     p.age = 'thirtythree'
    # except TypeError as e:
    #     print(e)

    print(p.name)
    # print(p.str_name)