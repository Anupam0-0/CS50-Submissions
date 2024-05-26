from cs50 import get_int

while True:
    h = get_int("Height: ")
    if h > 0 and h < 9:
        break
for i in range(0, h):
    for j in range(0, h - i - 1):
        print(" ", end="")
    for j in range(0, i + 1):
        print("#", end="")
    print()
