# 200925

- **[슬롯(slot)](#슬롯slot)**

- **[제너레이터](#제너레이터)**

- **[이상적인 반복](#이상적인-반복)**

    

<br>

**[처음으로](#200925)**
<br>



# 슬롯(slot)

-   클래스에 슬롯(\_\_slot_\_)을 정의하면 클래스가 기대하는 특정 속성만 정의하고 다른것은 제한할 수 있다.

-   클래스는 정적이되고, \_\_dict\_\_ 속성을 갖지 않는다.

    -   동적으로 속성을 추가할 수 없다.

        ```python
        class Coordinate2D:
            __slots__ = ("lat", "long")
        
            def __init__(self, lat, long):
                self.lat = lat
                self.long = long
        
            def __repr__(self):
                return f"{self.__class__.__name__}({self.lat}, {self.long})"
        
        
        a = Coordinate2D(1, 2)
        print(dir(a))
        # ['__class__', '__delattr__', ... , '__subclasshook__', 'lat', 'long'] -> __dict__가 없음
        print(a) 
        # Coordinate2D(1, 2)
        print(a.__slots__)
        # ('lat', 'long')  
        ```

    -   사전 타입이 아니기 때문에 메모리를 덜 사용한다.

<br>

**[처음으로](#200925)**
<br>

# 제너레이터

-   제너레이터는 한 번에 하나씩 구성요소를 반환해주는 이터러블을 생성하는 객체

    -   주요 목적은 **메모리 절약**

    -   거대한 요소를 한꺼번에 메모리에 적재하지 않고 필요할 때 하나씩만 가져오는 것

    ```python
    from _generate_data import PURCHASES_FILE, create_purchases_file
    from log import logger
    
    class PurchasesStats:
        def __init__(self, purchases):
            self.purchases = iter(purchases)
            self.min_price: float = None
            self.max_price: float = None
            self._total_purchases_price: float = 0.0
            self._total_purchases = 0
            self._initialize()
    
        def _initialize(self):
            try:
                first_value = next(self.purchases)
            except StopIteration:
                raise ValueError("no values provided")
    
            self.min_price = self.max_price = first_value
            self._update_avg(first_value)
    
        def process(self):
            for purchase_value in self.purchases:
                self._update_min(purchase_value)
                self._update_max(purchase_value)
                self._update_avg(purchase_value)
            return self
    
        def _update_min(self, new_value: float):
            if new_value < self.min_price:
                self.min_price = new_value
    
        def _update_max(self, new_value: float):
            if new_value > self.max_price:
                self.max_price = new_value
    
        @property
        def avg_price(self):
            return self._total_purchases_price / self._total_purchases
    
        def _update_avg(self, new_value: float):
            self._total_purchases_price += new_value
            self._total_purchases += 1
    
        def __str__(self):
            return (
                f"{self.__class__.__name__}({self.min_price}, "
                f"{self.max_price}, {self.avg_price})"
            )
    
    # with list
    def _load_purchases(filename):
        purchases = []
        with open(filename) as f:
            for line in f:
                *_, price_raw = line.partition(",")
                purchases.append(float(price_raw))
    
        return purchases
    
    # with generator
    def load_purchases(filename):
        with open(filename) as f:
            for line in f:
                *_, price_raw = line.partition(",")
                yield float(price_raw)
    
    
    def main():
        purchases = load_purchases(PURCHASES_FILE)
        stats = PurchasesStats(purchases).process()
        logger.info("Results: %s", stats)
    
    if __name__ == '__main__':
        main()
    ```

    -   process()가 실행될 때 전달받은 purchases에서 한 개씩 값을 처리한다.
    -   _load_purchases(): 리스트에 100만개의 데이터를 받아서 PurchasesStats 초기화 값에 전달
        -   100만개의 데이터를 메모리에 올린 후 process()에서 한 개씩 처리한다.
    -   load_purchases(): 제너레이터를 반환한다.
        -   100만개의 데이터를 한꺼번에 가져오지 않고 process()에서 제너레이터로부터 생성된 요소들을 하나씩 처리한다.

<br>

**[처음으로](#200925)**
<br>

# 이상적인 반복

### 관용적인 반복 코드

-   기본적으로 반복을 지원하기 위해서는 \_\_iter\_\_ 매직 메서드를 구현해야하고, 이와 더불어 \_\_next\_\_ 메서드를 구현하면 이 객체는 이터레이터가 된다.

```python
class NumberSequence:
    def __init__(self, start=0, end=100):
        self.current = start
        self.end = end

    def __next__(self):
        # end 조건은 내가 추가한 것
        if self.current == self.end:
            raise StopIteration  # 중지 조건을 만족할 떄 StopIteration 에러를 일으켜 반복을 중지
        current = self.current
        self.current += 1
        return current

    def __iter__(self):
        return self


ns = NumberSequence()
for i in ns:
    print(i)  # TypeError: 'NumberSequence' object is not isterable

print(list(zip(ns, 'abcde')))  # empty
print(list(zip(NumberSequence(), 'abcde')))  # [(0, 'a'), (1, 'b'), (2, 'c'), (3, 'd'), (4, 'e')]
```

-   \_\_method\_\_ 내장함수를 구현했기 때문에 next() 함수를 이용해 호출할 필요 없이 반복문(for)을 이용할 수 있다.



**제너레이터 사용하기** 

-   함수에 yield 키워드가 포함되어있을 경우 그 함수는 제너리어터가 된다.

-   위 코드를 제너레이터로 간단하게 구성하면 아래와 같다

    ```python
    def sequence(start=0):
        while True:
            yield start
            start += 1
    ```



<br>

**중첩 루프**

```python
# 2중 for문(bad)
def search_nested_bad(array, desired_value):
    coords = None
    for i, row in enumerate(array):
        for j, cell in enumerate(row):
            if cell == desired_value:
                coords = (i, j)
                break

        if coords is not None:
            break
    if coords is None:
        raise ValueError(f"{desired_value} not found")
    return coords


def _iterate_array2d(array2d):
    for i, row in enumerate(array2d):
        for j, cell in enumerate(row):
            yield (i, j), cell

# generator(good)
def search_nested(array, desired_value):
    try:
        coord = next(coord for (coord, cell) in _iterate_array2d(array)
                     if cell == desired_value)
    except StopIteration:
        raise ValueError(f"{desired_value} not found")
    return coord


li = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [5, 4, 3, 2, 1, 5, 4, 3, 2, 1]]
print(search_nested_bad(li, 3))  # (0, 2)
print(search_nested(li, 5))  # (0, 4)
```

-   **search_nested 함수의 try 구문을 잘 이해해 두도록**
-   private 함수를 생성하고 next 구문 내에서 사용 -> private 함수는 좌표(coord)와 요소(cell)을 각각 yield로 생성하고 next를 통해 가져옴
-   if 구문의 조건을 통해 값을 찾을 경우 coord를 전달



<br>

**[처음으로](#200925)**
<br>

























