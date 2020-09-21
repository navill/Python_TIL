# --------------- [개방폐쇄] ---------------------
class Event:
    def __init__(self, raw_data):
        self.raw_data = raw_data


class UnknownEvent(Event):
    """데이터만으로 식별할 수 없는 이벤트"""


class LoginEvent(Event):
    """로그인 사용자에 의한 이벤트"""


class LogoutEvent(Event):
    """로그아웃 사용자에 의한 이벤트"""


class SystemMonitor:
    """시스템에서 발생한 이벤트 분류"""

    def __init__(self, event_data):
        self.event_data = event_data

    def identify_event(self):
        if (
                self.event_data["before"]["session"] == 0
                and self.event_data["after"]["session"] == 1
        ):
            return LoginEvent(self.event_data)
        elif (
                self.event_data["before"]["session"] == 1
                and self.event_data["after"]["session"] == 0
        ):
            return LogoutEvent(self.event_data)

        return UnknownEvent(self.event_data)


l1 = SystemMonitor({"before": {"session": 0}, "after": {"session": 1}})
print(l1.identify_event().__class__.__name__)  # LoginEvent
l2 = SystemMonitor({"before": {"session": 1}, "after": {"session": 0}})
print(l2.identify_event().__class__.__name__)  # LogoutEvent
l3 = SystemMonitor({"before": {"session": 1}, "after": {"session": 1}})
print(l3.identify_event().__class__.__name__)  # UnknownEvent


# --------------- [개방폐쇄 - 확장성을 가진 이벤트 시스템] ---------------------
class Event:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    @staticmethod
    def meets_condition(event_data: dict):
        return False


class UnknownEvent(Event):
    """데이터만으로 식별할 수 없는 이벤트"""


class LoginEvent(Event):
    @staticmethod
    def meets_condition(event_data: dict):
        return (
                event_data["before"]["session"] == 0
                and event_data["after"]["session"] == 1
        )


class LogoutEvent(Event):
    @staticmethod
    def meets_condition(event_data: dict):
        return (
                event_data["before"]["session"] == 1
                and event_data["after"]["session"] == 0
        )


class SystemMonitor:
    """시스템에서 발생한 이벤트 분류 """

    def __init__(self, event_data):
        self.event_data = event_data

    def identify_event(self):
        for event_cls in Event.__subclasses__():
            try:
                if event_cls.meets_condition(self.event_data):
                    return event_cls(self.event_data)
            except KeyError:
                continue
        return UnknownEvent(self.event_data)


l1 = SystemMonitor({"before": {"session": 0}, "after": {"session": 1}})
print(l1.identify_event().__class__.__name__)  # LoginEvent
l2 = SystemMonitor({"before": {"session": 1}, "after": {"session": 0}})
print(l2.identify_event().__class__.__name__)  # LogoutEvent
l3 = SystemMonitor({"before": {"session": 1}, "after": {"session": 1}})
print(l3.identify_event().__class__.__name__)  # UnknownEvent


# ---------------- [사전/사후 조건을 적용한 LSP] -------------
class Event:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    @staticmethod
    def meets_condition(event_data: dict):
        return False

    @staticmethod
    def meets_condition_pre(event_data: dict):
        """인터페이스 계약의 사전조건.
        event_data가 적절한 형태인지 유효성 검사.
        """
        # dict type 사전 검사
        assert isinstance(event_data, dict), f"{event_data!r} is not a dict"
        for moment in ("before", "after"):
            # 데이터에 before 또는 after가 포함되어 있는지 사전 검사
            assert moment in event_data, f"{moment} not in {event_data}"
            # before, after 내의 데이터 타입이 dict인지 검사
            assert isinstance(event_data[moment], dict)


class UnknownEvent(Event):
    """A type of event that cannot be identified from its data"""


class LoginEvent(Event):
    @staticmethod
    def meets_condition(event_data: dict):
        return (
                event_data["before"].get("session") == 0
                and event_data["after"].get("session") == 1
        )


class LogoutEvent(Event):
    @staticmethod
    def meets_condition(event_data: dict):
        return (
                event_data["before"].get("session") == 1
                and event_data["after"].get("session") == 0
        )


class TransactionEvent(Event):
    """Represents a transaction that has just occurred on the system."""

    @staticmethod
    def meets_condition(event_data: dict):
        # 대괄호가 아닌 .get()을 이용해 'transaction'을 강제하지 않고 사용한다.
        # 없을 경우 None, 있을경우 transaction을 사용한다.
        return event_data["after"].get("transaction") is not None


class SystemMonitor:
    """Identify events that occurred in the system"""

    def __init__(self, event_data):
        self.event_data = event_data

    def identify_event(self):
        Event.meets_condition_pre(self.event_data)
        event_cls = next(
            (
                event_cls for event_cls in Event.__subclasses__()
                if event_cls.meets_condition(self.event_data)
            ),
            UnknownEvent,
        )
        return event_cls(self.event_data)


if __name__ == '__main__':
    l4 = SystemMonitor({"before": {}, "after": {"transaction": "Tx001"}})
    print(l4.identify_event().__class__.__name__)  # TransactionEvent
    """Identify events that occurred in the system

    >>> l1 = SystemMonitor({"before": {"session": 0}, "after": {"session": 1}})
    >>> l1.identify_event().__class__.__name__
    'LoginEvent'

    >>> l2 = SystemMonitor({"before": {"session": 1}, "after": {"session": 0}})
    >>> l2.identify_event().__class__.__name__
    'LogoutEvent'

    >>> l3 = SystemMonitor({"before": {"session": 1}, "after": {"session": 1}})
    >>> l3.identify_event().__class__.__name__
    'UnknownEvent'

    >>> l4 = SystemMonitor({"before": {}, "after": {"transaction": "Tx001"}})
    >>> l4.identify_event().__class__.__name__
    'TransactionEvent'

    """
