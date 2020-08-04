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

def create_db_entry(job):
    data_id = job.dataset.dataset_id
    brush_id = job.dataset.toothbrush_id



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
        data_id = job.dataset.dataset_id
        brush_id = job.dataset.toothbrush_id
        
        """
        For each JSON entry in stream 2 compare stream 2 tick to stream 1 tick
        if stream 1 tick is lower than stream 2 tick
        use current stream 2 JSON entry to find timestamp for current stream 1 entry
        using stream 2's timestamp and tick interval

        """


    # close connection to db
    db.close()
    raise NotImplementedError()
