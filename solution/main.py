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

"""
SOME ASSUMPTIONS MADE:
Stream 2 will always have the start and end updates
Tick 0 will always be the starting tick
JSON and CSV will not skip lines when capturing data
Device will make final update before turning off or running out of battery
Floats will only have 3 digits after the decimal point
Ticks and tick intervalswill never be more than 4 digits long before the decimal point
Longest continous string or integer is tick_interval and the UNIX timestamp when working properly
Duplicate data is still valuable data
"""

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

    """
    since this function is being continuously called only deal with one job per call
    instead of looping through the queue in function
    creates an instance of the queue and gets the job

    """
    queue = queue.JobQueue()
    try:
        job = queue.poll()
    except IOError as error:
        log.failure("Failed to get a job", exc=error)
        job.failure("Failed to get a job")

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

        # open each stream as a text to be used in the process
        f = job.dataset.brushing.open_text()
        if not f:
            log.failure("Stream 2 connect be opened")
            job.failed("Stream 2 cannot be opened")
        g = job.dataset.settings.open_text()
        if not g:
            log.failure("Stream 1 cannot be opened")
            job.failed("Stream 1 cannot be opened")

        # create dictionaries statistics to hold the data that will be inserted to to the db or saved for each job
        settings = {}
        brush = {'pct': 0, 'cur_tick': 0, 'tooth': 0}
        start = 0
        end = 0
        time_lost = 0

        # create variables necessary for the process
        z = 1
        passed = 0
        prev_stamp = 0
        if f:
            x = f.readline()

            # Cannot start with an empty line and will always have a start update with tick 0. If it is empty then the rest of the stream is empty
            if x is None:
                log.failure("Stream 2 is empty")
                job.failed("Stream 2 is empty")

            # JSON files have curly braces at the start and end of each entry. If it's true, Stream 2 input is trash input
            if x[0] != '{' and x[len(x) - 1] != '}':
                log.failure("Stream 2 input is trash")
                job.failed("Stream 2 input is trash")

            # iterate through stream 2
            while x:
                stamp = 0
                y = 0
                meas = ""
                val = None
                seen = 0
                log.debug(x)
                for idx, i in enumerate(x):

                    # finds '"' and if it's the first one, marks seen as 1 and if the second one, set meas to the key betweeen the two indices
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

                    # if a ',' is found the value of the previous key is found and val is set to that value
                    elif i == "," or i == "}":
                        val = float(x[y: idx])
                        if i == ",":
                            y = idx + 2
                        log.debug(i, x[y], val)

                    # if both meas and val are not empty, enter it in the settings dictionary
                    if meas != "" and val is not None:
                        log.debug(meas, val)
                        settings[meas] = val
                        meas = ""
                        val = None

                # Line of Stream 2 has been ingested
                # stream 1 iterate
                log.debug("Stream 1 iterate")

                # creates starting conditions for stream 1
                if settings["tick"] == 0.0:
                    start, prev_stamp, prev_interval = settings["timestamp"], settings["timestamp"], settings['tick_interval']
                    log.info(start)
                    log.info(prev_stamp)
                    log.info(prev_interval)

                # remove timestamp from dict so no redundancies in db entry
                stream_2_stamp = settings.pop("timestamp")

                # create db entry for the completed stream 2 line. db connect and close are called here to minimize network time
                try:
                    db.connect()
                except IOError as error:
                    log.failure("Failed to connect to database", exc=error)
                    job.failure("Failed to connect to database")
                db.insert("Stream 2", stream_2_stamp, id, settings)
                db.close()
                stream_2_tick = str(settings["tick"])
                log.info(stream_2_tick)
        
                while z:
                    if passed == 2:
                        log.debug("seen once")
                        log.debug(z)
                        brush_array = z.split(',')

                        # Each line of the csv always contains the tick, tooth number and percent clean. If the line, after splitting does not contain 3 indices, it is trash data
                        if len(brush_array) != 3:
                            log.failure("Stream 1 input is trash")
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
                        
                        
                        # create db entry for the completed stream 1 line db connect and close are called here to minimize network time
                        try:
                            db.connect()
                        except IOError as error:
                            log.failure("Failed to connect to database", exc=error)
                            job.failure("Failed to connect to database")
                        db.insert("Stream 2", stamp, id, brush)
                        db.close()
                        z = g.readline()
                    
                    # stream 1 tick is higher than stream 2 tick
                    elif int(brush["cur_tick"]) >= int(settings["tick"]) and passed == 2:
                        log.info("current tick is larger than stream 2 tick. Didn't call readline so the brush array will not "
                                 "be updated until after the next iteration")
                        break
                    
                    # First pass is to make z hold the first line of the CSV containing the titles fo each column. Second pass is for z to hold the first line with wanted info
                    if passed != 2:
                        log.debug("First pass complete z now equals first real line of stream 1")
                        passed += 1
                        z = g.readline()

                        # CSV do not have empty lines. If an empty line is encountered first, the stream is empty
                        if g is None:
                            log.failure("Stream 1 is empty")
                            job.failed("Stream 1 is empty")
                
                
                prev_interval = settings["tick_interval"]
                x = f.readline()
        
        # just in case Stream 2 closes before or during ingesting
        else:
            log.failure("Stream 2 is not open")
            job.failed("Stream 2 cannot be opened")
    
        # gather statistics to be saved
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
        
        # commit job as success
        job.commit()

    
    raise NotImplementedError()
