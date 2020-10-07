# -------------- adapter ---------------
from typing import Union


class UsernameLookup:
    def search(self, user_namespace):
        print(f"looking for {user_namespace}")


class UserSource(UsernameLookup):
    def fetch(self, user_id: str, username: str):
        user_namespace = self._adapt_arguments(user_id, username)
        return self.search(user_namespace)

    # @staticmethod
    def _adapt_arguments(self, user_id: str, username: str):
        return f"{user_id}:{username}"


class UserSource2:
    def __init__(self):
        self.username_lookup = UsernameLookup()

    def fetch(self, user_id: str, username: str):
        user_namespace = self._adapt_arguments(user_id, username)
        return self.username_lookup.search(user_namespace)

    # @staticmethod
    def _adapt_arguments(self, user_id: str, username: str):
        return f"{user_id}:{username}"


# us = UserSource()
# us.fetch("id", "jihoon")
# us = UserSource2()
# us.fetch("id", "jihoon")


# ------------ composite ------------------
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


# a = Product('a', 1000)
# b = Product('b', 2000)
# a_b = ProductBundle('ab_bundle', 0.3, a, b)
# print(a.price)
# print(b.price)
# print(a_b.price)


# ----------- decorator -------------
class DictQuery:
    def __init__(self, **kwargs):
        self._raw_query = kwargs

    def render(self):
        return self._raw_query


class QueryEnhancer:  # class 추상화
    def __init__(self, query):
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
print(new_query.render())


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
