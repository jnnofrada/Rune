import io
import logging

log = logging.getLogger()
logging.basicConfig(filename= 'tests.log', level=logging.DEBUG)
print("start")

f = open('settings.jsonlines', 'r')
g = open('brushing.csv', 'r')
settings = {}
start = 0
end = 0
cur_tick = 0
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
        
        # create db entry for the completed stream 2 line

        # stream 1 iterate
        z = g.readline()
        brush_array = z.split(',')
        cur_tick = z[0]
        tooth = z[1]
        pct = z[2]
        if cur_tick < settings["tick"]:
            stamp = settings["timestamp"] + (cur_tick * settings["tick_interval"])
        
        
        
        x = f.readline()

else:
    log.debug("not open")
    
end = settings["timestamp"]
log.debug(start)
log.debug(end)
f.close()
