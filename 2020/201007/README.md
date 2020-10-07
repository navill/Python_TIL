# 201007

- **[프로퍼티 메소드 중복 피하기](#프로퍼티-메소드-중복-피하기)**


<br>

**[처음으로](#201007)**
<br>

# 프로퍼티 메소드 중복 피하기

>   Python cookbook - chapter9.21

```python
# bad
class Person:
    def __init__(self, name, age):
        self._name = name
        self._age = age

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TypeError('must be a string')
        self._name = name

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, age):
        if not isinstance(age, int):
            raise TypeError('must be a integer')
        self._age = age
        
    ...
```

-   만약 타입 체크를 실행하는 프로퍼티를 적용해야할 인스턴스 속성이 많아진다면?..
    -   반복적으로 계속 적기엔 코드가 너무 지저분해 짐

<br>

```python
# good
def typed_property(name, expected_type):
    storage_name = '_' + name  # private 속성 이름 생성

    @property
    def prop(self):
        return getattr(self, storage_name)

    @prop.setter
    def prop(self, value):
        if not isinstance(value, expected_type):
            raise TypeError('{} must be a {}'.format(name, expected_type))
        setattr(self, storage_name, value)

    return prop  # <class 'property'>


class Person:
    name = typed_property('name', str)
    age = typed_property('age', int)

    def __init__(self, name, age):
        self.name = name  # self.<attr>는 프로퍼티 객체 - 이 부분에서 setter가 호출됨
        self.age = age


if __name__ == '__main__':
    p = Person('jihoon', 33)
    p.name = 'jihoon lee'  # setter 호출
    try:
        p.age = 'thirtythree'  # setter 호출 -> raise TypeError
    except TypeError as e:
        print(e)

```

-   storage_name은 **free variable([closure](http://schoolofweb.net/blog/posts/파이썬-클로저-closure/))**

    -   prop을 반환한 후에도 storage_name은 메모리에 남아있음

        ```python
        name = typed_property('name', str)
        print(name.fget.__closure__[0].cell_contents)
        >>> _name  # typed_property에서 정의한 자유 변수(storage_name)
        ```

-   만약 반복적으로 expected_type을 사용하는것이 맘에 안든다면?

    -   functools.partial() 사용

        ```python
        class Person:
            name = String('name')
            age = Integer('age')
        
            def __init__(self, name, age):
                self.name = name
                self.age = age
                
        p = Person('jihoon', 33)
        p.name = 'jihoon lee'
        print(p.name)  
        # 'jihoon lee'
        p.name = 1
        # TypeError: str_name must be a <class 'str'>
        ```

        -   단, 클래스 속성에 프로퍼티를 저장하기 때문에 클래스 속성의 특징(**인스턴스간 속성 공유**)을 고려해야한다.

