"""
Client for LlamaDB.

"""


class LlamaDB:
    """
    The Llama database client.

    LlamaDB is a NoSQL-like database with a focus on timeseries.
    It stores data in "measurements", which are roughly analogous to tables in
    relational databases.

    LlamaDB measurements have one required column: time. It uses floating
    point UNIX timestamps (such as returned by `time.time()`) to index all
    data points.

    Apart from time, each event stored may have *tags* and/or *fields*.

    A tag is a column which is indexed, and therefore searchable. In other
    words, you can put it in a WHERE or GROUP BY clause, if this were SQL.
    Tags may only contains strings. Among all the data points stored in a
    measurement, there should be a reasonable number of tag keys and values,
    as too many will grind performance to a halt.

    Fields are columns containing everything else. Mostly, this should be
    numeric data, but could in theory be boolean or string also. You cannot
    store arrays, dictionaries, or any kind of structures. Fields are
    not indexed, so you can't search by them later. You can only access them
    once you retrieve the event, they can't be used in a WHERE clause.

    """


    def close(self):
        """
        Close the connection.

        Ensure this is called at some point after every `connect()`, or there
        will be problems.

        """
        raise NotImplementedError()


    @classmethod
    def connect(cls):
        """
        Return a connected client. The client is an instamce of `LlamaDB`.

        Raises an `IOError` if the connection fails. You should also retry.

        """
        raise NotImplementedError()


    def insert(self, measurement, timestamp, tags, fields):
        """
        Insert a single event into the given measurement.

        If the measurement does not exist, it will be automagically created.

        measurement : str
            The name of the measurement (table).

        timestamp : float
            The UNIX timestamp of the event to be stored.

        tags : dict
            Dictionary of tags to index the event by. Each key and value must
            be a non-empty string.

        fields : dict
            Dictionary of fields to stored for this event. Each key must be a
            non-empty string, and the value may be `bool`, `int`, `float`, or
            `str`.

        Raises an `IOError` if there is a network error making the API call.

        Raises a `TypeError` if any of the arguments don't conform the
        expected data types. This is a programmer error.

        """
        raise NotImplementedError()


    def insert_batch(self, measurement, data):
        """
        Insert a batch of points at once. This is more efficient from a
        network and database I/O perspective. However, be careful how much
        data you buffer in local memory.

        measurement : str
            The name of the measurement (table).

        data : iterable
            Any iterable (implements `__iter__()`) such as a list. Each item
            returned must be 3-tuple containing `(timestamp, tags, fields)`,
            with those respective elements corresponding to the arguments of
            `LlamaDB.insert()`.

        """
        raise NotImplementedError()
