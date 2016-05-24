# Random Sort with Genetic Algorithm
Random sort 보통 bogosort나 stupid sort, slow sort로 불리는 바보같은 정렬은 정렬 알고리즘 중에서도 거의 최악의 알고리즘으로 수 만번 연산해도 원하는 정렬을 만들어내지 못할 수도 있습니다.

이에 유전알고리즘을 병합하면 유의미한 수준의 성능 향상을 이끌어낼 수 있습니다.

사실 방법은 매우 간단합니다.

몇 개의 무작위로 생성된 리스트를 하나로 묶어 한 세대라고 해봅시다.
이 세대들은 완전히 정렬된 어떤 배열 SORTED와 차이가 있을 겁니다.
이 차이가 작은 정도를 `적합도`라고 부릅시다.

그러면 첫 세대에서 가장 `적합도`가 높은 개체들을 많이 생존시키고
다른 개체들은 다시 무작위로 생성하거나 `교차` - `돌연변이`를 이용하여
계속 세대를 진행하다 보면 `적합도`가 높은 개체들은 많이 남고 그렇지 않은 개체들은 탈락하여
결과적으로 `적합도`가 가장 높을 때 우리는 완전히 정렬된 리스트를 얻을 수 있을 겁니다.

우리가 결정해야 될 몇 가지는 아래와 같습니다.

- 어떻게 `적합도`를 판단할 것인지
- 어느정도로 `교차`, `돌연변이`를 발생시킬 것인지
- `적합도`가 높은 개체들을 얼마나 생존시키게 할 것인지

이러한 준비가 끝나면 실제로 코드를 통해서 우리의 알고리즘이 어떤 무작위 배열을 정렬된 배열로
진화시킬 수 있을지 실험해 봅시다.

아래는 Python을 사용하여 실제로 랜덤하게 주어진 배열을 정렬하는 유전알고리즘을 구성하는 간단한 방법을 담고 있습니다.

---

일단 하나의 개체를 나타내는 클래스를 만들어 봅시다.
```
class DNA:
  def __init__(self, gene):
    self.gene = gene
```

여기에 이 개체의 적합도를 `@property`를 이용하여 만들어봅시다.
이 적합도를 어떻게 측정하느냐는 바꿀 수 있습니다.
아래의 코드는 어느 자리에 있어야 하는 X와 그 자리에 있는 숫자 Y의 차 abs(X-Y)를 SIZE에서(리스트의 길이) 빼주는것으로 정의되어있습니다.
```
  @property
  def fitness(self) -> int:
    return reduce(lambda x, y: x+y, list(map(lambda x, y: SIZE-abs(x-y), SORTED, self.gene)))
```
이제 이 개체들을 여럿 모은 하나의 세대를 나타내는 클래스를 꾸며봅시다.
초기화 할 때 위의 DNA들로 이루어진 리스트를 넣어 초기화 합니다.
```
class Generation:
  def __init__(self, DNA_list):
    self.DNA_list = DNA_list
```

이 Generation의 평균 적합도는 산술, 기하 평균을 사용해도 되지만 numpy의 mean를 사용해 간단히 만들수도 있습니다.
```
  def fitness(self):
    return mean([dna.fitness for dna in self.DNA_list])
```

기본적인 구성은 끝났으니 이제 다음 세대를 만드는 과정을 구현해야 합니다.
한 세대에서 다음 세대로 가는 '진화'를 담당하는 함수를 만들어봅시다. 다음 세대의 개체들을 먼저 만든후 새로운 Generation를 다음 세대의 개체들로 초기화 해서 반환해 주면 되겠죠.
```
  def evolution(self):
    childs = [this.child() for _ in range(CHILD_SIZE)]
    return Generation(childs)
```
여기서 CHILD_SIZE는 한 세대를 구성하는 개체의 수를 지정합니다.

그러면 이제 자식을 생성하는 child 함수도 꾸며야합니다.

이 자식을 어떻게 생성할 것이냐가 문제입니다.
어느정도는 가장 좋은 개체들을, 어느 정도는 교차-변이를 통해 교배된 자식들을 넘겨줘야합니다.

우선 가장 좋은 개체들을 찾아보죠
각 개체는 DNA 클래스로 만들어져 있고 우리는 fitness라는 적합도를 구하는 속성을 만들어 두었기 때문에 아래와 같이 간단하게 가장 높은 적합도를 가지는 개체를 찾아낼 수 있습니다.
```
  def best(self):
    return sorted(self.DNA_list, key=lambda dna: dna.fitness)[-1]
```



















