import collections
import contextlib

# ----------- index & slice ----------------
my_numbers = (1, 2, 3, 4, 5, 6)
print(my_numbers[2:5])  # (3, 4, 5)

# start, end, step
interval = slice(1, 6, 2)  # slice에 사용될 인자를 설정할 수 있다.
print(my_numbers[interval])  # 2, 4, 6

interval = slice(None, 3)
print(my_numbers[interval])  # 1, 2, 3


class Items:
    def __init__(self, *values):
        self._values = list(values)

    def __len__(self):
        return len(self._values)

    def __getitem__(self, item):
        return self._values.__getitem__(item)


a = Items(1, 2, 3, 4)


class Inheritance(collections.UserList):
    def __init__(self, values):
        super().__init__(values)


a = Inheritance([1, 2, 3, 4])
print(a[2])
print(len(a))


# ----------- context manager ----------------
def stop_db():
    print('stop db')
    return 1


def start_db():
    print('start db')
    return 2


class DBHandler:
    def __enter__(self):
        stop_db()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        start_db()


def db_backup():
    print('start backup')
    return


def main():
    with DBHandler():
        db_backup()


main()
"""
stop db
start backup
start db
"""


@contextlib.contextmanager
def db_handler():
    yield stop_db()
    start_db()


def main2():
    with db_handler() as x:
        db_backup()
    print(x)


main2()
"""
stop db
start backup
start db
1
"""

# ----------- property ----------------
import re

EMAIL_FORMAT = re.compile(r"[^@]+@[^@]+\.[^@]+")


def is_valid_email(potentially_valid_email: str) -> str:
    return re.match(EMAIL_FORMAT, potentially_valid_email) is not None


class User:
    def __init__(self, username):
        self.username = username
        self._email = None

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, new_email):
        if not is_valid_email(new_email):
            raise ValueError(
                f"Can't set {new_email} as it's not a valid email"
            )
        self._email = new_email


normal = ['test@test.com', 'test@test', 'testtest.com', 'testtestcom']

for email in normal:
    try:
        user = User('jihoon')
        user.email = email
        print(user.email)
    except Exception as e:
        print(e)
"""
test@test.com
Can't set test@test as it's not a valid email
Can't set testtest.com as it's not a valid email
Can't set testtestcom as it's not a valid email
"""
