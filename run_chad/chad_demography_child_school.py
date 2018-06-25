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
data for the school-age children demographic.

This module contains :class:`chad_demography_child_school.CHAD_demography_child_school`.
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
# class CHAD_demography_child_school
# ===========================================

class CHAD_demography_child_school(chad_demography.CHAD_demography):

    """
    This class contains the common functionality with accessing the CHAD data files
    relevant to school-age children demographic.

    :var keys: the ABMHAP activity codes for the activities simulated by the school-age children demographic
    :type keys: list of int
    :var dict fname_stats: for a given ABMHAP activity code, access the file names for CHAD longitudinal data for \
    the respective activity

    :var chad_params.CHAD_params commute_to_work: sampling parameters for the commuting to work activity within CHAD
    :var chad_params.CHAD_params commute_from_work: sampling parameters for commuting from work activity within CHAD
    :var chad_params.CHAD_params 'work': sampling parameters for schooling activity within CHAD
    :var chad_params.CHAD_params eat_breakfast: sampling parameters for the eating breakfast activity within CHAD
    :var chad_params.CHAD_params eat_dinner: sampling parameters for the eating dinner activity within CHAD
    :var chad_params.CHAD_params eat_lunch: sampling parameters for the eating lunch activity within CHAD
    :var chad_params.CHAD_params 'sleep': CHAD sampling parameters for the sleep activity within CHAD
    :var dict int_2_param: for a given activity code, choose the proper sampling parameters for the respective activity
    """

    def __init__(self):

        # use the parent-class constructor
        chad_demography.CHAD_demography.__init__(self, dmg.CHILD_SCHOOL)

        # the behaviors for the given demographic
        self.keys = [mg.KEY_COMMUTE_TO_WORK, mg.KEY_COMMUTE_FROM_WORK, mg.KEY_EAT_BREAKFAST, mg.KEY_EAT_LUNCH, \
                     mg.KEY_EAT_DINNER, mg.KEY_SLEEP, mg.KEY_WORK]

        #
        # the following data is read from the .zip files for the activities for the respective demographics
        #
        self.fname_stats = {mg.KEY_COMMUTE_FROM_WORK: self.fname_stats_commute_from_work,
                            mg.KEY_COMMUTE_TO_WORK: self.fname_stats_commute_to_work,
                            mg.KEY_EAT_BREAKFAST: self.fname_stats_eat_breakfast,
                            mg.KEY_EAT_DINNER: self.fname_stats_eat_dinner,
                            mg.KEY_EAT_LUNCH: self.fname_stats_eat_lunch,
                            mg.KEY_SLEEP: self.fname_stats_sleep,
                            mg.KEY_WORK: self.fname_stats_school,
                            }
        #
        # the CHAD parameters that limit sampling of the CHAD data
        #

        # parameters for commuting to work
        self.commute_to_work = cp.CHAD_params(dt_mean_min=self.commute_to_work_dt_mean_min, \
                                              dt_mean_max=self.commute_to_work_dt_mean_max, \
                                              dt_std_max=self.commute_to_work_dt_std_max, \
                                              start_mean_min=self.commute_to_work_start_mean_min, \
                                              start_mean_max=self.commute_to_work_start_mean_max, \
                                              start_std_max=self.commute_to_work_dt_std_max, \
                                              end_mean_min=self.commute_to_work_end_mean_min,\
                                              end_mean_max=self.commute_to_work_end_mean_max,\
                                              end_std_max=self.commute_to_work_end_std_max, \
                                              N=self.n_commute_to_work, do_dt=True, do_start=True, do_end=True)

        # default parameters for commuting from work
        self.commute_from_work = cp.CHAD_params(dt_mean_min=self.commute_from_work_dt_mean_min, \
                                                dt_mean_max=self.commute_from_work_dt_mean_max, \
                                                dt_std_max=self.commute_from_work_dt_std_max, \
                                                start_mean_min=self.commute_from_work_start_mean_min, \
                                                start_mean_max=self.commute_from_work_start_mean_max, \
                                                start_std_max=self.commute_from_work_start_std_max, \
                                                end_mean_min=self.commute_from_work_end_mean_min,\
                                                end_mean_max=self.commute_from_work_end_mean_max,\
                                                end_std_max=self.commute_from_work_end_std_max,\
                                                N=self.n_commute_from_work, do_dt=True, do_start=True, do_end=True)

        # default parameters for eating breakfast
        self.eat_breakfast = cp.CHAD_params(dt_mean_min=self.eat_breakfast_dt_mean_min, \
                                            dt_mean_max=self.eat_breakfast_dt_mean_max, \
                                            dt_std_max=self.eat_breakfast_dt_std_max, \
                                            start_mean_min=self.eat_breakfast_start_mean_min, \
                                            start_mean_max=self.eat_breakfast_start_mean_max, \
                                            start_std_max=self.eat_breakfast_start_std_max,\
                                            end_mean_min=self.eat_breakfast_end_mean_min,\
                                            end_mean_max=self.eat_breakfast_end_mean_max,\
                                            end_std_max=self.eat_breakfast_end_std_max,\
                                            N=self.n_eat_breakfast, do_dt=True, do_start=True, do_end=True)

        # default parameters for eating dinner
        self.eat_dinner = cp.CHAD_params(dt_mean_min=self.eat_dinner_dt_mean_min, \
                                         dt_mean_max=self.eat_dinner_dt_mean_max, \
                                         dt_std_max=self.eat_dinner_dt_mean_max, \
                                         start_mean_min=self.eat_dinner_start_mean_min, \
                                         start_mean_max=self.eat_dinner_start_mean_max, \
                                         start_std_max=self.eat_dinner_start_mean_max, \
                                         end_mean_min=self.eat_dinner_end_mean_min,\
                                         end_mean_max=self.eat_dinner_end_mean_max,\
                                         end_std_max=self.eat_dinner_end_std_max,\
                                         N=self.n_eat_dinner, do_dt=True, do_start=True, do_end=True)

        # default parameters for eating lunch
        self.eat_lunch = cp.CHAD_params(dt_mean_min=self.eat_lunch_dt_mean_min, \
                                        dt_mean_max=self.eat_lunch_dt_mean_max,
                                        dt_std_max=self.eat_lunch_dt_std_max, \
                                        start_mean_min=self.eat_lunch_start_mean_min, \
                                        start_mean_max=self.eat_lunch_start_mean_max, \
                                        start_std_max=self.eat_lunch_start_std_max, \
                                        end_mean_min=self.eat_lunch_end_mean_min,\
                                        end_mean_max=self.eat_lunch_end_mean_max,\
                                        end_std_max=self.eat_lunch_end_std_max,\
                                        N=self.n_eat_lunch, do_dt=True, do_start=True, do_end=True)

        # default parameters for sampling sleep data
        self.sleep = cp.CHAD_params(start_mean_min=self.sleep_start_mean_min, \
                                    start_mean_max=self.sleep_start_mean_max, \
                                    start_std_max=self.sleep_start_std_max,
                                    end_mean_min=self.sleep_end_mean_min, \
                                    end_mean_max=self.sleep_end_mean_max, \
                                    end_std_max=self.sleep_end_std_max, \
                                    dt_mean_min=self.sleep_dt_mean_min, \
                                    dt_mean_max=self.sleep_dt_mean_max,\
                                    dt_std_max=self.sleep_dt_std_max,\
                                    N=self.n_sleep, do_start=True, do_end=True, do_dt=True)

        #
        # adjust the sampling parameters for school behavior
        #

        # the minimum mean duration, the maximum mean duration
        self.school_dt_mean_min, self.school_dt_mean_max \
            = self.set_dt_bounds(start_min=self.school_start_mean_min, start_max=self.school_start_mean_max,\
                                 end_min=self.school_end_mean_min, end_max=self.school_end_mean_max)

        # the maximum standard deviation of duration
        self.school_dt_std_max = 1.0

        # default parameters for sampling schooling data
        self.work = cp.CHAD_params(start_mean_min=self.school_start_mean_min, \
                                   start_mean_max=self.school_start_mean_max, \
                                   start_std_max=self.school_start_std_max, \
                                   end_mean_min=self.school_end_mean_min, \
                                   end_mean_max=self.school_end_mean_max, \
                                   end_std_max=self.school_end_std_max, \
                                   dt_mean_min=self.school_dt_mean_min, \
                                   dt_mean_max=self.school_dt_mean_max, \
                                   dt_std_max=self.school_dt_std_max, N=self.n_school, \
                                   do_start=True, do_end=True, do_dt=True)

        # given an activity code, access the corresponding parameters used in sampling
        # the CHAD data
        self.int_2_param   = {mg.KEY_COMMUTE_FROM_WORK: self.commute_from_work,
                              mg.KEY_COMMUTE_TO_WORK: self.commute_to_work,
                              mg.KEY_EAT_BREAKFAST: self.eat_breakfast,
                              mg.KEY_EAT_DINNER: self.eat_dinner,
                              mg.KEY_EAT_LUNCH: self.eat_lunch,
                              mg.KEY_SLEEP: self.sleep,
                              mg.KEY_WORK: self.work,}



        return