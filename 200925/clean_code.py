# -------------- generator --------------------
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


def _load_purchases(filename):
    purchases = []
    with open(filename) as f:
        for line in f:
            *_, price_raw = line.partition(",")
            purchases.append(float(price_raw))

    return purchases


def load_purchases(filename):
    with open(filename) as f:
        for line in f:
            *_, price_raw = line.partition(",")
            yield float(price_raw)


def main():
    # create_purchases_file(PURCHASES_FILE)
    purchases = load_purchases(PURCHASES_FILE)
    stats = PurchasesStats(purchases).process()
    logger.info("Results: %s", stats)


# main()


# -------------- 관용적인 반복 코드 -----------
# enumerate와 유사한 클래스 생성
class NumberSequence:
    def __init__(self, start=0, end=100):
        self.current = start
        self.end = end

    def __next__(self):
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


# ----------- 중첩 루프 -------------
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


def search_nested(array, desired_value):
    try:
        coord = next(coord for (coord, cell) in _iterate_array2d(array)
                     if cell == desired_value)
    except StopIteration:
        raise ValueError(f"{desired_value} not found")
    return coord


li = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [5, 4, 3, 2, 1, 5, 4, 3, 2, 1]]
print(search_nested_bad(li, 3))
print(search_nested(li, 5))
