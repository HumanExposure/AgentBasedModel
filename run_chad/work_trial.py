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
Human Activity Database (CHAD) for the **work** activity.

This module contains class :class:`work_trial.Work_Trial`.
"""

# ===========================================
# import
# ===========================================
import sys
sys.path.append('..\\soruce')

# ABMHAP modules
import my_globals as mg
import chad, transport, temporal, trial, workplace

# ===========================================
# class Work_Trial
# ===========================================

class Work_Trial(trial.Trial):

    """
    This class runs the ABM simulations initialized with work data from CHAD.

    :param params.Params paramters: the parameters describing each person in the household
    :param chad_params.CHAD_params sampling_params: the sampling parameters used to filter "good" CHAD \
    work data
    :param int demographic: the demographic identifier
    """

    def __init__(self, parameters, sampling_params, demographic):

        # constructor
        trial.Trial.__init__(self, parameters, sampling_params, demographic)

        # the trial identifier
        self.id = trial.WORK

        # the filename for the chad
        self.fname = chad.FNAME_WORK

        return

    def adjust_params(self, start_mean, start_std, end_mean, end_std):

        """
        This function adjusts the values for the mean and standard deviation of both work \
        duration and work start time in the key-word arguments based on the CHAD data \
        that was sampled. These new values will be used in the runs.

        :param numpy.ndarray dt_mean: the work duration mean [minutes] for each person
        :param numpy.ndarray dt_std: the work duration standard deviation [minutes] for each person
        :param numpy.ndarray start_mean: the mean work start time [minutes] for each person
        :param numpy.ndarray start_std: the standard deviation of start time [minutes] for each person

        :return:
        """

        # the amount of minutes in 1 hour
        HOUR_2_MIN  = temporal.HOUR_2_MIN

        # the amount of minutes in 1 day
        DAY_2_MIN   = temporal.DAY_2_MIN

        # set the start time to be Day 1, Monday, at 14:00
        t_monday            = temporal.MONDAY * DAY_2_MIN
        self.params.t_start = t_monday + 4 * HOUR_2_MIN

        # set the standard deviations to zero (time is in hours)
        start_std[:]    = 0
        end_std[:]      = 0

        # set the mean start time for work (in minutes)
        self.params.work_start_mean = mg.hours_to_minutes(start_mean)

        # set the standard deviation for start time for work (in minutes)
        self.params.work_start_std  = mg.hours_to_minutes(start_std)

        # set the mean end time for work (in minutes)
        self.params.work_end_mean   = mg.hours_to_minutes(end_mean)

        # set the standard deviation for end time for work (in minutes)
        self.params.work_end_std    = mg.hours_to_minutes(end_std)

        return

    def create_universe(self):

        """
        This function creates a universe object that simulations will run in. The assets that this simulation
        uses in :class:`workplace.Workplace` and :class:`transport.Transport()`.

        :return: the universe
        :rtype: universe.Universe
        """

        # create the universe
        u = super(Work_Trial, self).create_universe()

        # the assets in the simulation
        u.home.assets = {
            'workplace': workplace.Workplace(),
            'transport': transport.Transport(),
        }

        return u

    def initialize(self):

        """
        This function sets up the trial.


        #. gets the CHAD data for work under the appropriate conditions for means and standard deviations \
        for both work duration and sleep start time
        #. gets N samples the CHAD data for work duration and work start time for the N trials
        #. updates the :attr:`params` to reflect the newly assigned sleep parameters for the simulation

        :return:
        """

        # get the appropriate parameters per person in the household
        keys    = [mg.KEY_WORK]

        # obtain the CHAD parameters relevant to working for each person in the household
        y       = super(Work_Trial, self).initialize(keys)

        # the mean and standard deviations of the start time, end time, and duration
        # for working
        start_mean, start_std, end_mean, end_std, dt_mean, dt_std = y[mg.KEY_WORK]

        # adjust the key-word arguments to take account to work information
        self.adjust_params(start_mean, start_std, end_mean, end_std)

        return