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
This module contains code in order to run Monte-Carlo simulations to comparing the \
Agent-Based Model of Human Activity Patterns (ABMHAP) with the data from the Consolidated \
Human Activity Database (CHAD) for the **eat lunch** activity.

This module contains class :class:`eat_lunch_trial.Eat_Lunch_Trial`.
"""

# ===========================================
# import
# ===========================================
import sys
sys.path.append('..\\source')

# math capabilities
import numpy as np

import my_globals as mg
import chad, food, location, meal, occupation, temporal, transport, trial, workplace

# ===========================================
# class Eat_Lunch_Trial
# ===========================================
class Eat_Lunch_Trial(trial.Trial):

    """
    This class runs the ABMHAP simulations initialized with eat lunch data from CHAD.

    :param params.Params parameters: the parameters describing each person in the household
    :param chad_params.CHAD_params sampling_params: the sampling parameters used to filter "good" CHAD \
    eat lunch data
    :param int demographic: the demographic identifier
    """

    def __init__(self, parameters, sampling_params, demographic):

        # constructor
        trial.Trial.__init__(self, parameters, sampling_params, demographic)

        # the trial identifier
        self.id = trial.EAT_LUNCH

        # the filename for the chad
        self.fname = chad.FNAME_EAT_LUNCH

        return

    def adjust_params(self, start_mean, start_std, dt_mean, dt_std):

        """
        This function adjusts the values for the mean and standard deviation of  eat lunch start time in the \
        key-word arguments based on the CHAD data that was sampled. These new values will be used in the runs.

        :param numpy.ndarray start_mean: the mean eat lunch start time [hours] for each person
        :param numpy.ndarray start_std: the standard deviation of eat lunch start time [hours] for each person
        :param numpy.ndarray dt_mean: the eat lunch mean duration [hours] for each person
        :param numpy.ndarray dt_std: the eat lunch standard deviation of duration [hours] for each person

        :return:
        """

        # the number of minutes in 1 hour and 1 day, respectively
        DAY_2_MIN   = temporal.DAY_2_MIN
        HOUR_2_MIN  = temporal.HOUR_2_MIN

        # set the job to not working
        self.params.job_id     = (occupation.STANDARD_JOB, ) * self.params.num_people

        # set the relevant parameters for the runs
        t_monday            = temporal.MONDAY * DAY_2_MIN
        self.params.t_start = t_monday + 5 *  HOUR_2_MIN

        # this converts time from hours to minutes
        f = mg.hours_to_minutes

        # set up the lunch for each person in the household
        self.params.lunches = \
            self.params.init_meal(meal.LUNCH, start_mean=f(start_mean), start_std=f(start_std), \
                                  dt_mean=f(dt_mean), dt_std=f(dt_std))

        # the number of people
        N = self.params.num_people

        # time in hours for mean start time and end time for work
        self.params.work_start_mean = f( 9 * np.ones(N) )
        self.params.work_end_mean   = f( 17 * np.ones(N) )

        return None


    def create_universe(self):

        """
        This function creates a universe object that simulations will run in. The only asset in this \
        simulation for an agent to use is a :class:`food.Food`.

        :return: the universe
        :rtype: universe.Universe
        """

        # create the universe
        u = super(Eat_Lunch_Trial, self).create_universe()

        # this allows eating at work
        cafeteria = food.Food()
        cafeteria.location.local = location.OFF_SITE

        # allow the appropriate assets
        u.home.assets = {
            'food': food.Food(),
            'transport': transport.Transport(),
            'workplace': workplace.Workplace(),
            'cafeteria': cafeteria,
        }

        return u

    def initialize(self):

        """
        This function sets up the trial

        #. gets the CHAD data for eat lunch under the appropriate conditions for means and standard deviations \
        for both eat lunch duration and eat lunch start time
        #. gets N samples the CHAD data for eat lunch duration and eat lunch start time for the N trials
        #. updates the :attr:`params` to reflect the newly assigned eat lunch parameters for the simulation

        :param str fname_dt: the filename of the duration statistics
        :param str fname_start: the filename of the start time statistics

        :return:
        """

        # get samples for the mean and standard deviation for the duration and start time
        keys    = [mg.KEY_EAT_LUNCH]

        # obtain the CHAD parameters relevant to eating lunch for each person in the household
        y       = super(Eat_Lunch_Trial, self).initialize(keys)

        # the mean and standard deviations of the start time, end time, and duration
        # for eating lunch
        start_mean, start_std, end_mean, end_std, dt_mean, dt_std, = y[mg.KEY_EAT_LUNCH]

        # set the standard deviation to zero
        start_std[:]    = 0
        dt_std[:]       = 0

        # adjust the key-word arguments to take account to eat dinner information
        self.adjust_params(start_mean, start_std, dt_mean, dt_std)

        return

    def initialize_person(self, u, idx):

        """
        This function creates and initializes a person with the proper parameters for the Eat Lunch Trial\
        simulation.

        More specifically, the function does

        #. creates a :class:`singleton.Singleton` person
        #. initializes the person's parameters to the respective values in :attr:`params`

        :param universe.Universe u: the universe the person will reside in
        :param int idx: the index of the person's parameters in :attr:`params`

        :return p: the agent to be simulated
        :rtype: person.Person
        """

        # initialize the person
        p = super(Eat_Lunch_Trial, self ).initialize_person(u, idx)

        # adjust to have only 1 meal
        p.socio.num_meals = 1

        # get the lunch parameters for this person
        m = self.params.lunches[idx]

        # create the meal object
        the_meal = meal.Meal( meal.LUNCH, start_mean=m.start_mean, start_std=m.start_std, \
                              dt_mean=m.dt_mean, dt_std=m.dt_std )

        # reset the meals list
        p.socio.meals = [ the_meal]

        return p