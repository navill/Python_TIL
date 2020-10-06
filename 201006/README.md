# 201006

- **[상태 객체 혹은 상태 기계 구현](#상태-객체-혹은-상태-기계-구현)**

- **[문자열로 이루어진 객체의 메소드 호출](#문자열로-이루어진-객체의-메소드-호출)**

    

<br>

**[처음으로](#201006)**
<br>

# 상태 객체 혹은 상태 기계 구현

>   Python cookbook chapter8.19

-   [상태 기계](https://namu.wiki/w/FSM#s-4)나 여러 상태로 동작하는 객체 구현
    -   단 많은 조건문을 사용하지 않고 구현

```python
# bad
class Connection:
    def __init__(self):
        self.state = 'CLOSED'

    def raed(self):
        if self.state != 'OPEN':
            raise RuntimeError('Not Open')
        print('reading')

    def write(self, data):
        if self.state !='OPEN':
            raise RuntimeError('Not Open')
        print('writing')

    def open(self):
        if self.state != 'OPEN':
            raise RuntimeError('Already Open')
        self.state = 'OPEN'

    def close(self):
        if self.state != 'CLOSED':
            raise RuntimeError('Already Closed')
        self.state = 'CLOSED'
```

-   if를 이용한 상태 확인을 위한 조건 
-   read(), write()에서 항상 상태를 확인해야함

=> 상태 관련 동작은 별도의 클래스로 만들고 Connection 클래스를 상태 클래스로 델리게이트(delegate: 위임)

```python
# better.1 - staticmethod

class Connection:
    def __init__(self):
        self.new_state(ClosedConnectionState)

    def new_state(self, newstate):
        self._state = newstate

    def read(self):
        return self._state.read(self)

    def write(self, data):
        return self._state.write(self, data)

    def open(self):
        return self._state.open(self)

    def close(self):
        return self._state.close(self)


# 기본 상태 클래스: 추상 클래스 역할(인터페이스 강제) + 코드의 가독성
class ConnectionState:
    @staticmethod
    def read(conn):
        # 상태 클래스에서 동일한 인터페이스를 구현하지 않을 경우 아래의 에러 발생
        raise NotImplementedError()  

    @staticmethod
    def write(conn, data):
        raise NotImplementedError()

    @staticmethod
    def open(conn):
        raise NotImplementedError()

    @staticmethod
    def close(conn):
        raise NotImplementedError()

# 상태 클래스: 닫힘
class ClosedConnectionState(ConnectionState):
    @staticmethod
    def read(conn):
        raise RuntimeError('Not open')

    @staticmethod
    def write(conn, data):
        raise RuntimeError('Not open')

    @staticmethod
    def open(conn):
        conn.new_state(OpenConnectionState)

    @staticmethod
    def close(conn):
        raise RuntimeError('Already closed')

# 상태 클래스: 열림
class OpenConnectionState(ConnectionState):
    @staticmethod
    def read(conn):
        print('reading')

    @staticmethod
    def write(conn, data):
        print('writing')

    @staticmethod
    def open(conn):
        raise RuntimeError('Already open')

    @staticmethod
    def close(conn):
        conn.new_state(ClosedConnectionState)
```

-   상태 클래스의 모든 메서드는 staticmethod

    -   staticmethod의 파라미터(conn): Connection 클래스에서 상태 클래스로 델리게이트할 때 인자로 전달된 self

        ```python
        class Connection:
            ...
            def read(self):
                return self._state.read(self)
        
        # 기본 상태 클래스: 추상 클래스 역할(인터페이스 강제) + 코드의 가독성
        class ConnectionState:
            @staticmethod
            def read(conn):  # 비정상 호출
                # 상태 클래스에서 동일한 인터페이스를 구현하지 않을 경우 아래의 에러 발생
                raise NotImplementedError()  
            ...
        
        class OpenConnectionState(ConnectionState):
            @staticmethod
            def read(conn):  # 정상 호출
                print('reading') 
            ...
        ```

        -   @staticmethod가 아닌 일반 메소드일 경우 self가 상태 클래스를 가리키기 때문에 올바른 동작을 할 수 없음
        -   상태 클래스에서는 어떠한 인자도 전달되서 안됨 -> 동작은 Connection 클래스에서 호출

-   닫힌 상태로 클래스가 시작하며 상태 클래스를 Connection 클래스 객체의 속성(self._state)으로 유지한다.

    ```python
    class Connection:
        def __init__(self):
            self.new_state(ClosedConnectionState)
    
        def new_state(self, newstate):
            self._state = newstate  # 동작(open, read 등)이 이뤄질 때 self._state.read()형식으로 호출된다.
    ```

    -   new_state 메서드를 이용해 상태가 변경될 때 해당 상태 클래스를 저장한다.
    -   결과적으로 ClosedConnectionState.read() 형식으로 호출된다.



<br>

```python
# better.2 - __class__ 변경
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

# 닫힌 상태 처리
class ClosedConnection(Connection):
    def read(self):
        raise RuntimeError('Not open')

    def write(self, data):
        raise RuntimeError('Not open')

    def open(self):  # 닫힌 상태에서 가능한 상태: open
        self.new_state(OpenConnection)  # new_state 호출

    def close(self):
        raise RuntimeError('Already closed')

# 열린 상태 처리
class OpenConnection(Connection):
    def read(self):
        print('reading')

    def write(self, data):
        print('writing')

    def open(self):
        raise RuntimeError('Already open')

    def close(self):
        self.new_state(ClosedConnection)  # new_state 호출

c = Connection()
print(c)  # <__main__.ClosedConnection object at 0x7fa0dc27b588>
try:
    c.read()
    except RuntimeError as e:
        print(e)  # Not open
c.open()
print(c)  # <__main__.OpenConnection object at 0x7fa0dc27b588>
c.read()  # reading
c.close()
print(c)  # <__main__.ClosedConnection object at 0x7fa0dc27b588>
```

-   기본 상태 클래스를 구현하는 대신 Connection.new_method에서 \_\_class\_\_를 상태 클래스로 직접 변경
    -   Connection 클래스가 상태에 따라 OpenConnection 또는 ClosedConnection이 된다.
    -   \_\_class\_\_ 변경에 대해 기술적으로 문제없음
    -   첫 번째 솔루션 보다 더 좋은 성능

<br>

**[처음으로](#201006)**
<br>



# 문자열로 이루어진 객체의 메소드 호출

1.  getattr()을 사용

2.  operator.methodcaller('method_name'[, arg1, arg2, ...])

    ```python
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y
    
        def __repr__(self):
            return 'Point({!r:},{!r:})'.format(self.x, self.y)
    
        def distance(self, x, y):
            return math.hypot(self.x - x, self.y - y)
    
    p = Point(3, 4)
    d = operator.methodcaller('distance', 0, 0)(p)
    print(d)
    # 5.0
    ```

    -   동일한 매개변수를 반복적으로 입력해야할 경우 getattr 보다 간단하게 구현할 수 있다.

        ```python
        points = [
            Point(1, 2),
            Point(3, 0),
            Point(10, -3),
            Point(-5, -7),
            Point(-1, 8),
            Point(3, 2)
        ]
        
        points.sort(key=operator.methodcaller('distance', 0, 0))
        for p in points:
            print(p)
        ```

        -   methodcaller를 이용한 Point객체 정렬

    -   메서드에 주어질 파라미터를 고장하는 기능을 구현할 수 있다.

        ```python
        p = Point(3, 4)
        d = operator.methodcaller('distance', 0, 0) # distance(0, 0) 고정
        d(p)
        # 5.0
        ```

        

<br>

**[처음으로](#201006)**
<br>