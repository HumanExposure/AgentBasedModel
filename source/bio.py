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
This module contains information about a Person's (:class:`person.Person`) biology.

This module contains the following class: :class:`bio.Bio`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# general math capability
import numpy as np

# agent-based model modules
import my_globals as mg
import temporal

# ===============================================
# constants
# ===============================================

# gender constants
FEMALE  = 0
MALE    = 1

# the default age
AGE     = 30

# default values for biology

# default sleep duration mean [minutes]
SLEEP_DT_MEAN       = 8 * temporal.HOUR_2_MIN

# default mean sleep start time [minutes]
SLEEP_START_MEAN    = 22 * temporal.HOUR_2_MIN
SLEEP_START_STD     = 0

# default mean sleep end time [minutes]
SLEEP_END_MEAN      = 6 * temporal.HOUR_2_MIN
SLEEP_END_STD       = 0

# the number of standard deviations to truncate the normal distribution
SLEEP_START_TRUNC   = 1
SLEEP_END_TRUNC     = 1

# This dictionary takes the INTEGER representation of a the gender and
# returns a STRING representation
INT_2_STR_GENDER = {
    FEMALE: 'Female',
    MALE: 'Male',
}

# ===============================================
# class Bio
# ===============================================

class Bio(object):

    """
    This class holds the biologically relevant information for a person. This information is:

    * age
    * gender
    * mean / standard deviation of start time for sleeping
    * mean / standard deviation of end time for sleeping
    * probability distribution function sleep start time / end time

    :ivar int age: the age [years]
    :ivar int gender: the gender

    :ivar int sleep_dt: the duration of time for a sleep event [minutes]
    
    :ivar int sleep_start_mean: the mean start time for a sleep event [minutes]
    :ivar int sleep_start_std: the standard deviation for start time for a sleep event [minutes]
    :ivar int sleep_start: the start time for sleep [minutes, time of day]
    :ivar int sleep_start_univ: the start time for sleep[minutes, universal time]
    
    :ivar int sleep_end_mean: the mean end time for a sleep event [minutes]
    :ivar int sleep_end_std: the standard deviation for end time for a sleep event [minutes]
    :ivar int sleep_end: the end time for sleep[minutes, time of day]
    :ivar int sleep_end_univ: the end time for sleep [minutes, universal time]

    :ivar int start_trunc: the number of standard deviations to allow when sampling sleep the \
    truncated distribution for start time
    :ivar int end_trunc: the number of standard deviations to allow when sampling sleep the \
    truncated distribution for end time
    
    :ivar func f_sleep_start: the distribution data for start time for sleep
    :ivar func f_sleep_end: the distribution data for end time for sleep
    
    """
    #
    # constructor
    #
    
    def __init__(self):

        DAY_2_MIN = temporal.DAY_2_MIN

        # the gender
        self.gender = FEMALE

        # the age [years]
        self.age    = AGE

        # biology related to sleeping
        self.sleep_start_mean   = SLEEP_START_MEAN
        self.sleep_start_std    = SLEEP_START_STD
        self.sleep_start        = self.sleep_start_mean
        self.sleep_start_univ   = 0

        self.sleep_end_mean     = SLEEP_END_MEAN
        self.sleep_end_std      = SLEEP_END_STD
        self.sleep_end          = self.sleep_end_mean
        self.sleep_end_univ     = 0

        self.sleep_dt           = (self.sleep_end - self.sleep_start + 1) % DAY_2_MIN

        self.start_trunc        = SLEEP_START_TRUNC
        self.end_trunc          = SLEEP_END_TRUNC

        # these are the probability distributions for sampling start and end times
        self.f_sleep_start  = mg.set_distribution(-self.start_trunc, self.start_trunc, self.sleep_start_mean, \
                                                    self.sleep_start_std)

        self.f_sleep_end    = mg.set_distribution(-self.end_trunc, self.end_trunc, self.sleep_end_mean, \
                                                    self.sleep_end_std)

        return

    def calc_awake_duration(self, t):

        """
        This function calculates the amount of time the person is expected to be awake.

        :param int t: time of day [minutes]
        :return: the duration [minutes] until the agent is expected to awaken
        """

        DAY_2_MIN   = temporal.DAY_2_MIN

        # the duration until the agent is expected to awaken
        dt = (self.sleep_start - t) % DAY_2_MIN

        return dt

    def print_gender(self):

        """
        This function returns a string representation of gender

        :return: the string representation of gender
        :rtype: str
        """

        # write an error message if an invalid choice for gender is given
        msg = 'ERROR! %d is an invalid choice for gender!' % self.gender

        # If a valid choice for gender is given, write the gender
        # If not, write the error message
        return INT_2_STR_GENDER.get(self.gender, msg)

    def set_sleep_params(self, start_mean, start_std, end_mean, end_std):

        """
        This function sets the biological sleep parameters themselves and the sleep parameter distribution functions.

        :param int start_mean: the mean sleep start time [minutes]
        :param int start_std: the standard deviation of start time [minutes]

        :param int end_mean: the mean sleep end time [minutes]
        :param int end_std: the standard deviation of end time [minutes]
        :return: None
        """

        DAY_2_MIN = temporal.DAY_2_MIN

        # set the standard deviation of the sleep duration
        self.sleep_start_mean, self.sleep_start_std     = start_mean, start_std
        self.sleep_end_mean, self.sleep_end_std         = end_mean, end_std

        self.sleep_start    = self.sleep_start_mean
        self.sleep_end      = self.sleep_end_mean
        self.sleep_dt       = (self.sleep_end - self.sleep_start) % DAY_2_MIN

        self.f_sleep_start  = mg.set_distribution(-self.start_trunc, self.start_trunc, self.sleep_start_mean, \
                                                   self.sleep_start_std)

        self.f_sleep_end    = mg.set_distribution(-self.end_trunc, self.end_trunc, self.sleep_end_mean, \
                                                    self.sleep_end_std)

        return

    def toString(self, do_decimal=False):

        """
        This function represents the Bio object as a string.

        :param bool do_decimal: This controls whether or not to represent the values in time in a \
                                decimal (hours) format where [1:30pm is 13.5] if True or as the minutes \
                                in the day if False [1:30pm is 13 * 60 + 30].

        :return msg: the string representation of the Bio object        
        :rtype: string
        """

        msg = ''
        # write the gender
        msg = msg + 'Gender:\t' + self.print_gender() + '\n'

        # write the age
        msg = msg + 'Age:\t%d\n' % self.age

        # write the currently set duration of sleep
        msg = msg + 'currently set sleep duration:\t%d\n' % self.sleep_dt

        if (do_decimal):
            # write the time data in an hours format

            # convert the mean start time to a decimal format
            start_mean  = temporal.convert_cyclical_to_decimal(self.sleep_start_mean)

            # convert the standard deviation of start time to a decimal format
            start_std   = temporal.convert_cyclical_to_decimal(self.sleep_start_std)

            # convert the mean start time to a decimal format
            end_mean    = temporal.convert_cyclical_to_decimal(self.sleep_end_mean)

            # convert the standard deviation of start time to a decimal format
            end_std     = temporal.convert_cyclical_to_decimal(self.sleep_end_std)

        else:
            # store the mean and standard deviation for start time for sleep [minutes]
            start_mean, start_std = self.sleep_start_mean, self.sleep_start_std

            # store the mean and standard deviation for end time for sleep [minutes]
            end_mean, end_std = self.sleep_end_mean, self.sleep_end_std


        # write the mean and standard deviation of the sleep start time
        msg = msg + 'sleep start time\n'
        msg = msg + '(mean, std):\t' + str((start_mean, start_std)) + '\n'

        # write the mean and standard deviation of the sleep end time
        msg = msg + 'sleep end time\n'
        msg = msg + '(mean, std):\t' + str((end_mean, end_std)) + '\n'

        return msg


    def update_sleep_start(self):

        """
        This function samples the sleep start time distribution and sets the start time.
        
        :return: None 
        """

        DAY_2_MIN   = temporal.DAY_2_MIN

        # rvs returns an array, so index it
        t_start = np.round( self.f_sleep_start(1)[0] ).astype(int) % DAY_2_MIN

        # set the start time
        self.sleep_start = t_start

        # update the duration
        self.update_sleep_dt()

        return

    def update_sleep_end(self):

        """
        This function samples the sleep end time distribution and sets the end time.
        
        :return: None 
        """

        DAY_2_MIN   = temporal.DAY_2_MIN

        # rvs returns an array, so index it
        t_end = np.round( self.f_sleep_end(1)[0] ).astype(int) % DAY_2_MIN

        self.sleep_end = t_end

        # update the duration
        self.update_sleep_dt()

        return

    def update_sleep_dt(self):

        """
        This function sets the duration of sleep.
         
        :return: None
        """

        do_test = False

        DAY_2_MIN   = temporal.DAY_2_MIN

        if do_test:
            self.sleep_dt = (self.sleep_end - self.sleep_start ) % DAY_2_MIN
        else:
            self.sleep_dt = (self.sleep_end - self.sleep_start + 1) % DAY_2_MIN

        return

    def update_sleep_start_univ(self, time_of_day, t_univ):

        """
        This function sets the start time for sleep in terms of universal time.
        
        :param int time_of_day: the current time of day [minutes] 
        :param int t_univ:  the universal time [minutes]
        :return: None 
        """

        self.start_univ = self.update_time_univ(time_of_day=time_of_day, t_univ=t_univ, t=self.sleep_start)

        return

    def update_sleep_end_univ(self, time_of_day, t_univ):

        """
        This function sets the end time for sleep in terms of universal time.
        
        :param int time_of_day: the current time of day [minutes] 
        :param int t_univ: the universal time [minutes]
        :return: None
        """
        self.start_univ = self.update_time_univ(time_of_day=time_of_day, t_univ=t_univ, t=self.sleep_end)

        return

    def update_time_univ(self, time_of_day, t_univ, t):

        """
        This function updates a time :math:`t`, which represents sleep start time or end time, to be in the \
        next occurrence
         
        :param int time_of_day: the current time of day [minutes] 
        :param int t_univ:  the universal time [minutes]
        :param int t: the time to be set[minutes, time of day]
        
        :return out: the time of the next event in universal time
        :rtype: int        
        """

        DAY_2_MIN = temporal.DAY_2_MIN

        # time until midnight
        dt_midnight = (DAY_2_MIN - time_of_day)

        # the time until the next event
        dt = t + dt_midnight

        # set the next time in universal time
        out = t_univ + dt

        return out