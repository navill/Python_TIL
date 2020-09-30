import re


class Event:
    pattern = None

    def __init__(self, next_event=None):
        self.successor = next_event

    def process(self, logline: str):
        if self.can_process(logline):
            return self._process(logline)

        if self.successor is not None:
            return self.successor.process(logline)

    def _process(self, logline: str):
        parsed_data = self._parse_data(logline)
        return {
            "type": self.__class__.__name__,
            "id": parsed_data['id'],
            "value": parsed_data['value']
        }

    @classmethod
    def can_process(cls, logline):
        return cls.pattern.match(logline) is not None

    @classmethod
    def _parse_data(cls, logline):
        return cls.pattern.match(logline).groupdict()


class LogoutEvent(Event):
    pattern = re.compile(r"(?P<id>\d+):\s+logout\s+(?P<value>\S+)")


class LoginEvent(Event):
    pattern = re.compile(r"(?P<id>\d+):\s+login\s+(?P<value>\S+)")


class SessionEvent(Event):
    pattern = re.compile(r"(?P<id>\d+):\s+log(in|out)\s+(?P<value>\S+)")


# chain = SessionEvent()
# print(chain.process("567: login User"))  # {'type': 'SessionEvent', 'id': '567', 'value': 'User'}
# chain = LoginEvent(SessionEvent())
# print(chain.process("567: login User"))  # {'type': 'LoginEvent', 'id': '567', 'value': 'User'}
chain = LogoutEvent(LoginEvent(SessionEvent()))
print(chain.process("567: login User"))  # {'type': 'LoginEvent', 'id': '567', 'value': 'User'}
print("567: login User".split(' '))
