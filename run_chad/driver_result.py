# The United States Environmental Protection Agency through its Office of
# Research and Development has developed this software. The code is made
# publicly available to better communicate the research. All input data
# used fora given application should be reviewed by the researcher so
# that the model results are based on appropriate data for any given
# application. This model is under continued development. The model and
# data included herein do not represent and should not be construed to
# represent any Agency determination or policy.
#
# This file was written by Dr. Namdi Brandon
# ORCID: 0000-0001-7050-1538
# March 22, 2018


"""
This module holds the results from running the Monte-Carlo simulations.

This module contains class :class:`driver_result.Driver_Result` and :class:`driver_result.Batch_Result`.
"""

# ===========================================
# import
# ===========================================
import sys
sys.path.append('..\\source')

# mathematical capabilities
import numpy as np

# dataframe capabilities
import pandas as pd

# ===========================================
# class Driver_Result
# ===========================================
class Driver_Result(object):

    """
    This class holds the result of running driver.run().

    :param list diaries: the activity diaries for each household in the simulation
    :type diaries: list of :class:`diary.Diary`
    :param list chad_param_list: the CHAD parameters used for sampling the CHAD data
    :type chad_param_list: list of :class:`chad_params.CHAD_params`
    :param int demographic: the demography identifier

    :var diaries: the activity diaries for each household in the simulation
    :type diaries: list of :class:`diary.Diary`

    :var chad_param_list: the CHAD parameters used for sampling the CHAD data
    :type chad_param_list: list of :class:`chad_params.CHAD_params`

    :var int demographic: the demography identifier
    :var int num_hhld: the number of households
    :var int num_people: the number of people in the simulation
    """

    def __init__(self, diaries, chad_param_list, demographic):

        # the diaries for each household in the simulation
        # each item in the list is a list of diaries for the household
        self.diaries = diaries

        # the parameters of the simulation
        self.chad_param_list = chad_param_list

        # the number of households per simulation
        self.num_hhld = len(self.diaries)

        # the demographic
        self.demographic = demographic

        # the number of people in the simulation
        self.num_people = len( [item.df for x in self.diaries for item in x] )

        return

    def add_id(self, df_list):

        """
        This function adds an integer identifier to each simulated agent's activity diary.

        :param df_list: the activity diaries for the simulated agents
        :type df_list: list of pandas.core.frame.DataFrame

        :return: the updated activity diaries for each agent
        :rtype: list of pandas.core.frame.DataFrame
        """

        # add an identifier for each simulated agent's diary
        for i, df in enumerate(df_list):
            df['id'] = i

        return df_list

    def get_all_data(self):

        """
        This function returns the diaries as a pandas data frame.

        :return: activity diaries for each person in the simulation
        :rtype list of pandas.core.frame.DataFrame
        """

        # 'flatten' out the list so that all the diaries are in 1 list
        result = [item.df for x in self.diaries for item in x]

        return result

    def get_combined_diary(self):

        """
        This function combines all of the activity diaries from the simulation into one.

        :return: all of the activity diaries from the simulated agents combine into one* dataframe
        :rtype: pandas.core.frame.DataFrame
        """

        # list of each data frame
        df_list = self.get_all_data()

        # add unique identifiers for each diary
        df_list = self.add_id(df_list)

        # get the name of the columns to include the id as the first column instead of the last
        colnames = df_list[0].columns.values.tolist()
        colnames = [colnames[-1]] + colnames[:-1]

        # set the reorder the columns for each dataframe
        df_list = [df[colnames] for df in df_list]

        # combine the data into one dataframe
        df      = pd.concat(df_list)

        return df

# ===========================================
# class Batch_Result
# ===========================================

class Batch_Result(Driver_Result):

    """
    This class holds the results from batch runs from the driver in one object.

    :param dr_list: the results from the simulation from each batch that was used.
    :type dr_list: list of :class:`driver_result.Driver_Result`
    """

    def __init__(self, dr_list):

        # the demographic
        self.demographic        = dr_list[0].demographic

        # the diaries
        self.diaries            = [item for dr in dr_list for item in dr.diaries]

        # CHAD parameter list
        self.chad_param_list    = [item for dr in dr_list for item in dr.chad_param_list]

        # number of people
        self.num_people         = np.array( [dr.num_people for dr in dr_list] ).sum()

        # number of households
        self.num_hhld           = np.array( [dr.num_hhld for dr in dr_list] ).sum()

        return