paths = [[0, 0], [20, 40], [22, 33]]

for i in range(10):
    print(paths[0])
    paths.pop(0)
    paths.append([i, 12])
