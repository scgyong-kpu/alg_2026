# 2주차 Python 키워드

## 리스트

- list
array라고도 하는데 list가 파이썬 공식 명칭
다른 언어에서 list라고 하면 linked list를 주로 부르는 경우가 있다.

- 원소
- index
list 내 원소를 호출하는 방식, 음수로 명칭 가능
- 음수 index

- slicing
- 시작 / 끝 / 간격


- append()
현재 list 맨 뒤에 붙이는 것

- len()
global 함수. 리스트말고도 사용할 수 있다. 

- range()
- 얕은 복사
- 중첩 리스트

## 딕셔너리

key로 value를 찾아가는 방법.
- dictionary
- key
보통 문자열을 사용함. hash값을 통해 찾아간다.(상수 시간)
- value
- item
- KeyError
키가 없으면 죽는다. 그래서 key in dict를 사용
- `key in dict`

- 조건식
- `value if condition else other`


- 반복문으로 key 순회
보통 key만으로는 안한다.
- key 정렬

- insertion order
dict는 빠른 것을 가장 중요하게 생각함.

- defaultdict
key in dict를 하고싶지 않을 때. 알아서 채워 넣어라

## 튜플
소괄호를 써서 만듬. 귀찮으면 그냥 이거 써라.(다들어간다.)
- tuple
- unpacking
이거 잘 모르겟는데요

- list와 tuple의 차이
avalable write과 readonly 차이

- 여러 값 반환
는 아니고 튜플에 다 때려넣고 반환

- immutable
변경가능하지 않은거
sort 불가능


## 함수
def
- 함수 정의
- 함수 호출

- parameter
- argument
두개가 같?은거?

- positional argument
순서가 필요함

- keyword argument
그딴거 필요없고 앞에 키워드 쓰면 그대로 넣어줌

- 기본값 인자
디폴트

- 지역 변수
- 전역 변수
write 후 read하는 경우 주의

- return
- 여러 값 반환
아까나온거

## 클래스와 객체

- class
- object
- instance
- attribute
속성
프로퍼티? 
a.b = 3
c에서 맴버변수를 3으로 바꿔라
다른언어에서 멤버변수를 3으로 바꾸는 함수호출
이 때 프로퍼티라 한다

파이썬의 프로퍼티는 런타임에 결정된다.


- method
- `self`
객체 자신이 모든 인자의 첫번째가 되도록 강제
c++은 this를 써야한다.
관용적으로 self를 쓰는거지 딴거 써도 된다.

- constructor

- `__init__()`
- 런타임 속성 추가
- polymorphism
폴리모피즘
나는 똑같은 일을 시켰는데 서로 다른 일을 하는거. 알아서 바꿔서 해라.

- inheritance
- `__repr__()`
- `__str__()`

## 문자열 포매팅

- text formatting
- `%` formatting
- `format()`
- f-string
이게 제일 깔쌈하다.

- format specifier
이게뭐임

- 객체 출력

## 모듈

- module
- import
- math module
- degree
- radian
- 삼각함수
- 회전 변환
- pygame
- window
- coordinate
- point
- line
- event loop

## 리스트 컴프리헨션과 함수형 도구

- list comprehension
for loop를 사용해서 리스트 내 내용을 다 loop안에 넣는거

- map()
배열 안에 있는 함수 하나하나를 모아서 새로운 함수를 만든다.
삼총사
필터 리듀스

- iterator
- list() 변환

- lambda
람다식. 이름없느 함수



- inline function
- `for _ in range(...)`

- 난수
- random module
이게 쥔짜 랜덤일꽈?
seed

- randrange()/randint()
끝을 포함하는함수?


- chr()
아스키 코드를 문자열로

- ord()
그반대로

- class 생성자와 함수 호출
