# 200924

- **[디스크립터를 사용한 어플리케이션](#디스크립터를-사용한-어플리케이션)**
- **[다른 형태의 디스크립터](#다른-형태의-디스크립터)**
- **[디스크립터에 대한 추가 고려사항](#디스크립터에-대한-추가-고려사항)**

- **[파이썬 내부에서의 디스크립터 활용](#파이썬-내부에서의-디스크립터-활용)**



<br>



**[처음으로](#20xx)**

<br>



# 디스크립터를 사용한 어플리케이션

```python
class Traveller:
    def __init__(self, name, current_city):
        self.name = name
        self._current_city = current_city
        self._cities_visited = [current_city]

    @property
    def current_city(self):
        return self._current_city

    @current_city.setter
    def current_city(self, new_city):
        if new_city != self._current_city:
            self._cities_visited.append(new_city)
            self._current_city = new_city

    @property
    def cities_visited(self):
        return self._cities_visited


alice = Traveller('alice', 'barcelona')
alice.current_city = 'paris'
alice.current_city = 'brussels'
alice.current_city = 'amsterdam'
print(alice.cities_visited)
# ['barcelona', 'paris', 'brussels', 'amsterdam']
```

-   setter에서 변경되는 사항을 리스트와 같은 내부 변수에 저장

-   만일 alice가 구입한 티켓, 방문했던 모든 국가를 추적하는 등의 일을 하고 싶다면 -> 동일한 로직을 구현한 클래스를 생성해야한다.

-   Solution: 모든 클래스에 적용할 수 있도록 디스크립터를 생성

    ```python
    class HistoryTracedAttribute:
        def __init__(self, trace_attribute_name):
            self.trace_attribute_name = trace_attribute_name  # [1] cities_visited
            self._name = None
    
        def __set_name__(self, owner, name):
            self._name = name  # current_city
    
        def __get__(self, instance, owner):
            if instance is None:
                return self
            print('__get__:', instance.__dict__[self._name])
            return instance.__dict__[self._name]  # __dict__[self._name] 전달
    
        def __set__(self, instance, value):
          	# (A)
            self._track_change_in_value_for_instance(instance, value)  # cities_visited 업데이트
            # (E)
            instance.__dict__[self._name] = value  # __dict__ 업데이트
            print('__set__:', instance.__dict__[self._name])
    
        def _track_change_in_value_for_instance(self, instance, value):
            # (B) 
            self._set_default(instance)  # [2]
            if self._needs_to_track_change(instance, value):
                # (D)
                instance.__dict__[self.trace_attribute_name].append(value)
    
        def _needs_to_track_change(self, instance, value):
            try:
                # (C)
                current_value = instance.__dict__[self._name]
            except KeyError:  # [3]
                return True
            return value != current_value  # [4]
    
        def _set_default(self, instance):
            instance.__dict__.setdefault(self.trace_attribute_name, [])  # [6]
    
    
    class Traveller:
        current_city = HistoryTracedAttribute('cities_visited')  # [1]
    
        def __init__(self, name, current_city):
            self.name = name
            self.current_city = current_city  # [5] __set__() 호출
    
            
    alice = Traveller('alice', 'barcelona')
    # __set__: barcelona
    
    alice.current_city = 'paris'  
    # __set__(): paris
    print('set paris:', vars(alice))
    # set paris: {'name': 'alice', 'cities_visited': ['barcelona', 'paris'], 'current_city': 'paris'}
    
    alice.current_city = 'brussels'
    # __set__(): brussels
    print('set brussels:', vars(alice))
    # set brussels: {'name': 'alice', 'cities_visited': ['barcelona', 'paris', 'brussels'], 'current_city': 'brussels'}
    
    alice.current_city = 'amsterdam'
    # __set__: amsterdam
    print('set amsterdam:', vars(alice))
    # set amsterdam: {'name': 'alice', 'cities_visited': ['barcelona', 'paris', 'brussels', 'amsterdam'], 'current_city': 'amsterdam'}
    
    print(alice.current_city)
    # __get__: amsterda
    # amsterdam
    
    print(alice.cities_visited)
    # ['barcelona', 'paris', 'brussels', 'amsterdam']
    
    ```

    1.  self._name은 클래스(Traveller) 속성의 이름(current_city)을, self.trace_attribute_name추적을 저장할 변수의 이름('cities_visited')을 저장한다.
    2.  디스크립터를 처음 호출 할 때는 추적값이 존재 하지 않기 때문에 setdefault를 이용해 **{'cities_visited': []}**로 초기화한다.

    3.  처음 Traveller를 호출할 때는 방문지가 없으므로 인스턴스 사전에 current_key도 존재하지 않음

        -   KeyError가 일어나는 것이 당연하므로 return True로 처리

            -   A: \_\_set\_\_ 진입하면서 값 변경 추적 메서드 실행

            -   B: 추적 속성 초기화(2번째 단계)

            -   C: current_city(dict에 저장된 current_city('barcelona'))와 새로 추가된 value(alice.current_city='paris')를 비교.

                -   단, 처음 초기화시기에는 instance.\_\_dict\_\_[self._name] **존재하지 않기 때문에** KeyError 예외를  True로 반환**(self.\_name == 'current_city')**

                    (**키값이 존재하지 않는 이유**: 위 예제는 **[데이터 디스크립터](https://github.com/navill/Python_TIL/tree/master/200923#데이터data-디스크립터디스크립터-우선)**로 구성된 코드. 사전보다 디스크립터를 먼저 호출하기 때문에 이 시점에 instance.\_\_dict\_\_에는 **current_city가 존재하지 않는다**. )

            -   D: 추적 속성 리스트에 외부에서 할당된 value('paris')를 추가 
            -   E: 이후 instance.\_\_dict\_\_[self._name] 업데이트

    4.  만약 새로운 장소가 이전에 방문했던 장소와 동일할 경우 return False -> 추적 리스트에 장소를 추가하지 않는다.

    5.  할당 명령(self.current_city=current_city)은 **2**번 단계를 실행하면서 빈 리스트를 생성하고, **3**번을 실행하면서 리스트에 값을 추가하고 'current_city' 키 값을 설정한다.

    6.  **setdefault**는 trace_attribute_name에 대한 KeyError에러를 피하기 위해 사용

        setdefault: 찾으려는 키값이 없을 경우 주어진 키(self.trace_attribute_name)와 값(빈 리스트)으로 초기화 한다.

<br>

**해결 코드를 사용할 경우 여러 클래스 또는 클래스 내의 여러 속성에 적용할 수 있기 때문에 범용성과 재사용성이 향상된다.**

```python
# 여행자가 구매한 티켓과 장소를 추적할 수 있다.
class Traveller:
    current_city = HistoryTracedAttribute('cities_visited')
    current_ticket = HistoryTracedAttribute('tickets_bought')

    def __init__(self, name, current_city):
        self.name = name
        self.current_city = current_city  
        self.current_ticket = current_ticket
```

<br>



**[처음으로](#20xx)**

<br>

# 다른 형태의 디스크립터



<br>

### 전역 상태 공유 이슈

-   디스크립터는 클래스 속성으로 설정해야 한다.

    -   디스크립터 객체에 데이터를 보관하면 모든 객체에 공유됨

        ```python
        class SharedDataDescriptor:
            def __init__(self, initail_value):
                self.value = initail_value
        
            def __get__(self, instance, owner):
                if instance is None:
                    return self
                return self.value
        
            def __set__(self, instance, value):
                self.value = value
        
        class ClientClass:
            descriptor = SharedDataDescriptor('첫 번째 값')
        
        client1 = ClientClass()
        print(client1.descriptor)  # '첫 번째 값'
        client2 = ClientClass()
        print(client2.descriptor)  # '첫 번째 값'
        client1.descriptor = 'client1을 위한 값'
        print(client2.descriptor)  # 'client1을 위한 값'
        print(vars(client1))  # {}
        ```

        -   두 클라이언트 객체가 descriptor를 공유하게 된다.

            -   각 client.\_\_dict\_\_는 비어있고, 디스크립터의 값을 가져오거나 할당한다. 

            -   ClientClass.descriptor는 고유하기 때문에 의도한(객체에 대해 상태 공유를 위한 Borg 패턴) 구조가 아니라면 이 구조는 사용할 수 없다.

        -   이러한 문제를 해결하기 위해 인스턴스의 \_\_dict\_\_에 값을 설정하고 검색해야한다.

<br>

### 약한 참조(특수한 상황에서 사용)

-   \_\_dict\_\_를 사용하지 않으면서 전역 상태 공유 문제를 해결해야할 경우 약한 참조(weakref) 모듈을 사용할 수 있다.
    -   디스크립터 객체가 직접 내부 매핑을 통해 각 인스턴스의 값을 보관하고 반환
    -   단, 이 경우 instance.\_\_dict\_\_을 사용할 수 없다
        -   클라이언트 객체 -> 디스크립터, 디스크립터 -> 클라이언트 객체를 참조하게되어 순환 종속성 발생

    ```python
    from weakref import WeakKeyDictionary
    
    
    class DescriptorClass:
        def __init__(self, initial_value):
            self.value = initial_value
            self.mapping = WeakKeyDictionary()
    
        def __get__(self, instance, owner):
            if instance is None:
                return self
            return self.mapping.get(instance, self.value)
    
        def __set__(self, instance, value):
            self.mapping[instance] = value
    
    
    class ClientClass:
        descriptor = DescriptorClass('첫 번째 값')
    
    
    client1 = ClientClass()
    print(client1.descriptor)  # '첫 번째 값'
    client2 = ClientClass()
    print(client2.descriptor)  # '첫 번째 값'
    client1.descriptor = 'client1을 위한 값'
    print(client2.descriptor)  # '첫 번째 값'
    print(client1.descriptor)  # 'client1을 위한 값'
    ```

    <br>

    **약한 참조를 적용할 때 고려사항**

    -   인스턴스 객체는 더 이상 속성을 보유할 수 없지만**(\_\_dict\_\_가 비어있음)** 디스크립터가 속성을 보유한다.
    -   객체는 반드시 **\_\_hash\_\_** 메서드를 구현하여 **해시 가능한 객체**여야 한다.

<br>



**[처음으로](#20xx)**

<br>

# 디스크립터에 대한 추가 고려사항

<br>

### 코드 재사용

-   프로퍼티가 필요한 구조가 반복되는 경우 디스크립터를 사용할 수 있다.

    -   @porperty: get, set, delete를 포함해 디스크립터 프로토콜을 모두 구현한 디스크립터

    -   이는 더 복잡한 작업에 사용될 수 있음을 의미한다.

-   디스크립터를 이용해 데코레이터가 메서드에서도 동작할 수 있도록 도울 수 있다.
-   클라이언트가 사용하게 되는 API에 대해 디스크립터를 사용하는 것이 좋다.
    -   일회성이 아닌 라이브러리나 프레임워크의 기능을 확장할 수 있기 때문에 반복적으로 사용된다.

-   디스크립터에 비지니스 로직(복잡한 기능 구현)을 넣지 말고 구현 코드를 많이 포함시켜야 한다.

<br>

### 클래스 데코레이터 피하기

-   데코레이터 클래스의 [코드 개선](https://github.com/navill/Python_TIL/tree/master/200922#코드-개선)하기 코드의 두 데코레이터를 디스크립터로 변경

    ```python
    class BaseFieldTransformation:
        def __init__(self, transformation: Callable[[], str]) -> None:
            self._name = None
            self.tranformation = transformation
    
        def __get__(self, instance, owner):
            if instance is None:
                return self
            raw_value = instance.__dict__[self._name]
            return self.tranformation(raw_value)
    
        def __set_name__(self, owner, name):
            self._name = name
    
        def __set__(self, instance, value):
            instance.__dict__[self._name] = value
    
    
    ShowOriginal = partial(BaseFieldTransformation, transformation=lambda x: x)
    HideField = partial(BaseFieldTransformation, transformation=lambda x: "민감한 정보")
    FormatTime = partial(
      BaseFieldTransformation, 
      transformation=lambda ft: ft.strftime("%Y-%m-%d %H:%M")
    )
    
    
    class LoginEvent:
        username = ShowOriginal()
        password = HideField()
        ip = ShowOriginal()
        timestamp = FormatTime()
    
        def __init__(self, username, password, ip, timestamp):
            self.username = username
            self.password = password
            self.ip = ip
            self.timestamp = timestamp
    
        def serialize(self):
            return {
                "username": self.username,
                "password": self.password,
                "ip": self.ip,
                "timestamp": self.timestamp
            }
    
    
    le = LoginEvent('jihoon', 'test1234', '123.123.123.1', datetime.utcnow())
    print(le.username)  # jihoon
    print(le.password)  # 민감한 정보
    print(le.ip)  # 123.123.123.1
    print(le.timestamp)  # 2020-09-24 05:12
    print(le.serialize())
    # {'username': 'jihoon', 'password': '민감한 정보', 'ip': '123.123.123.1', 'timestamp': '2020-09-24 05:15'}
    print(vars(le))
    # {'username': 'jihoon', 'password': 'test1234', 'ip': '123.123.123.1', 'timestamp': datetime.datetime(2020, 9, 24, 6, 3, 43, 180595)}
    ```

    -   \_\_set\_\_에서 instance.\_\_dict\_\_에 값을 할당하기 때문에 vars(le)를 통해 원본 데이터에 접근할 수 있다.

    -   만약 민감한 정보를 메모리상에서 유지하고싶지 않을 경우 아래와 같이 set에서 변경된 데이터를 사전에 저장할 수 있다.

        ```python
        def __get__(self, instance, owner):
            if instance is None:
                return self
            raw_value = instance.__dict__[self._name]
            return raw_value
        
        def __set__(self, instance, value):
            transformed_value = self.tranformation(value)
            instance.__dict__[self._name] = transformed_value
        ...
        
        print(vars(le))
        {'username': 'jihoon', 'password': '민감한 정보', 'ip': '123.123.123.1', 'timestamp': '2020-09-24 06:24'}
        
        ```

        



<br>



**[처음으로](#20xx)**

<br>



# 파이썬 내부에서의 디스크립터 활용

-   좋은 디스크립터는 파이썬에서 사용하는 디스크립터를 참고



### 함수와 메서드

-   함수는 내부에 \_\_get\_\_ 메서드를 구현하고 있기 때문에 클래스 내에서 메서드로 동작한다.
    -   메서드는 추가 파라미터(self)를 가진 함수

    -   메서드는 객체에 바인딩되어 있으며 객체를 수정하는 함수일 뿐이다.

        ```python
        class MyClass:
            def method(self, ...):
                self.x = 1
        
        # 위와 동일
        class MyClass: 
        def method(myclass_instance, ...):
            myclass_instance.x = 1
        method(MyClass())
        
        # ----------------------------------
        
        instance = MyClass()
        instance.method(...)
        
        # 위 코드를 파이썬은 아래와 같이 처리
        instance = MyClass()
        MyClass.method(instance, ...)
        ```

        -   instance.method(...): 괄호 안의 파라미터를 처리하기 전에 **'instance.method'가 먼저 평가**된다.

        -   method는 클래스 속성으로 정의된 객체이며 내부에 \_\_get\_\_ 메서드를 가지고 있기 때문에 호출 시 \_\_get\_\_이 먼저 호출된다(함수를 객체에 바인딩하여 메서드로 변환).

            

            <br>

            

        ```python
        class Method:
            def __init__(self, name):
                self.name = name
        
            def __call__(self, instance, arg1, arg2):
                print(f"{self.name}: {instance} 호출됨. 인자는 {arg1}과 {arg2}")
        
        class MyClass():
            method = Method('내부 호출')
        
        instance = MyClass()
        Method("외부 호출")(instance, 'first', 'second')
        # 외부 호출: <__main__.MyClass object at 0x7fa59bb4cb38> 호출됨. 인자는 first과 second
        instance.method('first', 'second')
        # TypeError: __call__() missing 1 required positional argument: 'arg2'
        ```

        -   파라미터의 위치가 한 칸씩 밀려서 second가 전달되어야 하는 arg2자리에 아무것도 전달되지 않는다.
        -   메서드를 디스크립터로 변경

        ```python
        class Method:
            def __init__(self, name):
                self.name = name
        
            def __call__(self, instance, arg1, arg2):
                print(f"{self.name}: {instance} 호출됨. 인자는 {arg1}과 {arg2}")
        
            def __get__(self, instance, owner):
                if instance is None:
                    return self
                return MethodType(self, instance)
        
        class MyClass:
            method = Method('내부 호출')
        
        instance = MyClass()
        Method("외부 호출")(instance, 'first', 'second')
        # 외부 호출: <__main__.MyClass object at 0x7fdef2331b70> 호출됨. 인자는 first과 second
        instance.method('first', 'second')
        # 내부 호출: <__main__.MyClass object at 0x7fdef2331b70> 호출됨. 인자는 first과 second
        
        ```

        -   비데이터 디스크립터에서 MethodType(self, instance)을 이용해 함수를 메서드로 변경
            -   self: 반드시 호출 가능(Method 객체(\_\_call\_\_ 메서드를 포함))한 객체여야 한다.
            -   instance: 이 함수에 바인딩할 객체(MyClass 객체)

        -   파이썬 함수도 이와 유사하게 동작

            

<br>



### 메서드를 위한 빌트인 데코레이터[추후 다시 정리]

-   @property, @classmethod, @staticmethod 데코레이터는 디스크립터로 구성되어있다.
-   메서드를 클래스에서 직접 호출하면 디스크립터 자체(self)를 반환
-   @classmethod를 사용하면 디스크립터의 \_\_get\_\_ 함수가 메서드를 데코레이팅 함수에 첫 번째 파라미터로 메서드를 소유한 클래스(owner)를 넘겨준다

<br>



**[처음으로](#20xx)**

<br>









