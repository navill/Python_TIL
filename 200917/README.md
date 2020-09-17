# Sequence

- Sequence는 **len**과 **getitem** 매직 메서드가 구현된 객체를 의미([자체 시퀀스 생성]([https://github.com/navill/Python_TIL/tree/master/200916#%EC%9E%90%EC%B2%B4-%EC%8B%9C%ED%80%80%EC%8A%A4-%EC%83%9D%EC%84%B1](https://github.com/navill/Python_TIL/tree/master/200916#자체-시퀀스-생성)) 참고) 

- iterable과 마찬가지로 반복문을 통해 객체의 여러 요소를 가져올 수 있다.

- 하지만 iterable과 sequence는 메모리와 CPU 사이의 트레이드오프 관계를 나타낸다.

  - iterable: n번째 요소를 메모리에 적재하고 필요할 때 꺼내서 쓴다.
    - 요소 한 개씩 소모하기 때문에 메모리 소모량이 낮음
    - n 번째 요소를 얻기 위한 시간복잡도는 O(n)

  - sequence: 전체 요소를 메모리에 적재하여 사용한다.
    - 전체 요소가 메모리에 할당되기 때문에 메모리 소모량이 높음
    - n번째 요소를 얻기(indexing) 위한 시간복잡도는 O(1)

  ```python
  class DateRangeSequence:
      def __init__(self, start_date, end_date):
          self.start_date = start_date
          self.end_date = end_date
          self._range = self._create_range()
  
      def _create_range(self):
          days = []
          current_day = self.start_date
          while current_day < self.end_date:
              days.append(current_day)
              current_day += timedelta(days=1)
          return days
  
      def __getitem__(self, day_no):
          return self._range[day_no]
  
      def __len__(self):
          return len(self._range)  
      
  drc = DateRangeSequence(date(2020, 9, 17), date(2020, 9, 20))
  print(drc[0])  # 2020-09-17
  print(drc[1])  # 2020-09-18
  print(drc[-1])  # 2020-09-19
  ```

  - 반환된 리스트 객체(days)에 의해 list가 가지고 있는 작업을 수행할 수 있음(음수를 이용한 indexing이 가능한 이유)
  - 내장된 자료구조를 래핑하여 구현할 경우 호환성과 일관성을 올바르게 유지할 수 있다.

- iterable과 sequence(+generator)를 사용할 때 메모리와 cpu의 트레이드 오프 관계를 생각하자.



# Container

- Container 객체는 일반적으로 boolean 값을 반환하는 contains 매직 메서드를 구현한 객체를 의미한다.

- 파이썬의 'in' 키워드가 호출될 때 contains 매직 메서드가 호출된다.

  ```python
  element in container == container.__contains__(element)
  ```



**예제:** 2차원 지도에 특정 위치를 표시하는 코드

```python
def mark_coordinate(grid, coord):
    if 0 <= coord.x < grid.width and 0 <= coord.y < grid.height:
        print('Mark:1')
```

- 난해한 코드

  

```python
# 개선된 코드
class Boundaries:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __contains__(self, coord):
        x, y = coord
        # return에서 실제 좌표가 경계를 넘지 않는지 검사
        return 0 <= x < self.width and 0 <= y < self.height

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.limits = Boundaries(width, height)

    def __contains__(self, coord):
        return coord in self.limits  # Boundaries에 검사를 위임

def mark_coordinate(grid, coord):
    if coord in grid:
        print('Mark:1')
    else:
        print('Mark:0')

g = Grid(4, 4)
mark_coordinate(g, [5, 3])  # Mark:0
mark_coordinate(g, [3, 3])  # Mark:1
```

- 실제 비교 구문을 Boundaries에 위임
- 외부에서 mark_coordnate()을 사용할 때 가독성을 높일 수 있다.



# 객체의 동적인 속성(\_\_getattr\_\_)

- getattr 매직 메서드를 이용해 객체에서 속성을 얻는 방법 제어

  1. obj.my_attr 호출 

  2. obj.\_\_dict\_\_에서 'my_attr'을 찾는다

  3. \_\_getattribute\_\_('my_attr') 호출 -> 없을 경우 \_\_getattr\_\_('my_attr') 호출 

  4. my_attr 반환

     ```python
     class DynamicAttributes:
         def __init__(self, attribute):
             self.attribute = attribute
     
         def __getattr__(self, attr):
             if attr.startswith('fallback_'):
                 name = attr.replace("fallback_", "")
                 return f"[fallback resolved] {name}"
             raise AttributeError(f"{self.__class__.__name__}에는 {attr} 속성이 없음")
     
     dyn = DynamicAttributes('value')
     print(dyn.attribute)  # value
     
     print(dyn.fallback_test)  # [fallback resolved] test
     
     dyn.__dict__["fallback_new"] = "new value"  
     # 위 코드는 dyn.fallback_new = "new value"와 동일하다.
     print(dyn.fallback_new)  # new value
     
     print(getattr(dyn, 'something','default'))  # default
     print(dyn.something)  # AttirbuteError: ... 
     ```

     - dyn.fallback_test: 객체에 없는 fallback_test 속성을 호출 -> \_\_getattr\_\_이 호출되면서 문자열을 반환한다.
     - getattr(dyn, 'something', 'default'): 디폴트값을 설정할 경우, exception이 일어날 때 디폴트 값이 반환된다.



# callable

- \_\_call\_\_ 매직 메서드를 구현할 경우 객체를 일반 함수처럼 호출 할 수 있다.

- 전달된 모든 파라미터는 \_\_call\_\_에 전달된다.

- callable 매직 메서드를 이용해 (상태를 저장하고 있는)객체를 함수처럼 호출하여 상태를 전달하거나 변경할 수 있다.

  ```python
  class CallCount:
      def __init__(self):
          self._count = defaultdict(int)
  
      def __call__(self, argument):
          self._count[argument] += 1
          return self._count[argument]
  
  cc = CallCount()
  print(cc(1))  # 1
  print(cc(1))  # 2
  print(cc(1))  # 3
  print(cc(2))  # 1
  print(cc(3))  # 1
  print(cc(2))  # 2
  print(cc('something'))  # 1
  ```

  - 객체를 생성할 때 _count는 dict 타입의 속성을 갖는다.
  - cc객체에 **매개 변수**를 전달할 경우 **\_\_call\_\_ 메서드의 매개변수**로 전달된다.
  - 해당 매개변수는 _count의 **키**로 사용되며 값으로 호출된 만큼의 숫자가 **값**으로 저장된다.



# 파이썬에서 유의할 점



### 매개변수의 기본값으로 가변형 데이터를 사용하면 안된다.

### 내장 타입 확장

- str, list, dict를 확장하고자 할 때는 반드시 collections의 UserString, UserList, UserDict를 상속받아 확장해야한다.

  ```python
  class BadList(list):
      def __getitem__(self, index):
          print(self.__class__)
          value = super().__getitem__(index)
          if index % 2 == 0:
              prefix = '짝수'
          else:
              prefix = '홀수'
          return f"[{prefix}] {value}"
  
  bl = BadList((0, 1, 2, 3, 4, 5))
  print(bl)  # [0, 1, 2, 3, 4, 5]
  print("".join(bl))  # TypeError: ... => join에 입력된 매개변수가 숫자일 것이라 예상하기 때문에 error
  ```

  - built-in list를 확장할 경우 BadList의 \_\_getitem\_\_ 이 아닌 list의 매직 메서드가 실행된다(print 출력 안됨)

  ```python
  class GoodList(UserList):
      def __getitem__(self, index):
          print(self.__class__)
          value = super().__getitem__(index)
          if index % 2 == 0:
              prefix = '짝수'
          else:
              prefix = '홀수'
          return f"[{prefix}] {value}"
  
  bl = GoodList((0, 1, 2, 3, 4, 5))
  print(bl)  # [0, 1, 2, 3, 4, 5]
  # __getitem__이 호출된 수 만큼 <class '__main__.GoodList'> 출력됨
  print(";".join(bl))  # [짝수] 0;[홀수] 1;[짝수] 2;[홀수] 3;[짝수] 4;[홀수] 5;
  ```

  - UserList를 호출할 경우 정상적으로 GoodList의 getitem 매직 메서드가 실행된다.













