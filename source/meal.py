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
This module contains contains information about various meals that an agent \
 would eat in.

This module contains code for class :class:`meal.Meal`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# general math capability
import numpy as np

# agent-based modules
import my_globals as mg
import temporal

# ===============================================
# constants
# ===============================================

# meals
# they must be in incremental order
BREAKFAST   = 0
LUNCH       = 1
DINNER      = 2

# values are in minutes
BREAKFAST_DT_MEAN       = 15
BREAKFAST_DT_STD        = 5

BREAKFAST_START_MEAN    = 6 * temporal.HOUR_2_MIN + 30
BREAKFAST_START_STD     = 10

# number of standard deviation
BREAKFAST_START_TRUNC   = 1
BREAKFAST_DT_TRUNC      = 1

# values are in minutes
LUNCH_DT_MEAN           = 30
LUNCH_DT_STD            = 10

LUNCH_START_MEAN        = 12 * temporal.HOUR_2_MIN
LUNCH_START_STD         = 30

# number of standard deviation
LUNCH_START_TRUNC       = 1
LUNCH_DT_TRUNC          = 1

# values are in minutes
DINNER_DT_MEAN          = 45
DINNER_DT_STD           = 15

DINNER_START_MEAN       = 19 * temporal.HOUR_2_MIN
DINNER_START_STD        = 60

# number of standard deviation
DINNER_START_TRUNC      = 1
DINNER_DT_TRUNC         = 1

# the minimum amount of time to eat a meal
DT_MIN = 5

# this takes an INTEGER representation for a meal and represents it as 
# a STRING
INT_2_STR = {
    BREAKFAST: 'Breakfast',
    LUNCH: 'Lunch',
    DINNER: 'Dinner',
}

# this takes a STRING representation for a meal and represents it as 
# an INTEGER
STR_2_INT = { v: k for k, v in INT_2_STR.items() }

# ===============================================
# class Meal
# ===============================================

class Meal(object):

    """
    This is class contains information about meals (breakfast, dinner, and lunch)

    :ivar int id: the meal type (breakfast, lunch, or dinner)
    :ivar int dt: the duration of a meal [minutes]
    :ivar int dt_mean: the mean duration of a meal [minutes]
    :ivar int dt_std: the standard deviation of meal duration [minutes]
    :ivar int dt_trunc: the number of standard deviation in the duration distribution
    :ivar int t_start: the start time of a meal [minutes, time of day]
    :ivar int t_start_univ: the start time of a meals [minutes, universal time]
    :ivar int start_mean: the mean start time of a meal [minutes, time of day]
    :ivar int start_std: the standard deviation of start time of a meal [minutes]
    :ivar int start_trunc: the number of standard deviation of in the start time distribution
    
    :ivar f_start: the start time distribution function
    :ivar f_dt: the duration distribution function 
    :ivar int day: the day the meal should occur 
    """

    #
    # constructor
    #
    def __init__(self, id=BREAKFAST, start_mean=BREAKFAST_START_MEAN, start_std=BREAKFAST_START_STD, \
                 start_trunc=BREAKFAST_START_TRUNC, dt_mean=BREAKFAST_DT_MEAN, dt_std=BREAKFAST_DT_STD, \
                 dt_trunc=BREAKFAST_DT_TRUNC):

        self.id = id

        self.start_mean     = start_mean
        self.start_std      = start_std
        self.start_trunc    = start_trunc

        self.dt_mean    = dt_mean
        self.dt_std     = dt_std
        self.dt_trunc   = dt_trunc

        self.t_start    = self.start_mean
        self.dt         = self.dt_mean

        self.f_start    = mg.set_distribution(-self.start_trunc, self.start_trunc, self.start_mean, self.start_std)
        self.f_dt       = mg.set_distribution(-self.dt_trunc, self.dt_trunc, self.dt_mean, self.dt_std)

        self.t_start_univ   = 0
        self.day            = 0

        return

    def initialize(self, t_univ):

        """
        At the beginning of the simulation, make sure that the meals are initialized to the proper times \
        (:mod:`t_start_univ`) so that they relate to the simulation time (t_univ)
        
        :param int t_univ: the simulation time [minutes, universal time]
        :return: None
        """

        # the amount of minutes in 1 day
        DAY_2_MIN = temporal.DAY_2_MIN

        # the current day
        day     = np.floor(t_univ / DAY_2_MIN).astype(int)

        # the day counter
        i       = 0

        # maximum number of iterations
        N_MAX   = 500

        # update the day the meal is supposed to happen so that it starts after the current time (t_start
        while (self.t_start_univ < t_univ) and (i < N_MAX):
            self.update(day + i)
            i = i + 1

        return

    def print_id(self):

        """
        This function returns a string representation of the meal id

        :return: a string representation of the meal id
        :rtype: str
        """

        # the error message, if the id is invalid
        msg = 'ERROR! %d is an Invalid choice of STATE.status!\n' % self.id

        # If the id is valid, represent the id as a string. If not, write the error message
        return INT_2_STR.get(self.id, msg)

    def set_meal(self, id, start_mean, start_std, start_trunc, dt_mean, dt_std, dt_trunc):

        """
        This function sets the values associated with the Meal object.

        :param int id: the meal type (breakfast, lunch, or dinner)
        :param int start_mean: the mean start time of the meal [minutes, time of day] 
        :param int start_std: the standard deviation of start time [minutes]
        :param int start_turnc: the number of standard deviations in the start time distribution        
        :param int dt_mean: the mean duration of a meal [minutes]
        :param int dt_std: the standard deviation of meal duration [minutes]
        :param int dt_trunc: the number of standard deviations in the duration distribution
                
        :return: None
        """

        self.id = id

        self.start_mean     = start_mean
        self.start_std      = start_std
        self.start_trunc    = start_trunc

        self.dt_mean        = dt_mean
        self.dt_std         = dt_std
        self.dt_trunc       = dt_trunc

        self.t_start    = self.start_mean
        self.dt         = self.dt_mean

        self.f_start            = mg.set_distribution(-self.start_trunc, self.start_trunc, self.start_mean, \
                                                      self.start_std)
        self.f_dt, self.dt_std  = mg.set_distribution_dt(-self.dt_trunc, self.dt_trunc, self.dt_mean, self.dt_std, \
                                                         x_min=DT_MIN)

        return

    #
    # this returns a string representation of the Meal object
    #
    def toString(self):

        """
        This function returns a string representation of the Meal object.

        :return msg: a string representation of the Meal object
        :rtype: str
        """

        msg = ''

        # the id
        msg = msg + 'Name:\t' + self.print_id() + '\n'

        # the start time as military time
        msg = msg + 'Start Time:\t' + temporal.print_military_time(self.t_start) + '\n'

        # the mean meal duration
        msg = msg + 'Expected Duration:\t%d[min]\n' % self.dt_mean

        # the actual duration of the meal
        msg = msg + 'Duration:\t%d[min]\n' % self.dt
        
        return msg

    def update(self, day):

        """
        Given the day for the meal, update the meal. The following does the following:
        
        #. Update the start time for the meal
        #. Update the duration for the meal
        #. Update the universal start time for the meal
        
        :param int day: the day for the meal to occur
         
        :return: None 
        """

        self.update_start()
        self.update_dt()

        self.update_start_univ(day)
        return

    def update_day(self):

        """
        Update the day for the next meal, given the universal start time for the meal (:mod:`t_start_univ`).
        
        :return: None 
        """

        DAY_2_MIN   = temporal.DAY_2_MIN
        self.day    = np.floor( self.t_start_univ / DAY_2_MIN).astype(int)

        return

    def update_dt(self):

        """
        Sample the duration distribution to get a duration.
        
        :return: None 
        """

        dt      =  self.f_dt(1)[0]
        self.dt = np.round(dt).astype(int)

        return

    def update_start(self):

        """
        Sample the start time distribution to get a start time.
        
        :return: None 
        """

        DAY_2_MIN   = temporal.DAY_2_MIN

        t            = self.f_start(1)[0]
        self.t_start = np.round(t).astype(int) % DAY_2_MIN

        return

    def update_start_univ(self, day):

        """
        Given the day for the next meal, update the universal start time for the meal.
        
        :param int day: the day for the meal  
        :return: None
        """

        DAY_2_MIN           = temporal.DAY_2_MIN

        self.t_start_univ   = day * DAY_2_MIN + self.t_start
        self.day            = day

        return


