# 200930

- **[행동 패턴](#행동-패턴)**

    - **[책임 연쇄](#책임-연쇄-패턴)**

    - **[템플릿 메서드](#템플릿-메서드-패턴)**

<br>

**[처음으로](#200930)**
<br>



# 행동 패턴

-   객체가 어떻게 협력해야하는지, 어떻게 통신해야하는지, 런타임 중에 인터페이스는 어떤 형태여야 하는지에 대한 문제 해결을 목표
-   정적으로는 상속을 통해, 동적으로는 컴포지션을 통해 해결
    -   **[책임 연쇄](#책임-연쇄-패턴)**
    -   **[템플릿 메서드](#템플릿-메서드-패턴)**

<br>

### 책임 연쇄 패턴

-   단일 요청을 충족시키기 위해 여러 객체에게 기회를 주거나 특정 요청을 처리해야 하는 객체를 미리 알 수 없는 경우에 사용 [Notion 정리](https://www.notion.so/navill/Behavioral-Design-Pattern-Chain-of-Responsibility-9486451cbc764ecfb7a262d34c83c2a1)

```python
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

chain = SessionEvent()
print(chain.process("567: login User"))  
# {'type': 'SessionEvent', 'id': '567', 'value': 'User'}
chain = LoginEvent(SessionEvent())
print(chain.process("567: login User"))  
# {'type': 'LoginEvent', 'id': '567', 'value': 'User'}
chain = LogoutEvent(LoginEvent(SessionEvent()))
print(chain.process("567: login User"))  
# {'type': 'LoginEvent', 'id': '567', 'value': 'User'}
```

-   세 번째 chain: 입력값에 대해 LogoutEvent에서 처리할 수 없음

-   LoginEvent(successor)로 작업을 전달하고 처리할 수 있기 때문에 LoginEvent.process 메서드의 첫 번째 조건이 실행되면서 값을 반환

    -   결과:  {'type': **'LoginEvent'**, 'id': '567', 'value': 'User'}

    -   만약 LoginEvent에서 처리할 수 없는 작업이었을 경우 SessionEvent 객체에 작업이 위임된다.

-   책임 연쇄 패턴을 사용할 경우, 작업의 우선순위를 조절할 수 있기 때문에 유연한 코드를 작성할 수 있다.

    ```python
    chain = SessionEvent(LoginEvent())
    ```

    -   SessionEvent를 LoginEvent보다 높은 우선순위로 선언
    -   상황에 따라 우선순위를 유연하게 조절할 수 있다.

 <br>

**[처음으로](#200930)**
<br>



### 템플릿 메서드 패턴

-   어떤 행위를 정의할 때 특정한 형태의 클래스 계층구조를 만드는 것

    -   게층구조를 이루는 모든 클래스는 공통된 템플릿을 공유하며 특정한 요소만 변경할 수도 있음
    -   공통 로직은 부모 클래스의 public 메서드로 구현
        -   하위 계층은 부모 클래스의 public 메서드에 정의된 로직을 사용하기 때문에 재사용성이 향상된다.

-   앞선 예제([책임 연쇄 패턴](#책임-연쇄-패턴))는 이미 템플릿 메서드 패턴을 기반으로 작성됨

    -   Event(부모)는 파생 클래스들이 사용할 공통 로직을 모두 구현 - 클라이언트에게 노출될 **public method(process)**와 내부에서 호출될 **private method(_process, can_process, _parse_data)**로 구성

    -   **private method**는 **파생 클래스의 속성(pattern)**에 의존

        >   **책에서는 추가 메서드는 파생 클래스의 속성에 의존한다**고 되어있지만 public method에서 클래스 속성을 사용(의존)하는 것도 가능할 것이라 생각함.

        -   때문에 새로운 파생 클래스를 정의할 때 추가 메서드들이 의존하는 클래스 속성과 동일한 속성(pattern)을 재정의해야 한다.

    -   반환 값의 타입이 동일하다면 하위 호환성이 유지된다.
        -   클래스의 일부 행동을 수정하기 위해 클라이언트는 하위 클래스를 만들고 특정 private 메서드를 오버라이딩함으로써  호환성이 유지되는 새로운 행동을 정의할 수 있다.

    -   결과적으로 파생 클래스에서 동작해야할 메서드를 호출하는 것은 템플릿 메서드이므로 자연스럽게 [리스코프 치환 원칙](https://github.com/navill/Python_TIL/tree/master/200921#리스코프-치환-원칙liskov-substitution-principle)과 [개방/폐쇄 원칙](https://github.com/navill/Python_TIL/tree/master/200921#개방폐쇄-원칙openclose-principle)을 준수할 수 있다.



 <br>

**[처음으로](#200930)**
<br>























