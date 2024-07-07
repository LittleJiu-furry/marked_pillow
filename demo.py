with open("a.txt", mode= "a+", encoding="utf-8") as f:
    f.seek(0)
    lines = f.readlines()
    f.truncate(0)
    for line in lines:
        if line == "\n":
            continue
        if(':' not in line):
            continue
        f.write(line)
