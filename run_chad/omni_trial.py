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
This is the module that is in charge of running simulations comparing the Agent-Based Model of \
Human Activity Patterns (ABMHAP) with the data from the Consolidated Human Activity Database (CHAD) \
comparing the performance of ABMHAP with all of the activity data.

This module contains class :class:`omni_trial.Omni_Trial`.
"""

# ===========================================
# import
# ===========================================

import sys
sys.path.append('..\\source')
sys.path.append('..\\processing')

# mathematical capability
import numpy as np

# ABMHAP modules
import my_globals as mg
import chad_demography_adult_non_work as cdanw
import chad_demography_adult_work as cdaw
import chad_demography_child_school as cdcs
import chad_demography_child_young as cdcy
import demography as dmg

import meal, occupation, temporal, trial

# ===========================================
# constants
# ===========================================

# the start time for the simulation
# Sunday, Day 0 at 16:00
T_START = (temporal.SUNDAY * temporal.DAY_2_MIN) + 16 * temporal.HOUR_2_MIN

# ===========================================
# class Omni_Trial
# ===========================================
class Omni_Trial(trial.Trial):

    """
    This class runs the ABMHAP simulations initialized with all of the activity data from CHAD for \
    a given demographic. For the respective demographic, the following activity-data from CHAD \
    are used:

        * commute from work
        * commute to work
        * eat breakfast
        * eat dinner
        * eat lunch
        * sleep
        * work

    :param params.Params params: the parameters that describe the household:
    :param sampling_parameters: maps an activity code to the sampling parameters \
    to the CHAD data for the respective activity
    :type sampling_parameters: dict of activity code - :class:`chad_params.CHAD_params`
    :param int demographic: the demographic identifier
    """

    def __init__(self, parameters, sampling_params, demographic):

        # constructor
        trial.Trial.__init__(self, parameters, sampling_params, demographic)

        # the trial identifier
        self.id = trial.OMNI

        return

    def adjust_commute_from_work(self, data, no_variation=False):

        """
        This function adjusts the household parameters to reflect the sampled parameters \
        (mean and standard deviation of start time, end time, and \
        duration, respectively), from the CHAD data for the commuting from work \
        activity.

        :param data: relevant parameters for each person in the household for \
        commuting from work. The tuple contains the following: mean start time, standard \
        deviation of start time, mean end time, standard deviation of end time, mean duration, \
        and standard deviation of duration for each person in the household.
        :type data: tuple of numpy.ndarray, numpy.ndarray, numpy.ndarray, \
        numpy.ndarray, numpy.ndarray, numpy.ndarray
        :param bool no_variation: whether (if True) or not (if False) intra-individual \
        variation is set to zero among the activities

        :return:
        """

        # the activity-related parameters (in hours)
        start_mean, start_std, end_mean, end_std, dt_mean, dt_std = data

        # set standard deviation to zero
        if no_variation:
            dt_std[:]   = 0

        # set the commuting from work mean duration (in minutes)
        self.params.commute_from_work_dt_mean = mg.hours_to_minutes(dt_mean)

        # set the commuting from work standard deviation for duration (in minutes)
        self.params.commute_from_work_dt_std  = mg.hours_to_minutes(dt_std)

        return

    def adjust_commute_to_work(self, data, no_variation=False):

        """
        This function adjusts the household parameters to reflect the sampled parameters \
        (mean and standard deviation of start time, end time, and \
        duration, respectively), from the CHAD data for the commuting to work \
        activity.

        :param data: relevant parameters for each person in the household for \
        commuting to work. The tuple contains the following: mean start time, standard \
        deviation of start time, mean end time, standard deviation of end time, mean duration, \
        and standard deviation of duration for each person in the household.
        :type data: tuple of numpy.ndarray, numpy.ndarray, numpy.ndarray, \
        numpy.ndarray, numpy.ndarray, numpy.ndarray
        :param bool no_variation: whether (if True) or not (if False) intra-individual \
        variation is set to zero among the activities

        :return:
        """

        # the activity-related parameters (in hours)
        start_mean, start_std, end_mean, end_std, dt_mean, dt_std = data

        # set standard deviation to zero
        if no_variation:
            dt_std[:] = 0

        # set the commuting to work mean duration (in minutes)
        self.params.commute_to_work_dt_mean = mg.hours_to_minutes(dt_mean)

        # set the commuting to work standard deviation for duration (in minutes)
        self.params.commute_to_work_dt_std  = mg.hours_to_minutes(dt_std)

        return

    def adjust_eat_breakfast(self, data, no_variation=False):

        """
        This function adjusts the household parameters to reflect the sampled parameters \
        (mean and standard deviation of start time, end time, and \
        duration, respectively), from the CHAD data for the eating breakfast \
        activity.

        :param data: relevant parameters for each person in the household for \
        eating breakfast. The tuple contains the following: mean start time, standard \
        deviation of start time, mean end time, standard deviation of end time, mean duration, \
        and standard deviation of duration for each person in the household.
        :type data: tuple of numpy.ndarray, numpy.ndarray, numpy.ndarray, \
        numpy.ndarray, numpy.ndarray, numpy.ndarray
        :param bool no_variation: whether (if True) or not (if False) intra-individual \
        variation is set to zero among the activities

        :return:
        """

        # t_start(commute to work) = t_start(work) - dt(commute to work)
        # t_start(eat breakfast)   = t_start(work) - dt(commute to work) - dt(eat breakfast)

        # the amount of minutes in 1 hour
        HOUR_2_MIN = temporal.HOUR_2_MIN

        # the activity-related parameters (in hours)
        start_mean, start_std, end_mean, end_std, dt_mean, dt_std = data

        # set the standard deviations to zero (time in hours)
        if no_variation:
            dt_std[:]       = 0
            start_std[:]    = 0

        # number of standard deviations for start time probability distribution
        start_trunc = meal.BREAKFAST_START_TRUNC * np.ones(start_mean.shape)

        # number of standard deviations for duration probability distribution
        dt_trunc    = meal.BREAKFAST_DT_TRUNC * np.ones(dt_mean.shape)

        #
        # for the demographics that commute, set the appropriate parameters
        #
        if self.demographic in [dmg.ADULT_WORK, dmg.CHILD_SCHOOL]:

            # commute start time converted to hours
            # t_start(commute to work) = t_start(work) - dt(commute to work)
            commute_start   = (self.params.work_start_mean - self.params.commute_to_work_dt_mean)/ HOUR_2_MIN % 24

            # the breakfast start time is the commute start time - breakfast duration
            # make sure that the time is in time of day
            start_mean      = (commute_start - dt_mean) % 24

        # this converts time from hours to minutes
        f = mg.hours_to_minutes

        # set up the breakfast for each person in the household
        self.params.breakfasts = \
            self.params.init_meal(meal.BREAKFAST, start_mean=f(start_mean), start_std=f(start_std), \
                                  start_trunc=start_trunc, dt_mean=f(dt_mean), dt_std=f(dt_std), \
                                  dt_trunc=dt_trunc)

        return

    def adjust_eat_dinner(self, data, no_variation=False):

        """
        This function adjusts the household parameters to reflect the sampled parameters \
        (mean and standard deviation of start time, end time, and \
        duration, respectively), from the CHAD data for the eating dinner \
        activity.

        :param data: relevant parameters for each person in the household for \
        eating dinner. The tuple contains the following: mean start time, standard \
        deviation of start time, mean end time, standard deviation of end time, mean duration, \
        and standard deviation of duration for each person in the household.
        :type data: tuple of numpy.ndarray, numpy.ndarray, numpy.ndarray, \
        numpy.ndarray, numpy.ndarray, numpy.ndarray
        :param bool no_variation: whether (if True) or not (if False) intra-individual \
        variation is set to zero among the activities

        :return:
        """

        # the activity-related parameters (in hours)
        start_mean, start_std, end_mean, end_std, dt_mean, dt_std = data

        # set the standard deviations to zero
        if no_variation:
            dt_std[:]       = 0
            start_std[:]    = 0

        # number of standard deviations for start time probability distributions
        start_trunc = meal.DINNER_START_TRUNC * np.ones(start_mean.shape)

        # number of standard deviations for duration probability distribution
        dt_trunc    = meal.DINNER_DT_TRUNC * np.ones(dt_mean.shape)

        # this converts time from hours to minutes
        f = mg.hours_to_minutes

        # set up the dinner for each person in the household
        self.params.dinners = \
            self.params.init_meal(meal.DINNER, start_mean=f(start_mean), start_std=f(start_std), \
                                  start_trunc=start_trunc, dt_mean=f(dt_mean), dt_std=f(dt_std), \
                                  dt_trunc=dt_trunc)

        return

    def adjust_eat_lunch(self, data, no_variation=False):

        """
        This function adjusts the household parameters to reflect the sampled parameters \
        (mean and standard deviation of start time, end time, and \
        duration, respectively), from the CHAD data for the eating lunch \
        activity.

        :param data: relevant parameters for each person in the household for \
        eating lunch. The tuple contains the following: mean start time, standard \
        deviation of start time, mean end time, standard deviation of end time, mean duration, \
        and standard deviation of duration for each person in the household.
        :type data: tuple of numpy.ndarray, numpy.ndarray, numpy.ndarray, \
        numpy.ndarray, numpy.ndarray, numpy.ndarray
        :param bool no_variation: whether (if True) or not (if False) intra-individual \
        variation is set to zero among the activities

        :return:
        """

        # the activity-related parameters (in hours)
        start_mean, start_std, end_mean, end_std, dt_mean, dt_std = data

        # set the standard deviations to zero
        if no_variation:
            dt_std[:]       = 0
            start_std[:]    = 0

        # number of standard deviations for start time probability distributions
        start_trunc = meal.LUNCH_START_TRUNC * np.ones(start_mean.shape)

        # number of standard deviations for duration probability distributions
        dt_trunc    = meal.LUNCH_DT_TRUNC * np.ones(dt_mean.shape)

        # this converts time from hours to minutes
        f = mg.hours_to_minutes

        # set up the lunch for each person in the household
        self.params.lunches = \
            self.params.init_meal(meal.LUNCH, start_mean=f(start_mean), start_std=f(start_std), \
                                  start_trunc=start_trunc,  dt_mean=f(dt_mean), dt_std=f(dt_std), \
                                  dt_trunc=dt_trunc)
        return

    def adjust_params(self, x):

        """
        This function adjusts the household parameters to reflect the sampled parameters \
        (mean and standard deviation of start time, end time, and \
        duration, respectively), from the CHAD data for simulating the respective demographic \
        in ABMHAP.

        :param x: maps an activity code to the parameterizing CHAD data for each activity, \
        respectively. The CHAD data are the mean and standard deviation of the start time, end time, \
        and duration.
        :type x: dict that maps int to a tuple: numpy.ndarray, numpy.ndarray, numpy.ndarray, \
        numpy.ndarray, numpy.ndarray, numpy.ndarray

        :return:
        """

        # flag indicating whether (if True) or not (if False) there should be
        # no intra-individual variation in the simulation
        no_variation = False

        # adjust parameters for simulating working adults
        if self.demographic == dmg.ADULT_WORK:
            self.adjust_params_adult_work(x, no_variation)

        # adjust parameters for simulating non-working adults
        elif self.demographic == dmg.ADULT_NON_WORK:
            self.adjust_params_adult_non_work(x, no_variation)

        # adjust parameters for simulating school-age children
        elif self.demographic == dmg.CHILD_SCHOOL:
            self.adjust_params_child_school(x, no_variation)

        # adjust parameters for simulating preschool children
        elif self.demographic == dmg.CHILD_YOUNG:
            self.adjust_params_child_young(x, no_variation)

        return

    def adjust_params_adult_non_work(self, x, no_variation=False):

        """
        For the non-working adult demographic, this function adjusts the \
        household parameters to reflect the sampled \
        parameters (mean and standard deviation of the activity start time, end \
        time, and duration, respectively, for the following activities:

        #. eat breakfast
        #. eat lunch
        #. eat dinner
        #. sleep

        :param x: maps an activity code to the parameterizing CHAD data for each activity, \
        respectively. The CHAD data are the mean and standard deviation of the start time, end time, \
        and duration.
        :type x: dict that maps int to a tuple: numpy.ndarray, numpy.ndarray, numpy.ndarray, \
        numpy.ndarray, numpy.ndarray, numpy.ndarray
        :param bool no_variation: off or on intra-individual variation among the activities

        :return:
        """

        # set the time relevant parameters for the runs
        # it is better to start on a Sunday because there are fewer activities. It is easier to initialize the
        # simulations.
        self.params.t_start = T_START

        #
        # need to set eat breakfast activity before sleep activity
        #

        # set the eat breakfast activity
        self.adjust_eat_breakfast(x[mg.KEY_EAT_BREAKFAST], no_variation)

        # set the sleep activity
        self.adjust_sleep(x[mg.KEY_SLEEP], no_variation)

        #
        # order does not matter
        #

        # set the eat lunch activity
        self.adjust_eat_lunch(x[mg.KEY_EAT_LUNCH], no_variation)

        # set the eat dinner activity
        self.adjust_eat_dinner(x[mg.KEY_EAT_DINNER], no_variation)

        # set the occupation to be employed
        self.params.job_id = (occupation.NO_JOB,) * self.params.num_people

        return

    def adjust_params_adult_work(self, x, no_variation=False):

        """
        For the working adult demographic, this function adjusts the \
        household parameters to reflect the sampled \
        parameters (mean and standard deviation of the activity start time, end \
        time, and duration, respectively, for the following activities:

        #. sleep
        #. eat breakfast
        #. eat lunch
        #. eat dinner
        #. commute to work
        #. commute from work
        #. work

        :param x: maps an activity code to the parameterizing CHAD data for each activity, \
        respectively. The CHAD data are the mean and standard deviation of the start time, end time, \
        and duration.
        :type x: dict that maps int to a tuple: numpy.ndarray, numpy.ndarray, numpy.ndarray, \
        numpy.ndarray, numpy.ndarray, numpy.ndarray
        :param bool no_variation: off or on intra-individual variation among the activities

        :return:
        """

        #
        # parameterizing order matters
        #

        # set the time relevant parameters for the runs
        # it is better to start on a Sunday because there are fewer activities. It is easier to initialize the
        # simulations.
        self.params.t_start =  T_START

        # adjust work parameters
        # t_start(work)
        self.adjust_work( x[mg.KEY_WORK], no_variation )

        # adjust commuting to work parameters
        # t_start(commute to work) = t_start(work) - dt(commute to work)
        self.adjust_commute_to_work( x[mg.KEY_COMMUTE_TO_WORK], no_variation )

        # adjust eating breakfast parameters
        # t_start(eat breakfast) = t_start(work) - dt(commute to work) - dt(eat breakfast)
        self.adjust_eat_breakfast( x[mg.KEY_EAT_BREAKFAST], no_variation )

        # adjust sleeping parameters
        # t_end(sleep) = t_start(work) - dt(commute to work) - dt(eat breakfast)
        self.adjust_sleep( x[mg.KEY_SLEEP], no_variation )

        #
        # parameterizing order does not matter
        #
        # set the eat lunch parameters
        self.adjust_eat_lunch( x[mg.KEY_EAT_LUNCH], no_variation )

        # set the eat dinner parameters
        self.adjust_eat_dinner( x[mg.KEY_EAT_DINNER], no_variation )

        # set the commute from work parameters
        self.adjust_commute_from_work( x[mg.KEY_COMMUTE_FROM_WORK], no_variation )

        return

    def adjust_params_child_school(self, x, no_variation=False):

        """
        For the school-age children demographic, this function adjusts the \
        household parameters to reflect the sampled \
        parameters (mean and standard deviation of the activity start time, end \
        time, and duration, respectively, for the following activities:

        #. sleep
        #. eat breakfast
        #. eat lunch
        #. eat dinner
        #. commute To work
        #. commute From work
        #. work

        :param x: maps an activity code to the parameterizing CHAD data for each activity, \
        respectively. The CHAD data are the mean and standard deviation of the start time, end time, \
        and duration.
        :type x: dict that maps int to a tuple: numpy.ndarray, numpy.ndarray, numpy.ndarray, \
        numpy.ndarray, numpy.ndarray, numpy.ndarray
        :param bool no_variation: off or on intra-individual variation among the activities

        :return:
        """

        # adjust the parameters
        self.adjust_params_adult_work(x, no_variation)

        return

    def adjust_params_child_young(self, x, no_variation=False):

        """
        For the preschool children demographic, this function adjusts the \
        household parameters to reflect the sampled \
        parameters (mean and standard deviation of the activity start time, end \
        time, and duration, respectively, for the following activities:

        #. eat breakfast
        #. eat lunch
        #. eat dinner
        #. sleep

        :param x: maps an activity code to the parameterizing CHAD data for each activity, \
        respectively. The CHAD data are the mean and standard deviation of the start time, end time, \
        and duration.
        :type x: dict that maps int to a tuple: numpy.ndarray, numpy.ndarray, numpy.ndarray, \
        numpy.ndarray, numpy.ndarray, numpy.ndarray
        :param bool no_variation: off or on intra-individual variation among the activities

        :return:
        """

        # adjust the parameters
        self.adjust_params_adult_non_work(x, no_variation)

        return

    def adjust_sleep(self, data, no_variation=False):

        """
        This function adjusts the household parameters to reflect the sampled parameters \
        (mean and standard deviation of start time, end time, and \
        duration, respectively), from the CHAD data for the sleeping \
        activity.

        :param data: relevant parameters for each person in the household for \
        sleeping. The tuple contains the following: mean start time, standard \
        deviation of start time, mean end time, standard deviation of end time, mean duration, \
        and standard deviation of duration for each person in the household.
        :type data: tuple of numpy.ndarray, numpy.ndarray, numpy.ndarray, \
        numpy.ndarray, numpy.ndarray, numpy.ndarray
        :param bool no_variation: whether (if True) or not (if False) intra-individual \
        variation is set to zero among the activities

        :return:
        """

        # the amount of minutes in 1 hour
        HOUR_2_MIN = temporal.HOUR_2_MIN

        # the activity-related parameters (in hours)
        start_mean, start_std, end_mean, end_std, dt_mean, dt_std = data

        # set the standard deviations to zero (time is in hours)
        if no_variation:
            start_std[:]    = 0
            end_std[:]      = 0

        # since the start time may occur over midnight, express time as [-12, 12)
        start_mean  = mg.from_periodic(start_mean)

        # for the demographics with a "work" or "school" occupation
        # set the sleep end time to the breakfast start time
        if self.demographic in [dmg.ADULT_WORK, dmg.CHILD_SCHOOL]:

            # breakfast start time in HOURS [0, 24)
            bf_start    = np.array( [ x.t_start for x in self.params.breakfasts] ) / HOUR_2_MIN

            # sleep end time is the breakfast start time
            # make sure time is in [0, 24) format
            end_mean    = bf_start

        # set the mean start time (in minutes)
        self.params.sleep_start_mean    = mg.hours_to_minutes(start_mean)

        # set the standard deviation of start time (in minutes)
        self.params.sleep_start_std     = mg.hours_to_minutes(start_std)

        # set the mean end time (in minutes)
        self.params.sleep_end_mean      = mg.hours_to_minutes(end_mean)

        # set the standard deviation of end time (in mintues)
        self.params.sleep_end_std       = mg.hours_to_minutes(end_std)

        return

    def adjust_work(self, data, no_variation=False):

        """
        This function adjusts the household parameters to reflect the sampled parameters \
        (mean and standard deviation of start time, end time, and \
        duration, respectively), from the CHAD data for the working \
        activity.

        :param data: relevant parameters for each person in the household for \
        working. The tuple contains the following: mean start time, standard \
        deviation of start time, mean end time, standard deviation of end time, mean duration, \
        and standard deviation of duration for each person in the household.
        :type data: tuple of numpy.ndarray, numpy.ndarray, numpy.ndarray, \
        numpy.ndarray, numpy.ndarray, numpy.ndarray
        :param bool no_variation: whether (if True) or not (if False) intra-individual \
        variation is set to zero among the activities

        :return:
        """

        # the activity-related parameters (in hours)
        start_mean, start_std, end_mean, end_std, dt_mean, dt_std = data

        # set the standard deviations to zero (time is in hours)
        if no_variation:
            start_std[:]    = 0
            end_std[:]      = 0

        # set the jobs for working adults
        if self.demographic == dmg.ADULT_WORK:
            job_id = occupation.STANDARD_JOB

        # set the jobs for school-age children
        elif self.demographic == dmg.CHILD_SCHOOL:
            job_id = occupation.STUDENT

        # set the job in the ABMHAP parameters
        self.params.job_id = ( job_id, ) * self.params.num_people

        # set the mean start time (in minutes)
        self.params.work_start_mean = mg.hours_to_minutes(start_mean)

        # set the standard deviation of start time (in minutes)
        self.params.work_start_std  = mg.hours_to_minutes(start_std)

        # set the mean end time (in minutes)
        self.params.work_end_mean   = mg.hours_to_minutes(end_mean)

        # set the standard deviation of end time (in minutes)
        self.params.work_end_std    = mg.hours_to_minutes(end_std)

        return

    def initialize(self):

        """
        This function initializes the parameters for the ABMHAP simulation based on the \
        CHAD data for the given demographic.

        :return:
        """

        # get the demographic information, given a demographic identifier
        chooser     = {dmg.ADULT_WORK: cdaw.CHAD_demography_adult_work(),
                       dmg.ADULT_NON_WORK: cdanw.CHAD_demography_adult_non_work(),
                       dmg.CHILD_SCHOOL: cdcs.CHAD_demography_child_school(),
                       dmg.CHILD_YOUNG: cdcy.CHAD_demography_child_young(),
                       }

        # the CHAD demographic
        chad_demo   = chooser[self.demographic]

        # initialize the trial for the given demographic
        y = super(Omni_Trial, self).initialize(chad_demo)

        # adjust the parameters for the given demographic
        self.adjust_params(y)

        return
