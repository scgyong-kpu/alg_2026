# Python 05. Class
#
# class는 관련 있는 데이터와 동작을 하나의 이름 아래 묶는 방법입니다.
# 시각화 도구, 게임 객체, 그래프의 정점처럼 "상태를 가진 대상"을 표현할 때 유용합니다.


class Student:
    pass


print("-- create objects --")

kim = Student()
lee = Student()

print(kim)
print(lee)
print("same object?", kim is lee)
print()


print("-- add attributes at runtime --")

# Python에서는 객체를 만든 뒤에도 속성을 붙일 수 있습니다.
kim.name = "Kim"
kim.score = 91

lee.name = "Lee"
lee.score = 84

print(kim.name, kim.score)
print(lee.name, lee.score)

# 하지만 이런 방식은 모든 객체가 같은 속성을 갖는다는 보장이 약합니다.
# 그래서 다음 단계에서는 생성자로 초기 상태를 보장합니다.
print()


print("-- constructor --")


class CourseStudent:
    def __init__(self, name, score):
        # __init__은 객체가 만들어질 때 자동으로 호출됩니다.
        # self.name과 self.score는 이 객체가 계속 가지고 있을 속성입니다.
        self.name = name
        self.score = score

    def is_passed(self):
        return self.score >= 70

    def print_report(self):
        print(self.name, self.score, "passed:", self.is_passed())


park = CourseStudent("Park", 77)
choi = CourseStudent("Choi", 95)

print(park.name, park.score)
print(choi.name, choi.score)
print()


print("-- instance methods --")

park.print_report()
choi.print_report()
print()


print("-- duck typing --")


class ConsolePrinter:
    def print_report(self):
        print("ConsolePrinter prints to terminal")


class FilePrinter:
    def print_report(self):
        print("FilePrinter writes to file")


# 두 객체는 상속 관계가 아니지만 print_report()라는 같은 동작을 제공합니다.
# 호출하는 쪽에서는 필요한 동작이 있는지만 보고 같은 방식으로 사용할 수 있습니다.
printers = [ConsolePrinter(), FilePrinter()]
for printer in printers:
    printer.print_report()
print()


print("-- inheritance --")


class ReportPrinter:
    def __init__(self, title):
        self.title = title

    def print_title(self):
        print("[", self.title, "]")


class ScorePrinter(ReportPrinter):
    def print_score(self, student):
        self.print_title()
        student.print_report()


score_printer = ScorePrinter("Score Report")
score_printer.print_score(choi)
