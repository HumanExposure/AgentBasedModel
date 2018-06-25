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
Human Activity Database (CHAD) for the **sleep** activity.

This module contains class :class:`sleep_trial.Sleep_Trial`.
"""

# ===========================================
# import
# =========================================
import sys
sys.path.append('..\\source')

# ABMHAP modules
import my_globals as mg
import bed, occupation, temporal, trial

# ===========================================
# class Sleep_Trial
# =========================================

class Sleep_Trial(trial.Trial):

    """
    This class runs the ABMHAP simulations initialized with sleep data from CHAD.

    :param params.Params parameters: the parameters describing each person in the household
    :param chad_params.CHAD_params sampling_params: the sampling parameters used to filter "good" CHAD \
    sleep data
    :param int demographic: the demographic identifier
    """

    def __init__(self, parameters, sampling_params, demographic):

        # constructor
        trial.Trial.__init__(self, parameters, sampling_params, demographic)

        # the trial identifier
        self.id = trial.SLEEP

        return

    def adjust_params(self, start_mean, start_std, end_mean, end_std):

        """
        This function adjusts the values for the mean and standard deviation of both sleep \
        duration and sleep start time in the key-word arguments based on the CHAD data \
        that was sampled. These new values will be used in the runs.

        :param numpy.ndarray start_mean: the mean sleep start time [hours] for each person
        :param numpy.ndarray start_std: the standard deviation of sleep start time [hours] for each person
        :param numpy.ndarray end_mean: the sleep mean end time [hours] for each person
        :param numpy.ndarray end_std: the sleep standard deviation of end time [hours] for each person

        :return:
        """

        # the number of minutes in 1 hour, the number of minutes in 1 day
        HOUR_2_MIN, DAY_2_MIN  = temporal.HOUR_2_MIN, temporal.DAY_2_MIN

        # convert hours into the minutes equivalent
        f = mg.hours_to_minutes

        # set the job in order to have workdays and non-workdays
        self.params.job_id     = (occupation.STANDARD_JOB, ) * self.params.num_people

        # set the start time to be Sunday, Day 0, at 17:00
        self.params.t_start     = (temporal.SUNDAY * DAY_2_MIN) + 17 * HOUR_2_MIN

        # mean start time for sleep (in minutes)
        self.params.sleep_start_mean    = f(start_mean)

        # standard deviation for for start time (in minutes)
        self.params.sleep_start_std     = f(start_std)

        # mean end time for sleep (in minutes)
        self.params.sleep_end_mean      = f(end_mean)

        # standard deviation of end time for sleep (in minutes)
        self.params.sleep_end_std       = f(end_std)

        return

    def create_universe(self):

        """
        This function creates a universe object that simulations will run in. The only \
        asset in this simulation for an agent to use is a :class:`bed.Bed`.

        :return: the universe
        :rtype: universe.Universe
        """

        # create the universe
        u = super(Sleep_Trial, self).create_universe()

        # allow only a bed for an asset
        u.home.assets = {
            'bed': bed.Bed(),
        }

        return u

    # def get_chad_stats_data_old(self, z, fname_start, fname_end, s_params):
    #
    #     """
    #     .. warning::
    #           this function is old and wil be deleted.
    #     Sample the activity data (mean, standard deviation) from CHAD according to the following limitations
    #
    #     #. minimum and maximum of sleep duration mean
    #     #. the maximum of sleep duration standard deviation
    #     #. minimum and maximum of sleep start time mean
    #     #. the maximum of sleep start time standard deviation
    #
    #     :param zipfile.ZipFile z: the zipfile of the demographic data
    #     :param string fname_dt: the filename of the moments of activity duration data
    #     :param string fname_start: the filename of the moments of activity start time data
    #     :param chad_params.CHAD_params s_params: the sampling parameters for the respective activity
    #     :param bool do_solo: this flag indicates whether the sampling of statistical activity-data is done for \
    #     people with sinlge-activity data only
    #     :return:
    #     """
    #
    #     #whether to not or to take an intersection of the start and duration sampled data
    #     do_test = False
    #
    #     # get the data from CHAD about start times
    #     data        = pd.read_csv( z.open(fname_start) )
    #     stats_start = self.sample_start(data, s_params)
    #
    #     # get the data from CHAD to limit duration
    #     data        = pd.read_csv(z.open(fname_end))
    #     stats_end    = self.sample_end(data, s_params)
    #
    #     # treat each duration / start time pairing as seperate independent events
    #     if do_test:
    #         start   = stats_start
    #         end     = stats_end
    #     else:
    #         # need to get the intersection of CHAD data
    #         end     = stats_end.loc[ stats_end.PID.isin(stats_start.PID) ]
    #         start   = stats_start.loc[ stats_start.PID.isin(stats_end.PID) ]
    #
    #     # sort both data frames by PID ("person identifier")
    #     df_start    = start.sort_values( ['PID'] )
    #     df_end      = end.sort_values(['PID'])
    #
    #     return df_start, df_end

    def initialize(self):

        """
        This function sets up the trial

        #. gets the CHAD data for sleep under the appropriate conditions for means and standard deviations \
        for both sleep duration and sleep start time
        #. gets N samples the CHAD data for sleep duration and sleep start time for the N trials
        #. updates the :attr:`params` to reflect the newly assigned sleep parameters for the simulation

        :return:
        """

        # get the appropriate parameters per person in the household
        keys = [mg.KEY_SLEEP]

        # obtain the CHAD parameters relevant to sleeping for each person in the household
        y   = super(Sleep_Trial, self).initialize(keys)

        # the mean and standard deviations of the start time, end time, and duration
        # for sleeping
        start_mean, start_std, end_mean, end_std, dt_mean, dt_std = y[mg.KEY_SLEEP]

        # Need to convert the start time from at [-12, 12) hours format to a [0, 24) hours format
        # for mean start time and end time
        start_mean  = mg.from_periodic(start_mean)
        end_mean    = mg.from_periodic(end_mean)

        # set the standard deviations to zero [time in hours]
        start_std[:]    = 0
        end_std[:]      = 0

        # adjust the key-word arguments to take account to sleep information
        self.adjust_params(start_mean=start_mean, start_std=start_std, end_mean=end_mean, end_std=end_std)

        return

    def sample_start(self, df, s_params):

        """
        This function is used for sampling mean and standard deviation data from start times.

        :param pandas.core.frame.DataFrame df: the statistical start time data
        :param chad_params.CHAD_params s_params: the parameters the limit the sampling of CHAD data

        :return: the start time time data in the range [-12, 12) [hours]
        :rtype: pandas.core.frame.DataFrame
        """

        return super(Sleep_Trial, self).sample_start(df, s_params, do_periodic=True)