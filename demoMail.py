color = [0,255,0]

for i in range(1, 101):
    print(color)
    if i < 50:
        color[0] += 255/50
    else:
        color[1] -= 255/50
