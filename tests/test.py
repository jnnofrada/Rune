import io
print("start")
path = "..\\sample\\settings.jsonlines"

f = open(path, 'r', )

if f:
    x = f.readline()

else:
    print("not open")

print(x)
