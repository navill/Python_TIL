# 200926

- **[이터레이션 인터페이스](#이터레이션-인터페이스)**

- **[코루틴](#코루틴)**

- **[코루틴 고급 주제](#코루틴-고급-주제)**

    

<br>

**[처음으로](#200926)**
<br>



# 이터레이션 인터페이스

-   보통 한 객체가 \_\_iter\_\_와 \_\_next\_\_를 같이 구현함

-   **이터러블(iterable):** 반복이 가능한 객체(자신(self)을 반환하는 **\_\_iter\_\_ 메서드**를 구현한 객체).

-   **이터레이터**(iterator): 내장 next() 함수에 의해 한 번에 값을 하나씩 생성하는지 알고 있는 객체(**\_\_next\_\_ 메서드**를 구현한 객체)

    -   하나씩 값을 전달한다는 의미에서 **제너레이터**는 **이터레이터**이다.
    -   더 이상 값을 생성하지 못할 때 StopIteration을 일으킨다.

    ```python
    class SequenceIterator:
        def __init__(self, start=0, step=1):
            self.current = start
            self.step = step
    
        def __next__(self):
            value = self.current
            self.current += self.step
            return value
    
    si = SequenceIterator(0, 2)
    print(next(si))  # 0
    print(next(si))  # 2
    print(next(si))  # 4
    print(next(si))  # 6
    for i in si: pass
    # TypeError: 'SequenceIterator' object is not iterable
    ```

    -   next를 이용해 값을 하나씩 가져올 수 있지만, for 문을 이용해 값을 반복적으로 가져올 수 없다.



### 이터러블이 가능한 시퀀스 객체

-   객체가 for에서 사용될 때 우선 \_\_iter\_\_()를 구현했는지 확인하고 있을경우 iter 매직 메서드를 호출

-   만일 없을 경우, \_\_getitem\_\_과 \_\_len\_\_ 매직 메서드의 유무를 확인하여 반복을 실행

    -   반복에 대한 중지를 알리기 위해 StopIteration이 아닌 **IndexError**을 일으킨다.

        ```python
        class MappedRange:
            def __init__(self, transformation, start, end):
                self._transformation = transformation
                self._wrapped = range(start, end)
        
            def __getitem__(self, index):
                value = self._wrapped.__getitem__(index)
                result = self._transformation(value)
                return result
        
            def __len__(self):
                return len(self._wrapped)
        
        mr = MappedRange(abs, 0, 10)
        for i in mr:
            print(i)
        # 0, 1, 2, 3, ... ,8 ,9
        ```

    **\_\_getitem\_\_은 대비책으로 사용될 수 있을뿐, 일반적인 반복 가능 객체를 생성하고자 할 경우 이터레이션 프로토콜을 준수하는 것이 좋다.**





<br>

**[처음으로](#200926)**
<br>





# 코루틴

**Coroutine(Cooperative routine):** 일반적인 함수나 메서드같은 서브 루틴(sub-routine)이 메인 루틴(main-routine)과 종속관계를 가진것과 달리, 메인루틴과 대등한 관계로 협력하는 모습을 보고 coroutine이라 불리게 됨

-   제너레이터를 기반으로 비동기 프로그래밍을 구성하기 위해 코루틴이 유용할 수 있다.

**제너레이터 인터페이스의 메서드**

-   **.close()**
-   **.throw(ex_type[, ex_value[, ex_traceback]])**
-   **.send(value)**

<br>



### **close()**

-   이 메서드를 호출하면 제너레이터에서 GeneratorExit 예외가 발생

-   별도로 예외를 처리하지 않으면 제너레이터가 값을 생성하지 않고 반복 중지

    -   만약 자원을 관리하는 코루틴일 경우 이 시점에 자원들을 해제 할 수 있다(컨텍스트 매니저 및 finally 블록과 유사).

        ```python
        class DBHandler:
            """Simulate reading from the database by pages."""
        
            def __init__(self, db):
                self.db = db
                self.is_closed = False
        
            def read_n_records(self, limit):
                return [(i, f"row {i}") for i in range(limit)]
        
            def close(self):
                logger.debug("closing connection to database %r", self.db)
                self.is_closed = True
        
        
        def stream_db_records(db_handler):
            try:
                while True:
                    yield db_handler.read_n_records(10)
                    time.sleep(.1)
            except GeneratorExit:
                print('GeneratorExit')
                db_handler.close()
        
        streamer = stream_db_records(DBHandler("testdb"))
        print(next(streamer))
        # [(0, 'row 0'), (1, 'row 1'), (2, 'row 2'), (3, 'row 3'), (4, 'row 4'), (5, 'row 5'), (6, 'row 6'), (7, 'row 7'), (8, 'row 8'), (9, 'row 9')]
        
        print(len(next(streamer)))
        # 10
        print(streamer.close())  # Generator에 close()을 호출하여 GeneratorExit 예외를 일으킨다.
        # GeneratorExit
        # None
        ```

        





### throw(ex_type[, ex_value[, ex_traceback]])

-   이 메서드는 현재 제너레이터가 중단된 위치에서 예외를 던진다.

    ```python
    class CustomException(Exception):
        """custom error"""
    
    def stream_data(db_handler):
        while True:
            try:
                yield db_handler.read_n_records(10)  #0
            except CustomException as e:
                print(f"controlled error {e.__class__.__name__}, continuing")
            except Exception as e:
                print(f"unhandled error {e.__class__.__name__}, stopping")
                db_handler.close()
                break
    
    streamer = stream_data(DBHandler('testdb'))
    print(next(streamer))
    # [(0, 'row 0'), (1, 'row 1'), (2, 'row 2'), (3, 'row 3'), (4, 'row 4'), (5, 'row 5'), (6, 'row 6'), (7, 'row 7'), (8, 'row 8'), (9, 'row 9')]
    
    streamer.throw(CustomException) 
    # controlled error CustomException, continuing
    
    streamer.throw(ValueError) 
    # unhandled error ValueError, stopping
    ```

    -   next() 함수에 의해 #0의 반환 값이 출력됨 -> 이후 yield에 대기
    -   만약 다음 next()가 호출된다면 위와 동일하게 출력되고 yield에서 대기
    -   streamer.throw(): 인가된 파라미터에 해당하는 에러 처리
        -   CustomException: 제너레이터에서 처리(계속 이어서 반복문 실행)
        -   Exception(ValueError): 데이터베이스 종료 후 반복 중단



<br>

### send(value)

-   값을 제너레이터에 전달하고 이를 제너레이터 내 에서 처리하고자 할 때 사용된다.

    ```python
    def stream_db_records2(db_handler):
        retrieved_data = None
        page_size = 10
        try:
            while True:
                page_size = (yield retrieved_data) or page_size
                retrieved_data = db_handler.read_n_records(page_size)
        except GeneratorExit:
            db_handler.close()
    
    
    streamer3 = stream_db_records2(DBHandler('testdb'))
    print(next(streamer3))  # None - Priming
    print(next(streamer3))  # [(0, 'row 0'), (1, 'row 1'), (2, 'row 2'), (3, 'row 3'), (4, 'row 4'), (5, 'row 5'), (6, 'row 6'), (7, 'row 7'), (8, 'row 8'), (9, 'row 9')]
    print(streamer3.send(3))  # [(0, 'row 0'), (1, 'row 1'), (2, 'row 2')]
    print(streamer3.send(4))  # [(0, 'row 0'), (1, 'row 1'), (2, 'row 2'), (3, 'row 3')]
    ```

    -   send를 통해 값을 전달할 경우 page_size가 설정되고 그렇지 않을 경우 default size(10)으로 설정된다.

    -   생성된 page_size를 기반으로 read_n_records() 매서드 실행

        -   next에 의해 yield 왼쪽에 위치한 함수의 값을 호출자에게 전달
        -   send의 인자값을 yield의 오른쪽에 위치한 할당 구문('page_size =')에 전달

        **Priming**: 제너레이터에서 처음 next()는 코드의 흐름을 yield의 오른쪽에 위치한 구문(retrieved_data)의 실행 대기 상태로 만들기 위해 사용된다. 이를 'priming(기동)' 이라고 한다. 다음 next() 함수에 의해 retrieved_data의 값은 호출자에게 전달된다.

        ```python
        def prepare_coroutine(coroutine):
            def wrapped(*args, **kwargs):
                advanced_coroutine = coroutine(*args, **kwargs)
                next(advanced_coroutine)
                return advanced_coroutine
        
            return wrapped
          
        @prepare_coroutine
        def auto_stream_db_records(db_handler):
            ...
        
        streamer = auto_stream_db_records(DBHnadler('test'))
        next(streamer)  # [(0, 'row 0'), (1, 'row 1'), (2, 'row 2'), ...
        ```

        -   위 코드는 사용자가 기동을 위해 next()를 한 번 호출하지 않고도 제너레이터를 편리하게 사용할 수 있도록 만들어진 데코레이터이다.

        



<br>

**[처음으로](#200926)**
<br>



# 코루틴 고급 주제

코루틴은 제너레이터를 기반으로 하지만 **반복에 초점**을 맞춘 **제너레이터**와 달리, **코루틴**은 나중에 실행될 때 까지 코드의 **흐름을 잠시 멈추는 것**을 목표로 한다.

<br>

### 코루틴에서 값 반환하기

```python
def generator():
    yield 1
    yield 2
    return 3


value = generator()
print(next(value))  # 1
print(next(value))  # 2
# print(next(value))  # StopIteration: 3
try:
    next(value)
except StopIteration as e:
    print(e.value)  # 3
```

-   더 이상 반환할 값이 없을 경우 마지막 return 값을 예외(Exception.value)에 저장하고, 예외가 발생할 때 이를 함께 전달한다.
-   StopIteration이 발생하기 전에 값을 반환할 경우 반복은 중단된다.



<br>

### 작은 코루틴에 위임하기 - yield from 구문

```python
def generator():
    for i in range(10):
        # yield가 iterable 객체에서 값을 직접 처리하지 못하기 때문에 반복문(for)을 이용해 값을 가져와야 한다.
		    yield i

value = generator()  # 제너레이터 객체를 전달할 뿐, 아무런 값을 출력하지 않는다.
next(value)  # next()을 통해 요소를 하나씩 가져올 수 있다.
```

-   제너레이터 함수 자체는 값을 출력하지 않는다.

<br>

```python
def chain(iterables):
    for it in iterables:
        # it: [1,2,3]
        for value in it:
          	# value: 1
            yield value

TEST_LIST = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(list(chain(TEST_LIST)))
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

-   중첩 리스트의 개별 요소를 출력하기 위해서 일반적인 제너레이터는 이중 for 문을 이용해 출력해야한다.
-   첫 번째 for: 전체 리스트에서 중첩된 리스트를 하나씩 가져온다.
-   두 번째 for: 첫 번째 반복문에서 가져온 리스트(it)에서 next 함수가 호출될 때 마다 외부로 각 요소가 전달됨.
    -   iterable(it)의 요소(value)는 반복문을 통해 yield에 전달될 수 있다.

<br>

```python
def chain(iterables):
    for it in iterables:
        # it: [1, 2, 3]
        yield from it  # sub-generator: 직접 이터러블 객체를 처리

print(list(chain(TEST_LIST)))
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

-   개별요소를 출력하기 위해 yield from을 이용할 경우 앞선 예제보다 간단하게 코드를 구현할 수 있다.

-   for: 중첩된 리스트를 하나씩 가져온다.

-   yield from: 리스트의 요소들을 하나씩 꺼내어 yield from에 대기. 외부에서 next가 호출될 때 이 값(요소)이 전달된다.

    -   **yield**는 **하나의 요소를 외부에 전달**하는 반면, **yield from**은 **이터러블 객체**를 받고 외부에서 next가 호출될 때 요소를 한 개씩 외부로 전달한다.

    -   yield from은 sub generator 역할을 하며 이터러블 객체로부터 직접 값을 생산할 수 있음(중첩루프 제거)

    -   어떤 형태의 이터러블에서도 동작 가능(표현식 포함)

        ```python
        def all_powers(n, pow):
            yield from (n ** i for i in range(pow + 1))
        ```

        

**서브 제너레이터에서 반환된 값 구하기**

```python
def sequence(name, start, end):
    print(f'{name} 제너레이터에서 start sequence:{start}')
    yield from range(start, end)
    print(f'{name} 제너레이터에서 end sequence:{end}')
    return end

def main():
    step1 = yield from sequence('first', 0, 5)
    step2 = yield from sequence('second', step1, 10)
    return step1 + step2

g = main()
for _ in range(11):
    print(next(g))

# first 제너레이터에서 start sequence:0
# 0
# ...
# 4
# first 제너레이터에서 end sequence:5
# second 제너레이터에서 start sequence:5
# 5
# ..
# 9
# second 제너레이터에서 end sequence:10
# ... 
# StopIteration: 15  # main의 return 값이 예외 속에 포함됨
```



<br>

**[처음으로](#200926)**
<br>



>### 코루틴 관련 내용은 전문가를 위한 파이썬(이해)과 파이썬 Cookbook(적용 및 실무)을 참고하는 것이 좋을듯

