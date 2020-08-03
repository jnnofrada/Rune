"""
Main job processing handler.

YOUR SOLUTION GOES HERE.

YOU MAY EXTEND THIS MODULE HOWEVER YOU LIKE, AS LONG AS YOU KEEP
process_next_job().

"""
import logging


log = logging.getLogger()
"""
You may log to your heart's content. We encourage it, and you're being scored
on it.

If you prefer other logger implementations, feel free to import them. Ideally
still something that writes to STDOUT or a file.

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
    raise NotImplementedError()
