# 200921

### SOLID 법칙
- [단일 책임 원칙](#단일-책임-원칙single-responsibility-principle)

- [개방/폐쇄 원칙](#개방폐쇄-원칙openclose-principle)

- [리스코브 치환 원칙](#리스코프-치환-원칙liskov-substitution-principle)

- [인터페이스 분리 원칙](#인터페이스-분리-원칙interface-segregation-principle)

- [의존성 역전 원칙](#의존성-역전dependency-inversion)

    

**[처음으로](#200921)**

  


# 단일 책임 원칙(Single Responsibility Principle)
- 소프트웨어 컴포넌트(일반적으로 클래스)는 단 하나의 책임을 가져야 한다.
- 변경해야할 이유도 단 하나뿐이다.

- 클래스의 속성과 프로퍼티는 메서드를 통해 사용되도록 유도 - 관련된 개념끼리 추상화 가능
  - 관계형 데이터베이스의 정규화와 유사함: 만일 객체의 속성이나 메서드의 특성이 다른 그룹이 발견될 경우, 그들을 다른 곳으로 옮겨야 한다.



**너무 많은 책임을 가진 클래스**

```python
# 세부 구현은 제외
class SystemMonitor:
    def load_activity(self):
        """소스에서 처리할 이벤트 가져오기"""

    def identify_events(self):
        """가져온 데이터를 파싱하여 도메인 객체 이벤트로 변환"""

    def stream_events(self):
        """파싱한 이벤트를 외부 에이전트로 전송"""
```

- 각각의 독립적인 동작을 하는 메서드를 하나의 인터페이스에 정의

- 각 메서드는 클래스의 책임을 대표하는 기능 -> 한 클래스에 여러 책임을 갖는다.

  이는 각 책임마다 수정사유가 발생하므로 기능(메서드) 하나를 수정하기 위해 클래스를 수정해야 한다.

  => 클래스의 유지보수가 어려워진다.

**책임 분산**

```python
class AlertSystem:
    def run(self):
      	"""경고 시스템 실행"""
    # 1, 2, 3
    
class ActivityReader:  # 1
    def load(self):
        """소스에서 처리할 이벤트 가져오기"""

class SystemMonitor:  # 2
  	def identify_event(self):
        """가져온 데이터를 파싱하여 도메인  객체 이벤트로 변환"""
        
class Output:  # 3
    def stream(self):
        """파싱한 이벤트를 외부 에이전트로 전송"""
```

- 각각의 기능을 갖춘 객체들과(ActivityReader, SystemMonitor, Output) 객체들과 협력하여 동일한 기능을 수행하는 객체(AlertSystem)로 구성

  ex: 데이터 로드 방법을 변경하더라도 AlertSystem과 나머지 클래스들은 변경하지 않아도 된다 - 독립성이 보장된다.

- 만약 어플리케이션에서 로그를 다른용도로 읽어야 한다고 할 때, ActivityReader 객체를 사용할 수 있다.

  - 기존의 방법은 SystemMonitor를 사용해야하기 때문에 불필요한 메서드(identify_event(), stream_event())를 가져와야만 한다.

- 처리해야할 로직이 같은 경우 **하나의 클래스에 여러 메서드가 추가될 수 있다**(개념상 관련된 기능인지 확인하고 그렇지 않을 경우 **새로운 클래스로 분리**하라)

    

**[처음으로](#200921)**

  



# 개방/폐쇄 원칙(Open/Close Principle)

- 확장에는 개방, 수정에는 폐쇄적인 클래스를 디자인하라

- 이상적으로는 요구사항이 변경되면 새로운 기능을 구현하기 위한 모듈만 확장하고, 기존 코드는 변경하지 않아야 한다.

  ```python
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
      """시스템에서 발생한 이벤트 분류
  
      >>> l1 = SystemMonitor({"before": {"session": 0}, "after": {"session": 1}})
      >>> l1.identify_event().__class__.__name__
      'LoginEvent'
  
      >>> l2 = SystemMonitor({"before": {"session": 1}, "after": {"session": 0}})
      >>> l2.identify_event().__class__.__name__
      'LogoutEvent'
  
      >>> l3 = SystemMonitor({"before": {"session": 1}, "after": {"session": 1}})
      >>> l3.identify_event().__class__.__name__
      'UnknownEvent'
  
      """
  
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
  
  ```

  - 위 코드의 문제는 이벤트 논리를 결정하는 로직이 하나의 메서드에 중앙화되어 있다.

    - 새로운 기능을 추가할 때 마다 identify_event()는 커진다.

      \+ elif 명령문 체인은 가독성 측명에서 최악이므로 사용하지 말자

    - 기능 추가를 위해 이 메서드를 수정한다는 의미는 폐쇄 원칙에 위반된다.

  

**확장성을 가진 이벤트 시스템(리팩토링)**

```python
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
    """시스템에서 발생한 이벤트 분류

    >>> l1 = SystemMonitor({"before": {"session": 0}, "after": {"session": 1}})
    >>> l1.identify_event().__class__.__name__
    'LoginEvent'

    >>> l2 = SystemMonitor({"before": {"session": 1}, "after": {"session": 0}})
    >>> l2.identify_event().__class__.__name__
    'LogoutEvent'

    >>> l3 = SystemMonitor({"before": {"session": 1}, "after": {"session": 1}})
    >>> l3.identify_event().__class__.__name__
    'UnknownEvent'

    """

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

```

- identify_event는 특정 이벤트 타입 대신 인터페이스를 따르는 제네릭 이벤트와 동작
  - 제네릭들은 모두 meets_condition을 구현하여 다형성을 보장한다.

- 새로운 기능을 추가할 때 단지 Event클래스를 상속받고 로직에 meets_condition() 메서드를 구현하기만 하면 된다.
  - Event는 **확장 원칙**을 보장하고, identify_event는 **폐쇄 원칙**을 보장한다.



### OCP 정리

- 이 원칙은 다형성의 효과적인 사용과 밀접한 관련 및 유지보수성에 대한 문제 해결
- OCP를 위반할 경우 파급효과가 생기거나 작은 변경사항이 시스템 전체에 영향을 미칠 수 있다.
- 모든 프로그램에서 이 원칙을 적용하는 것이 가능하지 않지만 최대한 개방 폐쇄 원칙을 따르도록 디자인해야한다.

  

**[처음으로](#200921)**



  

# 리스코프 치환 원칙(Liskov Substitution Principle)

- 설계 시 안정성을 유지하기 위해 객체 타입이 유지해야하는 일련의 특성
  - 만약 S가 T의 하위 타입이라면 프로그램을 변경하지 않고 T타입의 객체를 S타입의 객체로 지환 가능해야한다.

    ```python
    
    class Event:
        ...
    
        def meets_condition(self, event_data: dict) -> bool:
            return False
    
    class LoginEvent(Event):
        def meets_condition(self, event_data: list) -> bool:
            return bool(event_data)
    
    class LogoutEvent(Event):
        def meets_condition(self, event_data: dict, override: bool) -> bool:
            if override:
                return True
    ```

    - LoginEvent의 메서드는 Event에서 정의한 메서드와 다른 타입의 파라미터를 사용한다.
      - Client는 Event와 동일한 매개 변수를 사용하더라도 LoginEvent가 동작하길 기대하지만, LoginEvent의 메서드에 dict 타입의 파라미터를 전달할 경우 에러를 일으킬 수 있다.

    - LogoutEvent는 계층 구조의 호환성을 깨는 클래스 - 아무런 변경사항 없이 Event와 동일하게 사용할 수 없다.



### 에매한 위반

- 자동화 검사 모듈(pylint)로 검출되지 않는 오류는 코드 리뷰를 통해 확인해야한다.

```python
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
        # dict type (강한)사전조건 검사
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
        # get이 아닌 기존의 코드(event_data['after']['session'])로 사용할 경우 transaction은 			      # KeyError를 일으킨다.
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

```

- 서브 클래스는 기반(Event) 클래스의 **사전조건**과 같거나 **더 약한 수준**의 사전조건으로 대체할 수 있다.

  - 기반 클래스의 사전조건에 실패할 경우 시스템 실패로 처리해도 무방
  - 만약 서브 클래스를 기반 클래스로 대체 할 때, 기반 클래스의 사전조건보다 **매우 강한 수준**일 경우 기존에 통과하던 조건들이 통과할 수 없는 문제가 생길 수 있다.

- 서브 클래스는 기반 클래스의 **사후조건**과 같거나 **더 강한 수준**의 사후조건으로 대체할 수 있다.

  - 만약 서브 클래스를 기반 클래스로 대체할 때, 기반 클래스의 사후조건보다 **매우 약한 수준**일 경우 사후조건을 통과할 수 없는 조건들이 통과할 수 있는 문제가 있다. 

    

### LSP 정리

- LSP는 자식 클래스가 부모 클래스의 다형성을 유지하도록 한다.
- 새로운 클래스가 원래의 계약과 호환되지 않는 상태에서 확장하려 할 경우 오류를 일으킬 수 있다.
  - 확장을 위해 코드를 수정할 경우 폐쇄되어야 한다는 [OCP](#개방_폐쇄-원칙)를 위반하게 된다.
- **LSP**를 준수하여 디자인된 클래스는 **OCP**에 기여한다.

  

**[처음으로](#200921)**

  



# 인터페이스 분리 원칙(Interface Segregation Principle)

- **인터페이스**: 객체가 노출하는 **메서드의 집합**
- 클래스에 노출된 동작의 정의와 구현을 분리
- 객체의 본질을 정의하는 것은 궁극적으로 **메서드의 형태** - Duck typing
  - **Duck typing**: "어떤 새가 오리처럼 걷고 꽥꽥 소리를 낸다면 오리여야만 한다" -> 클래스의 메서드가 오리처럼 걷고 꽥꽥 소리를 낸다면 그것은 오리 클래스여야만 한다.

- **ISP**: 다중 메서드를 가진 인터페이스가 있다면 매우 정확하고 구체적인 구분에 따라 더 적은 수의 메서드(가급적 한 개)를 가진 여러 개의 메서드로 분할하는 것이 좋다.



**너무 많은 일을 하는 인터페이스**

```python
class EventParser:
    def from_xml(self):
    		"""xml 데이터 파싱"""

    def from_json(self):
        """json 데이터 파싱"""
```

- EventParser.from_json()을 사용할 때 필요하지 않은 from_xml이 제공된다.
- 결합력을 높이고 유연성을 떨어뜨리는 구조

**독립적인 인터페이스**

```python
class XMLEventParser:
    def from_xml(self):
    		"""xml 데이터 파싱"""

class JSONEventParser:
    def from_json(self):
        """json 데이터 파싱"""
```

- 각 메서드의 독립성이 보장되고 작은 객체를 이용해 기능을 유연하게 조합할 수 있다.

- SRP와 유사하지만 ISP는 인터페이스의 관점 - 행동의 추상화
  - 인터페이스가 실제 구현될 때 까지는 아무 것도 정해진 것이 없음

**인터페이스의 규모**

- 추상 클래스를 포함해 기본 클래스는 다른 클래스들이 확장할 수 있도록 인터페이스를 잘 정의해야 한다.
- 위 예제에서는 전혀 관련없는 두 메서드를 분리하여 개별적인 인터페이스를 구현하였지만, 필요에 따라 둘 이상의 메서드가 포함될 수 있다(ex: context manager의 \_\_enter\_\_(), \_\_exit\_\_())

  

**[처음으로](#200921)**



  

# 의존성 역전(Dependency Inversion)

- 상위 모듈은 하위 모듈에 의존해서는 안된다 - 추상화에 의존해야한다.
- 추상화는 세부사항에 의존해서는 안된다 - 세부사항이 추상화에 의존해야 한다. [wiki](https://ko.wikipedia.org/wiki/의존관계_역전_원칙)



예) 상호 교류하는 A와 B 객체가 있다고 생각해보자. A는 B의 인스턴스를 사용하지만 B모듈(외부 라이브러리)을 직접 관리하지 않는다. 만약 B에 크게 의존할 경우, B가 변경될 때 정상적인 동작을 기대하기 어려워진다.

이때 **의존성 역전 원칙**이 필요하다.

기존에 B에 의존하던 A의 관계를 **B가 A에 의존**하도록 하는 것. A는 인터페이스(**추상 클래스**)로 구성하고, 이를 준수하는 것은 **B의 책임**이 된다.

- 시스템의 변경, 수정 또는 확장될 것으로 예상되는 지점에 유연성 확보를 위해 추상화(인터페이스)를 사용한다.



### 엄격한 의존의 예 ([잔재미 코딩](https://www.fun-coding.org/PL&OOP2-1.html))

```python
class BubbleSort:  # B
    def bubble_sort(self): 
        # sorting algorithms
        pass
      
class SortManager:  # A
    def __init__(self):
        self.sort_method = BubbleSort() # <--- SortManager 는 BubbleSort에 의존적
        
    def begin_sort(self): 
        self.sort_method.bubble_sort() # <--- BubbleSort의 bubble_sort 메서드에 의존적
        
sortmanager = SortManager()
sortmanager.begin_sort()  
```

- 위 코드에서 만약 bubble_sort의 메서드명을 변경할 경우 begin_sort 메서드는 실행될 수 없다.

  **-> A가 B에 의존하는 관계**



### 의존성을 거꾸로

```python
class Sort(metaclass=ABCMeta):
    @abstractmethod
    def sort(self):
        pass

class BubbleSort(Sort):  # B
    def sort(self): 
        # sorting algorithms
        pass
      
class SortManager:  # A
    def __init__(self, sort_method):  # 의존성 주입
        self.sort_method = None  # 실제로 이렇게 짜면 안됨...
        self.set_sort_method(sort_method)
        
    def set_sort_method(self, sort_method):
        self.sort_method = sort_method
        
    def begin_sort(self):
        self.sort_method.sort()  # A.begin_sort에서 B에 대한 의존성을 강제한다.
```

**-> B가 A에 의존하는 관계(엄밀히 말하면 B가 추상화에 의존하는 관계)**

- Sort 클래스를 상속받는 모든 자식 클래스는 sort 메서드를 포함해야한다.
- SortManager.begin_sort는 추상 클래스의 인터페이스를 따르기 때문에 모든 Sort의 자식 클래스는 동작이 가능하다.

- 다른 Sort의 자식 클래스가 생성되어도 **동일한 인터페이스를 강제**하기 때문에 **추가 또는 변경없이 동작이 가능**하다.



늘 필수는 아니지만 추상 클래스를 통해 인터페이스를 구성하는 것은 좋은 습관이다

- Duck typing이 가능해지면서 모델의 가독성이 높아진다.
  - class의 상속관계는 **'is a'**관계이다.
  - 'BubbleSort' is 'Sort' = 코드 사용자는 BubbleSort가 Sort의 인터페이스로 구성되었음을 알 수 있다.
  - 자주 발생할 수 있는 실수를 줄일 수 있다.





**[처음으로](#200921)**

