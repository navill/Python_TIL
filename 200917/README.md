# 200917

- [Sequence](#sequence)
- [Container](#container)
- [객체의 동적인 속성](#객체의-동적인-속성__getattr__)
- [callable](#callable)
- [파이썬에서 유의할 점](#파이썬에서-유의할-점)

- [계약에 의한 디자인](#계약에-의한-디자인)

- [파이썬스러운 계약](#파이썬스러운-계약)

- [방어적 프로그래밍](#방어적-프로그래밍)





# Sequence 

- Sequence는 **len**과 **getitem** 매직 메서드가 구현된 객체를 의미([자체 시퀀스 생성]([https://github.com/navill/Python_TIL/tree/master/200916#%EC%9E%90%EC%B2%B4-%EC%8B%9C%ED%80%80%EC%8A%A4-%EC%83%9D%EC%84%B1](https://github.com/navill/Python_TIL/tree/master/200916#자체-시퀀스-생성)) 참고) 

- iterable과 마찬가지로 반복문을 통해 객체의 여러 요소를 가져올 수 있다.

- 하지만 iterable과 sequence는 메모리와 CPU 사이의 트레이드오프 관계를 나타낸다.

  - iterable: n번째 요소를 메모리에 적재하고 필요할 때 꺼내서 쓴다.
    - 요소 한 개씩 소모하기 때문에 메모리 소모량이 낮음
    - n 번째 요소를 얻기 위한 시간복잡도는 O(n)

  - sequence: 전체 요소를 메모리에 적재하여 사용한다.
    - 전체 요소가 메모리에 할당되기 때문에 메모리 소모량이 높음
    - n번째 요소를 얻기(indexing) 위한 시간복잡도는 O(1)

  ```python
  class DateRangeSequence:
      def __init__(self, start_date, end_date):
          self.start_date = start_date
          self.end_date = end_date
          self._range = self._create_range()
  
      def _create_range(self):
          days = []
          current_day = self.start_date
          while current_day < self.end_date:
              days.append(current_day)
              current_day += timedelta(days=1)
          return days
  
      def __getitem__(self, day_no):
          return self._range[day_no]
  
      def __len__(self):
          return len(self._range)  
      
  drc = DateRangeSequence(date(2020, 9, 17), date(2020, 9, 20))
  print(drc[0])  # 2020-09-17
  print(drc[1])  # 2020-09-18
  print(drc[-1])  # 2020-09-19
  ```

  - 반환된 리스트 객체(days)에 의해 list가 가지고 있는 작업을 수행할 수 있음(음수를 이용한 indexing이 가능한 이유)
  - 내장된 자료구조를 래핑하여 구현할 경우 호환성과 일관성을 올바르게 유지할 수 있다.

- iterable과 sequence(+generator)를 사용할 때 메모리와 cpu의 트레이드 오프 관계를 생각하자.

[처음으로](#200917)



# Container

- Container 객체는 일반적으로 boolean 값을 반환하는 contains 매직 메서드를 구현한 객체를 의미한다.

- 파이썬의 'in' 키워드가 호출될 때 contains 매직 메서드가 호출된다.

  ```python
  element in container == container.__contains__(element)
  ```



**예제:** 2차원 지도에 특정 위치를 표시하는 코드

```python
def mark_coordinate(grid, coord):
    if 0 <= coord.x < grid.width and 0 <= coord.y < grid.height:
        print('Mark:1')
```

- 난해한 코드

  

```python
# 개선된 코드
class Boundaries:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __contains__(self, coord):
        x, y = coord
        # return에서 실제 좌표가 경계를 넘지 않는지 검사
        return 0 <= x < self.width and 0 <= y < self.height

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.limits = Boundaries(width, height)

    def __contains__(self, coord):
        return coord in self.limits  # Boundaries에 검사를 위임

def mark_coordinate(grid, coord):
    if coord in grid:
        print('Mark:1')
    else:
        print('Mark:0')

g = Grid(4, 4)
mark_coordinate(g, [5, 3])  # Mark:0
mark_coordinate(g, [3, 3])  # Mark:1
```

- 실제 비교 구문을 Boundaries에 위임
- 외부에서 mark_coordnate()을 사용할 때 가독성을 높일 수 있다.

[처음으로](#200917)



# 객체의 동적인 속성(\_\_getattr\_\_)

- getattr 매직 메서드를 이용해 객체에서 속성을 얻는 방법 제어

  1. obj.my_attr 호출 

  2. obj.\_\_dict\_\_에서 'my_attr'을 찾는다

  3. \_\_getattribute\_\_('my_attr') 호출 -> 없을 경우 \_\_getattr\_\_('my_attr') 호출 

  4. my_attr 반환

     ```python
     class DynamicAttributes:
         def __init__(self, attribute):
             self.attribute = attribute
     
         def __getattr__(self, attr):
             if attr.startswith('fallback_'):
                 name = attr.replace("fallback_", "")
                 return f"[fallback resolved] {name}"
             raise AttributeError(f"{self.__class__.__name__}에는 {attr} 속성이 없음")
     
     dyn = DynamicAttributes('value')
     print(dyn.attribute)  # value
     
     print(dyn.fallback_test)  # [fallback resolved] test
     
     dyn.__dict__["fallback_new"] = "new value"  
     # 위 코드는 dyn.fallback_new = "new value"와 동일하다.
     print(dyn.fallback_new)  # new value
     
     print(getattr(dyn, 'something','default'))  # default
     print(dyn.something)  # AttirbuteError: ... 
     ```

     - dyn.fallback_test: 객체에 없는 fallback_test 속성을 호출 -> \_\_getattr\_\_이 호출되면서 문자열을 반환한다.
     - getattr(dyn, 'something', 'default'): 디폴트값을 설정할 경우, exception이 일어날 때 디폴트 값이 반환된다.

[처음으로](#200917)



# callable

- \_\_call\_\_ 매직 메서드를 구현할 경우 객체를 일반 함수처럼 호출 할 수 있다.

- 전달된 모든 파라미터는 \_\_call\_\_에 전달된다.

- callable 매직 메서드를 이용해 (상태를 저장하고 있는)객체를 함수처럼 호출하여 상태를 전달하거나 변경할 수 있다.

  ```python
  class CallCount:
      def __init__(self):
          self._count = defaultdict(int)
  
      def __call__(self, argument):
          self._count[argument] += 1
          return self._count[argument]
  
  cc = CallCount()
  print(cc(1))  # 1
  print(cc(1))  # 2
  print(cc(1))  # 3
  print(cc(2))  # 1
  print(cc(3))  # 1
  print(cc(2))  # 2
  print(cc('something'))  # 1
  ```

  - 객체를 생성할 때 _count는 dict 타입의 속성을 갖는다.
  - cc객체에 **매개 변수**를 전달할 경우 **\_\_call\_\_ 메서드의 매개변수**로 전달된다.
  - 해당 매개변수는 _count의 **키**로 사용되며 값으로 호출된 만큼의 숫자가 **값**으로 저장된다.

[처음으로](#200917)



# 파이썬에서 유의할 점



### 매개변수의 기본값으로 가변형 데이터를 사용하면 안된다.

### 내장 타입 확장

- str, list, dict를 확장하고자 할 때는 반드시 collections의 UserString, UserList, UserDict를 상속받아 확장해야한다.

  ```python
  class BadList(list):
      def __getitem__(self, index):
          print(self.__class__)
          value = super().__getitem__(index)
          if index % 2 == 0:
              prefix = '짝수'
          else:
              prefix = '홀수'
          return f"[{prefix}] {value}"
  
  bl = BadList((0, 1, 2, 3, 4, 5))
  print(bl)  # [0, 1, 2, 3, 4, 5]
  print("".join(bl))  # TypeError: ... => join에 입력된 매개변수가 숫자일 것이라 예상하기 때문에 error
  ```

  - built-in list를 확장할 경우 BadList의 \_\_getitem\_\_ 이 아닌 list의 매직 메서드가 실행된다(print 출력 안됨)

  ```python
  class GoodList(UserList):
      def __getitem__(self, index):
          print(self.__class__)
          value = super().__getitem__(index)
          if index % 2 == 0:
              prefix = '짝수'
          else:
              prefix = '홀수'
          return f"[{prefix}] {value}"
  
  bl = GoodList((0, 1, 2, 3, 4, 5))
  print(bl)  # [0, 1, 2, 3, 4, 5]
  # __getitem__이 호출된 수 만큼 <class '__main__.GoodList'> 출력됨
  print(";".join(bl))  # [짝수] 0;[홀수] 1;[짝수] 2;[홀수] 3;[짝수] 4;[홀수] 5;
  ```

  - UserList를 호출할 경우 정상적으로 GoodList의 getitem 매직 메서드가 실행된다.

[처음으로](#200917)





# 계약에 의한 디자인

계약(contract): 코드가 정상적으로 동작하기 위해 기대하는 것(input)과 호출자가 반환 받기를 기대하는 것(output)은 코드 디자인에 포함되어있어야 한다.

- 오류를 쉽게 찾아낼 수 있고, 잘못된 가정하에 코드의 핵심부분이 동작하는 것을 막기 위해 사용된다.

- 관계자(사용자 또는 클라이언트 코드)가 기대하는 바를 코드에 삽입하는 대신 **양측이 동의하는 계약**을 하고, 계약을 어길 경우 명시적으로 왜 계속 할 수 없는지 예외를 발생시켜야 한다. 코드 레벨에서는 **사전조건**과 **사후조건**으로 나뉜다.



**사전조건(Precondition)** - Client 책임

- 코드가 실행되기 전에 체크해야하는 것들(ex: 파라미터의 유효성 체크)
- 런타임 중에 확인할 수 있다 -> 사전조건에 맞지않으면 코드가 실행되면 안된다.
  - **관용적인(tolerant) 접근법**: 클라이언트가 함수를 호출하기 전에 **인가될 파라미터의 유효성을 검사**
  - **까다로운(demanding) 접근법**: 함수가 자체적으로 로직을 실행하기 전 **인가된 파라미터의 유효성을 검사(지향)**
  - 두 접근법 중 **한 가지만** 사용해야한다 - 중복 제거 원칙 준수



**사후조건(Postcondition)** - Module or Component 책임

- 코드가 실행된 후 체크해야하는 것들(ex: 반환 값에 대한 유효성 체크)

- 사후조건을 만족할 경우 특정 속성이 보전되도록 보장해야하며, 조건에 맞지 않을 경우 **예외 처리**를 하여 호출자에게 알려야한다.
- 사용자는 아무 문제 없이 반환 객체를 사용할 수 있어야 한다.

[처음으로](#200917)



# 파이썬스러운 계약

- 메서드, 함수 및 클래스에 RuntimeError 또는 ValueError 예외를 발생시키는 제어 메커니즘을 추가
- 문제를 정확히 특정하기 어려운 사용자 정의 예외를 만들어서 사용
- 코드를 격리된 상태 유지 -> 사전조건에 대한 검사, 사후 조건에 대한 검사, 핵심 기능을 구분하여 구현해야한다(데코레이터를 이용하여 분리할 수 있다).

[처음으로](#200917)



# 방어적 프로그래밍

- 방어적 프로그래밍: 계약을 통해 성공과 실패를 포함한 모든 조건을 서술하는 대신, 객체, 함수 또는 메서드와 같이 코드 레벨에서 유효하지 않은 것으로부터 보호하는 방법
- 예상할 수 있는 시나리오의 오류를 처리하는 방법 - 에러 핸들링 프로시저
- 발생하지 않아야 하는 오류를 처리하는 방법 - 어썰션(assertion)

[처음으로](#200917)



### 에러 핸들링

**값 대체**

- 예상되는 에러에 대해 계속 실행할지 아니면 중단할지 결정하는 것
  - 값 대체: 잘못된 값을 생성하거나 시스템에 치명적인 위험(프로그램이 종료되는)이 있을 경우 결과값을 안전한 값(잘 알려진 상수, 초기값 등)으로 대체
    - 제공되지 않은 데이터에 기본값을 사용하는 방법

**예외 처리**

- 함수는 발생한 오류에 대해 명확하고 분명하게 호출자에게 알려주고 적절히 처리할 수 있도록 해야 한다.

- 예외를 이용해 시나리오나 비지니스 로직을 처리하려고 할 경우 프로그램의 흐름을 이해하기 어려워질 수 있기 때문에 지양하는 것이 좋다.

  - 예외는 반드시 호출자가 아얄아하는 실질적인 문제를 알리기 위한 용도로 사용해야 한다.
  - 예외는 오직 한가지 일을 하는 함수의 한 부분이어야 한다.

  ```python
  import logging
  import time
  
  logger = logging.getLogger(__name__)
  
  
  class Connector:
      """Abstract the connection to a database."""
  
      def connect(self):
          """Connect to a data source."""
          return self
  
      @staticmethod
      def send(data):
          return data
  
  
  class Event:
      def __init__(self, payload):
          self._payload = payload
  
      def decode(self):
          return f"decoded {self._payload}"
  
  
  class DataTransport:
      """An example of an object badly handling exceptions of different levels."""
  
      retry_threshold: int = 5
      retry_n_times: int = 3
  
      def __init__(self, connector):
          self._connector = connector
          self.connection = None
  
      def deliver_event(self, event):  
          try:
              self.connect()  # *
              data = event.decode()  # **
              self.send(data)
          except ConnectionError as e:  # from *
              logger.info("connection error detected: %s", e)
              raise
          except ValueError as e:  # from **
              logger.error("%r contains incorrect data: %s", event, e)
              raise
  
      def connect(self):
          for _ in range(self.retry_n_times):
              try:
                  self.connection = self._connector.connect()
              except ConnectionError as e:
                  logger.info(
                      "%s: attempting new connection in %is",
                      e,
                      self.retry_threshold,
                  )
                  time.sleep(self.retry_threshold)
              else:
                  return self.connection
          raise ConnectionError(
              f"Couldn't connect after {self.retry_n_times} times"
          )
  
      def send(self, data):
          return self.connection.send(data)
  
  ```

  - 주석이 달린 두 예외는 서로 관련이 없음 -> 별도의 예외로 나뉘어야 한다.
    - ConnectionError -> self.connect
    - ValueError -> event.decode()

  ```python
  def connect_with_retry(connector, retry_n_times, retry_threshold=5):
      for _ in range(retry_n_times):
          try:
              return connector.connect()
          except ConnectionError as e:
              logger.info(
                  "%s: attempting new connection in %is", e, retry_threshold
              )
              time.sleep(retry_threshold)
      exc = ConnectionError(f"Couldn't connect after {retry_n_times} times")
      logger.exception(exc)
      raise exc
      
  class DataTransport:
      """An example of an object that separates the exception handling by
      abstraction levels.
      """
  
      retry_threshold: int = 5
      retry_n_times: int = 3
  
      def __init__(self, connector):
          self._connector = connector
          self.connection = None
  
      def deliver_event(self, event):
          self.connection = connect_with_retry(
              self._connector, self.retry_n_times, self.retry_threshold
          )
          self.send(event)
  
      def send(self, event):
          try:
              return self.connection.send(event.decode())
          except ValueError as e:
              logger.error("%r contains incorrect data: %s", event, e)
              raise
  
  ```

  - deliver_event() 메서드는 이벤트를 전달하는 기능을 담당하고, 연결(connect_with_retry)과 전송(send)에서 각각의 에러를 처리한다.
    - 개인적인 생각: event.decode()에서 발생하는 에러(ValueError)는 Event.decode 메서드에서 처리하는게 맞지 않을까 생각함([사전조건-demanding 접근법](#계약에-의한-디자인))

**Traceback 노출금지**

- 특정 예외를 효율적으로 해결할 수 있또록 traceback 정보, 메시지 등을 로그로 남기는 것은 중요하지만 절대 세부사항을 사용자에게 드러내서는 안된다.

**비어있는 except(극 안티패턴) 블록 지양**

- 예상되는 문제가 발생할 경우 반드시 그에 맞는 조치를 취해야한다.
- except: pass 블록은 이를 무시하는 행위로 올바른 동작을 방해할 뿐만 아니라 유지보수를 어렵게 한다.
  - 아래의 두 항목을 적용하라
    1. 광범위한 예외(Exception)보다 구체적인 예외(AttributeError, KeyError 등)를 사용하라
    2. except 블록에서 실제 오류 처리

**원본 예외 포함**

```python
class InternalDataError(Exception):
    """업무 도메인 데이터의 예외"""

def process(data_dictionary, record_id):
    try:
        return data_dictionary[record_id]
    except KeyError as e:
        raise InternalDataError("기록 없음") from e
```

- 원본 예외(KeyError)를 사용자 정의 예외(InternalDataError)로 래핑할 때 **raise \<exception\> from \<original exception\>** 을 사용한다.
- 원본의 traceback이 새로운 exception에 포함되고, 원본 예외는 exception.\_\_cause\_\_ 속성으로 설정된다.

[처음으로](#200917)

























