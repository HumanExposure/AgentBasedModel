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
data for the pre-school children demographic.

This module contains :class:`chad_demography_child_young.CHAD_demography_child_young`.
"""

# ===========================================
# import
# ===========================================
import sys
sys.path.append('..\\source')
sys.path.append('..\\processing')

# ABMHAP modules
import my_globals as mg
import chad_params as cp
import demography as dmg
import chad_demography


# ===========================================
# class CHAD_demography_child_young
# ===========================================

class CHAD_demography_child_young(chad_demography.CHAD_demography):

    """
    This class contains the common functionality with accessing the CHAD data files
    relevant to preschool chidlren  demographic.

    :var keys: the ABMHAP activity codes for the activities simulated by the preschool children demographic
    :type keys: list of int
    :var dict fname_stats: for a given ABMHAP activity code, access the file names for CHAD longitudinal data for \
    the respective activity

    :var chad_params.CHAD_params eat_breakfast: sampling parameters for the eating breakfast activity within CHAD
    :var chad_params.CHAD_params eat_dinner: sampling parameters for the eating dinner activity within CHAD
    :var chad_params.CHAD_params eat_lunch: sampling parameters for the eating lunch activity within CHAD
    :var chad_params.CHAD_params 'sleep': CHAD sampling parameters for the sleep activity within CHAD
    :var dict int_2_param: for a given activity code, choose the proper sampling parameters for the respective activity
    """

    def __init__(self):

        # use the parent-class constructor
        chad_demography.CHAD_demography.__init__(self, dmg.CHILD_YOUNG)

        # the behaviors for the given demographic
        self.keys = [mg.KEY_EAT_BREAKFAST, mg.KEY_EAT_LUNCH, mg.KEY_EAT_DINNER, mg.KEY_SLEEP]

        #
        # some CHAD sampling parameters
        #
        # default parameters for sampling sleep data

        #  minimum mean start time. the time is in periodic hours [-12, 12]
        self.sleep_start_mean_min   = -5

        #  maximum mean start time. the time is in periodic hours [-12, 12]
        self.sleep_start_mean_max   = -2

        #  minimum mean end time
        self.sleep_end_mean_min     = 5

        # maximum mean end time
        self.sleep_end_mean_max     = 9

        # number of entries needed for the sleep activity to be considered "longitudinal"
        # i.e. there were next to no longitudinal entries within CHAD
        self.n_sleep                = 1

        # the maximum mean start time for eating breakfast
        self.eat_breakfast_start_mean_max   = 9.5

        #
        # the following data is read from the .zip files for the activities for the respective demographics
        #
        #
        # the following data is read from the .zip files for the activities for the respective demographics
        # the non-working adults had NO longitudinal data

        self.fname_stats_sleep = {chad_demography.START: 'solo/sleep/all/stats_start.csv',
                                  chad_demography.END: 'solo/sleep/all/stats_end.csv',
                                  chad_demography.DT: 'solo/sleep/all/stats_dt.csv',
                                  chad_demography.RECORD: 'solo/sleep/all/record.csv', }

        self.fname_stats = {mg.KEY_EAT_BREAKFAST: self.fname_stats_eat_breakfast,
                            mg.KEY_EAT_DINNER: self.fname_stats_eat_dinner,
                            mg.KEY_EAT_LUNCH: self.fname_stats_eat_lunch,
                            mg.KEY_SLEEP: self.fname_stats_sleep,
                            }
        #
        # the CHAD parameters that limit sampling of the CHAD data
        #


        # parameters for commuting to work

        # default parameters for eating breakfast
        self.eat_breakfast      = cp.CHAD_params(dt_mean_min=self.eat_breakfast_dt_mean_min, \
                                                 dt_mean_max=self.eat_breakfast_dt_mean_max, \
                                                 dt_std_max=self.eat_breakfast_dt_std_max, \
                                                 start_mean_min=self.eat_breakfast_start_mean_min, \
                                                 start_mean_max=self.eat_breakfast_start_mean_max, \
                                                 start_std_max=self.eat_breakfast_start_std_max,
                                                 end_mean_min=self.eat_breakfast_end_mean_min, \
                                                 end_mean_max=self.eat_breakfast_end_mean_max, \
                                                 end_std_max=self.eat_breakfast_end_std_max, \
                                                 N=self.n_eat_breakfast, do_dt=True, do_start=True, do_end=True)

        # default parameters for eating dinner
        self.eat_dinner         = cp.CHAD_params(dt_mean_min=self.eat_dinner_dt_mean_min, \
                                                 dt_mean_max=self.eat_dinner_dt_mean_max, \
                                                 dt_std_max=self.eat_dinner_dt_mean_max, \
                                                 start_mean_min=self.eat_dinner_start_mean_min, \
                                                 start_mean_max=self.eat_dinner_start_mean_max, \
                                                 start_std_max=self.eat_dinner_start_mean_max, \
                                                 end_mean_min=self.eat_dinner_end_mean_min, \
                                                 end_mean_max=self.eat_dinner_end_mean_max, \
                                                 end_std_max=self.eat_dinner_end_std_max, \
                                                 N=self.n_eat_dinner, do_dt=True, do_start=True, do_end=True)

        # default parameters for eating lunch
        self.eat_lunch          = cp.CHAD_params(dt_mean_min=self.eat_lunch_dt_mean_min, \
                                                 dt_mean_max=self.eat_lunch_dt_mean_max,
                                                 dt_std_max=self.eat_lunch_dt_std_max, \
                                                 start_mean_min=self.eat_lunch_start_mean_min, \
                                                 start_mean_max=self.eat_lunch_start_mean_max, \
                                                 start_std_max=self.eat_lunch_start_std_max, \
                                                 end_mean_min=self.eat_lunch_end_mean_min, \
                                                 end_mean_max=self.eat_lunch_end_mean_max, \
                                                 end_std_max=self.eat_lunch_end_std_max, \
                                                 N=self.n_eat_lunch, do_dt=True, do_start=True, do_end=True)

        # default parameters for sampling sleeping
        self.sleep              = cp.CHAD_params(start_mean_min=self.sleep_start_mean_min, \
                                                 start_mean_max=self.sleep_start_mean_max, \
                                                 start_std_max=self.sleep_start_std_max,
                                                 end_mean_min=self.sleep_end_mean_min, \
                                                 end_mean_max=self.sleep_end_mean_max, \
                                                 end_std_max=self.sleep_end_std_max, N=self.n_sleep, \
                                                 dt_mean_min=self.sleep_dt_mean_min, \
                                                 dt_mean_max=self.sleep_dt_mean_max, \
                                                 dt_std_max=self.sleep_dt_std_max, \
                                                 do_start=True, do_end=True, do_dt=True)

        # given an activity code, access the corresponding parameters used in sampling
        # the CHAD data
        self.int_2_param   = {mg.KEY_EAT_BREAKFAST: self.eat_breakfast,
                              mg.KEY_EAT_DINNER: self.eat_dinner,
                              mg.KEY_EAT_LUNCH: self.eat_lunch,
                              mg.KEY_SLEEP: self.sleep,
                              }

        return