from cs50 import get_float


def factor(n):
    l1 = n // 25
    r1 = n % 25
    l2 = r1 // 10
    r2 = r1 % 10
    l3 = r2 // 5
    r3 = r2 % 5
    l4 = r3 // 1
    r4 = r3 % 1
    total = l1 + l2 + l3 + l4
    p = int(total)
    print(f"{p}")


while True:
    cents = get_float("Change: ")
    if cents > 0:
        break
cents = round(cents * 100)
factor(cents)

# while cents >= 25:
#     cents = cents - 25
#     count += 1
# while cents >= 10:
#     cents = cents - 10
#     count += 1
# while cents >= 5:
#     cents = cents - 5
#     count += 1

# while cents >= 1:
#     cents = cents - 1
#     count += 1
