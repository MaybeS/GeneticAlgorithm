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

## 만들어보기
---

### 개체를 나타내는 클래스
일단 하나의 개체를 나타내는 클래스를 만들어 봅시다.
```
class DNA:
  def __init__(self, gene):
    self.gene = gene
```

### 각 개체의 적합도
여기에 이 개체의 적합도를 `@property`를 이용하여 만들어봅시다.
이 적합도를 어떻게 측정하느냐는 바꿀 수 있습니다.
아래의 코드는 어느 자리에 있어야 하는 X와 그 자리에 있는 숫자 Y의 차 abs(X-Y)를 DNA_SIZE에서(유전자의 크기(여기에선 리스트의 길이)) 빼주는것으로 정의되어있습니다.
```
  @property
  def fitness(self) -> int:
    return reduce(lambda x, y: x+y, list(map(lambda x, y: DNA_SIZE-abs(x-y), SORTED, self.gene)))
```

### 세대를 나타내는 클래스
이제 이 개체들을 여럿 모은 하나의 세대를 나타내는 클래스를 꾸며봅시다.
초기화 할 때 위의 DNA들로 이루어진 리스트를 넣어 초기화 합니다.
```
class Generation:
  def __init__(self, DNA_list):
    self.DNA_list = DNA_list
```

### 세대의 적합도
이 Generation의 평균 적합도는 산술, 기하 평균을 사용해도 되지만 numpy의 mean를 사용해 간단히 만들수도 있습니다.
```
  def fitness(self):
    return mean([dna.fitness for dna in self.DNA_list])
```

### 다음 세대 만들기
기본적인 구성은 끝났으니 이제 다음 세대를 만드는 과정을 구현해야 합니다.
한 세대에서 다음 세대로 가는 '진화'를 담당하는 함수를 만들어봅시다. 다음 세대의 개체들을 먼저 만든후 새로운 Generation를 다음 세대의 개체들로 초기화 해서 반환해 주면 되겠죠.
```
  def evolution(self):
    childs = [self.best if uniform(0.0, 1.0) < SELECT_BEST_RATE else self.child() for _ in range(CHILD_SIZE)]
    return Generation(childs)
```
*여기서 CHILD_SIZE는 한 세대를 구성하는 개체의 수를 지정합니다.*
*SELECT_BEST_RATE는 가장 높은 적합도를 가지는 개체들을 얼마나 물려줄 것인지를 결정합니다.*

그러면 이제 자식을 생성하는 child 함수도 꾸며야합니다.

이 자식을 어떻게 생성할 것이냐가 문제입니다.
어느정도는 가장 좋은 개체들을, 어느 정도는 교차-변이를 통해 교배된 자식들을 넘겨줘야합니다.

#### 가장 적합도가 높은 개체 찾기
우선 가장 적합도가 높은 개체들을 찾아보죠
각 개체는 DNA 클래스로 만들어져 있고 우리는 fitness라는 적합도를 구하는 속성을 만들어 두었기 때문에 아래와 같이 간단하게 가장 높은 적합도를 가지는 개체를 찾아낼 수 있습니다.
```
  def best(self):
    return sorted(self.DNA_list, key=lambda dna: dna.fitness)[-1]
```

#### 자식 만들기
가장 적합도가 높은 개체들로만 다음 세대를 구성한다면 아무런 진화가 일어나지 못할 것입니다.
따라서 우리는 적합도가 높지 않을 수 있지만 다양성을 확보하기 위해 일정확률로 부모를 선택하여 자식을 만드는 과정도 추가해야 합니다.

물론 이러한 부모를 선택하는 과정도 적합도에 비례하는 확률로 선택하면 더 좋은 결과를 가져올 수 있을 것 입니다.

어떤 두 DNA 클래스를 받아 교배시켜 자식을 반환해주는 함수를 하나 구성해 봅시다.

정말 간단한 교차과정으로 어떤 점을 잡아 그 점 전까지는 아버지 DNA, 그 이후는 어머니 DNA를 물려받고 일정확률로 변이가 일어나도록 하는 함수를 만들어 봅시다.
```
def breeding(mother, father):
  point = randrange(0, DNA_SIZE)
  sperm = father.gene[:point]
  fetus = [x for x in mother.gene if x not in sperm]
  offspring = sperm + fetus
  
  if uniform(0.0, 1.0) < MUTATION_RATE:
    x = randrange(0, DNA_SIZE)
    y = randrange(0, DNA_SIZE)
    offspring[x], offspring[y] = offspring[y], offspring[x]
    
  return offspring
  
```
*DNA_SIZE는 개체의 유전자 정보의 크기를 나타냅니다. 여기서는 배열의 길이가 되겠네요.*
*MUTATION_RATE는 변이가 얼마나 일어날지를 나타냅니다.*

추가로 다양한 교차 방법을 추가해 볼 수 있을 겁니다.

#### 적절한 부모 찾기
그러면 이제 breeding함수를 호출할 적절한 두 부모를 세대 내에서 찾아봐야 합니다.
여기서 많은 방법들이 존재하는데 '룰렛 휠', '토너먼트', '순위 기반', '공유' 등 다양한 방법이 존재합니다.

여기에서는 룰렛 휠을 통해 적절한 부모를 선택해 볼것입니다.
이 룰렛 휠 방법은 룰렛의 각 영역을 개체들이라 생각하고 여기에 다트를 던지는 것입니다. 영역의 크기가 모두 같다면 같은 확률이지만 영역의 크기를 적합도에 비례해서 조절한다면 결과는 달라질 것입니다.

```
  def findParents(self):
    p = uniform(0.0, sum([x.fitness for x in self.DNA_list]))
    c = 0
    for dna in self.DNA_list:
      c += dna.fitness
      if c>p:
        return dna
```

### 다음 세대 만들기
그럼 이제 evolution함수에서 필요했던 child함수를 만들어 봅시다.
```
  def child():
    father = findParents()
    mother = findParents()
    return breeding(mother, father)
```

### 거의 다 왔습니다.
이제 대부분의 코드들을 모두 작성했 습니다.
나머지는 main을 구성하면 됩니다.

세대들을 담을 리스트를 하나 만들고 첫 세대를 무작위한 배열로 주어준 후 적합도가 최대일 때 까지 세대를 거듭해 보도록 만들어 봅시다.

### 완성
아마 완성된 모습은 [이 코드]('https://gist.github.com/MaybeS/dd975a898ca8a603d936672d46697e6a')와 비슷할 것입니다.

*사용을 간편하게 하는 몇 가지 함수가 추가되어있으며 main 부분이 따로 구성되어 있습니다.*

한 번 실행해보고 주어진 여러 비율들을 잘 조절해 더 나은 결과를 얻을 수 있도록 해 보세요.
