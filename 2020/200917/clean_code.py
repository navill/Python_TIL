# ------------- sequence --------------
from datetime import timedelta, date


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
print(drc[0])
print(drc[-1])


# ------------- container --------------

#
# def mark_coordinate(grid, coord):
#     if 0 <= coord.x < grid.width and 0 <= coord.y < grid.height:
#         grid[coord] = 1


class Boundaries:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __contains__(self, coord):
        x, y = coord
        return 0 <= x < self.width and 0 <= y < self.height


class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.limits = Boundaries(width, height)

    def __contains__(self, coord):
        return coord in self.limits


# Grid2도 동작은 하지만 코드를 이해하기 어렵다
# Boundaries를 재사용하긴 하지만 Grid 클래스가 더 낫다고 생각됨
# class Grid2(Boundaries):
#     def __init__(self, width, height):
#         super(Grid2, self).__init__(width, height)
#         self.limits = Boundaries(width, height)


def mark_coordinate(grid, coord):
    if coord in grid:
        print('Mark:1')
    else:
        print('Mark:0')


g = Grid(4, 4)
mark_coordinate(g, [5, 3])
mark_coordinate(g, [3, 3])


# g = Grid2(4, 4)
# mark_coordinate(g, [5, 3])
# mark_coordinate(g, [3, 3])

# ------------- dynamic attributes --------------
class DynamicAttributes:
    def __init__(self, attribute):
        self.attribute = attribute

    def __getattr__(self, attr):
        if attr.startswith('fallback_'):
            name = attr.replace("fallback_", "")
            return f"[fallback resolved] {name}"
        raise AttributeError(f"{self.__class__.__name__}에는 {attr} 속성이 없음")


print()
dyn = DynamicAttributes('value')
print(dyn.attribute)
print(dyn.fallback_test)
dyn.__dict__["fallback_new"] = "new value"
print(dyn.fallback_new)
print(getattr(dyn, 'something', 'default'))
# print(dyn.something)
print(dyn.__getattr__('fallback_new1'))

# ------------- callable --------------
from collections import defaultdict, UserList


class CallCount:
    def __init__(self):
        self._count = defaultdict(int)

    def __call__(self, argument):
        self._count[argument] += 1
        return self._count[argument]


cc = CallCount()
print(cc(1))
print(cc(1))
print(cc(1))
print(cc(2))
print(cc(3))
print(cc(2))


# ------------- Note on Python --------------
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
print(bl)


# "".join(bl)


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
print(bl)
print(";".join(bl))

# ------------- Design by Contract --------------
import os
print(os.getenv('DBHOST'))