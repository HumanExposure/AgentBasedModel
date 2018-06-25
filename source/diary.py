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
# August 14, 2017

"""
This module contains code that governs the activity-diaries. Each activity diary contains
dataframes that store the activity-diaries for each person. The activity-diaries are the
output of the Agent-Based Model of Human Activity Patterns (ABMHAP) simulation.

This module contains class :class:`diary.Diary`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# general math capability
import numpy as np

# dataframe capability
import pandas as pd

from itertools import groupby
from operator import itemgetter

# agent-based model modules
import activity, location, temporal

# ===============================================
# constants
# ===============================================

# the order of the columns in the activity-diary database
COLNAMES = ['day', 'start', 'end', 'dt', 'act', 'loc']


# ===============================================
# class
# ===============================================

class Diary(object):

    """
    This class represents the activity-diaries for a person.
    
    :param numpy.ndarray t: the start times for each activity [universal time, minutes]
    :param numpy.ndarray act: the activity code done at each time step [integer] (flattened array)
    :param numpy.ndarray local: the history of location codes done by a person
     
    
    :ivar list colnames: the column names for the activity diary in order
    :ivar pandas.core.frame.DataFrame df: the activity-diary
    """

    def __init__(self, t, act, local):

        # the column names explaining the diary information
        self.colnames = COLNAMES

        # the activity-diary data frame
        self.df = pd.DataFrame( self.create_activity_diary(t, act, local), columns=self.colnames )

        return

    def create_activity_diary(self, t, act, local):

        """
        This function creates the activity diary for a given agent in the simulation.

        The activity diary contains:

        #. the start-time and end-time for each activity
        #. the activity code


        :param numpy.ndarray t: the simulation times [universal time, minutes]
        :param numpy.ndarray act: the activity code done at each time step [integer] (flattened array)

        :return: a tuple containing the following: the array indices for each activity grouping, the activity diaries \
        in a numerical format, the activity diary in a string format, and the column names for each data type

        Each diary is a tuple that contains the following:
        
        #. the day number of the start of the activity
        #. the (start-time, end-time) for the activity event
        #. the activity code for the activity event
        #. the location of the event
        """

        # constants
        DAY_2_MIN   = temporal.DAY_2_MIN
        HOUR_2_MIN  = temporal.HOUR_2_MIN

        # get an array of day number corresponding to each time
        day = t // DAY_2_MIN

        # the steps in the simulation
        steps = list(range(len(act)))

        # time_step-activity_code pairings
        groups = self.group_activity(steps, act)

        # the time steps in groups
        idx = self.group_activity_indices(groups)

        #
        # store the start-time and end-time for each activity event
        #

        # the start and end time of each activity in universal time
        ranges = [(t[i].min(), t[i].max()) for i in idx]

        # the start and end time of each activity in time of day
        ranges = [(np.array(r) % DAY_2_MIN).tolist() for r in ranges]

        # calculate the duration (add + 1 because
        dt = [(i[1] - i[0] + 1) % DAY_2_MIN for i in ranges]

        # convert the time of day and duration to hours
        ranges  = np.array(ranges) / HOUR_2_MIN
        dt      = np.array(dt) / HOUR_2_MIN

        # start and end time for each activity in military time
        start_time, end_time = ranges[:, 0], ranges[:, 1]

        #
        # get the activity codes for each activity event
        #

        # the activity code for each activity
        # ech group entry g: list [ (index, activity code) ]
        act_code = [g[0][1] for g in groups]

        #
        # get the location information
        #
        # first index for each event
        x = [i[0] for i in idx]

        # the day the first activity starts
        act_day = np.array([day[i] for i in x]).flatten()

        # numeric local location code
        loc_code = local[x].flatten().tolist()

        #
        # create the diary
        #

        # numerical diary
        y = list(zip(act_day, start_time, end_time, dt, act_code, loc_code))

        return y

    def get_day_end(self, day_start, start, dt):

        """
        This function gets the day that an activity ends.
        
        :param day_start: the day an activity starts
        :type day_start: numpy.ndarray
        
        :param start: the time an activity starts [hours]
        :type start: numpy.ndarray
        
        :param dt: the duration for an activity [hours]
        :type dt: numpy.ndarray
        
        :return: the day an activity ends
        :rtype: numpy.ndarray
        
        """
        # the time is in hours
        # this function assumes that the event is under 24 hours long
        # time until midnight
        dt_midnight = 24 - start

        # if the duration of the activity lasted longer than the amount of time until midnight,
        # increase the end date from the start date
        day_end = day_start + (dt >= dt_midnight)

        return day_end


    def get_weekday_data(self, df=None):

        """
        This function pulls out data that only corresponds to the weekday data.
        
        :param pandas.core.frame.DataFrame df: the activity-diary of interest. If df is None, then use the dataframe \
        associated with the diary object
         
        :return: the activity-diary of data that occur on weekdays 
        """

        # if there is no input dataframe, use this object's dataframe
        if df is None:
            df = self.df

        # get the indices associated to the weekday events
        idx = self.get_weekday_idx(df)

        # the activity-diary associated with weekday events
        result = df[idx]

        return result

    def get_weekday_idx(self, df=None):

        """
        Get the indices of the data that occurs on weekdays. An activity is considered to be on the weekday if \
        the activity **ends** on Monday - Friday. 

        :param pandas.core.frame.DataFrame df: the activity-diary of interest. If df is None, then use the dataframe \
        associated with the diary object

        :return: boolean indices of which activities end during the weekend
        :rtype: numpy.ndarray
        """

        # if no dataframe is passed, do the results on all the data
        if df is None:
            df = self.df

        # the boolean indices of whether or not an activity DOES NOT end on a weekend
        #(i.e. the indices are True if the event is a weekeday and false otherwise)
        idx = self.get_weekend_idx(df) == False

        return idx

    def get_weekend_data(self, df=None):

        """
        This function pulls out data that only corresponds to the weekend data.
                
        :param pandas.core.frame.DataFrame df: the activity-diary of interest. If df is None, the use  the dataframe \
        associated with the current diary object
        
        :return: an activity-diary of data that occurs on weekends        
        """

        # if there is no input dataframe, use this object's dataframe
        if df is None:
            df = self.df

        # get the indices associated to the weekend events
        idx = self.get_weekend_idx(df)

        # the activity-diary associated with weekend events
        result = df[idx]

        return result

    def get_weekend_idx(self, df=None):

        """
        Get the indices of the data that occurs on weekend. An activity is considered to be on the weekend if \
        the activity **ends** on Saturday or Sunday. 
        
        :param pandas.core.frame.DataFrame df: the activity-diary of interest. If df is None, then use the dataframe \
        associated with the diary object
        
        :return: boolean indices of which activities end during the weekend
        :rtype: numpy.ndarray
        """

        # if no dataframe is passed, do the results on all the data
        if df is None:
            df = self.df

        # this indexes events that start and end on the same day
        idx = df.apply( lambda row: self.same_day( row['start'], row['dt']), axis=1)

        # these are the days that an event ends
        day_end = df.day + (idx == False)

        # the boolean indices of whether an activity ended on a weekend
        idx_weekend = day_end.apply(self.is_weekend)

        return idx_weekend

    def group_activity(self, t, y):

        """
        This function groups activities in chronological order.
        
        :param numpy.ndarray t: the start time for activities
        :param numpy.ndarray y: the activity code that corresponds with the respective time  
        
        :return: a list of each unique group-lists. Each group-list contains a tuple \
        for (time step, activity code)

        """

        # make a time_step-activity_code pairing
        z = zip(t, y)

        # a list for each group
        groups = []

        # group entries by consecutive time AND activity code
        for k, g in groupby(enumerate(z), self.group_activity_key):

            # the group will contain tuples of (time step, activity code)
            group = list(map(itemgetter(1), g))
            groups.append(group)

        return groups

    def group_activity_indices(self, groups):

        """
        This function returns the indices for each continuous activity in chronological order.
        
        .. note::
            The output is the time step number **not** the value of time
            
        :param list groups: a list of tuples of (time step, activity code)  
        :return:
        """

        idx = []

        # loop through each entry and return the time step
        for g in groups:
            idx.append([x[0] for x in g])

        return idx

    def group_activity_key(self, x):

        """
        This is the key function used in groupby in order to group consecutive time-step-activity pairs. This is \
        necessary for creating an activity diary.

        :param tuple x: the data in the form of ( index, (time step, activity code) )
        :return: the key for sorting ( , activity code)
        :rtype: tuple
        """

        # the index from enumerating each time step
        idx = x[0]

        # the time step number and activity code
        t, act = x[1]

        # the key used in groupby
        # the first entry is for grouping by consecutive times
        # the second entry is for grouping by activity code
        k = (idx - t, act)

        return k

    def is_weekend(self, day):

        """
        This function returns true if a day is in the weekend and false if it's in a weekday.
        
        :param numpy.ndarray day: the day of the weekd 
        :return:  boolean index of whether or not a day is in the weekend (True) or not (False)
        :rtype: numpy.ndarray
        """

        # the weekend days
        weekend = (temporal.SATURDAY, temporal.SUNDAY)

        # the day of the week
        day_of_week = day % 7

        # check to see if it is the weekend
        result = day_of_week in weekend

        return result

    def same_day(self, start, dt):

        """
        This function returns true if the activity starts and ends on the same day.
        
        :param numpy.ndarray start: the time an activity starts [hours]
        :param numpy.ndarray dt: the duration of an activity, :math:`\\Delta{t}` [hours]
        
        :return: a boolean index of whether or not an activity started and ended on the same day
        :rtype: numpy.ndarray        
        """

        # the time is in hours

        # time until midnight
        dt_midnight = 24 - start

        # if the duration of the activity lasted longer than the amount of time until midnight,
        # increase the end date from the start date
        return (dt < dt_midnight)

    def toString(self):
        """
        This function expresses the Diary object as a string

        :return: an expression of the diary as a string
        :rtype: string
        """

        # the dataframe
        df  = self.df

        # the day
        act_day = df.day.values

        # the string version of each activity
        act_str = [ activity.INT_2_STR[a] for a in df['act'].values ]

        # string version of local location code
        loc_str = [ location.INT_2_STR_LOCAL[i] for i in df['loc'].values ]

        # write the start time, end time, and duration of each activity in military time
        f = temporal.print_military_time
        g = temporal.convert_decimal_to_min

        # the corresponding times in minutes
        start_time  = [ g(x) for x in df.start.values ]
        end_time    = [ g(x) for x in df.end.values ]
        dt_time     = [ g(x) for x in df.dt.values ]

        # the times in military time
        m_start = [f(x) for x in start_time]
        m_end   = [f(x) for x in end_time]
        m_dt    = [f(x) for x in dt_time]

        #
        # store the diary information as a string
        #

        # the string to return
        msg = ''

        for day, start, end, dt, act, local  in zip(act_day, m_start, m_end, m_dt, act_str, loc_str):

            # write information to a string
            msg = msg + '%s\t%s\t%s\t%s\t%20s\t%s\n' % (day, start, end, dt, act, local)

        return msg
