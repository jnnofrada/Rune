"""
Job queue.

"""


class JobQueue:
    """
    Client for the distributed job queue.

    """


    @classmethod
    def poll(cls):
        """
        Makes a network request to the distributed queue service, and returns
        the next job in the queue. If no jobs are available, blocks for up to
        20 seconds waiting for one, then times out.

        Return an instance of `Job` if a job is available.

        Return `None` if no job is available for 20 seconds.

        Raise an `IOError` if there are network or other API issues. Consider
        such errors temporary network outages, and keep retrying.

        """
        raise NotImplementedError()
