# 200923

**이번 내용은 어렵기 때문에 코드를 여러번 짜보고 반복해서 읽으면서 완전히 이해할 것**



<br>

- **[디스크립터](#디스크립터)**
- **[디스크립터의 유형](#디스크립터의-유형)**
- **[setattr(instance, "descriptor", value)가 아닌 instance.\_\_dict\_\_['descriptor']를 쓰는 이유는?](#setattrinstance-descriptor-value가-아닌-instance__dict__descriptor를-쓰는-이유는)**
- **[디스크립터가 모든 인스턴스의 속성 값을 보관할 수 없는 이유는?](#디스크립터가-모든-인스턴스의-속성-값을-보관할-수-없는-이유는)**

    



<br>



**[처음으로](#200923)**

<br>



# 디스크립터

- 디스크립터는 단지 디스크립터 프로토콜을 구현한 클래스의 **인스턴스**

- 아래의 메서드를 최소 한 개 이상 구현해야한다.

    - **[\_\_get_\_](#__get__self-instance-owner)**
    - **[\_\_set_\_](#__set__self-instance-value)**
    - **[\_\_delete_\_](#__delete__self-instance)**
    - **[\_\_set_name_\_](#__set_name__self-owner-name)**

        

- 아래와 같은 네이밍 컨벤션을 사용한다.
    - **ClientClass:** 디스크립터 구현체의 기능을 활용할 추상화 객체(디스크립터의 클라이언트). 클래스 속성(init의 속성이 아닌 본문)으로 디스크립터를 갖는다.
    - **DescriptorClass:** 매직 메서드를 포함하는 디스크립터 클래스
    - **client:** client = ClientClass()
    - **descriptor:**  descriptor = DescriptorClass()

<br>

**일반 클래스와 디스크립터의 차이**

```python
# 일반적인 클래스와 클래스 속성(attribute)
class Attribute:
    value = 2

class Client:
    attribute = Attribute()

c = Client()
print(c.attribute.value)  # 2
print(c.attribute is c)  # False

# descriptor
class DescriptorClass:
    def __get__(self, instance, owner):
        if instance is None:
            print('instance is None')
            return self
        print(self.__class__.__name__)
        return instance

class ClientClass:
    descriptor = DescriptorClass()

client = ClientClass()
print(client.descriptor)  # DescriptorClass
ClientClass.descriptor  # 'instance is None'

# <__main__.ClientClass object at 0x7fc6e109c438>
print(client.descriptor is client)  # True
```

- 마지막 출력값은 DescriptorClass의 인스턴스가 아닌 \_\_get\_\_() 메서드의 결과값을 반환한다.



<br>



### \_\_get\_\_(self, instance, owner)

**디스크립터 호출할 때 사용되는 매직 메서드**(get 이후에 call 매직 메서드가 호출된다.)

- instance: 디스크립터를 호출한 객체(client)를 의미

    - 디스크립터의 행동을 취하려는 객체

- owner: 해당 객체의 클래스(ClientClass)를 의미

    - 인스턴스의 클래스(DescriptorClass가 아님)

    - owner = instance.\_\_class\_\_ (x)

        - **ClientClass에서 디스크립터를 직접 호출하는 특별한 경우 instance는 None이기 때문에 클래스를 구할 수 없으므로 owner라는 파라미터를 추가함**

        - instance가 None일 경우 일반적으로 디스크립터 자체(self)를 반환

<br>



**[처음으로](#200923)**

<br>

### \_\_set\_\_(self, instance, value)

**디스크립터에 값을 할당할 때 사용되는 매직 메서드**

```python
client.descriptor = 'value'
print(client.descriptor)  # value
```

- set 매직 메서드를 구현하지 않았기 때문에 client.descriptor는 'value'라는 문자열로 덮어 씌워진다.

```python
class Validation:
    def __init__(self, validation_function, error_msg: str):
        self.validation_function = validation_function
        self.error_msg = error_msg

    def __call__(self, value):
        if not self.validation_function(value):
            raise ValueError(f"{value!r}{self.error_msg}")

class Field:
    def __init__(self, *validations):
        self._name = None
        self.validations = validations

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self._name]

    def __set__(self, instance, value):
        self.validate(value)
        instance.__dict__[self._name] = value

    def validate(self, value):
        for validation in self.validations:
            validation(value)


class ClientClass:
    descriptor = Field(Validation(lambda x: isinstance(x, (int, float)), '는 숫자가 아님'),
                       Validation(lambda x: x >= 0, "는 0보다 작음"))

client = ClientClass()
client.descriptor = 42  # ok
client.descriptor = -42  # ValueError: -42는 0보다 작음
client.descriptor = '42'  # ValueError: '42'는 숫자가 아님
```

- instance.\_\_dict\_\_[self._name] = value는 client.descriptor = value와 동일하다.
- @property에 놓일 수 있는 것은 디스크립터로 추상화 할 수 있음 -> 재사용 용이함
    - \_\_set\_\_()이 @propert.setter의 역할을 하고 있다.

<br>



**[처음으로](#200923)**

<br>

### \_\_delete\_\_(self, instance)

- self: descriptor(속성)을 나타낸다.

- instance: client(ClientClass의 객체)

    ```python
    del client.descriptor
    ```

    **delete 예제**

    ```python
    # 'admin' permission을 가진 유저만 email을 지울 수 있는 코드
    class ProtectedAttribute:
        def __init__(self, requires_role=None):
            self.permission_required = requires_role
            self._name = None
    
        def __set_name__(self, owner, name):
            self._name = name
    
        def __set__(self, user, value):
            if value is None or value == '':
                raise ValueError(f"{self._name}를 None으로 설정할 수 없음")
            user.__dict__[self._name] = value
    
        def __delete__(self, user):
            if self.permission_required in user.permissions:
                user.__dict__[self._name] = None
            else:
                raise ValueError(f"{user.username} 사용자는 {self.permission_required} 권한이 없음")
    
    class User:
        email = ProtectedAttribute(requires_role='admin')
    
        def __init__(self, username, email, permission_list):
            self.username = username
            self.email = email
            self.permissions = permission_list or []
    
        def __str__(self):
            return self.username
    
    
    admin = User('jh', 'ji@nad.com', ['admin'])
    user = User('jh2', 'ji@nad2.com', ['user'])
    print(admin.email)  # ji@nad.com
    print(user.email)  # ji@nad2.com
    del admin.email
    print(admin.email is None)  # True
    del user.email  # ValueError: jh2 사용자는 admin 권한이 없음
    abnormal_user = User('', '', ['admin'])  # ValueError: email를 None으로 설정할 수 없음
    ```

    - User 객체를 생성할 때 email 속성이 없을 경우(혹은 빈 값) set 매직 메서드에서 ValueError를 일으킨다.
        - 위치 인자로 인해 username과 email 파라미터는 필수로 받아야 한다.
    - (디스크립터가 아닌)user.email 속성을 지워버리면 User 객체는 **인터페이스와 맞지 않는 불완전 객체**가 된다.
        - 사용자는 username과 email은 필수 속성으로 기대하고 있기 때문에 중간에 email 속성 자체를 지우는건 안된다.
        - 때문에 email 속성 자체를 지우지 않고 None으로 값을 대체한다.

<br>



**[처음으로](#200923)**

<br>

### \_\_set\_name\_\_(self, owner, name)

- 클래스 속성의 이름을 얻고자 할 때 사용된다.
- owner: ClientClass(User)
- name: descriptor를 할당받는 속성의 이름(email)



<br>



**[처음으로](#200923)**

<br>

# 디스크립터의 유형

**[데이터 디스크립터(data descriptor)](#비데이터non-data-디스크립터사전-우선)**: **\_\_set\_\_**또는 **\_\_delete\_\_** 메서드를 구현한 디스크립터

​	**(우선순위: obj.\_\_dict\_\_ < data_descriptor)**

**[비데이터 디스크립터(non-data descripto)](#데이터data-디스크립터디스크립터-우선)**: **\_\_get\_\_** 메서드만 구현한 디스크립터

​	**(우선순위: obj.\_\_dict\_\_ > data_descriptor)**

>   \_\_set\_name\_\_은 어떤 유형에도 속하지 않는다.
>
>   \_\_dict\_\_와의 관계를 이해하는 것이 중요하다.

<br>

- 객체의 속성을 결정할 때 데이터 디스크립터가 객체의 사전(\_\_dict\_\_)보다 우선적으로 적용되지만 비데이터 디스크립터는 그렇지 않음
    - 비데이터 디스크립터는 **객체의 사전에 동일한 이름의 키가 있을 경우 객체의 <u>사전값</u>을 적용**하고 **디스크립터는 호출되지 않는다.**
    - 데이터 스크립터는 **디스크립터가 객체의 사전보다 먼저 호출**되기 때문에 **객체의 사전 값은 사용되지 않는다.**



<br>

### 비데이터(non-data) 디스크립터(사전 우선)

```python
class NonDataDescriptor:
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return 42

class ClientClass:
    descriptor = NonDataDescriptor()

client = ClientClass()
print(vars(client))  # {}
print(client.descriptor)  # 42
client.descriptor = 50
print(client.descriptor)  # 50(변경)
print(vars(client))  # {'descriptor': 50}  
del client.descriptor
print(client.descriptor)  # 42
print(vars(client))  # {}
```

-   **client = ClientClass():** 디스크립터가 아직 클래스 내에 있기 때문에 get을 호출하기 전(client.\_\_dict\_\_는 비어있음)
-   **client.descriptor:** client 내 **사전의 값이 없기 때문에 \_\_get\_\_ 메서드 호출** -> 42 반환
-   **client.descriptor = 50:** 비데이터 디스크립터는 사전의 우선순위가 높기 때문에 50을 할당할 경우 **사전에 우선적**으로 할당한다.
-   **client.descriptor:** **사전에 저장된 값 출력**
-   **vars(client):** 사전값이 변경됨
-   **del client.descriptor:** 비데이터 디스크립터(\_\_delete\_\_이 구현되지 않음)이기 때문에 **객체의 사전**에서 디스크립터의 키를 삭제
-   **client.descriptor:** 처음 디스크립터를 호출할 때와 동일한 상태를 갖으며 사전은 빈 상태가 된다.

<br>

### 데이터(data) 디스크립터(디스크립터 우선)

```python
class DataDescriptor:
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return 42

    def __set__(self, instance, value):
        instance.__dict__['descriptor'] = value  # 'descriptor' -> __set_name__ 대체 가능

class ClientClass:
    descriptor = DataDescriptor()

client = ClientClass()
print(vars(client))  # {}
print(client.descriptor)  # 42
client.descriptor = 50
print(client.descriptor)  # 42(변경안됨-디스크립터가 객체의 사전보다 높은 우선순위)
print(vars(client))  # {'descriptor': 50}
del client.descriptor  # AttributeError: __delete__
```

-   **vars(client) & client.descriptor**: 사전은 비어있지만 디스크립터는 get이 호출되면서 42를 출력한다.
-   **client.descriptor = 50:** \_\_set\_\_이 호출되면서 사전값 변경
-   **client.descriptor:** **디스크립터를 우선 호출**하면서 사전이 아닌 **\_\_get\_\_의 반환값**이 출력됨(42 출력)
-   **vars(client): \_\_set\_\_** 메서드에 의해서 사전 값이 변경됨
    -   결과적으로 입력된 값은 **set에 의해 사전**에 저장되지만, 출력될 때 사전보다 높은 우선순위를 같은 **get의 반환값이 출력**된다.
-   **del client.descriptor:** 데이터 디스크립터이기 때문에 사전의 키값을 지우는 것이 아닌 구현되지 않은 \_\_delete\_\_를 호출하면서 에러를 일으킨다.

<br>



**[처음으로](#200923)**

<br>

### setattr(instance, "descriptor", value)가 아닌 instance.\_\_dict\_\_['descriptor']를 쓰는 이유는?

-   디스크립터의 속성에 값을 할당할때 \_\_set\_\_ 메서드 호출 -> setattr 호출 -> 다시 \_\_set\_\_ 호출 => **무한루프**
-   instance.descriptor = value도 마찬가지로 무한루프를 일으킨다.

<br>



**[처음으로](#200923)**

<br>



### 디스크립터가 모든 인스턴스의 속성 값을 보관할 수 없는 이유는?

-   ClientClass는 이미 디스크립터에 대한 참조를 가지고 있다.
-   이때 디스크립터가 ClientClass 객체를 참조할 경우 **순환 종속성(서로를 참조하면서 참조 카운트가 임계치 이하로 떨어지지 않음)**이 일어나면서 **가비지 컬렉션**이 되지 않는다.
-   이 문제를 해결하기 위해 약한 참조(**weakref**)를 이용하여 client 객체에 대한 **약한 참조 키**를 만들 수 있다.



<br>



**[처음으로](#200923)**

<br>





