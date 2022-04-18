"""
(la)Monty Python
Ali Klemencic
March 2022

Abstract API class.
"""

from abc import ABC, abstractmethod


class API(ABC):
    """
    Abstract class for an API call.
    """

    @abstractmethod
    def get_data(self):
        """
        Method to get a request back from an API connection.

        :return: Pandas dataframe(s) of data from API call
        """
        pass

    @abstractmethod
    def clean_data(self, dataframes):
        """
        Method to clean and merge the dataframes from an API call.

        :param dataframes: dictionary or list of Pandas dataframes

        :return: a Pandas dataframe of cleaned and merged data
        """
        pass
