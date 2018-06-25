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
This file contains code that handles the time related aspects of this code.

This file contains code for class :class:`temporal.Temporal`. This file also \
includes other functions that are accessed outside of the Temporal class.

.. moduleauthor:: Dr. Namdi Brandon
"""


# ===============================================
# import
# ===============================================

# general math capabilities
import numpy as np

# ===============================================
# constants
# ===============================================

# days of the week
SUNDAY      = 0
MONDAY      = 1
TUESDAY     = 2
WEDNESDAY   = 3
THURSDAY    = 4
FRIDAY      = 5
SATURDAY    = 6


# useful conversions
HOUR_2_MIN  = 60
DAY_2_MIN   = 24 * HOUR_2_MIN

WEEK_2_DAY  = 7
WEEK_2_MIN  = WEEK_2_DAY * DAY_2_MIN

YEAR_2_WEEK = 52
YEAR_2_DAY  = YEAR_2_WEEK * WEEK_2_DAY
YEAR_2_MIN      = YEAR_2_DAY * DAY_2_MIN

SEASON_2_WEEK   = YEAR_2_WEEK // 4
SEASON_2_DAY    = SEASON_2_WEEK * WEEK_2_DAY
SEASON_2_MIN    = SEASON_2_DAY * DAY_2_MIN

# the seasons
WINTER  = 0
SPRING  = 1
SUMMER  = 2
FALL    = 3
 
# the times for dawn (day) and dusk (night)
DAWN = 6 * HOUR_2_MIN
DUSK = 18 * HOUR_2_MIN

# This dictionary takes the INTEGER representation of the day and
# returns the STRING representation
DAY_2_STR = {
    SUNDAY: 'Sunday',
    MONDAY: 'Monday',
    TUESDAY: 'Tuesday',
    WEDNESDAY: 'Wednesday',
    THURSDAY: 'Thursday',
    FRIDAY: 'Friday',
    SATURDAY: 'Saturday',
    }

# ===============================================
# class Temporal
# ===============================================

class Temporal(object):

    """
    This class handles all the time keeping responsibilities.

    Universal time is the total amount of time in minutes elapsed from the start of the
    calendar year.

    Day 0 at 0:00 corresponds to a universal time of 0

    Day 1 at 0:00 corresponds to a universal time of 1 * 24 * 60

    Day 359 at 0:00 corresponds to a universal time of 359 * 24 * 60

    :param int t_univ: the time in universal time [minutes]

    :var int day: the day number in the simulation
    :var int day_of_week: a number 0, 1, 2, ... 6 corresponding to days of the week where 0 is Sunday, 1 is \
    Monday,  ... 6 is Saturday
    :var int dt: the step size in the simulation [minutes] (**antiquated**)
    :var int hour_of_day: the hour of the day [0, 23]
    :var bool is_weekday: a flag indicating if it's a weekday (Monday-Friday) if True. False, otherwise.
    :var bool is_night: a flag indicating if the time of day is after **dusk** and before **dawn** if True. \
    False, otherwise.
    :var int min_of_day: the minute of the day [0, 60 - 1]

    :var int t_univ: the universal time [minutes]
    :var int time_of_day: the time of the day [minutes], [0, 1, ... 24 * 60 -1]
    :var int season: the season
    :var int tic: indicates that current tick (each tick corresponds to a step of size dt)
    :var int step: indicates the current step in the simulation [0, ... num_steps-1]

    """
    #
    # constructor
    #

    # set the start time to Day 0 at midnight
    def __init__(self, t_univ=0):

        self.t_univ         = t_univ
        self.dt             = 1

        self.day            = None
        self.day_of_week    = None
        self.hour_of_day    = None
        self.min_of_day     = None
        self.time_of_day    = None
        self.is_weekday     = None
        self.is_night       = None
        self.season         = None
        self.week_of_year   = None
        self.tic            = None

        self.set_time()
        self.initial_step   = True

        # the counter for time steps (jumping)
        self.step           = 0

        # the history of the universal time [minutes]
        self.hist_time      = -1 * np.ones( YEAR_2_MIN + 1, dtype=int)

        return


    def print_day_night(self):

        """
        Represents whether it's day or night as a string

        :return msg: daytime / nightime status (or an error message, if there is an error)
        :rtype: str
        """

        msg = ''
        if (self.is_day):
            msg = msg + 'Day time'
        else:
            msg = msg + 'Night time'

        return msg

    def print_day_of_week(self):

        """
        Represents the day of the week as a string

        :return msg: the day of the week (or an error message, if there is an error)
        :rtype: str
        """

        # an error message
        msg = 'ERROR! Invlid choice for Temporal.dayOfWeek!'

        return DAY_2_STR.get(self.day_of_week, msg)

    def print_season(self):

        """
        Represents the seasons as a string

        :return: the season (or an error message, if there is an error)
        :rtype: str
        """

        switcher = {
            WINTER: 'Winter',
            SPRING: 'Spring',
            SUMMER: 'Summer',
            FALL: 'Fall',
        }

        # error message
        msg = 'ERROR! %d is an invalid choice for Temporal.season!\n' % self.season

        return switcher.get(self.season, msg)

    def print_time_of_day_to_military(self):

        """
        Represents the time of day as military time.

        :return: the time of day in military time
        :rtype: str
        """
        msg = print_military_time(self.time_of_day)

        return msg

    #------------------------------------------------------
    # methods
    #-------------------------------------------------------

    def reset(self, t_univ):

        """
        Reset the temporal object to the initial state.

        :param int t_univ: The time [seconds, universal time] that the time should be reset to
        :return:
        """

        self.t_univ         = t_univ
        self.step           = 0
        self.initial_step   = True
        self.set_time()
        self.hist_time[:]   = -1

        return

    def set_day_of_week(self):

        """
        This function sets the day of the week. In addition, this function sets the day count, \
        the day of the week, and a flag indicating whether it is a weekday or not.

        :return: None
        """

        # the current universe time
        t = self.t_univ

        # the number of hours that have overlapped in the year, integer division
        h = t // 60

        # the number of days that have overlapped in the year, integer division
        self.day = h // 24

        # set the week of the year, integer division
        w = self.day // 7
        self.week_of_year = w %  YEAR_2_WEEK
 
        # set the day of the week
        self.day_of_week = self.day % 7

        # set flag to see if it's a week day
        if (self.day_of_week == SATURDAY) or (self.day_of_week == SUNDAY):
            self.is_weekday = False
        else:
            self.is_weekday = True
        return

    def set_time(self):

        """
        This function sets all the time variable due to the universal time. This function sets

        #. the time of day
        #. the day of the week
        #. the season
        #. the tic.

        :return: None
        """

        self.set_time_of_day()
        self.set_day_of_week()
        self.set_season()
        self.tic = self.t_univ // self.dt

        return

    def set_time_of_day(self):

        """
        Given the universal time, this function sets the time of day in minutes.

        :return: None
        """

        # the current universe time
        t = self.t_univ

        # the number of hours that have overlapped in the year, integer division
        h = t // HOUR_2_MIN

        # the number of minutes within the hour (h)
        m = t % 60

        # the minute count within the hour
        self.min_of_day = m

        # set the hour of day
        self.hour_of_day = h % 24

        # set the time of day
        self.time_of_day = (self.hour_of_day * 60) + m

        # set whether it is day or night
        if (self.time_of_day >= DAWN) and (self.time_of_day < DUSK):
            self.is_day = True
        else:
            self.is_day = False

        return

    def set_season(self):

        """
        This function sets the season. Day 0 is the beginning of winter.

        :return: None
        """

        # this can also be (t // DAY_2_MIN / 7 // SEASON_2_WEEK) % 4
        self.season = self.week_of_year // SEASON_2_WEEK

        return

    def toString(self):

        """
        This function represents the Temporal object as a string.

        :return msg: the representation of the temporal object
        :rtype: str
        """

        msg = ''

        msg = msg + 't_univ:\t%d[min]\n' % self.t_univ
        msg = msg + 'dt:\t%d[min]\n' % self.dt
        msg = msg + 'day:\t%d\n' % self.day
        msg = msg + 'week of year:\t%d\n' % self.week_of_year
        msg = msg + 'season:\t' + self.print_season() + '\n\n'

        msg = msg + 'time of the day:\t%d[min]\n' % self.time_of_day
        msg = msg + 'time of day:\t' + print_military_time( self.time_of_day) + '\n'
        msg = msg + 'hour of the day:\t%d[hour]\n' % self.hour_of_day
        msg = msg + 'Sun status:\t%s\n' % self.print_day_night()
        msg = msg + 'day of the week:\t' + self.print_day_of_week() + '\n'
        msg = msg + 'Weekday?: ' + str(self.is_weekday) + '\n'
        msg = msg + 'current tic:\t%d\n' % self.tic

        return msg

    def update_time(self):

        """
        Increments the time by 1 time step.

        .. warning::
            This function is outdated!

        :return: None
        """

        # update the universe time
        self.t_univ = self.t_univ + self.dt

        # set all time variables
        self.set_time()

        return

def convert_cyclical_to_decimal(t):

    """
    This function converts cyclical time to decimal time

    :param int t: the time of day [minutes]

    :return out: the time of day in [hours]
    :rtype: float
    """

    out = t / 60.0
    
    return out

def convert_cylical_to_universal(day, time_of_day):

    """
    This function converts a cyclical time to the universal time.

    :param int day: the day of the year
    :param int time_of_day: the time of day [minutes]

    :return t: the time in universal time
    :rtype: int
    """

    t = day * DAY_2_MIN + time_of_day
    
    return t

def convert_decimal_to_min(t):

    """
    This function takes in the time of day as a decimal and outputs the time in minutes

    :param float t: the time of day [0, 24) [hours]

    :return out: the time of day [minutes]
    :rtype: int
    """

    # hours 
    h = np.floor(t)
    
    # the minutes past the hour
    m = round( (t - h) * HOUR_2_MIN )
    
    # time of day in minutes
    out = int( (h * HOUR_2_MIN) + m )
    
    return out

def convert_universal_to_decimal(t_univ):

    """
    This function takes in the universal time and converts it to the time of day in decimal format [0, 24)

    :param int t_univ: the universal time [minutes]

    :return out: the universal time [hours]
    :rtype: float
    """

    # convert the universal time to a cyclical time
    time_of_day = t_univ % DAY_2_MIN
    
    # convert the cyclical time to a decimal format
    out = np.float(time_of_day) / HOUR_2_MIN
    
    return out
    
def print_military_time(t):

    """
    Represents the time of day in military time  assume that time is in minutes format.

    :param int t: the time of day [minutes]

    :return msg: the time of day in military time 00:00
    :rtype: str
    """

    # the number of hours, integer division
    h = t  // HOUR_2_MIN

    # the number of minutes
    m = t % HOUR_2_MIN

    msg = '%02d:%02d' % (h, m)
    
    return msg    