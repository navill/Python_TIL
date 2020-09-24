# -------------- 디스크립터 예제 ---------------
from datetime import datetime


class Traveller:
    def __init__(self, name, current_city):
        self.name = name
        self._current_city = current_city
        self._cities_visited = [current_city]

    @property
    def current_city(self):
        return self._current_city

    @current_city.setter
    def current_city(self, new_city):
        if new_city != self._current_city:
            self._cities_visited.append(new_city)
            self._current_city = new_city

    @property
    def cities_visited(self):
        return self._cities_visited


alice = Traveller('alice', 'barcelona')
alice.current_city = 'paris'
alice.current_city = 'brussels'
alice.current_city = 'amsterdam'
print(alice.cities_visited)


# 어려움......... 코드를 자세히 뜯어보면서 이해가 필요함
class HistoryTracedAttribute:
    def __init__(self, trace_attribute_name):
        self.trace_attribute_name = trace_attribute_name  # cities_visited
        self._name = None

    def __set_name__(self, owner, name):
        self._name = name  # current_city

    def __get__(self, instance, owner):
        if instance is None:
            return self
        print('__get__:', instance.__dict__[self._name])
        return instance.__dict__[self._name]  # __dict__[self._name] 전달

    def __set__(self, instance, value):
        self._track_change_in_value_for_instance(instance, value)  # cities_visited 업데이트
        instance.__dict__[self._name] = value  # __dict__ 업데이트
        print('__set__:', instance.__dict__[self._name])

    def _track_change_in_value_for_instance(self, instance, value):
        self._set_default(instance)
        if self._needs_to_track_change(instance, value):
            instance.__dict__[self.trace_attribute_name].append(value)

    def _needs_to_track_change(self, instance, value):
        try:
            current_value = instance.__dict__[self._name]
        except KeyError:
            return True
        return value != current_value

    def _set_default(self, instance):
        instance.__dict__.setdefault(self.trace_attribute_name, [])


class Traveller:
    current_city = HistoryTracedAttribute('cities_visited')
    # current_ticket = HistoryTracedAttribute('ticket_bought')
    print(1)

    def __init__(self, name, current_city):
        self.name = name
        print(2)
        self.current_city = current_city  # __set__() 호출
        print(3)
        # self.current_ticket = current_ticket


# alice = Traveller('alice', 'barcelona')
# print('set barcelona:', vars(alice))
#
# alice.current_city = 'paris'  # __set__()
# print('set paris:', vars(alice))
#
# alice.current_city = 'brussels'
# print('set brussels:', vars(alice))
#
# alice.current_city = 'amsterdam'
# print('set amsterdam:', vars(alice))
#
# print(alice.current_city)
# print(alice.cities_visited)


# --------------- 다른 형태의 디스크립터-------------
class SharedDataDescriptor:
    def __init__(self, initail_value):
        self.value = initail_value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.value

    def __set__(self, instance, value):
        self.value = value


class ClientClass:
    descriptor = SharedDataDescriptor('첫 번째 값')


client1 = ClientClass()
print(client1.descriptor)  # '첫 번째 값'
client2 = ClientClass()
print(client2.descriptor)  # '첫 번째 값'
client1.descriptor = 'client1을 위한 값'
print(client2.descriptor)  # 'client1을 위한 값'
print(vars(client1))

# ------------ 약한 참조 --------------
from weakref import WeakKeyDictionary


class DescriptorClass:
    def __init__(self, initial_value):
        self.value = initial_value
        self.mapping = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.mapping.get(instance, self.value)

    def __set__(self, instance, value):
        self.mapping[instance] = value


class ClientClass:
    descriptor = DescriptorClass('첫 번째 값')


client1 = ClientClass()
print(client1.descriptor)  # '첫 번째 값'
client2 = ClientClass()
print(client2.descriptor)  # '첫 번째 값'
client1.descriptor = 'client1을 위한 값'
print(client2.descriptor)  # '첫 번째 값'
print(client1.descriptor)  # 'client1을 위한 값'

# -------- 클래스 데코레이터 피하기 ----------
from functools import partial
from typing import Callable


class BaseFieldTransformation:
    def __init__(self, transformation: Callable[[], str]) -> None:
        self._name = None
        self.tranformation = transformation

    def __get__(self, instance, owner):
        if instance is None:
            return self
        raw_value = instance.__dict__[self._name]
        return self.tranformation(raw_value)

    def __set_name__(self, owner, name):
        self._name = name

    def __set__(self, instance, value):
        instance.__dict__[self._name] = value


ShowOriginal = partial(BaseFieldTransformation, transformation=lambda x: x)
HideField = partial(BaseFieldTransformation, transformation=lambda x: "민감한 정보")
FormatTime = partial(BaseFieldTransformation, transformation=lambda ft: ft.strftime("%Y-%m-%d %H:%M"))


class LoginEvent:
    username = ShowOriginal()
    password = HideField()
    ip = ShowOriginal()
    timestamp = FormatTime()

    def __init__(self, username, password, ip, timestamp):
        self.username = username
        self.password = password
        self.ip = ip
        self.timestamp = timestamp

    def serialize(self):
        return {
            "username": self.username,
            "password": self.password,
            "ip": self.ip,
            "timestamp": self.timestamp
        }


le = LoginEvent('jihoon', 'test1234', '123.123.123.1', datetime.utcnow())
print(le.username)
print(le.password)
print(le.ip)
print(le.timestamp)
print(le.serialize())