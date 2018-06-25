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
Human Activity Database (CHAD) for the **commute to work** activity.

This module contains class :class:`commute_to_work_trial.Commute_To_Work_Trial`.
"""

# ===========================================
# import
# ===========================================
import sys
sys.path.append('..\\source')

# ABMHAP modules
import my_globals as mg
import chad, temporal, transport, trial, workplace

# ===========================================
# class Commute_To_Work_Trial
# ===========================================

class Commute_To_Work_Trial(trial.Trial):

    """
    This class sets up runs for the ABMHAP initialized with data from CHAD to focus on the "commute \
    to work" activity.

    :param params.Params parameters: the parameters that describe the household
    :param chad_params.CHAD_params sampling_params: he sampling parameters used to filter "good" CHAD \
    commute to work data
    :param int demographic: the demographic identifier
    """

    def __init__(self, parameters, sampling_params, demographic):

        # constructor
        trial.Trial.__init__(self, parameters, sampling_params, demographic)

        # the trial identifier
        self.id = trial.COMMUTE_TO_WORK

        # the filename for the chad
        self.fname = chad.FNAME_COMMUTE_TO_WORK

        return

    def adjust_params(self, commute_dt_mean, commute_dt_std, work_start_mean, work_start_std, \
                      work_end_mean, work_end_std):

        """
        This function adjusts the values for the mean and standard deviation of both commute to work \
        duration and start time in the key-word arguments based on the CHAD data \
        that was sampled. These new values will be used in the runs.

        :param numpy.ndarray commute_dt_mean: the commute duration mean [hours] for each person
        :param numpy.ndarray commute_dt_std: the commute duration standard deviation [hours] for each person
        :param numpy.ndarray work_start_mean: the mean work start time [hours] for each person
        :param numpy.ndarray work_start_std: the standard deviation of work start time [hours] for each person
        :param numpy.ndarray work_end_mean: the mean work end time [hours] for each person
        :param numpy.ndarray work_end_std: the standard deviation of work end time [hours] for each person

        :return:
        """

        # the number of minutes in 1 hour and 1 day, respectively
        HOUR_2_MIN, DAY_2_MIN = temporal.HOUR_2_MIN, temporal.DAY_2_MIN

        # set the initial time
        t_monday            = temporal.MONDAY * DAY_2_MIN
        self.params.t_start = t_monday + 4 * HOUR_2_MIN

        # set the work parameters for start time (mean start time, standard deviation of start time)
        self.params.work_start_mean = mg.hours_to_minutes(work_start_mean)
        self.params.work_start_std  = mg.hours_to_minutes(work_start_std)

        # set the work parameters for end time (mean start time, standard deviation of end time)
        self.params.work_end_mean   = mg.hours_to_minutes(work_end_mean)
        self.params.work_end_std    = mg.hours_to_minutes(work_end_std)

        # set the commute to work information (mean duration and standard deviation of duration)
        self.params.commute_to_work_dt_mean   = mg.hours_to_minutes(commute_dt_mean)
        self.params.commute_to_work_dt_std    = mg.hours_to_minutes(commute_dt_std)

        return

    def create_universe(self):

        """
        This function creates a universe object that simulations will run in. The only asset in this \
        simulation for an agent to use is a :class:`transport.Transport` and :class:`workplace.Workplace`.

        :return: the universe
        :rtype: universe.Universe
        """

        # create the universe
        u = super(Commute_To_Work_Trial, self).create_universe()

        # add a workplace and a transport
        u.home.assets = {
            'transport': transport.Transport(),
            'workplace': workplace.Workplace(),
        }

        return u

    def initialize(self):

        """
        This function sets up the trial

        #. gets the CHAD data for commuting to work under the appropriate conditions
        #. gets N samples the CHAD data for workng and commuting for the N trials
        #. updates the :attr:`params` to reflect the newly assigned working and commuting parameters for the simulation

        :return:
        """

        # the activities
        keys    = [mg.KEY_COMMUTE_TO_WORK, mg.KEY_WORK]

        # obtain the CHAD parameters relevant to commuting to work for each person in the household
        y       = super(Commute_To_Work_Trial, self).initialize(keys)

        # adjust the parameters for working
        work_start_mean, work_start_std, work_end_mean, work_end_std, work_dt_mean, work_dt_std \
            = y[mg.KEY_WORK]

        # adjust the parameters for commuting from work
        commute_start_mean, commute_start_std, commute_end_mean, commute_end_std, commute_dt_mean, commute_dt_std \
            = y[mg.KEY_COMMUTE_TO_WORK]

        # set the standard deviation to zero
        work_start_std[:]   = 0
        work_end_std[:]     = 0
        commute_dt_std[:]   = 0

        # adjust the parameters for the simulation
        self.adjust_params(commute_dt_mean, commute_dt_std, work_start_mean, work_start_std, work_end_mean, work_end_std)

        return
