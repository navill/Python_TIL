# 200918

- [관심사의 분리](#관심사의-분리)
- [컴포지션과 상속](#컴포지션composition과-상속inheritance)
- [상속 안티패턴](#상속-안티패턴)

  
<br>
**[처음으로](#200918)**
<br>


# 관심사의 분리

- 관심사(기능)를 분리하는 목표는 파급 효과를 최소화하여 유지보수성을 향상시킨다.

  파급(ripple): 어느 지점의 변화가 전체로 전파되는 것을 말한다.

  - 응집력(cohesion): 객체는 작고 잘 정의된 목적을 가져야 하며 가능하면 작은 구조를 가져야 한다.

    -> 응집력이 높을수록 더 유용하고 재사용성이 높아진다.

  - 결합력(coupling): 두 개 이상의 객체가 서로 어떻게 의존하는지를 나타낸다(제한을 의미).

    -> 결합력(의존성)이 높을 수록 낮은 재사용성, 높은 파급 효과를 의미한다.
    
    
<br>
**[처음으로](#200918)**
<br>


# 컴포지션(Composition)과 상속(Inheritance)

- 상속에서 가장 많이 사용하는 용도는 재사용

- 하지만 **부모 클래스의 기능을 공짜로 얻기 위해 상속**을 하는것은 **좋은 방법이 아니다**.
  
  - 자식 클래스는 부모와 강력한 결합력을 갖춘 클래스가 된다([관심사의 분리](#관심사의-분리) 위배).
  
- 클래스를 상속할 때 상속된 **모든 메서드**를 실제로 사용하는지 확인하라.
  - 만약 일부 메서드만 사용하고 대부분의 메서드를 오버라이딩하거나 다른 메서드로 대체해야 한다면 설계상의 실수로 볼 수 있다.
    1. 상위 클래스는 잘 정의된 인터페이스 대신 막연한 정의와 너무 많은 책임을 지닌다.
    2. 하위 클래스는 확장하려는 상위 클래스의 적절한 세분화가 아니다.
  
- 상속의 좋은 예를 [BaseHTTPRequestHandler](https://docs.python.org/ko/3/library/http.server.html?highlight=basehttprequesthandler#http.server.BaseHTTPRequestHandler)에서 참고할 수 있다.
  
- BaseHttpRequestHandler를 상속하는 SimpleHTTPRequestHandler는 상위 클래스의 기본 인터페이스를 기준으로 **일부를 추가하거나 변경**하여 확장한다.
  
- 어떤 객체에 잘 정의된 인터페이스를 강제하는 것도 상속의 좋은 예가 될 수 있다.

  
<br>
**[처음으로](#200918)**
<br>


# 상속 안티패턴

- 상속된 메서드(부모)는 새로운 클래스(자식)의 일부가 된다.

- public method는 부모 클래스가 정의하는 것과 일치 해야한다.

  - BaseHTTPReqeustHandler의 자식 클래스가 handle()이라는 메서드를 구현했다면, 부모 클래스의 일부를 오버라이딩한 것임 - HTTP 요청과 관련된 이름의 메서드

  - process_purchase() 같은 메서드를 추가할 경우, 상속된 메서드도 아니며 올바른 확장이라고 보기 어려움 - 부모와 전혀 관련 없는 메서드

  - 위와 같은 문제는 재사용을 목적으로만 상속받을 때 자주 발생한다.

  - **예제**: 여러 고객에게 정책을 적용하는 기능을 가진 관리 시스템

    - 정책이 변경되면 현재 트랜잭션의 모든 고객에게 정책을 적용해야한다.

    ```python
    import collections
    from datetime import datetime
    
    class TransactionalPolicy(collections.UserDict):
        def change_in_policy(self, customer_id, **new_policy_data):
            self[customer_id].update(**new_policy_data)
    
    policy = TransctionalPolicy({
        "client001": {
            "fee": 1000.0,
            "expiration_date": datetime(2020, 9, 18),
        }
    })
    print(policy['client001'])  
    # {'fee': 1000.0, 'expiration_date': datetime.datetime(2020, 9, 18, 0, 0)}
    policy.change_in_policy('client001', expiration_date=datetime(2020, 9, 20))
    print(policy['client001'])  
    # {'fee': 1000.0, 'expiration_date': datetime.datetime(2020, 9, 20, 0, 0)}
    print(dir(policy))
    """
    [..., __weakref__', '_abc_impl', 'change_in_policy', 'clear', 'copy', 'data', 'fromkeys', 'get', 'items', 'keys', 'pop', 'popitem', 'setdefault', 'update', 'values']
    """
    ```

    - 기능은 정상적으로 동작한다.

    - 비용적인 측면에서 볼 때 올바른 코드가 아니다.

    - 두 가지 주요 문제점: 잘못된 계층구조와 강력한 결합력

      **잘못된 계층구조**

      - 기본 클래스를 상속하여 새로운 클래스를 만드는 것은 개념적으로 **확장되고 세부적인 것을 의미**
      - class 이름(TransactionalPolicy)을 보고 dict(부모 클래스)임을 바로 이해하기 어려움 -> 인터페이스에 노출된 public method를 통해 알게될 것이다.

      **강한 결합력**

      - pop(), items()와 같이 dict로부터 전달받은 **불필요한 public method**를 포함한다.
      - public method이므로 잘못된 호출을 할 가능성이 있다(UserDict를 상속 받음으로써 얻는 이득이 없음).

      - 현재 정책을 고객에게 업데이트하는 기능만 필요로하는 메서드에 UserDict 부모 클래스는 의미없음

    - **Solution:** Composition

    ```python
    class TransactionalPolicy:
        def __init__(self, policy_data, **extra_data):
            self._data = {**policy_data, **extra_data}
    
        def change_in_policy(self, customer_id, **new_policy_data):
            self._data[customer_id].update(**new_policy_data)
    
        def __getitem__(self, customer_id):
            return self._data[customer_id]
    
        def __len__(self):
            return len(self._data)
    
    ...
    print(dir(policy))
    """
    [..., '__weakref__', '_data', 'change_in_policy']
    """
    ```

    - 클래스를 dict으로 만들지 않고 **composition**을 통해 dict를 활용한다.

    - private(self._data) 속성에 dict를 저장

    - \_\_getitem\_\_으로 사전의 프록시(중개자)를 생성 

    - 필요한 public method(change_in_policy)를 구현

      ```python
      class TransactionalPolicy:
          def change_in_policy(self, customer_id, **new_policy_data):
              self._data[customer_id].update(**new_policy_data)
      
      policy.change_in_policy('client001', expiration_date=datetime(2020, 9, 20))      
      ```

      - public method는 단지 self_.data의 **update** 기능을 끌어다 쓸 뿐이다.

  - 두 번째 예제는 개념적으로 정확하고 확장성 또한 뛰어나다.

    -> 낮은 결합력과 낮은 파급효과를 갖춘 코드



- 온전히 기본 클래스에 추가적으로, 그리고 보다 특화된 것을 구현할 필요가 있을 때 확장(상속)해야 한다.

  (기본 기능을 바탕으로 구체적이거나 약간 수정된 **'dict'**가 필요할 때에만 사전을 상속받아 확장해야 한다.)

  - 위 예제는 **dict의 전체적인 기능을 유지**하면서 특화된 기능을 추가하는 예제가 아닌, **추가된 메서드**(change_in_policy)의 **기능이 객체의 핵심**이 되는 예제이다.
  - 따라서 solution 예제에서는 **proxy**를 이용해 composition된 dict객체 일부를 사용하고 public 메서드를 추가하여 원하는 기능을 구현

  
<br>
**[처음으로](#200918)**
<br>
