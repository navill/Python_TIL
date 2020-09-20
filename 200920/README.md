# 200920

- [함수 인자의 개수](#함수-인자의-개수 )

- [소프트웨어의 독립성](#소프트웨어의-독립성)



**[처음으로](#200918)**



# 함수 인자의 개수

- 함수나 메서드에 너무 많은 인자를 전달하는 것은 잘못 디자인 되었음을 의미한다.
  1. 여러 인자를 포함하는 하나의 새로운 객체를 생성하고 그것을 메서드나 함수의 인자로 전달한다.
  2. 가변인자(*args) 또는 키워드 인자(*kwargs)로 전달한다.
     - 매우 동적이기 때문에 유지보수가 어려워질 수 있다.



### 함수 인자와 결합력

- **f1**과 **f2** 두 개의 함수가 있다고 가정
- **f2**는 다섯 개의 파라미터를 사용
  - **f2**를 호출하기 위해 많은 정보(다섯 개의 파라미터)를 수집해야햔다.
  - **f1**이 **f2**를 호출하기 위한 모든 파라미터를 갖고 있을 경우 
    - 많은 파라미터를 바탕으로 **f2**의 기능을 유추할 수 있음.
    - 따라서 **f1** 내에서 자체적으로 **f2**의 역할을 수행할 수 있음
    - **f2**는 많은 것을 추상화하지 않았음을 의미



### 많은 인자를 취하는 작은 함수의 서명

```python
# bad
track_request(request.headers, request.ip_addr, request.request_id)

# good
track_request(request)
```

- 여러 파라미터가 한 객체의 속성들일 경우, 객체의 속성을 하나씩 넘기지 말고 **객체**를 전달하라.
  - 단, 그중 변경 가능 객체가 있는지 반드시 확인이 필요 - 부작용을 낳을 수 있다.

**파라미터 그루핑**

- 한 개의 객체(컨테이너)에 파라미터를 담고, 그것을 인자로 전달하는 방법 

**\*args & \*\*args**

- 파라미터를 유연하게 활용할 수 있다는 장점을 가지지만, 가독성을 거의 상실하기 때문에 주의해서 사용해야한다.
- 파라미터가 많을 경우 위치&키워드 인자는 자제하는 것이 좋다.
  - 꼭 사용해야할 경우, 잘 작성된 docstring이 필수





# 소프트웨어의 독립성

직교(orthogonality): 어느 하나가 변해도 다른 하나에는 영향을 미치지 않는다.

- 모듈, 클래스 또는 함수를 변경하면 수정한 컴포턴트가 외부 세계에 영향을 미치지 않아야 한다.

- 이는 항상 가능할 수 없기 때문에 외부에 미치는 영향을 최소화하려는 시도가 필요하다([관심사의 분리](https://github.com/navill/Python_TIL/tree/master/200918#관심사의-분리)).

  ```python
  class BaseTokenizer:
      def __init__(self, str_token):
          self.str_token = str_token
  
      def __iter__(self):  # *
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
  print(list(token))  # ['1', '2', '3', '4', '5', '6']
  print(list(token2))  # ['A', 'B', 'C', 'D', 'E', 'F', 'G']
  ```

  - 만약 iter 매직 메서드가 제너레이터가 아닌 리스트를 반환한다면, 나머지 클래스에 종속성이 생기게 된다.

    - BaseTokenizer에서 반환된 리스트가 Mixin 클래스에 의해 변경될 수 있다(map은 복사본을 이용해 새로운 값을 반환하기 때문에 실제로 리스트가 변경되지는 않는다).

      

  ```python
  def calculate_price(base_price, tax, discount):  # 1
      return (base_price * (1 + tax)) * (1 - discount)
  
  
  def show_price(price):  # 2
      return f"${price:.2f}"
  
  
  def str_final_price(base_price, tax, discount, fmt_function=str):
      return fmt_function(calculate_price(base_price, tax, discount))
  
  
  print(str_final_price(100, 0.2, 0.5))  # 600
  print(str_final_price(1000, 0.2, 0.5, fmt_function=show_price))  # $600.00
  ```

  - 위 두 개의 함수는 서로 독립적이다(1번 함수와 2번 함수).
  - **str_final_price**: fmt_function을 인가할 경우 해당 **함수를 이용해 값을 출력**하고, 없을 경우 **기본 문자열(str)을 출력**한다.
  - 최소한의 인터페이스를 유지한다면 어느 함수를 변경하더라도 다른 함수에 영향을 미치지 않는다.

- 두 코드가 독립적일 경우, 두 개의 테스트가 통과하면 전체 회귀 테스트를 하지 않고도 어플리케이션에 문제가 없다고 확신할 수 있다.



