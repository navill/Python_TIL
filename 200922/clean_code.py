# ----------- [decorator] ---------------
from asyncio.log import logger
from dataclasses import dataclass
from functools import wraps


class ControlledException(Exception):
    """도메인에서 발생하는 일반적인 예외"""


def retry(operation):
    @wraps(operation)
    def wrapped(*args, **kwargs):
        last_raised = None
        RETRIES_LIMIT = 3
        for _ in range(RETRIES_LIMIT):
            try:
                return operation(*args, **kwargs)
            except ControlledException as e:
                last_raised = e
        raise last_raised

    return wrapped


@retry
def run_operation(task):
    print(f'{task} - run operation')
    return


run_operation('task')

# -------- [class decorator] ---------
from datetime import datetime


def hide_field(field) -> str:
    return "**redacted**"


def format_time(field_timestamp: datetime) -> str:
    return field_timestamp.strftime("%Y-%m-%d %H:%M")


def show_original(event_field):
    return event_field


class EventSerializer:
    def __init__(self, serialization_fields: dict) -> None:
        print('EventSerializer.init')
        self.serialization_fields = serialization_fields

    def serialize(self, event) -> dict:
        print('EventSerializer.serialize')
        return {
            field: transformation(getattr(event, field))
            for field, transformation in self.serialization_fields.items()
        }


class Serialization:
    def __init__(self, **transformations, ):
        print('Serialization.init')
        self.serializer = EventSerializer(transformations)

    def __call__(self, event_class):
        print('Serialization.call')

        def serialize_method(event_instance: "LoginEvent") -> dict:
            print('Serialization.call.serialize_method')
            # -> return EventSerializer.serialize(event_instance)
            return self.serializer.serialize(event_instance)

        event_class.serialize = serialize_method
        return event_class


@Serialization(
    username=str.lower,
    password=hide_field,
    ip=show_original,
    timestamp=format_time,
)
class LoginEvent:
    def __init__(self, username, password, ip, timestamp):
        print('LoginEvent.init')
        self.username = username
        self.password = password
        self.ip = ip
        self.timestamp = timestamp


le = LoginEvent('JH', '1234', '123.0.0.1', datetime(2020, 9, 22, 22, 26))
print(le.serialize())
print(dir(le))


@Serialization(username=str.lower, password=hide_field, ip=show_original, timestamp=format_time)
@dataclass
class LogoutEvent:
    username: str
    password: str
    ip: str
    timestamp: datetime


le = LogoutEvent('JH', '4567', '123.0.0.1', datetime(2020, 9, 22, 22, 26))
# print(le.serialize())
# print(dir(le))

# --------- 중첩함수의 데코레이터 ----------------
RETRIES_LIMIT = 3


def with_retry(retries_limit=RETRIES_LIMIT, allowed_exceptions=None):
    allowed_exceptions = allowed_exceptions or (ControlledException,)

    def retry(operation):
        @wraps(operation)
        def wrapped(*args, **kwargs):
            last_raised = None
            for _ in range(retries_limit):
                try:
                    return operation(*args, **kwargs)
                except allowed_exceptions as e:
                    last_raised = e
            raise last_raised

        return wrapped

    return retry


class OperationObject:
    """A helper object to test the decorator."""

    def __init__(self):
        self._times_called: int = 0

    def run(self) -> int:
        """Base operation for a particular action"""
        self._times_called += 1
        return self._times_called

    def __str__(self):
        return f"{self.__class__.__name__}()"

    __repr__ = __str__


class RunWithFailure:
    def __init__(
            self,
            task: "OperationObject",
            fail_n_times: int = 0,  # 입력된 실패 횟수
            exception_cls=ControlledException,
    ):
        self._task = task
        self._fail_n_times = fail_n_times
        self._times_failed = 0  # 실행중 실패한 횟수
        self._exception_cls = exception_cls

    def run(self):
        called = self._task.run()
        if self._times_failed < self._fail_n_times:
            self._times_failed += 1
            raise self._exception_cls(f"{self._task} failed!")
        return called


# oo = OperationObject()
# rwf = RunWithFailure(oo, 2)  # oo에서 run()이 이미 한번 실행된 상태


@with_retry(retries_limit=3)
def run_operation(task):
    return task.run()


@with_retry(retries_limit=3)
def run_operation_with_fail(task):
    return task.run()


# print(run_operation(oo))  # 1
# print(run_operation_with_fail(rwf))  # 4


# ---------------------- class decorator ---------------------

class WithRetry:
    def __init__(self, retries_limit=RETRIES_LIMIT, allowed_exceptions=None):
        self.retries_limit = retries_limit
        self.allowed_exceptions = allowed_exceptions or (ControlledException,)

    def __call__(self, operation):
        @wraps(operation)
        def wrapped(*args, **kwargs):
            last_raised = None

            for _ in range(self.retries_limit):
                try:
                    return operation(*args, **kwargs)
                except self.allowed_exceptions as e:
                    last_raised = e
            raise last_raised

        return wrapped


@WithRetry(retries_limit=3)
def run_operation_with_fail(task):
    return task.run()


@WithRetry(retries_limit=3)
def run_operation(task):
    return task.run()


class A:
    def __init__(self):
        self.a = 'retry with A class'

    @WithRetry(retries_limit=3)
    def show(self):
        print(self.a)
        # raise ControlledException('a')

A().show()


oo = OperationObject()
rf = RunWithFailure(oo, 2)
print('1111111111111')
print(run_operation(oo))  # 1
print(run_operation_with_fail(rf))  # 4


# ---------- usage -------------------
def trace_decorator(function):
    def wrapped(*args, **kwargs):
        logger.info("%s 실행", function.__qualname__)
        return function(*args, **kwargs)

    return wrapped


@trace_decorator
def process_account(account_id):
    logger.info("%s 계정처리", account_id)


help(process_account)
print(process_account.__qualname__)

# ---------------usage decorator with side effect -----------


EVENT_REGISTRY = {}


def register_event(event_cls):
    EVENT_REGISTRY[event_cls.__name__] = event_cls
    return event_cls


class Event:
    """기본 이벤트"""


class UserEvent:
    TYPE = 'User'


@register_event
class UserLoginEvent(UserEvent):
    """사용자가 접근했을 때 이벤트 발생"""


@register_event
class UserLogoutEvent(UserEvent):
    """사용자가 시스템에서 나갈 때 이벤트 발생"""


# ---------- generic decorator with fail -----------
import logging

logger = logging.getLogger(__name__)


class DBDriver:
    def __init__(self, dbstring):
        self.dbstring = dbstring

    def excute(self, query):
        return f"{self.dbstring} 에서 쿼리 {query} 실행"


def inject_db_driver(function):
    @wraps(function)
    def wrapped(dbstring):
        return function(dbstring)

    return wrapped


@inject_db_driver
def run_query(driver):
    return driver.excute('test_function')


dbd = DBDriver('test')
print(run_query(dbd))


class DataHandler:
    @inject_db_driver
    def run_query(self, driver):
        return driver.excute(self.__class__.__name__)


# DataHandler().run_query('test_fail')

# --------------- generic decorator using descriptor -------------
from types import MethodType


class inject_db_driver:
    def __init__(self, function):
        self.function = function
        wraps(self.function)(self)

    def __call__(self, dbstring):
        return self.function(dbstring)

    def __get__(self, instance, owner):  # class 사용 시 동작
        if instance is None:
            return self
        return self.__class__(MethodType(self.function, instance))


@inject_db_driver
def run_query(driver):
    return driver.excute('test_function')


dbd = DBDriver('test')
print(run_query(dbd))


class DataHandler:
    @inject_db_driver
    def run_query(self, driver):
        return driver.excute(self.__class__.__name__)


print(DataHandler().run_query(dbd))
