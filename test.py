a = 1

c = []
for a in range(1, 80):
    x = 5777 - 2 * a ** 2
    if x < 0:
        break
    c.append(x)

print(c)

print(len(c))


def is_prime(n):
    if n == 1:
        return False
    for _ in range(2, int(n ** 0.5) + 1):
        if n % _ == 0:
            return False
    return True


for i in c:
    print(is_prime(i), i)
