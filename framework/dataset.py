"""
Representation of a single dataset from a smart toothbrush.

"""


class Dataset:
    """
    The dataset being ingested.

    """


    @property
    def brushing(self):
        """
        The tooth brushing progress stream. This is an instance of
        `Stream`.

        """
        raise NotImplementedError()


    @property
    def dataset_id(self):
        """
        Randomly assigned unique ID of this dataset.

        """
        raise NotImplementedError()


    @property
    def settings(self):
        """
        The toothbrush settings update stream. This is an instance of
        `Stream`.

        """
        raise NotImplementedError()


    @property
    def toothbrush_id(self):
        """
        The anonymous ID of the toothbrush from which the dataset was
        recorded.

        """
        raise NotImplementedError()
