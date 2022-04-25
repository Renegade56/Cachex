# for elem in enumerate(["red", "blue"], 1):
#     print(elem)

from collections import Counter

a = [1, 1, 1, 3, 3, 5, 6, 8, 9]

print(Counter(a).items())