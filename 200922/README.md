# 200922

- [함수 데코레이터](#함수-데코레이터)
- [클래스 데코레이터](#클래스-데코레이터)
- [데코레이터에 인자 전달](#데코레이터에-인자-전달)
- [데코레이터 활용](#데코레이터-활용)
- [Generic Decorator(임의로 지은 이름)](#generic-decorator어느곳에서나-동작하는-데코레이터)



<br>



**[처음으로](#200922)**

<br>



### 데코레이터 사용 시 고려사항

- 처음부터 데코레이터를 생성하지 않고, 데코레이터에 대한 추상화가 명확해질 때 리팩토링
- 반복 작업이 적어도 3회 이상 필요한 경우
- 데코레이터 코드는 최소한으로 구현



<br>



# 함수 데코레이터

- 파라미터의 유효성 검사, 사전조건 검사, 기능 정의, 서명 변경, 캐시 등 다양한 목적으로 사용할 수 있다.

  ```python
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
      return task.run()
  
  # 아래의 코드와 동일
  run_operation = retry(run_operation)
  ```

<br>



**[처음으로](#200922)**

<br>

# 클래스 데코레이터

- 클래스 데코레이터는 코드 재사용과 DRY 원칙의 이점을 공유한다. 

- 여러 클래스가 특정 인터페이스나 기준을 따르도록 강제할 수 있다.

- 메타 클래스보다 클래스 데코레이터가 더 좋은 결과를 낳을 수 있다.

  ```python
  import unittest
  from datetime import datetime
  
  
  def hide_field(field) -> str:
      return "**redacted**"
  
  def format_time(field_timestamp: datetime) -> str:
      return field_timestamp.strftime("%Y-%m-%d %H:%M")
  
  def show_original(event_field):
      return event_field
  
  class EventSerializer:
      def __init__(self, serialization_fields: dict) -> None:
          print('EventSerializer.__init__')
          self.serialization_fields = serialization_fields
  
      def serialize(self, event) -> dict:
          print('EventSerializer.serialize')
          return {
              field: transformation(getattr(event, field))
              for field, transformation in self.serialization_fields.items()
          }
  
  class Serialization:
      def __init__(self, **transformations, ):
          print('Serialization.__init__')
          self.serializer = EventSerializer(transformations)
  
      def __call__(self, event_class):
          print('Serialization.__call__')
          def serialize_method(event_instance: "LoginEvent") -> dict:
              print('Serialization.__call__.serialize_method')
              # -> return EventSerializer.serialize(event_instance)
              return self.serializer.serialize(event_instance)
  
          # LoginEvent에 serialize 속성에 serialize_method 할당
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
          print('LoginEvent.__init__')
          self.username = username
          self.password = password
          self.ip = ip
          self.timestamp = timestamp
  
  
  le = LoginEvent('JH', '1234', '123.0.0.1', datetime(2020, 9, 22, 22, 26))
  print(le.serialize())
  # 1. Serialization.__init__
  # 2. EventSerializer.__init__
  # 3. Serialization.__call__
  # 4. LoginEvent.__init__
  # 5. Serialization.__call__.serialize_method
  # 6. EventSerializer.serialize
  # {'username': 'jh', 'password': '**redacted**', 'ip': '123.0.0.1', 'timestamp': '2020-09-22 22:26'}
  
  ```

  - le.serialize()는 (#5)Serialization.\_\_call\_\_.serialize_method()를 호출하고 내부에서 (#6)EventSerializer.serialize()를 실행시킨다.

  

  ### 코드 개선

  단순히 속성을 저장하기 위한 클래스를 사용할 경우 **@dataclass** 데코레이터를 이용할 수 있다.
  
  ```python
  @Serialization(username=str.lower, password=hide_field, ip=show_original, timestamp=format_time)
  @dataclass
  class LogoutEvent:
      username: str
      password: str
      ip: str
      timestamp: datetime
  
  
  le = LogoutEvent('JH', '4567', '123.0.0.1', datetime(2020, 9, 22, 9, 30))
  print(le.serialize())
  {'username': 'jh', 'password': '**redacted**', 'ip': '123.0.0.1', 'timestamp': '2020-09-22 9:30'}

  ```
  
  

<br>



**[처음으로](#200922)**

<br>





# 데코레이터에 인자 전달

**데코레이터에 인자를 전달하는 방법**

- 간접 참조(중첩 함수 - 가독성이 떨어짐)
- 데코레이터를 위한 클래스(가독성이 뛰어남)

<br>

### 중첩 함수의 데코레이터

데코레이터에 인자를 전달하기 위해 3단계로 이루어진 중첩함수를 생성한다.

- 첫 번째 함수: 파라미터를 받아서 내부 함수에 전달

- 두 번째 함수: 데코레이터가 될 함수

- 세 번째 함수: 데코레이팅 결과 반환

  ```python
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
              fail_n_times: int = 0,  
              exception_cls=ControlledException,
      ):
          self._task = task
          self._fail_n_times = fail_n_times  # 입력된 실패 횟수
          self._times_failed = 0  # 실행중 실패한 횟수
          self._exception_cls = exception_cls
  
      def run(self):
          called = self._task.run()
          if self._times_failed < self._fail_n_times:
              self._times_failed += 1
              raise self._exception_cls(f"{self._task} failed!")
          return called
  
  
  oo = OperationObject()
  rwf = RunWithFailure(oo, 2)  # oo에서 run()이 이미 한번 실행된 상태
  
  
  @with_retry(retries_limit=3)
  def run_operation(task):
      return task.run()  
  
  
  @with_retry(retries_limit=3)
  def run_operation_with_fail(task):
      return task.run()  
  
  
  print(run_operation(oo))  # 1(실행) 
  print(run_operation_with_fail(rwf))  # 4(실행, 실패, 실패, 실행)
  ```

<br>



### 클래스를 이용한 데코레이터

```python
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

oo = OperationObject()
rf = RunWithFailure(oo)
print(run_operation(oo, 2))  # 1
print(run_operation_with_fail(rf)  # 4
```

- @WithRetry(retries_limit=3): 데코레이터 객체 생성 이후 초기화
- run_operation을 래핑하고 \_\_call\_\_() 호출
  - wrapped(*args, **kwargs): 래핑된 함수의 위치 인자와 키워드 인자가 args, kwargs에 전달

<br>



### 데코레이터 사례

- **파라미터 변환:** 함수의 서명을 변경하는 경우. 이 때 파라미터가 어떻게 처리되고 변환되는지 캡슐화하여 숨길 수 있음(사전/사후조건을 강제할 수 있다)
- **코드 추적:** 파라미터와 함께 함수의 실행을 로깅하려는 경우
- **파라미터 유효성 검사**
- **재시도 로직 구현**
- **일부 반복 작업을 데코레이터에 위임**



<br>



**[처음으로](#200922)**

<br>



# 데코레이터 활용

### 래핑된 원본 객체의 데이터 보존

- @wraps를 사용하지 않을 경우 원본 객체의 데이터가 유지되지 않는다.

  ```python
  def trace_decorator(function):
      def wrapped(*args, **kwargs):
          logger.info("%s 실행", function.__qualname__)
          return function(*args, **kwargs)
      return wrapped
      
  @trace_decorator
  def process_account(account_id):
      logger.info("%s 계정처리", account_id)
  
  help(process_account)
  # Help on function wrapped in module __main__:
  # 
  # wrapped(*args, **kwargs)
  print(process_account.__qualname__)
  # trace_decorator.<locals>.wrapped 
  ```

  - **help():** 원본 함수(process_account)가 아닌 wrapped 함수를 나타냄(process_account를 찾을 수 없음)
  - 만약 docstring을 작성한 경우, 데코레이터에 덮어 써진다는 문제가 생긴다.

<br>

### 데코레이터 부작용

- 실행시간을 기록하는 데코레이터를 작성한다고 가정하고 아래의 코드를 작성

  ```python
  def traced_function_wrong(function):
      logger.info("%s 함수 실행", function)
      start_time = time.time()  # 문제 지점
      
      @wraps(function)
      def wrapped(*args, **kwargs)
  ```

  - 데코레이터는 **임포트 시점**에 이미 한번 실행된다.
    - **process_with_delay = traced_function_wrong(process_with_delay)** 이 구문이 import에서 실행된다.
  - 시간을 측정하는 시점(logger.info...)을 wrapped 함수 내에 구현해야 한다.

**데코레이터 작성 시 import 시점에 아직 로딩되지 않을 수 있는 객체에 대해 고려해야 한다.**

<br>

### 데코레이터 부작용의 활용

```python
# test/clean_code.py
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
    
    
# test/decorator_side_effect.py
from test.clean_code import EVENT_REGISTRY
print(EVENT_REGISTRY)
# {'UserLoginEvent': <class 'test.clean_code.UserLoginEvent'>, 'UserLogoutEvent': <class 'test.clean_code.UserLogoutEvent'>}

```

- clean_code의 일부 모듈을 불러오는 순간(import 시점) 각 decorator가 한 번씩 실행된다.
- 이때 register_event함수에 의해 EVENT_REGISTRY에 값이 채워진다.
  - 많은 웹 프레임워크나 라이브러리들이 이 원리로 객체를 노출하거나 활용하고 있다.

<br>



**[처음으로](#200922)**

<br>



# Generic decorator(어느곳에서나 동작하는 데코레이터)



- 데코레이터를 함수나 클래스, 메서드 또는 정적 메서드 등 여러 곳(여러 객체 타입)에서 사용할 수 있는 데코레이터가 필요할 수 있다.

  ```python
  class DBDriver:
      def __init__(self, dbstring):
          self.dbstring = dbstring
  
      def excute(self, query):
          return f"{self.dbstring} 에서 쿼리 {query} 실행"
  
  def inject_db_driver(function):
      @wraps(function)
      def wrapped(dbstring):  # 한 개의 파라미터를 인자로 받는다.
          return function(dbstring)
  
      return wrapped
  
  @inject_db_driver
  def run_query(driver):
      return driver.excute('test_function')
  
  dbd = DBDriver('test')
  print(run_query(dbd)) # 정상 동작
  # test 에서 쿼리 test_function 실행
  
  class DataHandler:
      @inject_db_driver
      def run_query(self, driver):  # 2개의 파라미터를 전달(self가 문제)
          return driver.excute(self.__class__.__name__)
  
  
  DataHandler().run_query('test_fail')  # TypeError: ...
  ```

  - 작성된 wrapped에 전달되는 매개변수는 **1개**이지만 메서드는 기본적으로 **self**를 전달해야하기 때문에 메서드에서 일반 데코레이터를 사용할 경우 **TypeError**를 일으킨다.

  - 이 문제는 클래스 데코레이터를 구성하면서 **\_\_get\_\_** 메서드를 구현한 **디스크립터 객체**를 이용해 해결 할 수 있다.

    ```python
    class inject_db_driver:
        def __init__(self, function):
            self.function = function
            wraps(self.function)(self)
    
        def __call__(self, dbstring):  # function 사용 시 동작
            return self.function(dbstring)
    
        def __get__(self, instance, owner):  # method 사용 시 동작
            if instance is None:
                return self
            return self.__class__(MethodType(self.function, instance))  # *
    
    @inject_db_driver
    def run_query(driver):
        return driver.excute('test_function')
    
    dbd = DBDriver('test')
    print(run_query(dbd))
    # test 에서 쿼리 test_function 실행
    
    class DataHandler:
        @inject_db_driver
        def run_query(self, driver):
            return driver.excute(self.__class__.__name__) 
    
    DataHandler().run_query(dbd)
    print(DataHandler().run_query(dbd))
    # test 에서 쿼리 DataHandler 실행
    ```

    - **[types.MethodType](https://docs.python.org/ko/3/c-api/method.html#method-objects):** 클래스 객체에 함수를 동적으로 연결시킬 수 있다.

    - ***:** inject_db_driver 클래스로부터 생성된 객체(instance)에 self.function **메서드**를 연결시킨다.

      -> method는 self를 제대로 인식할 수 있다.

    - 이후 **\_\_call\_\_** 실행

    - 위 코드는 **[디스크립터](https://github.com/navill/Python_TIL/tree/master/200923#디스크립터)**에 대한 내용을 이해하고 다시 정리 할 예정
    
      

<br>



**[처음으로](#200922)**

<br>

