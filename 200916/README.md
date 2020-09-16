# index & slice

```python
my_numbers = (1, 2, 3, 4, 5, 6)
print(my_numbers[2:5])  # (3, 4, 5)

# start, end, step
interval = slice(1, 6, 2)  # slice에 사용될 인자를 설정할 수 있다.
print(my_numbers[interval])  # 2, 4, 6

interval = slice(None, 3)
print(my_numbers[interval])  # 1, 2, 3
```

- 튜플, 문자열, 리스트에서 특정 요소를 가져올 때 for 보다 slice를 이용하는 것이 좋다.
- 위와 같이 object[key]와 같은 형태를 호출 할 때 '\_\_getitem\_\_' 매직 메서드가 호출 된다.



### 자체 시퀀스 생성

- \_\_getitem\_\_ + \_\_len\_\_ 매직 메서드로 구성
- 이터러블 객체의 구성요소와 다르지만 위 매직메서드를 이용해 이터러블 처럼 사용할 수 있다.

**리스트 캡슐화**

```python
class Items:
    def __init__(self, *values):
        self._values = list(values)

    def __len__(self):
        return len(self._values)

    def __getitem__(self, item):
        return self._values.__getitem__(item)
```

- Items 클래스는 list의 wrapper가 된다(캡슐화).
- 클래스가 list를 래핑함으로써 list에 내장된 기능(indexing, slicing)을 모두 사용할 수 있다.
- Items.\_\_getitem\_\_ 는 list.\_\_getitem\_\_ 를 호출하여 키에 해당하는 값을 가져올 수 있다.

**[collections.UserList](https://python.flowdas.com/library/collections.html#collections.UserList) 상속**

```python
class Inheritance(collections.UserList):
    def __init__(self, values):
        super().__init__(values)
        
a = Inheritance([1, 2, 3, 4])
print(a[2])  # 3
print(len(a))  # 4
```

- collections.UserList를 상속함으로써 Inheritance는 indexing과 slicing 기능을 사용할 수 있다.



**자신만의 시퀀스**

시퀀스를 구현할 때 아래의 사항에 유의해야한다.

- 범위로 인덱싱하는 결과는 해당 클래스와 같은 타입의 인스턴스여야 한다.
  - list[1:2] -> list-type, tuple[1:2] -> tuple
- slice에 제공된 범위는 파이썬과 동일하게 마지막 요소는 제외



# Context Manager

- 사전조건과 사후조건을 가지고 있기 때문에 다양한 코드에 적용할 수 있다.
- 주요 동작의 전후에 작업을 실행할 때 유용

- 'with' 구문을 통해 context manager로 진입
  - context manager는 enter & exit 매직 메서드로 구성됨(+ 제너레이터를 이용할 수 있음)
  - with -> enter(값을 반환하지 않아도 된다), 해당 블록의 끝에 도달 -> exit
  - 블록 내에 오류나 예외가 있더라고 exit 매직 메서드는 호출된다.
  - 따라서 exit에서 예외 처리를 할 수 있다. 

**예제: 데이터베이스 백업을 위해 db server를 중지 시킨 후 백업 시작, 백업이 완료된 후 db server 시작**

```python
def stop_db():
    print('stop db')
    return

def start_db():
    print('start db')
    return

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

# output
stop db
start backup
start db
```

- 위 예제에서 exit에서 에러처리를 하지 않는다. -> 절대 에러는 무시하면 안됨

**contextlib.contextmanager와 generator를 이용한 context manager 구현**

```python
import contextlib

@contextlib.contextmanager
def db_handler():
  	stop_db()
    yield
    start_db()

with db_handler():
    db_backup()

# output
stop db
start backup
start db
```

- @contextlib.contextmanager를 사용하는 함수는 반드시 제너레이터(yield)

- yield를 기준으로 enter와 exit로 구분된다.

  - db_handler 진입 -> stop_db() -> yield 전까지 진행 -> db_backup() -> yield 이후 진행 -> start_db()

  ```python
  def stop_db():
      print('stop db')
      return 1
  
  def start_db():
      print('start db')
      return 2
  
  @contextlib.contextmanager
  def db_handler():
      yield stop_db()
      start_db()
  
  def main2():
      with db_handler() as x:
          db_backup()
      print(x)
  
  main2()
  # output
  stop db
  start backup
  start db
  1  # stop_db()의 결과값
  ```

  - enter 메서드와 동일하게 **yield** 전의 결과값을 **... as x** 변수에 전달하여 context manager의 결과값으로 사용할 수 있다. 

**ContextDecorator - 원본 함수를 래핑하는 데코레이터**

```python
class dbhandler_decorator(contextlib.ContextDecorator):
  	def __enter__(self):
        stop_db()
    def __exit__(self, ext_type, ex_value, ex_traceback):
        start_db()

@dbhandler_decorator()
def offline_backup():
    db_backup()
```

- 데코레이터의 장점인 재사용이 용이하다.
- 단점은 완전히 독립적이다.
  - 위 방식은 **... as x** 와 같이 컨텍스트 관리자 내부에서 생성된 객체를 얻을 수 없다.

### 이점

- 기존의 함수를 리팩토링하기 쉬워진다.
  - 많은 상태를 관리할 필요가 없고 다른 클래스와 독립적인 컨텍스트 관리자가 필요할 경우 유용



# Property

- 객체의 속성에 접근할 때 사용

- java의 getter & setter와 같은 기능

  **예제: validate email**

  ```python
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
  
  
  test_email = ['test@test.com', 'test@test', 'testtest.com', 'testtestcom']
  
  for email in test_email:
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
  ```

  

- Property는 명령-쿼리 분리 원칙([Command and query seperation]([https://en.wikipedia.org/wiki/Command%E2%80%93query_separation](https://en.wikipedia.org/wiki/Command–query_separation)) 또는 CQRS 원칙)을 준수하기 좋은 방법

  - 객체의 메서드가 상태를 변경하는 작업(set) 또는 값을 반환하는 작업(get) 둘 중 하나만 수행해야한다.

