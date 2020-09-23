# ---------------- descriptor basic ---------------
class Attribute:
    value = 2


class Client:
    attribute = Attribute()


c = Client()


# print(c.attribute.value)
# print(c.attribute is c)

# descriptor
class DescriptorClass:
    def __get__(self, instance, owner):
        if instance is None:
            return self
        # print(self.__class__.__name__)
        return instance


class ClientClass:
    descriptor = DescriptorClass()


client = ClientClass()
client.descriptor
ClientClass.descriptor
# print(client.descriptor)
# print(client.descriptor is client)

client.descriptor = 'value'


# print(client.descriptor)


# ------------ descriptor __set__() --------------
class Validation:
    def __init__(self, validation_function, error_msg: str):
        self.validation_function = validation_function
        self.error_msg = error_msg

    def __call__(self, value):
        if not self.validation_function(value):
            raise ValueError(f"{value!r}{self.error_msg}")


class Field:
    def __init__(self, *validations):
        self._name = None
        self.validations = validations

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self._name]

    def __set__(self, instance, value):
        self.validate(value)
        instance.__dict__[self._name] = value

    def validate(self, value):
        for validation in self.validations:
            validation(value)


class ClientClass:
    descriptor = Field(Validation(lambda x: isinstance(x, (int, float)), '는 숫자가 아님'),
                       Validation(lambda x: x >= 0, "는 0보다 작음"))


# client = ClientClass()
# client.descriptor = 42
# client.descriptor = -42
# client.descriptor = '42'


# ------------- descriptor __delete__() ---------------

class ProtectedAttribute:
    def __init__(self, requires_role=None):
        self.permission_required = requires_role
        self._name = None

    def __set_name__(self, owner, name):
        self._name = name

    def __set__(self, user, value):
        if value is None or value == '':
            raise ValueError(f"{self._name}를 None으로 설정할 수 없음")
        user.__dict__[self._name] = value

    def __delete__(self, user):
        if self.permission_required in user.permissions:
            user.__dict__[self._name] = None
        else:
            raise ValueError(f"{user.username} 사용자는 {self.permission_required} 권한이 없음")


class User:
    email = ProtectedAttribute(requires_role='admin')

    def __init__(self, username, email, permission_list):
        self.username = username
        self.email = email
        self.permissions = permission_list or []

    def __str__(self):
        return self.username


admin = User('jh', 'ji@nad.com', ['admin'])
normal_user = User('jh2', 'ji@nad2.com', ['user'])
print(admin.email)
print(normal_user.email)
del admin.email
print(admin.email is None)


# del user.email
# abnormal_user = User('', '', ['admin'])

# -------------- type of descriptor(non-data descriptor) ----------------
class NonDataDescriptor:
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return 42


class ClientClass:
    descriptor = NonDataDescriptor()


client = ClientClass()
print(vars(client))
print(client.descriptor)  # 42
client.descriptor = 50
print(client.descriptor)  # 50(변경)
print(vars(client))  # {'descriptor': 50}
del client.descriptor
print(client.descriptor)  # 42
print(vars(client))  # {}


# -------------- type of descriptor(data descriptor) ----------------
class DataDescriptor:
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return 42

    def __set__(self, instance, value):
        print('1111.', instance, value)
        instance.__dict__['descriptor'] = value


class ClientClass:
    descriptor = DataDescriptor()

#
# client = ClientClass()
# print(vars(client))  # {}
# print(client.descriptor)  # 42
# client.descriptor = 50
# print(client.descriptor)  # 42(변경안됨)
# print(vars(client))  # {'descriptor': 50}
# del client.descriptor  # AttributeError: __delete__
