"""
Main job processing handler.

YOUR SOLUTION GOES HERE.

YOU MAY EXTEND THIS MODULE HOWEVER YOU LIKE, AS LONG AS YOU KEEP
process_next_job().

"""
import logging
from ..framework import stream, queue, llamadb, job, dataset

log = logging.getLogger()
"""
You may log to your heart's content. We encourage it, and you're being scored
on it.

If you prefer other logger implementations, feel free to import them. Ideally
still something that writes to STDOUT or a file.

"""

logging.basicConfig(filename= 'test.log', level=logging.DEBUG)

def process_next_job():
    """
    Uses JobQueue to get the next job, connects to LlamaDB, and ingests the
    job dataset.

    This functions SHOULD NOT raise any exceptions. It must always return
    (no return value). Use the `Job` object you pull from the queue to report
    the result (success or failure).

    This function is called continuously in a loop by "the framework". Keep
    that in mind when designing your code.

    """
    # open connection to db
    db = llamadb.LlammaDB()
    db.connect()

    """
    since this function is being continuously called only deal with one job per call
    instead of looping through the queue in function
    creates an instance of the queue and gets the job

    """
    queue = queue.JobQueue()
    job = queue.poll()

    # if it's a non empty job continue
    if job:
        """
        data_id and brush_id are going to be used as tags in both stream db entries
        are immutable so keep a handy variable for use later

        """
        id = {}
        id["data_id"] = job.dataset.dataset_id
        id["brush_id"] = job.dataset.toothbrush_id
        
        """
        For each JSON entry in stream 2 compare stream 2 tick to stream 1 tick
        if stream 1 tick is lower than stream 2 tick
        use current stream 2 JSON entry to find timestamp for current stream 1 entry
        using stream 2's timestamp and tick interval

        """
        f = job.dataset.brushing.open_text()
        if not f:
            job.failed("Stream 2 cannot be opened")
        g = job.dataset.settings.open_text()
        if not g:
            job.failed("Stream 1 cannot be opened")
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
            if x is None:
                job.failed("Stream 2 is empty")
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
                if settings is None:
                    job.failed("Stream 2 had trash input")

                # stream 1 iterate
                log.debug("Stream 1 iterate")

                # creates starting conditions for stream 1
                if settings["tick"] == 0.0:
                    start, prev_stamp, prev_interval = settings["timestamp"], settings["timestamp"], settings['tick_interval']
                    log.info(start)
                    log.info(prev_stamp)
                    log.info(prev_interval)

                # remove timestamp from dict so no redundancies in db entry
                strea_2_stamp = settings.pop("timestamp")

                # create db entry for the completed stream 2 line
                db.insert("Stream 2", stream_2_stamp, id, settings)
            
                stream_2_tick = str(settings["tick"])
                log.info(stream_2_tick)
        
                while z:
                    if passed == 2:
                        log.debug("seen once")
                        log.debug(z)
                        try:
                            brush_array = z.split(',')
                        except:
                            job.failed("Separator in stream not found, trash input")
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
                        db.insert("Stream 2", stamp, id, brush)
                        z = g.readline()
                    elif int(brush["cur_tick"]) >= int(settings["tick"]) and passed == 2:
                        log.info("current tick is larger than stream 2 tick. Didn't call readline so the brush array will not "
                                 "be updated until after the next iteration")
                        break
                    if passed != 2:
                        log.debug("First pass complete z now equals first real line of stream 1")
                        passed += 1
                        z = g.readline()
                        if g is None:
                            job.failed("Stream 1 is empty")
                prev_interval = settings["tick_interval"]
                x = f.readline()

        else:
            log.error("not open")
            job.failed("Stream 2 cannot be opened")
    
        end = settings["timestamp"]
        log.info("start stamp")
        log.debug(start)
        job.save_statistic("t_start", start)
        log.info("end stamp")
        log.debug(end)
        job.save_statistic("t_end", end)
        job.save_statistic("time_lost", time_lost)
        # close files
        f.close()
        g.close()
        # close connection to db
        db.close()
        job.commit()

    
    raise NotImplementedError()
