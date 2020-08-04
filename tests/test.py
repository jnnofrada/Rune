import io
print("start")

f = open('settings.jsonlines', 'r', )
settings = {}
if f:
    x = f.readline()
    y = 0
    meas = ""
    val = None
    seen = 0
    print(x)
    for idx, i in enumerate(x):
        if i == '"':
            if seen:
                seen = 0
                meas = x[y + 1: idx]
                print(meas)
                y = idx + 3
                print(i, x[y], meas)
                continue
            seen = 1
            y = idx
            print(x[y], i)
        elif i == "," or i == "}":
            val = float(x[y: idx])
            if i == ",":
                y = idx + 2
            print(i, x[y], val)
        if meas != "" and val is not None:
            print(meas, val)
            settings[meas] = val
            meas = ""
            val = None

else:
    print("not open")
    
print(settings)
z = settings["tick"]
print(z)

