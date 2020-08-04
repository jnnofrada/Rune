import io
import logging

log = logging.getLogger()
logging.basicConfig(filename='tests.log', level=logging.DEBUG)
print("start")

f = open('settings.jsonlines', 'r')
g = open('brushing.csv', 'r')
settings = {}
brush = {'pct': 0, 'cur_tick': 0, 'tooth': 0}
start = 0
end = 0
z = 1
time_lost = 0
passed = 0
prev_stamp = 0
if f:
    x = f.readline()
    while x:
        stamp = 0
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

        # create db entry for the completed stream 2 line

        # stream 1 iterate
        log.debug("Stream 1 iterate")

        # creates starting conditions for stream 1
        if settings["tick"] == 0.0:
            start, prev_stamp, prev_interval = settings["timestamp"], settings["timestamp"], settings['tick_interval']
            log.info(start)
            log.info(prev_stamp)
            log.info(prev_interval)
            
        stream_2_tick = str(settings["tick"])
        log.info(stream_2_tick)
        
        while z:
            if passed == 2:
                log.debug("seen once")
                log.debug(z)
                brush_array = z.split(',')
                log.debug(brush_array)
                brush["cur_tick"] = brush_array[0]
                brush["tooth"] = brush_array[1]
                brush["pct"] = brush_array[2]
            if int(brush["cur_tick"]) < int(settings["tick"]) and passed == 2:
                log.debug("current stream 2 tick is larger than current stream 1 tick")
                # gets timestamp for current tick
                log.debug("gets timestamp for current tick")
                stamp = prev_stamp + (float(brush["cur_tick"]) * prev_interval)
                log.debug(stamp)
                # time between stream 2 timestamp and current timestamp minus the prev tick's timestamp
                # to get the difference in seconds between the two ticks
                log.debug("time lost is the sum of difference between two tick's timstamps")
                time_lost += stamp - prev_stamp
                log.debug(time_lost)
                log.info("keeping track of current tick's timestamp for use in next iteration")
                prev_stamp = stamp
                log.debug(prev_stamp)
                log.debug(brush)
                # create db entry for the completed stream 1 line
                z = g.readline()
            elif int(brush["cur_tick"]) >= int(settings["tick"]) and passed == 2:
                log.info("current tick is larger than stream 2 tick. Didn't call readline so the brush array will not "
                         "be updated until after the next iteration")
                break
            if passed != 2:
                log.debug("First pass complete z now equals first real line of stream 1")
                passed += 1
                z = g.readline()
        prev_interval = settings["tick_interval"]
        x = f.readline()

else:
    log.error("not open")
    
end = settings["timestamp"]
log.info("start stamp")
log.debug(start)
log.info("end stamp")
log.debug(end)
f.close()

"""
returns t_start as measured where the tick in the update is zero
returns t_end as measured in the last entry in stream 2 being the final update for the entire job
returns time_lost as measured as the sum of differences between the timestamps of each tick
will need to translate each file open to stream open_text but it also acts as file.readline()
pass dataset_id and toothbrush_id into here to create db entries

"""