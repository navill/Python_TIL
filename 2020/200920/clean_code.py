# ------------ [orthogonality] -------------


class BaseTokenizer:
    def __init__(self, str_token):
        self.str_token = str_token

    def __iter__(self):
        yield from self.str_token.split('-')


class UpperIterableMixin:
    def __iter__(self):
        return map(str.upper, super().__iter__())


class Tokenizer(UpperIterableMixin, BaseTokenizer):
    pass


number_str = '1-2-3-4-5-6'
token = Tokenizer(number_str)
alphabet_str = 'a-b-c-d-e-f-g'
token2 = Tokenizer(alphabet_str)
print(list(token))
print(list(token2))
list1 = [1, 2, 3, 4, 5]
print(list(map(lambda x: x - 1, list1)))
print(list1)


# ----------------------------------
def calculate_price(base_price, tax, discount):
    return (base_price * (1 + tax)) * (1 - discount)


def show_price(price):
    return f"${price:.2f}"


def str_final_price(base_price, tax, discount, fmt_function=str):
    return fmt_function(calculate_price(base_price, tax, discount))


print(str_final_price(1000, 0.2, 0.5))
print(str_final_price(1000, 0.2, 0.5, fmt_function=show_price))
# ------------  -------------
