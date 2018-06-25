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
The purpose of this module is to assign parameters necessary to run the ABMHAP initialized with \
data from the Consolidated Human Activity Database (CHAD).

This module contains :class:`chad_params.CHAD_params`.
"""

# ===========================================
# import
# ===========================================

import sys
sys.path.append('..\\source')

# math capability
import numpy as np

# ABMHAP modules
import my_globals as mg

# ===========================================
# constants
# ===========================================


# the times are in hours

#
# school
#
EDUCATION_DT_MEAN_MIN       = 4
EDUCATION_DT_MEAN_MAX       = 11
EDUCATION_DT_STD_MAX        = 1

EDUCATION_START_MEAN_MIN    = 5
EDUCATION_START_MEAN_MAX    = 11
EDUCATION_START_STD_MAX     = 1

EDUCATION_END_MEAN_MIN      = 13
EDUCATION_END_MEAN_MAX      = 18
EDUCATION_END_STD_MAX       = 1

#
# work
#

WORK_DT_MEAN_MIN            = 5
WORK_DT_MEAN_MAX            = 11
WORK_DT_STD_MAX             = 1

WORK_START_MEAN_MIN         = 6
WORK_START_MEAN_MAX         = 11
WORK_START_STD_MAX          = 1

WORK_END_MEAN_MIN           = 15
WORK_END_MEAN_MAX           = 19
WORK_END_STD_MAX            = 1

#
# commute to work (time is in hours)
#
COMMUTE_TO_WORK_DT_MEAN_MIN = 5/60
COMMUTE_TO_WORK_DT_MEAN_MAX = 1
COMMUTE_TO_WORK_DT_STD_MAX  = 2

COMMUTE_TO_WORK_START_MEAN_MIN  = (WORK_START_MEAN_MIN - COMMUTE_TO_WORK_DT_MEAN_MAX) % 24
COMMUTE_TO_WORK_START_MEAN_MAX  = (WORK_START_MEAN_MAX - COMMUTE_TO_WORK_DT_MEAN_MIN) % 24
COMMUTE_TO_WORK_START_STD_MAX   = 2

#
# eat breakfast
#
EAT_BREAKFAST_DT_MEAN_MIN       = 5/60
EAT_BREAKFAST_DT_MEAN_MAX       = 1
EAT_BREAKFAST_DT_STD_MAX        = 1

EAT_BREAKFAST_START_MEAN_MIN    = 6
EAT_BREAKFAST_START_MEAN_MAX    = 9
EAT_BREAKFAST_START_STD_MAX     = 1

#
# commute from work
#
COMMUTE_FROM_WORK_DT_MEAN_MIN   = COMMUTE_TO_WORK_DT_MEAN_MIN
COMMUTE_FROM_WORK_DT_MEAN_MAX   = COMMUTE_TO_WORK_DT_MEAN_MAX
COMMUTE_FROM_WORK_DT_STD_MAX    = COMMUTE_TO_WORK_DT_STD_MAX

COMMUTE_FROM_WORK_START_MEAN_MIN  = 15
COMMUTE_FROM_WORK_START_MEAN_MAX  = 22
COMMUTE_FROM_WORK_START_STD_MAX   = COMMUTE_TO_WORK_START_STD_MAX

#
# sleep
#
# the time is in periodic hours [-12, 12]
SLEEP_START_MEAN_MIN        = -3
SLEEP_START_MEAN_MAX        = 3 # 3
SLEEP_START_STD_MAX         = 1

SLEEP_END_MEAN_MIN          = 5
SLEEP_END_MEAN_MAX          = 10
SLEEP_END_STD_MAX           = 1

#
# eat lunch
#
EAT_LUNCH_DT_MEAN_MIN       = 5/60
EAT_LUNCH_DT_MEAN_MAX       = 1
EAT_LUNCH_DT_STD_MAX        = 1

EAT_LUNCH_START_MEAN_MIN    = 11.5
EAT_LUNCH_START_MEAN_MAX    = 15.5
EAT_LUNCH_START_STD_MAX     = 1

#
# eat dinner
#
EAT_DINNER_DT_MEAN_MIN      = 5/60
EAT_DINNER_DT_MEAN_MAX      = 1
EAT_DINNER_DT_STD_MAX       = 1

EAT_DINNER_START_MEAN_MIN   = 17
EAT_DINNER_START_MEAN_MAX   = 21.5
EAT_DINNER_START_STD_MAX    = 1

#
# the minimum number of events needed in sampling from the CHAD statistical data for each activity
#
N_COMMUTE_FROM_WORK = 1
N_COMMUTE_TO_WORK   = 1
N_EAT_BREAKFAST     = 2
N_EAT_DINNER        = 2
N_EAT_LUNCH         = 2
N_EDUCATION         = 2
N_SLEEP             = 2
N_WORK              = 1

# ===========================================
# class CHAD_params
# ===========================================

class CHAD_params(object):

    """
    This class holds sampling parameters for various activities in CHAD that are used to filter out what is \
    considered "good" data for a given activity.

    :param float dt_mean_min: the minimum mean duration to be sampled in hours [0, 24)
    :param float dt_mean_max: the maximum mean duration to be sampled in hours [0, 24)
    :param float dt_std_max: the maximum standard deviation of duration to be sampled in hours [0, 24)

    :param float start_mean_min: the minimum mean start time to be sampled in hours [0, 24)
    :param float start_mean_max: the maximum mean start time to be sampled in hours [0, 24)
    :param float start_std_max: the maximum standard deviation of start time to be sampled in hours [0, 24)

    :param float end_mean_min: the minimum mean end time to be sampled in hours [0, 24)
    :param float end_mean_max: the maximum mean end time to be sampled in hours [0, 24)
    :param float end_std_max: the maximum standard deviation of end time to be sampled in hours [0, 24)

    :param int N: the minimum amount of activity-events needed in sampling
    :param bool do_solo: a flag indicating whether to take single activity-events only
    :param bool do_dt: a flag indicating whether (if True) or not (if False) to sample duration data from CHAD
    :param bool do_start: a flag indicating whether (if True) or not (if False) to sample start time data from CHAD
    :param bool do_end: a flag indicating whether (if True) or not (if False) to sample end time data from CHAD

    :var float dt_mean_min: the minimum mean duration to be sampled in hours [0, 24)
    :var float dt_mean_max: the maximum mean duration to be sampled in hours [0, 24)
    :var float dt_std_max: the maximum standard deviation of  duration to be sampled in hours [0, 24)

    :var float start_mean_min: the minimum mean start time to be sampled in hours [0, 24)
    :var float start_mean_max: the maximum mean start time to be sampled in hours [0, 24)
    :var float start_std_max: the maximum standard deviation of  start time to be sampled in hours [0, 24)

    :var float end_mean_min: the minimum mean end time to be sampled in hours [0, 24)
    :var float end_mean_max: the maximum mean end time to be sampled in hours [0, 24)
    :var float end_std_max: the maximum standard deviation of end time to be sampled in hours [0, 24)

    :var int N: the minimum amount of activity-events needed in sampling
    :var bool do_solo: a flag indicating whether to take single activity-events only

    :var bool do_dt: a flag indicating whether (if True) or not (if False) to sample duration data from CHAD
    :var bool do_start: a flag indicating whether (if True) or not (if False) to sample start time data from CHAD
    :var bool do_end: a flag indicating whether (if True) or not (if False) to sample end time data from CHAD
    """

    def __init__(self, dt_mean_min=None, dt_mean_max=None, dt_std_max=None, start_mean_min=None, \
                 start_mean_max=None, start_std_max=None, end_mean_min=None, end_mean_max=None, end_std_max=None, \
                 N=1, do_solo=False, do_dt=False, do_start=False, do_end=False):

        # the minimum mean duration
        self.dt_mean_min    = dt_mean_min

        # the maximum mean duration
        self.dt_mean_max    = dt_mean_max

        # the maximum standard deviation for duration
        self.dt_std_max     = dt_std_max

        # the minimum mean start time
        self.start_mean_min = start_mean_min

        # the maximum mean start time
        self.start_mean_max = start_mean_max

        # the maximum standard deviation for start time
        self.start_std_max  = start_std_max

        # the minimum mean end time
        self.end_mean_min   = end_mean_min

        # the maximum mean end time
        self.end_mean_max   = end_mean_max

        # the maximum standard deviation for end time
        self.end_std_max    = end_std_max

        # the minimum amount of activity-events needed
        self.N          = N

        # a flag indicating whether to take single activity-events only
        self.do_solo    = do_solo

        # a flag indicating whether (if True) or not (if False) to sample duration
        self.do_dt      = do_dt

        # a flag indicating whether (if True) or not (if False) to sample start time
        self.do_start   = do_start

        # a flag indicating whether (if True) or not (if False) to sample end time
        self.do_end     = do_end

        return

    def get_dt(self, df_stats):

        """
        This function samples CHAD data for duration.

        :param pandas.core.frame.DataFrame df_stats: the duration data from CHAD for a given activity

        :return: the duration data from CHAD that satisfies statistical properties to use in ABMHAP.
        :rtype: pandas.core.frame.DataFrame
        """

        df = self.get_stats(df_stats, mean_min=self.dt_mean_min, mean_max=self.dt_mean_max, \
                            std_max=self.dt_std_max, N=self.N)

        return df


    def get_end(self, df_stats):

        """
        This function samples CHAD data for end time.

        :param pandas.core.frame.DataFrame df_stats: the end time data from CHAD for a given activity

        :return: the end time data from CHAD that satisfies statistical properties to use in ABMHAP.
        :rtype: pandas.core.frame.DataFrame
        """

        df = self.get_stats(df_stats, mean_min=self.end_mean_min, mean_max=self.end_mean_max, \
                            std_max=self.end_std_max, N=self.N)

        return df

    def get_record(self, df, do_periodic):

        """
        Given a data frame of CHAD records, return the results where conditions are met according to the \
        chad_param object.

        .. note:
            Will need to include variation

        :param pandas.core.frame.DataFrame df: the CHAD records from participants for a given activity
        :param bool do_periodic: a flag indicating whether (if True) or not (if False) to convert time to a [-12, 12) \
        format due to an activity that could occur over midnight.

        :return: the records from CHAD that satisfy the statistical data for duration, start time, and end time.
        :rtype: pandas.core.frame.DataFrame
        """

        # the boolean indices of the individuals in CHAD that satisfy the sampling data properties
        # for duration, start time, and end time
        idx_dt      = np.ones( len(df), dtype=bool)
        idx_start   = np.ones( len(df), dtype=bool)
        idx_end     = np.ones( len(df), dtype=bool)

        # sample the duration data
        if self.do_dt:
            lower, upper = self.dt_mean_min, self.dt_mean_max
            idx_dt = self.get_record_help(df.dt.values, lower, upper, do_periodic=False)

        # sample the start time data
        if self.do_start:
            lower, upper = self.start_mean_min, self.start_mean_max
            idx_start = self.get_record_help(df.start.values, lower, upper, do_periodic=do_periodic)

        # sample the end time data
        if self.do_end:
            lower, upper = self.end_mean_min, self.end_mean_max
            idx_end = self.get_record_help(df.end.values, lower, upper, do_periodic=do_periodic)

        # obtain the data that satisfy the requirements for start time, end time, and duration
        result = df[ idx_dt & idx_start & idx_end]

        return result

    def get_record_help(self, x, lower, upper, do_periodic):

        """
        This function finds the boolean indices of acceptable entries from an activity-parameter within \
        the CHAD data.

        :param numpy.ndarray x: data for a given activity-parameter (i.e., duration, start time, or end time)
        :param float lower: the lower bound of acceptable values
        :param float upper: the upper bound of acceptable values
        :param bool do_periodic: a flag indicating whether (if True) or not (if False) to convert time to a [-12, 12) \
        format due to an activity that could occur over midnight.

        :return: boolean indices of acceptable values, respectively
        :rtype: numpy.ndarray of int
        """

        # covert time to a [-12, 12) format
        if do_periodic:
            x = mg.to_periodic(x)

        # boolean indices of acceptable values
        idx = np.array( (x >= lower) & (x <= upper) )

        return idx

    # def get_record_old(self, df, pid):
    #
    #     """
    #
    #     :param pandas.core.frame.DataFrame df: a record of event data
    #     :param list pid_list: a list of unique identifiers of people to sample
    #
    #     :return:
    #     :rtype: pandas.core.frame.DataFrame
    #     """
    #
    #     # get the records of people who are used in the empirical distribution of BOTH start times AND durations
    #     f       = lambda x: x in pid
    #     idx     = df.PID.apply(f)
    #     record  = df[idx]
    #
    #     return record

    def get_start(self, df_stats):

        """"
        This function samples CHAD data for start time.

        :param pandas.core.frame.DataFrame df_stats: the start time data from CHAD for a given activity

        :return: the start time data from CHAD that satisfies statistical properties to use in ABMHAP.
        :rtype: pandas.core.frame.DataFrame
        """

        df = self.get_stats(df_stats, mean_min=self.start_mean_min, mean_max=self.start_mean_max, \
                            std_max=self.start_std_max, N=self.N)

        return df

    def get_stats(self, df, mean_min, mean_max, std_max, N):

        """
        This function samples the CHAD longitudinal data and selects entries with the selected \
        characteristics: the mean within the given range, within the maximum standard deviation, \
        and having longitudinal data with at least N entries.

        :param pandas.core.frame.DataFrame df: the duration statistical data for a given activity
        :param float mean_min:
        :param float mean_max:
        :param float std_max:
        :param int N:

        :return: the CHAD data that satisfies the given statistical constraints
        :rtype: pandas.core.frame.DataFrame
        """

        # assuming longitudinal data, take into account data about the standard deviation
        if N > 1:
            result = df[ (df['mu'] >= mean_min) & (df['mu'] <= mean_max) & (df.N >= N) \
                         & (df['std'] > 0) & (df['std'] <= std_max) ]
        else:
            result = df[ (df['mu'] >= mean_min) & (df['mu'] <= mean_max) & (df.N >= N) ]

        return result

    def toString(self):

        """
        Represent the object as a string.

        :return: the representation of the object as a string
        :rtype: str
        """

        msg = ''

        if self.do_start:
            msg = msg + ('start mean min: %.3f, start mean max: %.3f, start std max: %.3f\n' \
                         % (self.start_mean_min, self.start_mean_max, self.start_std_max) )

        if self.do_end:
            msg = msg + ('end mean min: %.3f, end mean max: %.3f, end std max: %.3f\n' \
                         % (self.end_mean_min, self.end_mean_max, self.end_std_max) )

        if self.do_dt:
            msg = msg + ('dt mean min: %.3f, dt mean max: %.3f, dt std max: %.3f\n' \
                         % (self.dt_mean_min, self.dt_mean_max, self.dt_std_max) )

        return msg

# ===========================================
# global constants
# ===========================================

#
# default parameters for various activities. The times are in hours.
#

# default parameters for commuting to work

#
# For commute to work, commute from work, and work, N is set to 1 because there is not enough longitudinal
# data
#
COMMUTE_TO_WORK = CHAD_params(dt_mean_min=COMMUTE_TO_WORK_DT_MEAN_MIN, dt_mean_max=COMMUTE_TO_WORK_DT_MEAN_MAX,
                              dt_std_max=COMMUTE_TO_WORK_DT_STD_MAX, start_mean_min=COMMUTE_TO_WORK_START_MEAN_MIN,
                              start_mean_max=COMMUTE_TO_WORK_START_MEAN_MAX, start_std_max=COMMUTE_TO_WORK_DT_STD_MAX,
                              N=N_COMMUTE_TO_WORK, do_dt=True, do_start=True)

# default parameters for commuting from work
COMMUTE_FROM_WORK = CHAD_params(dt_mean_min=COMMUTE_FROM_WORK_DT_MEAN_MIN, dt_mean_max=COMMUTE_FROM_WORK_DT_MEAN_MAX,
                                dt_std_max=COMMUTE_FROM_WORK_DT_STD_MAX,
                                start_mean_min=COMMUTE_FROM_WORK_START_MEAN_MIN,
                                start_mean_max=COMMUTE_FROM_WORK_START_MEAN_MAX,
                                start_std_max=COMMUTE_FROM_WORK_START_STD_MAX,
                                N=N_COMMUTE_FROM_WORK, do_dt=True, do_start=True)

# default parameters for eating breakfast
EAT_BREAKFAST = CHAD_params(dt_mean_min=EAT_BREAKFAST_DT_MEAN_MIN, dt_mean_max=EAT_BREAKFAST_DT_MEAN_MAX,
                            dt_std_max=EAT_BREAKFAST_DT_STD_MAX, start_mean_min=EAT_BREAKFAST_START_MEAN_MIN,
                            start_mean_max=EAT_BREAKFAST_START_MEAN_MAX, start_std_max=EAT_BREAKFAST_START_STD_MAX,
                            N=N_EAT_BREAKFAST, do_dt=True, do_start=True)

# default parameters for eating dinner
EAT_DINNER = CHAD_params(dt_mean_min=EAT_DINNER_DT_MEAN_MIN, dt_mean_max=EAT_DINNER_DT_MEAN_MAX,
                         dt_std_max=EAT_DINNER_DT_MEAN_MAX, start_mean_min=EAT_DINNER_START_MEAN_MIN,
                         start_mean_max=EAT_DINNER_START_MEAN_MAX, start_std_max=EAT_DINNER_START_STD_MAX,
                         N=N_EAT_DINNER, do_dt=True, do_start=True)

# default parameters for eating lunch
EAT_LUNCH = CHAD_params(dt_mean_min=EAT_LUNCH_DT_MEAN_MIN, dt_mean_max=EAT_LUNCH_DT_MEAN_MAX,
                        dt_std_max=EAT_LUNCH_DT_STD_MAX, start_mean_min=EAT_LUNCH_START_MEAN_MIN,
                        start_mean_max=EAT_LUNCH_START_MEAN_MAX, start_std_max=EAT_LUNCH_START_STD_MAX,
                        N=N_EAT_LUNCH, do_dt=True, do_start=True)

# default parameters for schooling
EDUCATION = CHAD_params( start_mean_min=EDUCATION_START_MEAN_MIN, start_mean_max=EDUCATION_START_MEAN_MAX, \
                         start_std_max=EDUCATION_START_STD_MAX, end_mean_min=EDUCATION_END_MEAN_MIN, \
                         end_mean_max=EDUCATION_END_MEAN_MAX,end_std_max=EDUCATION_END_STD_MAX, \
                         N=N_EDUCATION, do_start=True, do_end=True)


# default parameters for sampling sleep data
SLEEP = CHAD_params(start_mean_min=SLEEP_START_MEAN_MIN, start_mean_max=SLEEP_START_MEAN_MAX, \
                    start_std_max=SLEEP_START_STD_MAX, end_mean_min=SLEEP_END_MEAN_MIN, \
                    end_mean_max=SLEEP_END_MEAN_MAX, end_std_max=SLEEP_END_STD_MAX, N=N_SLEEP,\
                    do_start=True, do_end=True)

# default parameters for working
WORK = CHAD_params( start_mean_min=WORK_START_MEAN_MIN, start_mean_max=WORK_START_MEAN_MAX, \
                    start_std_max=WORK_START_STD_MAX, end_mean_min=WORK_END_MEAN_MIN, end_mean_max=WORK_END_MEAN_MAX,\
                    end_std_max=WORK_END_STD_MAX, N=N_WORK, do_start=True, do_end=True)


# the default parameters for the macro parameters
OMNI = { mg.KEY_COMMUTE_TO_WORK: COMMUTE_TO_WORK,
         mg.KEY_COMMUTE_FROM_WORK:COMMUTE_FROM_WORK,
         mg.KEY_EAT_BREAKFAST: EAT_BREAKFAST,
         mg.KEY_EAT_DINNER: EAT_DINNER,
         mg.KEY_EAT_LUNCH: EAT_LUNCH,
         mg.KEY_SLEEP: SLEEP,
         mg.KEY_WORK: WORK,
         }


