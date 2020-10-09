# 201009

- **[캐시 인스턴스](#캐시-인스턴스)**

- **[]()**

- **[]()**

<br>

**[처음으로](#20xxxx)**
<br>

# 캐시 인스턴스

>   Python Cookbook - Chapter 8.25

-   동일한 매개변수로 생성한 기존 인스턴스의 캐시 참조를 사용하고 싶을 때

    ```python
    # ex: logging
    from logging
    a = logging.getLogger('foo')
    b = logging.getLogger('bar')
    a is b  # False
    c = logging.getLogger('foo')
    a is c  # True
    ```

-   동일한 매개변수를 사용한 인스턴스(동일한 객체)를 참조하고자 할 경우 별도의 팩토리 함수를 생성해야한다.

    ```python
    import weakref
    
    class Spam:
        def __init__(self, name):
            self.name = name
    
    _spam_cache = weakref.WeakValueDictionary()  # 가비지 컬렉션과 관련된 중요한 역할
    
    def get_spam(name):
        if name not in _spam_cache:
            s = Spam(name)
            _spam_cache[name] = s
    
        else:
            s = _spam_cache[name]
        return s
      
    a = get_spam('foo')
    b = get_spam('bar')
    a is b  # False
    c = get_spam('foo')
    a is c  # True
    
    ```

    [weakref.WeakValueDictionary()](https://docs.python.org/ko/3/library/weakref.html#weakref.WeakValueDictionary): 참조한 아이템이 존재하는 경우에만 담고 그렇지 않을 경우 삭제

