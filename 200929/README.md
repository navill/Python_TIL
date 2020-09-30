# 200929

- **[구조 패턴](#구조-패턴)**
    - **[어댑터](#어댑터-패턴)**
    - **[컴포지트](#컴포지트)**
    - **[데코레이터](#데코레이터)**
    - **[파사드](#파사드facade)**

<br>

**[처음으로](#200200929)**
<br>



# 구조 패턴

-   인터페이스를 복잡하게 하지 않으면서 기능을 확장하여 더 나은 인터페이스 또는 객체를 만들어야 하는 상황에 유용함
    -   여러 객체 또는 (응집력이 높은)인터페이스들을 조합하여 구성

<br>

### 어댑터 패턴

-   래퍼(wrapper)라고도 불리우며 호환되지 않는 두 개 이상의 객체에 대한 인터페이스를 동시에 사용할 수 있게 한다.

    -   예) fetch() 메서드를 사용하는 여러 객체 - fetch 인터페이스를 유지하면 클라이언트는 코드 변경없이 여러 객체를 사용할 수 있다.

    -   하지만 fetch 메서드를 구현하지 않는 객체 + 외부 API를 사용하는 등의 이유로 객체에 대한 수정 권한이 없을 경우 문제가 된다.

    -   이때 **어댑터 패턴**을 구현하여 새로운 **객체를 수용할 수 있는 새로운 인터페이스**를 개발하여 문제를 해결할 수 있다.

        ```python
        # 상속을 이용한 어댑터 패턴
        class UsernameLookup:
            def search(self, user_namespace):
                print(f"looking for {user_namespace}")
        
        class UserSource(UsernameLookup):
            def fetch(self, user_id: str, username: str):
                user_namespace = self._adapt_arguments(user_id, username)
                return self.search(user_namespace)
        
            @staticmethod
            def _adapt_arguments(user_id: str, username: str):
                return f"{user_id}:{username}"
        
        us = UserSource()
        us.fetch("id", "jihoon")
        # looking for id:jihoon
        ```

        -   UsernameLookup 클래스는 fetch를 가지고 있지 않음
        -   UserSource.fetch 인터페이스는 두 개의 파라미터를 받아서 하나의 반환 값을 갖는다.
            -   self._adapt_arguments는 기존 파라미터(fetch의 파라미터 형식)를 알맞게 변환해서 외부 함수(search)를 호출
        -   **문제점**
            -   기존 클래스가 다른 클래스의 파생 클래스일 수 있다.
            -   파이썬은 다중 상속을 지원하기 때문에 문제가 되지 않지만, 클래스간에 강한 결합력을 갖게 된다.
            -   개념적으로 상속은 **is a**관계에 한정해서 적용하는 것이 바람직하지만, 타 클래스를 완전히 이해하지 못한 상태에서 상속을 받을 경우 **is a 관계**인지 분명히 알 수 없다.

        ```python
        # composition을 이용한 어댑터 패턴
        class UserSource:
            def __init__(self):
                self.username_lookup = UsernameLookup()
        
            def fetch(self, user_id: str, username: str):
                user_namespace = self._adapt_arguments(user_id, username)
                return self.username_lookup.search(user_namespace)
        
            # @staticmethod  -> 왜 staticmethod를 지정하는지?
            def _adapt_arguments(self, user_id: str, username: str):
                return f"{user_id}:{username}"
        
        us = UserSource()
        us.fetch("id", "jihoon")
        # looking for id:jihoon
        ```

        -   위 문제점을 개선하기 위해 [composition[Notion]](https://www.notion.so/navill/Fast-Campus-3-22-744d17941dad443cbf5b47b97337840c#d3ade1020b14492db7080503f299a0cd)을 이용한 어댑터 패턴을 구현할 수 있다.

    

<br>

**[처음으로](#200200929)**
<br>



### 컴포지트

```python
class Product:  # 하위 계층(리프 노드)
    def __init__(self, name, price):
        self._name = name
        self._price = price

    @property
    def price(self):
        return self._price


class ProductBundle:  # (product의)상위 계층(중간 노드)
    def __init__(
            self, name, perc_discount, *products: Union[Product, "ProductBundle"]
    ) -> None:
        self._name = name
        self._perc_discount = perc_discount
        self._products = products

    @property
    def price(self):
        total = sum(p.price for p in self._products)
        return total * (1 - self._perc_discount)


a = Product('a', 1000)
b = Product('b', 2000)
a_b = ProductBundle('ab_bundle', 0.3, a, b)
print(a.price)  # 1000
print(b.price)  # 2000
print(a_b.price)  # 2100
```

-   기본 객체(Product)와 컨테이너 객체(ProductBundle)를 구분없이 동일하게 사용하길 원할 경우 컴포지트 패턴을 사용



<br>

**[처음으로](#200200929)**
<br>

### 데코레이터

-   상속없이 객체의 기능을 동적으로 확장

    -   유연한 객체를 만들려고 할 때 다중 상속의 대안이 될 수 있다.

    ```python
    # 예제1
    class QueryEnhancer:
        def __init__(self, **kwargs):
            self._raw_query = kwargs
    
        # @decorator를 이용할 수 있지만 문제가 있음
        def render(self):
            # do something
            return self._raw_query
    ```

    -   런타임에서 변경이 유연하지 않음
    -   self._raw_query의 일부만 취하거나 일부는 제외해야할 경우 데코레이터를 사용하기 어려움

    ```python
    # 예제2(예제1 개선)
    class DictQuery:
        def __init__(self, **kwargs):
            self._raw_query = kwargs
    
        def render(self):
            return self._raw_query
    
    
    class QueryEnhancer:  # class 추상화
        def __init__(self, query:DictQuery):  # annotation
            self.decorated = query
    
        def render(self):
            return self.decorated.render()
    
    
    class RemoveEmpty(QueryEnhancer):
        def render(self):
            original = super().render()
            return {k: v for k, v in original.items() if v}
    
    
    class CaseInsensitive(QueryEnhancer):
        def render(self):
            original = super().render()
            return {k: v.lower() for k, v in original.items()}
    
    
    original = DictQuery(key="value", empty="", none=None, upper="UPPER", title="title")
    
    new_query = CaseInsensitive(RemoveEmpty(original))
    print(original.render())
    # {'key': 'value', 'empty': '', 'none': None, 'upper': 'UPPER', 'title': 'title'}
    print(new_query.render())
    # {'key': 'value', 'upper': 'upper', 'title': 'title'}
    ```

    -   파이썬의 **덕타이핑(duck typing)** 특성상 새로운 기본 클래스를 만들어 클래스 계층 구조에 편입할 필요가 없음 

    -   QueryEnhancer를 상속받은 객체 공통된 인터페이스를 가지며 상호 교환이 가능

        -   단지 공통 인터페이스(위 예제에서는 render 메서드)를 구현하기만 하면 된다.

        >   duck typing: CaseInsesitive의 파라미터는 DictQuery 객체(# annotation부분)가 필요하지만, **DictQuery 인터페이스를 유지는 객체(RemoveEmpty)라면 DictQuery 대신 사용할 수 있다.**

        

    ```python
    # 예제3
    class DictQuery:
        def __init__(self, **kwargs):
            self._raw_query = kwargs
    
        def render(self) -> dict:
            return self._raw_query
    
    
    class QueryEnhancer:
        def __init__(self, query, *decorators):
            self._decorated = query
            self._decorators = decorators
    
        def render(self):
            current_result = self._decorated.render()
            for deco in self._decorators:
                current_result = deco(current_result)
            return current_result
    
    
    def remove_empty(original: dict) -> dict:
        return {k: v for k, v in original.items() if v}
    
    
    def case_insensitive(original: dict) -> dict:
        return {k: v.lower() for k, v in original.items()}
    
    
    query = DictQuery(foo='bar', empty='', none=None, upper='UPPERCASE', title='title')
    qe = QueryEnhancer(query, remove_empty, case_insensitive).render()
    
    print(qe)
    # {'foo': 'bar', 'upper': 'uppercase', 'title': 'title'}
    ```

    -   용도에 따라 위와 같이 변환 함수를 데코레이터의 파라미터에 추가하여 사용할 수 있다.
        -   개인적으로 이 예제가 이해하고 사용하기 쉽다고 생각함(객체 지향적인 구현은 아님)

<br>

**[처음으로](#200200929)**
<br>

### 파사드(Facade) - [Notion 예제](https://www.notion.so/navill/Structural-Design-Pattern-Facade-7fdb9c8375e24aa8b4911d0482c6218f)

>   facade: 건물의 가장 중요한 면을 가리키는 단어로 보통은 정면을 의미함. 소프트웨어 공학에서는 복잡한 시스템을 가려주는 단일 통합 창구 역할을 하는 객체를 말함.

-   파사드는 객체 간 상호 작용을 단순화하려는 상황에 유용 + 클라이언트에게 내부를 감추고 필요한 인터페이스만 제공
    -   허브 또는 단일 참조점의 역할
    -   장점
        -   객체 간 결합력을 낮춤
        -   인터페이스의 개수를 줄일 수 있음
        -   캡슐화 지원 -> 간단한 디자인 유도



<br>

**[처음으로](#200200929)**
<br>































