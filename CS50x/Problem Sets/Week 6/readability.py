from cs50 import get_string

str = get_string("Text: ")

letters = 0
words = 1
sen = 0  # sentences

for i in str:
    if i.isalpha():
        letters += 1
    elif i == " ":
        words += 1
    elif i == "." or i == "!" or i == "?":
        sen += 1

# formula/equation
eq = 0.0588 * (letters / words * 100) - 0.296 * (sen / words * 100) - 15.8
eq = round(eq)
if eq < 1:
    print("Before Grade 1")
elif eq >= 16:
    print("Grade 16+")
else:
    print(f"Grade {eq}")

# codebyanupam:)
