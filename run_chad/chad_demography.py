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
This module contains code that handles accessing the Consolidated Human Activity Database (CHAD)
data for various demographics.

This module contains :class:`chad_demography.CHAD_demography`.
"""

# ===========================================
# import
# ===========================================
import sys
sys.path.append('..\\source')
sys.path.append('..\\processing')

# ABMHAP modules
import demography as dmg
import chad

# ===========================================
# constants
# ===========================================

# the file names for the CHAD activity-moments data
START, END, DT, RECORD   = chad.START, chad.END, chad.DT, chad.RECORD

# ===========================================
# class CHAD_demography
# ===========================================

class CHAD_demography(object):

    """
    This class contains the common functionality with accessing the CHAD data files
    relevant to different demographics.

    :param int demographic: the demographic identifier


    :var int demographic: the demographic identifier
    :var str fname_zip: the name of the file (.zip) that contains the CHAD data

    :var dict fname_stats_commute_to_work: the file names for the CHAD longitudinal data \
    (start time, end time, duration, and records) to be sampled for commuting to work
    :var dict fname_stats_commute_from_work: the file names for the CHAD longitudinal data \
    (start time, end time, duration, and records) to be sampled for commuting from work
    :var dict fname_stats_eat_breakfast: the file names for the CHAD longitudinal data \
    (start time, end time, duration, and records) to be sampled for eating breakfast
    :var dict fname_stats_eat_dinner: the file names for the CHAD longitudinal data \
    (start time, end time, duration, and records) to be sampled for eating dinner
    :var dict fname_stats_eat_lunch: the file names for the CHAD longitudinal data \
    (start time, end time, duration, and records) to be sampled for eating lunch
    :var dict fname_stats_school: the file names for the CHAD longitudinal data \
    (start time, end time, duration, and records) to be sampled for schooling
    :var dict fname_stats_sleep: the file names for the CHAD longitudinal data \
    (start time, end time, duration, and records) to be sampled for sleeping
    :var dict fname_stats_work: the file names for the CHAD longitudinal data \
    (start time, end time, duration, and records) to be sampled for working

    :var int n_commute_from_work: the minimum number of events needed in sampling \
    from CHAD longitudinal data for commuting from work
    :var int n_commute_to_work: the minimum number of events needed in sampling \
    from CHAD longitudinal data for commuting to work
    :var int n_eat_breakfast: the minimum number of events needed in sampling \
    from CHAD longitudinal data for eating breakfast
    :var int n_eat_dinner: the minimum number of events needed in sampling \
    from CHAD longitudinal data for eating dinner
    :var int n_eat_lunch: the minimum number of events needed in sampling \
    from CHAD longitudinal data for eating lunch
    :var int n_school: the minimum number of events needed in sampling \
    from CHAD longitudinal data for schooling
    :var int n_sleep: the minimum number of events needed in sampling \
    from CHAD longitudinal data for sleeping
    :var int n_work: the minimum number of events needed in sampling \
    from CHAD longitudinal data for working

    :var float work_start_mean_min: the minimum mean start time for working when sampling CHAD data
    :var float work_start_mean_max: the maximum mean start time for working when sampling CHAD data
    :var float work_start_std_max: the maximum standard deviation for start time for working when sampling CHAD data
    :var float work_end_mean_min: the minimum mean end time for working when sampling CHAD data
    :var float work_end_mean_max: the maximum mean end time for working when sampling CHAD data
    :var float work_end_std_max: the maximum standard deviating for end time for working when sampling CHAD data
    :var float work_dt_mean_min: the minimum mean duration for working when sampling CHAD data
    :var float work_dt_mean_max: the maximum mean duration for working when sampling CHAD data
    :var float work_dt_std_max: the maximum standard deviation for working when sampling CHAD data

    :var float school_start_mean_min: the minimum mean start time for schooling when sampling CHAD data
    :var float school_start_mean_max: the maximum mean start time for schooling when sampling CHAD data
    :var float school_start_std_max: the maximum standard deviation for start time for schooling when sampling CHAD data
    :var float school_end_mean_min: the minimum mean end time for schooling when sampling CHAD data
    :var float school_end_mean_max: the maximum mean end time for schooling when sampling CHAD data
    :var float school_end_std_max: the maximum standard deviating for end time for schooling when sampling CHAD data
    :var float school_dt_mean_min: the minimum mean duration for schooling when sampling CHAD data
    :var float school_dt_mean_max: the maximum mean duration for schooling when sampling CHAD data
    :var float school_dt_std_max: the maximum standard deviation for schooling when sampling CHAD data

    :var float commute_to_work_start_mean_min: the minimum mean start time for commuting to work when sampling CHAD data
    :var float commute_to_work_start_mean_max: the maximum mean start time for commuting to work when sampling CHAD data
    :var float commute_to_work_start_std_max: the maximum standard deviation for start time for commuting to work when sampling CHAD data
    :var float commute_to_work_end_mean_min: the minimum mean end time for commuting to work when sampling CHAD data
    :var float commute_to_work_end_mean_max: the maximum mean end time for commuting to work when sampling CHAD data
    :var float commute_to_work_end_std_max: the maximum standard deviating for end time for commuting to work when sampling CHAD data
    :var float commute_to_work_dt_mean_min: the minimum mean duration for commuting to work when sampling CHAD data
    :var float commute_to_work_dt_mean_max: the maximum mean duration for commuting to work when sampling CHAD data
    :var float commute_to_work_dt_std_max: the maximum standard deviation for commuting to work when sampling CHAD data

    :var float eat_breakfast_start_mean_min: the minimum mean start time for eating breakfast when sampling CHAD data
    :var float eat_breakfast_start_mean_max: the maximum mean start time for eating breakfast when sampling CHAD data
    :var float eat_breakfast_start_std_max: the maximum standard deviation for start time for eating breakfast when sampling CHAD data
    :var float eat_breakfast_end_mean_min: the minimum mean end time for eating breakfast when sampling CHAD data
    :var float eat_breakfast_end_mean_max: the maximum mean end time for eating breakfast when sampling CHAD data
    :var float eat_breakfast_end_std_max: the maximum standard deviating for end time for eating breakfast when sampling CHAD data
    :var float eat_breakfast_dt_mean_min: the minimum mean duration for eating breakfast when sampling CHAD data
    :var float eat_breakfast_dt_mean_max: the maximum mean duration for eating breakfast when sampling CHAD data
    :var float eat_breakfast_dt_std_max: the maximum standard deviation for eating breakfast when sampling CHAD data

    :var float commute_from_work_start_mean_min: the minimum mean start time for commuting from work when sampling CHAD data
    :var float commute_from_work_start_mean_max: the maximum mean start time for commuting from work when sampling CHAD data
    :var float commute_from_work_start_std_max: the maximum standard deviation for start time for commuting from work when sampling CHAD data
    :var float commute_from_work_end_mean_min: the minimum mean end time for commuting from work when sampling CHAD data
    :var float commute_from_work_end_mean_max: the maximum mean end time for commuting from work when sampling CHAD data
    :var float commute_from_work_end_std_max: the maximum standard deviating for end time for commuting from work when sampling CHAD data
    :var float commute_from_work_dt_mean_min: the minimum mean duration for commuting from work when sampling CHAD data
    :var float commute_from_work_dt_mean_max: the maximum mean duration for commuting from work when sampling CHAD data
    :var float commute_from_work_dt_std_max: the maximum standard deviation for commuting from work when sampling CHAD data

    :var float sleep_start_mean_min: the minimum mean start time for sleeping when sampling CHAD data
    :var float sleep_start_mean_max: the maximum mean start time for sleeping when sampling CHAD data
    :var float sleep_start_std_max: the maximum standard deviation for start time for sleeping when sampling CHAD data
    :var float sleep_end_mean_min: the minimum mean end time for sleeping when sampling CHAD data
    :var float sleep_end_mean_max: the maximum mean end time for sleeping when sampling CHAD data
    :var float sleep_end_std_max: the maximum standard deviating for end time for sleeping when sampling CHAD data
    :var float sleep_dt_mean_min: the minimum mean duration for sleeping when sampling CHAD data
    :var float sleep_dt_mean_max: the maximum mean duration for sleeping when sampling CHAD data
    :var float sleep_dt_std_max: the maximum standard deviation for sleeping when sampling CHAD data

    :var float eat_lunch_start_mean_min: the minimum mean start time for eating lunch when sampling CHAD data
    :var float eat_lunch_start_mean_max: the maximum mean start time for eating lunch when sampling CHAD data
    :var float eat_lunch_start_std_max: the maximum standard deviation for start time for eating lunch when sampling CHAD data
    :var float eat_lunch_end_mean_min: the minimum mean end time for eating lunch when sampling CHAD data
    :var float eat_lunch_end_mean_max: the maximum mean end time for eating lunch when sampling CHAD data
    :var float eat_lunch_end_std_max: the maximum standard deviating for end time for eating lunch when sampling CHAD data
    :var float eat_lunch_dt_mean_min: the minimum mean duration for eating lunch when sampling CHAD data
    :var float eat_lunch_dt_mean_max: the maximum mean duration for eating lunch when sampling CHAD data
    :var float eat_lunch_dt_std_max: the maximum standard deviation for eating lunch when sampling CHAD data

    :var float eat_dinner_start_mean_min: the minimum mean start time for eating dinner when sampling CHAD data
    :var float eat_dinner_start_mean_max: the maximum mean start time for eating dinner when sampling CHAD data
    :var float eat_dinner_start_std_max: the maximum standard deviation for start time for eating dinner when sampling CHAD data
    :var float eat_dinner_end_mean_min: the minimum mean end time for eating dinner when sampling CHAD data
    :var float eat_dinner_end_mean_max: the maximum mean end time for eating dinner when sampling CHAD data
    :var float eat_dinner_end_std_max: the maximum standard deviating for end time for eating dinner when sampling CHAD data
    :var float eat_dinner_dt_mean_min: the minimum mean duration for eating dinner when sampling CHAD data
    :var float eat_dinner_dt_mean_max: the maximum mean duration for eating dinner when sampling CHAD data
    :var float eat_dinner_dt_std_max: the maximum standard deviation for eating dinner when sampling CHAD data
    """


    def __init__(self, demographic):

        # store the demographic
        self.demographic    = demographic

        # the file name on the .zip file
        self.fname_zip      = dmg.FNAME_DEMOGRAPHY[self.demographic]

        #
        # defaults
        #
        #
        # the following data is read from the .zip files for the activities for the respective demographics
        #

        # file names for CHAD longitudinal data for commuting to work
        self.fname_stats_commute_to_work    = {START: 'longitude/commute_to_work/stats_start.csv',
                                               END: 'longitude/commute_to_work/stats_end.csv',
                                               DT: 'longitude/commute_to_work/stats_dt.csv',
                                               RECORD: 'longitude/commute_to_work/record.csv'}

        # file names for CHAD longitudinal data for commuting from work
        self.fname_stats_commute_from_work  = {START: 'longitude/commute_from_work/stats_start.csv',
                                               END: 'longitude/commute_from_work/stats_end.csv',
                                               DT: 'longitude/commute_from_work/stats_dt.csv',
                                               RECORD: 'longitude/commute_from_work/record.csv',}

        # file names for CHAD longitudinal data for eating breakfast
        self.fname_stats_eat_breakfast      = {START: 'longitude/eat_breakfast/stats_start.csv',
                                               END: 'longitude/eat_breakfast/stats_end.csv',
                                               DT: 'longitude/eat_breakfast/stats_dt.csv',
                                               RECORD: 'longitude/eat_breakfast/record.csv',
                                               }
        # file names for CHAD longitudinal data for eating dinner
        self.fname_stats_eat_dinner         = {START: 'longitude/eat_dinner/stats_start.csv',
                                               END: 'longitude/eat_dinner/stats_end.csv',
                                               DT: 'longitude/eat_dinner/stats_dt.csv',
                                               RECORD: 'longitude/eat_dinner/record.csv',
                                               }

        # file names for CHAD longitudinal data for eating lunch
        self.fname_stats_eat_lunch          = {START: 'longitude/eat_lunch/stats_start.csv',
                                               END: 'longitude/eat_lunch/stats_end.csv',
                                               DT: 'longitude/eat_lunch/stats_dt.csv',
                                               RECORD: 'longitude/eat_lunch/record.csv',}

        # file names for CHAD longitudinal data for schooling
        self.fname_stats_school             = {START: 'longitude/education/stats_start.csv',
                                               END: 'longitude/education/stats_end.csv',
                                               DT: 'longitude/education/stats_dt.csv',
                                               RECORD: 'longitude/education/record.csv',
                                               }

        # file names for CHAD longitudinal data for sleeping
        self.fname_stats_sleep              = {START: 'longitude/sleep/all/stats_start.csv',
                                               END: 'longitude/sleep/all/stats_end.csv',
                                               DT: 'longitude/sleep/all/stats_dt.csv',
                                               RECORD: 'longitude/sleep/all/record.csv',}

        # file names for CHAD longitudinal data for working
        self.fname_stats_work               = {START: 'longitude/work/stats_start.csv',
                                               END: 'longitude/work/stats_end.csv',
                                               DT: 'longitude/work/stats_dt.csv',
                                               RECORD: 'longitude/work/record.csv',
                                               }


        #
        # the minimum number of events needed in sampling from the CHAD ("longitudinal") statistical data \
        # for each activity
        #

        # minimum for commuting from work
        self.n_commute_from_work    = 1

        # minimum for commuting to work
        self.n_commute_to_work      = 1

        # minimum for eating breakfast
        self.n_eat_breakfast        = 2

        # minimum for eating dinner
        self.n_eat_dinner           = 2

        # minimum for eating lunch
        self.n_eat_lunch            = 2

        # minimum for schooling
        self.n_school               = 1

        # minimum for sleeping
        self.n_sleep                = 2

        # minimum for working
        self.n_work                 = 1


        #
        # the ABM's limiting parameters for each activity in CHAD
        #

        #
        # work
        #

        # minimum mean start time
        self.work_start_mean_min    = 6

        # maximum mean start time
        self.work_start_mean_max    = 11

        # maximum standard deviation for start time
        self.work_start_std_max     = 1

        # minimum mean end time
        self.work_end_mean_min      = 15

        # maximum mean end time
        self.work_end_mean_max      = 19

        # maximum standard deviation for end time
        self.work_end_std_max       = 1

        # minimum mean duration, maximum mean duration
        self.work_dt_mean_min, self.work_dt_mean_max = \
            self.set_dt_bounds(start_min=self.work_start_mean_min, start_max=self.work_start_mean_max, \
                               end_min=self.work_end_mean_min, end_max=self.work_end_mean_max)

        # maximum standard deviation for duration
        self.work_dt_std_max        = 1

        #
        # school
        #

        # minimum mean start time
        self.school_start_mean_min  = 7

        # maximum mean start time
        self.school_start_mean_max  = 9

        # maximum standard deviation for start time
        self.school_start_std_max   = 1

        # minimum mean end time
        self.school_end_mean_min    = 13

        # maximum mean end time
        self.school_end_mean_max    = 17

        # maximum standard deviation for end time
        self.school_end_std_max     = 1

        # minimum mean duration, maximum mean duration
        self.school_dt_mean_min, self.school_dt_mean_max = \
            self.set_dt_bounds(start_min=self.school_start_mean_min, start_max=self.school_start_mean_max, \
                               end_min=self.school_end_mean_min, end_max=self.school_end_mean_max)

        # maximum standard deviation for duration
        self.school_dt_std_max      = 1

        #
        # commute to work (time is in hours)
        #

        # minimum mean duration
        self.commute_to_work_dt_mean_min    = 5. / 60

        # maximum mean duration
        self.commute_to_work_dt_mean_max    = 1

        # maximum standard deviation for duration
        self.commute_to_work_dt_std_max     = 2

        # minimum mean start time
        self.commute_to_work_start_mean_min = (self.work_start_mean_min - self.commute_to_work_dt_mean_max) % 24

        # maximum mean start time
        self.commute_to_work_start_mean_max = (self.work_start_mean_max - self.commute_to_work_dt_mean_min) % 24

        # maximum standard deviation for start time
        self.commute_to_work_start_std_max  = 2

        # minimum mean end time, maximum mean end time
        self.commute_to_work_end_mean_min, self.commute_to_work_end_mean_max \
            = self.set_end_bounds(start_min=self.commute_to_work_start_mean_min, \
                                  start_max=self.commute_to_work_start_mean_max,\
                                  dt_min=self.commute_to_work_dt_mean_min,\
                                  dt_max=self.commute_to_work_dt_mean_max)

        # maximum standard deviation for end time
        self.commute_to_work_end_std_max    = 1

        #
        # eat breakfast
        #

        # minimum mean duration
        self.eat_breakfast_dt_mean_min  = 5 / 60

        # maximum mean duration
        self.eat_breakfast_dt_mean_max  = 1

        # maximum standard deviation for duration
        self.eat_breakfast_dt_std_max   = 1

        # minimum mean start time
        self.eat_breakfast_start_mean_min   = 6

        # maximum mean start time
        self.eat_breakfast_start_mean_max   = 9

        # maximum standard deviation for start time
        self.eat_breakfast_start_std_max    = 1

        # minimum mean end time, maximum mean end time
        self.eat_breakfast_end_mean_min, self.eat_breakfast_end_mean_max \
            = self.set_end_bounds(start_min=self.eat_breakfast_start_mean_min, \
                                  start_max=self.eat_breakfast_start_mean_max, \
                                  dt_min=self.eat_breakfast_dt_mean_min, \
                                  dt_max=self.eat_breakfast_dt_mean_max)

        # maximum standard deviation for end time
        self.eat_breakfast_end_std_max  = 1

        #
        # commute from work
        #

        # minimum mean duration
        self.commute_from_work_dt_mean_min  = self.commute_to_work_dt_mean_min

        # maximum mean duration
        self.commute_from_work_dt_mean_max  = self.commute_to_work_dt_mean_max

        # maximum standard deviation for duration
        self.commute_from_work_dt_std_max   = self.commute_to_work_dt_std_max

        # minimum mean start time
        self.commute_from_work_start_mean_min   = 15

        # maximum mean start time
        self.commute_from_work_start_mean_max   = 22

        # maximum standard deviation for start time
        self.commute_from_work_start_std_max    = self.commute_to_work_start_std_max

        # minimum mean end time, maximum mean end time
        self.commute_from_work_end_mean_min, self.commute_from_work_end_mean_max \
            = self.set_end_bounds(start_min=self.commute_from_work_start_mean_min, \
                                  start_max=self.commute_from_work_start_mean_max, \
                                  dt_min=self.commute_from_work_dt_mean_min,\
                                  dt_max=self.commute_from_work_dt_mean_max)

        # maximum standard deviation for end time
        self.commute_from_work_end_std_max      = 1

        #
        # sleep
        #

        #  minimum mean start time. the time is in periodic hours [-12, 12]
        self.sleep_start_mean_min   = -3

        # maximum mean start time
        self.sleep_start_mean_max   = 3

        # maximum standard deviation for start time
        self.sleep_start_std_max    = 1

        #  minimum mean end time
        self.sleep_end_mean_min     = 5

        # maximum mean end time
        self.sleep_end_mean_max     = 10

        # maximum standard deviation for end time
        self.sleep_end_std_max      = 1

        # minimum mean duration, maximum mean duration
        self.sleep_dt_mean_min, self.sleep_dt_mean_max = \
            self.set_dt_bounds(start_min=self.sleep_start_mean_min, start_max=self.sleep_start_mean_max, \
                               end_min=self.sleep_end_mean_min, end_max=self.sleep_end_mean_max)

        #  minimum mean duration
        self.sleep_dt_mean_min      = 4

        # maximum standard deviation for duration
        self.sleep_dt_std_max       = 1

        #
        # eat lunch
        #

        #  minimum mean duration
        self.eat_lunch_dt_mean_min  = 5 / 60

        # maximum mean duration
        self.eat_lunch_dt_mean_max  = 1

        # maximum standard deviation for duration
        self.eat_lunch_dt_std_max   = 1

        #  minimum mean start time
        self.eat_lunch_start_mean_min   = 11.5

        # maximum mean start time
        self.eat_lunch_start_mean_max   = 15.5

        # maximum standard deviation for start time
        self.eat_lunch_start_std_max    = 1

        #  minimum mean end time, maximum mean end time
        self.eat_lunch_end_mean_min, self.eat_lunch_end_mean_max \
            = self.set_end_bounds(start_min=self.eat_lunch_start_mean_min, start_max=self.eat_lunch_start_mean_max, \
                                 dt_min=self.eat_lunch_dt_mean_min, dt_max=self.eat_lunch_dt_mean_max)

        # maximum standard deviation for end time
        self.eat_lunch_end_std_max       = 1

        #
        # eat dinner
        #

        #  minimum mean duration
        self.eat_dinner_dt_mean_min     = 5 / 60

        # maximum mean duration
        self.eat_dinner_dt_mean_max     = 1

        # maximum standard deviation for duration
        self.eat_dinner_dt_std_max      = 1

        #  minimum mean start time
        self.eat_dinner_start_mean_min  = 17

        # maximum mean start time
        self.eat_dinner_start_mean_max  = 21.5

        # maximum standard deviation for start time
        self.eat_dinner_start_std_max   = 1

        #  minimum mean end time, maximum mean end time
        self.eat_dinner_end_mean_min, self.eat_dinner_end_mean_max \
            = self.set_end_bounds(start_min=self.eat_dinner_start_mean_min, start_max=self.eat_dinner_start_mean_max, \
                                  dt_min=self.eat_dinner_dt_mean_min, dt_max=self.eat_dinner_dt_mean_max)

        # maximum standard deviation for end time
        self.eat_dinner_end_std_max     = 1

        return

    def set_dt_bounds(self, start_min, start_max, end_min, end_max):

        """
        This function calculates the bounds for duration time [expressed in hours}

        :param float start_min: the minimum start time [hours]
        :param float start_max: the maximum start time [hours]
        :param float end_min: the minimum end time [hours]
        :param float end_max: the maximum end time [hours]


        :return: the minimum duration, the maximum duration
        :rtype: float, float
        """

        dt_min  = end_min - start_max
        dt_max  = end_max - start_min

        return dt_min, dt_max

    def set_end_bounds(self, start_min, start_max, dt_min, dt_max):

        """
        This function calculates the bounds for end time [expressed in hours]

        :param float start_min: the minimum start time [hours]
        :param float start_max: the maximum start time [hours]
        :param float dt_min: the minimum duration [hours]
        :param float dt_max: the maximum duration [hours]

        :return: the minimum end time, the maximum end time
        :rtype: float, float
        """

        end_min     = start_min + dt_min
        end_max     = start_max + dt_max

        return end_min, end_max

