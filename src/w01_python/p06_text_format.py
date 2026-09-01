# Python 06. Text Formatting
#
# 프로그램은 계산 결과를 사람이 읽을 수 있는 문자열로 보여주어야 합니다.
# 문자열 포맷팅은 디버깅 출력, 채점용 출력, 로그 메시지에서 계속 사용됩니다.


name = "Kim"
score = 91
average = 87.625

print("-- percent formatting --")

# % 연산자를 이용한 방식은 C의 printf 스타일과 비슷합니다.
# 오래된 Python 코드에서 여전히 볼 수 있으므로 읽을 수 있어야 합니다.
print("%s scored %d points" % (name, score))
print("average: %.2f" % average)
print()


print("-- format function --")

# format()은 문자열 안의 {} 자리에 값을 채웁니다.
print("{} scored {} points".format(name, score))

# 번호를 쓰면 값을 넣을 위치를 직접 정할 수 있습니다.
print("{1} points were scored by {0}".format(name, score))

# 이름을 쓰면 출력 문장의 의미가 더 분명해집니다.
print("{student}: {points}".format(student=name, points=score))
