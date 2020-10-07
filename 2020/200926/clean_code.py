# ----------- iteration interface ------------
class SequenceIterator:
    def __init__(self, start=0, step=1):
        self.current = start
        self.step = step

    def __next__(self):
        value = self.current
        self.current += self.step
        return value


# si = SequenceIterator(0, 2)
# print(next(si))  # 0
# print(next(si))  # 2
# print(next(si))  # 4
# print(next(si))  # 6


# for i in si: pass


# TypeError: 'SequenceIterator' object is not iterable


# ---------이터러블이 가능한 시퀀스 객체--------------
class MappedRange:
    def __init__(self, transformation, start, end):
        self._transformation = transformation
        self._wrapped = range(start, end)

    def __getitem__(self, index):
        value = self._wrapped.__getitem__(index)
        result = self._transformation(value)
        return result

    def __len__(self):
        return len(self._wrapped)


# mr = MappedRange(abs, 0, 10)
# for i in mr:
#     print(i)
# 0, 1, 2, 3, ... ,8 ,9

# ---------- coroutine ------------
import time

from log import logger


class DBHandler:
    """Simulate reading from the database by pages."""

    def __init__(self, db):
        self.db = db
        self.is_closed = False

    def read_n_records(self, limit):
        return [(i, f"row {i}") for i in range(limit)]

    def close(self):
        logger.debug("closing connection to database %r", self.db)
        self.is_closed = True


def stream_db_records(db_handler):
    try:
        while True:
            yield db_handler.read_n_records(10)
    except GeneratorExit:
        print('GeneratorExit')
        db_handler.close()


#
# streamer = stream_db_records(DBHandler("testdb"))
# print(next(streamer))
# # [(0, 'row 0'), (1, 'row 1'), (2, 'row 2'), (3, 'row 3'), (4, 'row 4'), (5, 'row 5'), (6, 'row 6'), (7, 'row 7'), (8, 'row 8'), (9, 'row 9')]
#
# print(len(next(streamer)))
# # 10
# print(streamer.close())


# GeneratorExit
# None


class CustomException(Exception):
    """Customerror"""


def stream_data(db_handler):
    while True:
        try:
            yield db_handler.read_n_records(10)
        except CustomException as e:
            print(f"controlled error {e.__class__.__name__}, continuing")
        except Exception as e:
            print(f"unhandled error {e.__class__.__name__}, stopping")
            db_handler.close()
            break


# streamer2 = stream_data(DBHandler('testdb'))
# print(next(streamer2))
# streamer2.throw(CustomException)
# # streamer2.throw(ValueError)


def stream_db_records2(db_handler):
    retrieved_data = None
    page_size = 10
    try:
        while True:
            page_size = (yield retrieved_data) or page_size
            retrieved_data = db_handler.read_n_records(page_size)
    except GeneratorExit:
        db_handler.close()


# streamer3 = stream_db_records2(DBHandler('testdb'))
# print(next(streamer3))
# print(next(streamer3))
# print(streamer3.send(3))
# print(streamer3.send(4))

# ------------- 코루틴 고급 주제 ----------------
def generator():
    yield from [1, 2, 3, 4, 5]
    yield from [6, 7, 8, 9, 10]
    return 3


value = generator()
print(next(value))  # 1
print(next(value))  # 2
print(next(value))  # 2

# print(next(value))  # StopIteration: 3
try:
    next(value)
except StopIteration as e:
    print(e.value)  # 3


def chain(iterables):
    for it in iterables:
        for value2 in it:
            yield value2


TEST_LIST = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(list(chain(TEST_LIST)))


def chain2(iterables):
    for it in iterables:
        yield from it


print(list(chain2(TEST_LIST)))


# -------------------- 서브 제너레이터에서 반환된 값 구하기 ----------------------
def sequence(name, start, end):
    print(f'{name} 제너레이터에서 start sequence:{start}')
    yield from range(start, end)
    print(f'{name} 제너레이터에서 end sequence:{end}')
    return end


def main():
    step1 = yield from sequence('first', 0, 5)
    step2 = yield from sequence('second', step1, 10)
    return step1 + step2


g = main()
for _ in range(11):
    print(next(g))

