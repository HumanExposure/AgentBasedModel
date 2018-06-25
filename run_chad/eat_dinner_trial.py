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
Human Activity Database (CHAD) for the **eat dinner** activity.

This module contains class :class:`eat_dinner_trial.Eat_Dinner_Trial`.
"""

# ===========================================
# import
# ===========================================

import sys
sys.path.append('..\\source')

# ABMHAP modules
import my_globals as mg
import chad, food, meal, occupation, temporal, trial

# ===========================================
# class Eat_Dinner_Trial
# ===========================================

class Eat_Dinner_Trial(trial.Trial):

    """
    This class runs the ABMHAP simulations initialized with eat dinner data from CHAD.

    :param params.Params paramters: the parameters describing each person in the household
    :param chad_params.CHAD_params sampling_params: the sampling parameters used to filter "good" CHAD \
    eat dinner data
    :param int demographic: the demographic identifier
    """

    def __init__(self, parameters, sampling_params, demographic):

        # constructor
        trial.Trial.__init__(self, parameters, sampling_params, demographic)

        # the trial identifier
        self.id = trial.EAT_DINNER

        # the filename for the chad
        self.fname = chad.FNAME_EAT_DINNER

        return

    def adjust_params(self, start_mean, start_std, dt_mean, dt_std):

        """
        This function adjusts the values for the mean and standard deviation of both eat dinner \
        duration and eat dinner start time in the key-word arguments based on the CHAD data \
        that was sampled. These new values will be used in the runs.

        :param numpy.ndarray start_mean: the mean eat dinner start time [hours] for each person
        :param numpy.ndarray start_std: the standard deviation of eat dinner start time [hours] for each person
        :param numpy.ndarray dt_mean: the eat dinner mean duration [hours] for each person
        :param numpy.ndarray dt_std: the eat dinner standard deviation of duration [hours] for each person

        :return:
        """

        # the number of minutes in 1 hour and 1 day, respectively
        DAY_2_MIN   = temporal.DAY_2_MIN
        HOUR_2_MIN  = temporal.HOUR_2_MIN

        # set the job to not working
        self.params.job_id     = (occupation.NO_JOB, ) * self.params.num_people

        # set the relevant parameters for the runs
        t_monday            = temporal.MONDAY * DAY_2_MIN
        self.params.t_start = t_monday + 15 *  HOUR_2_MIN

        # this converts time from hours to minutes
        f = mg.hours_to_minutes

        # set up the dinner for each person in the household
        self.params.dinners = \
            self.params.init_meal(meal.DINNER, start_mean=f(start_mean), start_std=f(start_std), \
                                  dt_mean=f(dt_mean), dt_std=f(dt_std) )

        return None

    def create_universe(self):

        """
        This function creates a universe object that simulations will run in. The only asset in this \
        simulation for an agent to use is a :class:`food.Food`.

        :return: the universe
        :rtype: universe.Universe
        """

        # create the universe
        u = super(Eat_Dinner_Trial, self).create_universe()

        # allow only a bed for an asset
        u.home.assets = {
            'food': food.Food(),
        }

        return u

    def initialize(self):

        """
        This function sets up the trial

        #. gets the CHAD data for eat dinner under the appropriate conditions for means and standard deviations \
        for both eat dinner duration and eat dinner start time
        #. gets N samples the CHAD data for eat dinner duration and eat dinner start time for the N trials
        #. updates the :attr:`params` to reflect the newly assigned eat dinner parameters for the simulation

        :return:
        """

        # get samples for the mean and standard deviation for the duration and start time
        keys    = [mg.KEY_EAT_DINNER]

        # obtain the CHAD parameters relevant to eating dinner for each person in the  household
        y       = super(Eat_Dinner_Trial, self).initialize(keys)

        # the mean and standard deviations of the start time, end time, and duration
        # for eating dinner
        # obtain the CHAD parameters relevant to sleeping for each person in the  household
        start_mean, start_std, end_mean, end_std, dt_mean, dt_std = y[mg.KEY_EAT_DINNER]

        # standard deviation
        start_std[:]    = 0
        dt_std[:]       = 0

        # adjust the key-word arguments to take account to eat dinner information
        self.adjust_params(start_mean, start_std, dt_mean, dt_std)

        return


    def initialize_person(self, u, idx):

        """
        This function creates and initializes a person with the proper parameters for the Eat Dinner Trial\
        simulation. This is necessary because it changes the meal structure to having only one meal per day.

        More specifically, the function does

        #. creates a :class:`singleton.Singleton` person
        #. initializes the person's parameters to the respective values in :attr:`params`

        :param universe.Universe u: the universe the person will reside in
        :param int idx: the index of the person's parameters in :attr:`params`

        :return p: the agent to simulate
        :rtype: person.Person
        """

        # initialize the person
        p = super(Eat_Dinner_Trial, self ).initialize_person(u, idx)

        # adjust to have only 1 meal
        p.socio.num_meals = 1

        # get the dinner parameters for this person
        m = self.params.dinners[idx]

        # create the meal object
        the_meal = meal.Meal( meal.DINNER, start_mean=m.start_mean, start_std=m.start_std, \
                              dt_mean=m.dt_mean, dt_std=m.dt_std )

        # reset the meals list
        p.socio.meals = [ the_meal]

        return p