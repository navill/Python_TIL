# 200928

- **[파이썬에 디자인 패턴 적용 시 고려사항](#파이썬에-디자인-패턴-적용-시-고려사항)**

- **[생성 패턴](#생성creational-패턴)**

    


<br>

**[처음으로](#200928)**
<br>



# 파이썬에 디자인 패턴 적용 시 고려사항

-   파이썬에서는 고전적인 디자인 패턴 중 일부는 실제로 필요하지 않음

    -   파이썬 자체에서 해당 기능을 지원하기 때문에 지원되는지 알지 못할 수 있다.

    -   ex: 이터레이터 패턴(파이썬의 이터레이터 프로토콜을 구현해 이터레이터 객체를 쉽게 생성할 수 있음)
    -   객체 생성을 위한 특별한 팩토리 클래스가 필요 없다(함수 자체가 팩토리처럼 동작)

-   디자인 패턴은 보통 디자인을 하는 도중에 **'출현'** 또는 **발견**된다.
    -   패턴이 출현할 때 까지 리팩토링하고 개선해야 한다.
-   앞으로 다룰 예제는 기존의 디자인 패턴 표준이나 구상과 다를 수 있다.
    -   특정 시나리오에 대한 솔루션을 찾는 실용적인 접근
    -   파이썬의 특수성



<br>

**[처음으로](#200928)**
<br>



# 생성(creational) 패턴

-   객체를 인스턴스화할 때의 복잡성을 최대한 추상화하기 위해 사용
    -   객체 초기화에 필요한 작업을 단순화하기 위함

-   [monostate](#monostate-패턴)
-   [borg](#borg-패턴)
-   [builder](#builder-패턴) - [Notion 예제](https://www.notion.so/navill/Creational-Design-Pattern-Builder-f7e8b75c7b6c4bf9ad466d3fdaf603fa)

<br>

### 싱글턴과 공유 상태(monostate)

-   싱글턴 사용을 지양하라(기능의 이점보다 부작용이 더 큼)
-   꼭 필요하다면 모듈을 사용
    -   파이썬의 유일한 싱글턴
        -   아마도 import logging도 싱글턴으로 사용되지 않을까? - (확인이 필요함)
        -   

### 공유 상태(monostate pattern)

-   모든 인스턴스에 하나의 속성만 공유될 필요가 있다고 가정
    -   클래스 변수를 통해 구현할 수 있지만, 속성의 값을 업데이트하고 검색하는 인터페이스가 필요하다

```python
# 클래스 속성을 이용한 단순한 monostate
class GitFetcher1:
    current_tag = 'develop'

feature_1 = GitFetcher1()
feature_2 = GitFetcher1()

# 속성값을 처리할 수 있는 인터페이스가 구현된 monostate pattern
class GitFetcher:
    _current_tag = None

    def __init__(self, tag):
        self.current_tag = tag

    @property
    def current_tag(self):
        if self._current_tag is None:
            raise AttributeError('tag가 초기화되지 않음')
        return self._current_tag

    @current_tag.setter
    def current_tag(self, new_tag):
        self.__class__._current_tag = new_tag  # [*]

    def pull(self):
        print(f"{self._current_tag}에서 풀")
        return self.current_tag

feature_1 = GitFetcher(0.1)
print(feature_1.current_tag)  # 0.1
print(vars(feature_1))  # {}

feature_2 = GitFetcher(0.2)
print(feature_2.current_tag)  # 0.2
print(vars(feature_1))  # {}

feature_1.current_tag = 'develop'

print(feature_1.pull())  # develop
print(feature_2.pull())  # develop

```

-   **\# \[\*\]**: setter에서 인스턴스의 속성이 아닌 클래스 속성(_current_tag) 에 값을 할당하고 getter 또한 클래스 속성에서 값을 가져온다.

    -   클래스 속성값은 여러 객체에 공유되며, 언제든 property를 이용해 업데이트 할 수 있다.

    -   디스크립터를 이용해 더 깔끔하게 구현할 수 있다.

        ```python
        class SharedAttribute:
            def __init__(self, initial_value=None):
                self.value = initial_value
                self._name = None
        
            def __set_name__(self, owner, name):
                self._name = name
        
            def __get__(self, instance, owner):
                if instance is None:
                    return self
                if self.value is None:
                    raise AttributeError(f"{self._name}가 초기화 안됨")
                return self.value
        
            # data descriptor - desciptor 우선
            def __set__(self, instance, value):
                self.value = value
        
        class GitFetcherWithDescriptor:
            current_tag = SharedAttribute()
            current_branch = SharedAttribute()
        
            def __init__(self, tag, branch=None):
                self.current_tag = tag
                self.current_branch = branch
        
            def pull(self):
                print(f"{self.current_tag}에서 풀")
                return self.current_tag
        
        feature_1 = GitFetcherWithDescriptor(0.1, 'master')
        print(feature_1.current_tag)  # 0.1
        print(feature_1.current_branch)  # master
        feature_2 = GitFetcherWithDescriptor(0.2, 'develop')
        print(feature_2.current_tag)  # 0.2
        print(feature_2.current_branch)  # develop
        print(feature_1.current_tag)  # 0.2
        print(feature_1.current_branch)  # develop
        
        feature_2.current_tag = 0.0
        print(feature_2.current_tag)  # 0.0
        print(feature_1.current_tag)  # 0.0
        ```

        -   공유하고자 하는 객체의 속성을 [디스크립터]()를 이용해 공유할 수 있다.

        -   디스크립터를 이용함으로써 **단일 책임 원칙**을 준수하고 **재사용성**을 높일 수 있다.

<br>

**[처음으로](#200928)**
<br>

### borg 패턴

-   같은 클래스의 모든 인스턴스가 모든 속성을 복제하는 객체를 생성

-   싱클턴의 대안(되도록 지양)

    ```python
    class SharedAllMixin:
        def __init__(self, *args, **kwargs):
            try:
                self.__class__._attributes
            except AttributeError:
                self.__class__._attributes = {}
    
            self.__dict__ = self.__class__._attributes
            super(SharedAllMixin, self).__init__(*args, **kwargs)
    
    
    class BaseFetcher:
        def __init__(self, source):
            self.source = source
    
    
    class TagFetcher(SharedAllMixin, BaseFetcher):
        def pull(self):
            print(f"{self.source}에서 풀")
            return f"Tag = {self.source}"
    
    
    class Branch(SharedAllMixin, BaseFetcher):
        def pull(self):
            print(f"{self.source}에서 풀")
            return f"Branch = {self.source}"
    
    tf1 = TagFetcher("tag1")
    tf2 = TagFetcher("tag2")
    tf3 = TagFetcher("tag3")
    print(tf1.pull())
    # tag3에서 풀
    # Tag = tag3
    print(tf1._attributes)  # {'source': 'tag3'}
    print(dir(tf1))  # [, ... ,'__weakref__', '_attributes', 'pull', 'source']
    print(vars(tf1))  # {'source': 'tag3'}
    ```

<br>

**[처음으로](#200928)**
<br>

###builder 패턴 - [Notion 예제](https://www.notion.so/navill/Creational-Design-Pattern-Builder-f7e8b75c7b6c4bf9ad466d3fdaf603fa)

-   필요한 모든 객체를 직접 생성해주는 하나의 복잡한 객체

-   builder 패턴은 언어의 특수성에 의존하지 않으므로 파이썬에서도 똑같이 적용된다.

    

<br>

**[처음으로](#200928)**
<br>

