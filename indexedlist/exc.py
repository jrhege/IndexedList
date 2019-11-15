""" Custom exceptions """


class SkipItem(Exception):
    """ Raised by functions to indicate an item should not be added to a Lookup """

    pass
