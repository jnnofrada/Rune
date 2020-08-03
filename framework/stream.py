"""
Standard representation of data streams.

"""


class Stream:
    """
    A stream in the dataset.

    A stream is effecively a big blob of bytes. Those bytes may represents
    characters, but may also be garbage if there were any hardware problems
    encountered. No validation has been performed on the contents before this
    point.

    """


    @property
    def name(self):
        """
        The name of this stream as a string.

        Returns either `brushing` or `settings`.

        """
        raise NotImplementedError()


    def open_bytes(self):
        """
        Return an object implementing the standard `io.BytesIO` interface, and
        represents the byte contents of the stream. You may use the returned
        object with any function that accepts a `ByteIO`.

        If your code needs `io.StringIO`, use `open_string()` instead. Exactly
        one of these two method may be called on a Stream object, and only
        once during the lifetime of the Stream object.

        Raises an `IOError` if the stream cannot be opened.

        The return stream may also raise `IOError` on any method call, as it's
        streaming the actual data from the network.

        """
        raise NotImplementedError()


    def open_text(self):
        """
        Return an object implementing the standard `io.TextIOBase` interface,
        and represents the text contents of the stream. You may use the
        returned object with any function that accepts a `TextIOBase` or
        `StringIO`.

        The returned text stream supports all TextIOBase methods EXCEPT
        `seek()`, `tell()`, and `write()`.

        If your code needs `io.BytesIO`, use `open_bytes()` instead. Exactly
        one of these two method may be called on a Stream object, and only
        once during the lifetime of the Stream object.

        Raises an `IOError` if the stream cannot be opened.

        The return stream may also raise `IOError` on any method call, as it's
        streaming the actual data from the network.

        """
        raise NotImplementedError()
