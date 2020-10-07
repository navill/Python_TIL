# class Connection:
#     def __init__(self):
#         self.state = 'CLOSED'
#
#     def raed(self):
#         if self.state != 'OPEN':
#             raise RuntimeError('Not Open')
#         print('reading')
#
#     def write(self, data):
#         if self.state !='OPEN':
#             raise RuntimeError('Not Open')
#         print('writing')
#
#     def open(self):
#         if self.state != 'OPEN':
#             raise RuntimeError('Already Open')
#         self.state = 'OPEN'
#
#     def close(self):
#         if self.state != 'CLOSED':
#             raise RuntimeError('Already Closed')
#         self.state = 'CLOSED'


class Connection:
    def __init__(self):
        self.new_state(ClosedConnection)

    def new_state(self, state):
        self.__class__ = state

    def read(self):
        raise NotImplementedError()

    def write(self, data):
        raise NotImplementedError()

    def open(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()


class ClosedConnection(Connection):
    def read(self):
        raise RuntimeError('Not open')

    def write(self, data):
        raise RuntimeError('Not open')

    def open(self):  # 닫힌 상태에서 가능한 상태: open
        self.new_state(OpenConnection)  # new_state 호출

    def close(self):
        raise RuntimeError('Already closed')


class OpenConnection(Connection):
    def read(self):
        print('reading')

    def write(self, data):
        print('writing')

    def open(self):
        raise RuntimeError('Already open')

    def close(self):
        self.new_state(ClosedConnection)  # new_state 호출


# Example
if __name__ == '__main__':
    c = Connection()
    print(c)
    try:
        c.read()
    except RuntimeError as e:
        print(e)

    c.open()
    print(c)
    c.read()
    c.close()
    print(c)
