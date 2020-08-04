import io
import logging

log = logging.getLogger()
logging.basicConfig(filename= 'tests.log', level=logging.DEBUG)
print("start")

f = open('settings.jsonlines', 'r', )
settings = {}
start = 0
end = 0
if f:
    x = f.readline()
    while x:
        y = 0
        meas = ""
        val = None
        seen = 0
        log.debug(x)
        for idx, i in enumerate(x):
            if i == '"':
                if seen:
                    seen = 0
                    meas = x[y + 1: idx]
                    log.debug(meas)
                    y = idx + 3
                    log.debug(i, x[y], meas)
                    continue
                seen = 1
                y = idx
                log.debug(x[y], i)
            elif i == "," or i == "}":
                val = float(x[y: idx])
                if i == ",":
                    y = idx + 2
                log.debug(i, x[y], val)
            if meas != "" and val is not None:
                log.debug(meas, val)
                settings[meas] = val
                meas = ""
                val = None

        if settings["tick"] == 0.0:
            start = settings["timestamp"]

        log.debug(settings)
        z = settings["tick"]
        log.debug(z)
        
        x = f.readline()

else:
    log.debug("not open")
    
end = settings["timestamp"]
log.debug(start)
log.debug(end)
f.close()
