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
Human Activity Patterns (ABMHAP) with the data from the Consolidated Human Activity Database \
(CHAD).

This module contains the class :class:`trial.Trial`.
"""

# ===========================================
# import
# ===========================================

import sys
sys.path.append('..\\source')
sys.path.append('..\\run')
sys.path.append('..\\processing')

# mathematical capability
import numpy as np

# dataframe capability
import pandas as pd

# zipfile capability
import zipfile

# ABMHAP modules
import my_globals as mg
import activity, chad, diary, location, singleton, state, universe

# ===========================================
# constants
# ===========================================
NO_TRIAL = -100

SLEEP               = 1
WORK                = 2
COMMUTE_TO_WORK     = 3
COMMUTE_FROM_WORK   = 4
EAT_BREAKFAST       = 5
EAT_LUNCH           = 6
EAT_DINNER          = 7
OMNI                = 1000

#
# coefficient of variation. This avoids negative numbers for sampling duration
#
# the minimum amount of time for an event duration will be considered long [hours]
LONG_DURATION = 3

# maximum coefficient of variation
CV_MIN  = 0.10
CV_MAX  = 0.80

CV_SHORT   = 0.3
CV_LONG    = 0.1

# represent the integer identifier as a string
INT_2_STR = { NO_TRIAL: 'No trial', SLEEP: 'sleep trial', WORK: 'work trial',
              COMMUTE_TO_WORK: 'commute to work trial', COMMUTE_FROM_WORK: 'commute from work trial',
              EAT_BREAKFAST: 'eat breakfast trial', EAT_LUNCH: 'eat lunch trial', EAT_DINNER: 'eat dinner trial'}

# represent the string identifier as an integer
STR_2_INT = { (value, key) for (key, value) in INT_2_STR.items() }

# indicates which activities are in the OMNI trial
OMNI_ACTIVITIES = [activity.COMMUTE_TO_WORK, activity.COMMUTE_FROM_WORK, activity.EAT_BREAKFAST, \
                   activity.EAT_DINNER, activity.EAT_LUNCH, activity.SLEEP, activity.WORK]

# indicates which activities are contained in each trial.
# Note: each value in the dictionary is a list
TRIAL_2_ACTIVITY = {COMMUTE_TO_WORK: (activity.COMMUTE_TO_WORK,),
           COMMUTE_FROM_WORK: (activity.COMMUTE_FROM_WORK,),
           EAT_BREAKFAST: (activity.EAT_BREAKFAST,),
           EAT_DINNER: (activity.EAT_DINNER,),
           EAT_LUNCH: (activity.EAT_LUNCH,),
           SLEEP: (activity.SLEEP,),
           WORK: (activity.WORK,),
           OMNI: OMNI_ACTIVITIES,
           }

# ===========================================
# class Trial
# ===========================================

class Trial(object):

    """
    This class is sets up runs for the ABMHAP initialized with data from CHAD.

    This is how to run a trial

    #. create the Trial object via __init__()
    #. initialize the Trial. That is, one must set up the distribution for sampling means and standard deviations) \
     via initialize(). This is usually done by sending the appropriate files names to the function for the respective \
     distributions.
    #. create the universe for the simulation
    #. add the people to the household
    #. run the simulation

    :param params.Params params: the parameters that describe the household
    :param chad_params.CHAD_params sampling_params: the sampling parameters used to filter "good" CHAD activity data
    :param int demographic: the demographic identifier used to parametrize the agent

    :var int id: the trial identifier
    :var params.Params 'params': the parameters that describe the household
    :var chad_params.CHAD_params sampling_params: the sampling parameters used to filter "good" CHAD data
    :var int num_samples: the number of ABMHAP samples (or trials) to be run
    :var int demographic: the demographic identifier used to parametrize the agent
    :var str fname: the name of the zipfile for the CHAD data
    """

    def __init__(self, parameters, sampling_params, demographic):


        # the identifier for the trial
        self.id = NO_TRIAL

        # number of samples
        self.num_samples = 1

        # relevant ABM parameters
        self.params = parameters

        # relevant CHAD activity parameters
        self.sampling_params = sampling_params

        # name of the zipfile for the CHAD stats
        self.fname = ''

        # the demographic identifier
        self.demographic = demographic

        return

    def add_person_to_universe(self, u, idx):

        """
        This function creates a person and sets up the universe for simulation.

        .. note::
            This function currently only assumes that each simulation has only 1 person / household. \
            This will need to be changed later. There will be conflicts with the idx and id.

        :param universe.Universe u: the universe the simulation will run in
        :param int idx: the index for :attr:`params` to access to parametrize this person.

        :return u: the updated/ initialized universe
        :rtype: universe.Universe
        """

        # initialize / create the person
        p = self.initialize_person(u, idx)

        # person identifier number
        p.id = idx

        # add person to the universe
        u.people.append(p)

        # set the agent's state to be in the initial state
        for p in u.people:
            p.state.is_init = True

        # initialize the needs
        u.initialize_needs()

        # initialize the home assets
        u.home.initialize(u.people)

        # set the home economics
        u.home.set_revenue(u.people)

        # set the population
        u.home.set_population(u.people)

        return

    def assign_chad_params(self, z, f_stats, s_params):

        """
        Assign the CHAD statistical parameters for a given activity to the agent.

        :param zipfile.ZipFile z: the file name (.zip) for the demographic data
        :param f_stats: the file names of the statistical data relevant to the start time, \
        end time, duration, and CHAD records for a given activity
        :type f_stats: a dictionary of int - str
        :param chad_params.CHAD_params s_params: the parameters that limit the sampling of \
        respective statistical data

        :return: relevant parameters for each person in the household for \
        a given activity. The tuple contains the following [in hours]: mean start time, standard \
        deviation of start time, mean end time, standard deviation of end time, mean duration, \
        and standard deviation of duration for each person in the household.
        :rtype data: tuple of numpy.ndarray, numpy.ndarray, numpy.ndarray, \
        numpy.ndarray, numpy.ndarray, numpy.ndarray
        """

        x = self.get_stats_data(z, f_stats, s_params)

        return x

    def check_spacing(self, start_mean, start_std, end_mean, end_std, spacing):

        """
        This is done to make sure the minimum end time does not overlap with plausible start times. The \
        function returns the indices of agents with a parametrization that causes this overlap. This is \
        a concern for activities like sleeping where the agent can be assigned to end too early after \
        starting the sleep too quickly.

        :param numpy.ndarray start_mean: the mean start time for the given activity for each person \
        in the household
        :param numpy.ndarray start_std: the standard deviation of start time for the given activity \
        for each person in the household
        :param numpy.ndarray end_mean: the mean end time for the given activity for each person in \
        the household
        :param numpy.ndarray end_std: the standard deviation of end time for the given activity for \
        each person in the household
        :param float spacing: the minimum amount

        :return: the indices of the agents with improper parametrization
        :rtype: numpy.ndarray
        """

        # the amount of hours to 1 day
        DAY_2_HOUR  = 24

        # the maximum allowed value for start time, assuming 1 standard deviation
        start_max   = (start_mean + start_std) % DAY_2_HOUR

        # the minimum allowed value for end time, assuming 1 standard deviation
        end_min     = (end_mean - end_std) % DAY_2_HOUR

        # if there is too much overlap (i.e., if the minimum end time overlaps the maximum start time, the
        # parametrization is seen as bad
        gap         = (start_max - end_min) % DAY_2_HOUR
        idx         = gap <= spacing

        return idx

    def create_universe(self):

        """
        This function creates a universe object that simulations will run in.

        :return u: the universe for the simulation to run in
        :rtype: universe.Universe
        """

        # set up universe
        u = universe.Universe(self.params.num_steps, self.params.dt, self.params.t_start, self.params.num_people)

        # set the clock to the desired start time
        u.clock.t_univ = self.params.t_start
        u.clock.set_time()

        return u

    def get_chad_stats_data_dt(self, z, fname, s_params):

        """
        This function obtains the CHAD data for activity duration data that are \
        suitable for ABMHAP simulation.

        :param zifpile.Zipfile z: the zipfile of the activity data
        :param str fname: the file name for the data file for activity duration
        :param chad_params.CHAD_params s_params: the parameters that limit the sampling of \
        respective statistical data for a given activity

        :return: the CHAD data for activity duration suitable for ABMHAP simulation
        :rtype: pandas.core.frame.DataFrame
        """

        # get the data from CHAD to limit duration
        data    = pd.read_csv ( z.open(fname) )

        # get the duration data
        dt      = s_params.get_dt(data).sort_values( ['PID'])

        return dt

    def get_chad_stats_data_end(self, z, fname, s_params):

        """
        This function obtains the CHAD data for activity end time data that are \
        suitable for ABMHAP simulation.

        :param zifpile.Zipfile z: the zipfile of the activity data
        :param str fname: the file name for the data file for activity duration
        :param chad_params.CHAD_params s_params: the parameters that limit the sampling of \
        respective statistical data for a given activity

        :return: the CHAD data for activity end time suitable for ABMHAP simulation
        :rtype: pandas.core.frame.DataFrame
        """

        # get the data from CHAD to limit end time
        data    = pd.read_csv ( z.open(fname) )

        # get end time
        end     = s_params.get_end(data).sort_values( ['PID'] )

        return end

    # def get_chad_stats_data_same_day(self, z, f_stats, s_params):
    #
    #     """
    #     This function obtains the CHAD data for activity duration data that are \
    #     suitable for ABMHAP simulation.
    #
    #     :param zifpile.Zipfile z: the zipfile of the activity data
    #     :param str fname: the file name for the data file for activity duration
    #     :param chad_params.CHAD_params s_params: the parameters that limit the sampling of \
    #     respective statistical data for a given activity
    #
    #     :return: the CHAD data for activity duration suitable for ABMHAP simulation
    #     :rtype: pandas.core.frame.DataFrame
    #     """
    #
    #     # get the file names
    #     fname_dt, fname_start = f_stats
    #
    #     df_dt, df_start = self.get_chad_stats_data(z, fname_dt, fname_start, s_params)
    #
    #     # sample the the each moment independently for each Person in the simulation
    #     dt_mean, dt_std, start_mean, start_std = self.sample(df_dt, df_start)
    #
    #     # set duration of standard deviations to zero
    #     dt_std      = np.zeros(dt_std.shape)
    #
    #     # set start time of standard deviations to zero
    #     start_std   = np.zeros(start_std.shape)
    #
    #     # store the moments for the respective activity
    #     x = (dt_mean, dt_std, start_mean, start_std)
    #
    #     return x

    def get_chad_stats_data_start(self, z, fname, s_params):

        """
        This function obtains the CHAD data for activity start time data that are \
        suitable for ABMHAP simulation.

        :param zifpile.Zipfile z: the zipfile of the activity data
        :param str fname: the file name for the data file for activity duration
        :param chad_params.CHAD_params s_params: the parameters that limit the sampling of \
        respective statistical data for a given activity

        :return: the CHAD data for activity duration suitable for ABMHAP simulation
        :rtype: pandas.core.frame.DataFrame
        """

        # get the data from CHAD to limit start time
        data    = pd.read_csv ( z.open(fname) )

        # get the start time
        start   = s_params.get_start(data).sort_values( ['PID'] )

        return start

    def get_diary(self, u):

        """
        This function takes the simulation data in terms of a list of \
        :class:`universe.Universe` and creates a list \
        of :class:`diary.Diary` that contain the activity diaries. \
        One per each household in the simulation.

        :param universe.Universe u: contains all of the simulation data
        :return: the activity diaries (1 entry per person)
        :rtype: list of :class:`diary.Diary`
        """

        # the list of diaries for each agent in the household
        diary_hhld = list()

        # the household diaries for each agent in the simulation
        for p in u.people:

            # get the information about the diary
            t, act, loc = self.get_diary_help(u.clock.hist_time, p.hist_activity, p.hist_local)

            # add the diary to the list
            diary_hhld.append( diary.Diary(t, act, loc) )

        return diary_hhld

    def get_diary_help(self, t, hist_act, hist_loc):

        """
        This function takes data on the activity start times, activity codes, and location codes \
        from an activity diary and fills out the activity, minute-by-minute in between two adjacent \
        activities.

        :param numpy.ndarray t: the start time from an activity diary
        :param numpy.ndarray hist_act: the activity codes from an activity diary
        :param numpy.ndarray hist_loc: the location codes from an activity diary

        :return: the minute by minute information from an ABMHAP simulation for the \
        following: time information, activity codes, and location codes
        :rtype: numpy.ndarray, numpy.ndarray, numpy.ndarray
        """

        # get indices that indicate the simulation data
        idx = t != -1

        # start times of the simulation only
        t_data      = t[idx]

        # activity codes of the simulation only
        act_data    = hist_act[idx]

        # location codes of the simulation only
        loc_data    = hist_loc[idx]

        # the minute by minute time information for the simulation
        t_all       = mg.fill_out_time(t_data)

        # the minute by minute activity code information for the simulation
        act_all     = mg.fill_out_data(t_data, act_data)

        # the minute by minute location code information for the simulation
        loc_all     = mg.fill_out_data(t_data, loc_data)

        return t_all, act_all, loc_all

    # def get_moments(self, fname_dt, fname_start):
    #
    #     # get the moments of CHAD data for activity duration and activity start time, respectively
    #     chad_df_dt, chad_df_start = self.get_chad_stats_data(self.fname, fname_dt=fname_dt, fname_start=fname_start)
    #
    #     # sample the the each moment independently for each Person in the ABM simulation
    #     abm_dt_mean, abm_dt_std, abm_start_mean, abm_start_std = self.sample(chad_df_dt, chad_df_start)
    #
    #     return chad_df_dt, chad_df_start, abm_dt_mean, abm_dt_std, abm_start_mean, abm_start_std

    def get_stats_data(self, z, f_stats, s_params):

        """
        Assign the CHAD statistical parameters for a given activity to the agent.

        :param zipfile.ZipFile z: the file name (.zip) for the demographic data
        :param f_stats: the file names of the statistical data relevant to the start time, \
        end time, duration, and CHAD records for a given activity
        :type f_stats: a dictionary of int - str
        :param chad_params.CHAD_params s_params: the parameters that limit the sampling of \
        respective statistical data

        :return: relevant parameters for each person in the household for \
        a given activity. The tuple contains the following [in hours]: mean start time, standard \
        deviation of start time, mean end time, standard deviation of end time, mean duration, \
        and standard deviation of duration for each person in the household.
        :rtype data: tuple of numpy.ndarray, numpy.ndarray, numpy.ndarray, \
        numpy.ndarray, numpy.ndarray, numpy.ndarray

        """

        # number of people per household
        N       = self.params.num_people

        # the file name for the start time, end time, and duration for a given activity
        fname_start, fname_end, fname_dt = f_stats[chad.START], f_stats[chad.END], f_stats[chad.DT]

        # time is in hours[0, 24)

        # initialize duration mean and standard deviation values, respectively, to zero
        dt_mean, dt_std         = np.zeros(N), np.zeros(N)

        # initialize start time mean and standard deviation values, respectively, to zero
        start_mean, start_std   = np.zeros(N), np.zeros(N)

        # initialize end time mean and standard deviation values, respectively, to zero
        end_mean, end_std       = np.zeros(N), np.zeros(N)

        #
        # duration
        #
        if s_params.do_dt:

            # sample duration data from CHAD
            df_dt           = self.get_chad_stats_data_dt(z, fname_dt, s_params)

            # sample mean and standard deviation duration data based on the empirical
            # data distributions for the agent
            dt_mean, dt_std = self.get_stats_data_dt(df_dt, N, s_params.N)

        #
        # both start and end time
        #
        if s_params.do_start and s_params.do_end:

            # sample start time data from CHAD
            df_start    = self.get_chad_stats_data_start(z, fname_start, s_params)

            # sample end time data from CHAD
            df_end      = self.get_chad_stats_data_end(z, fname_end, s_params)

            # sample mean and standard deviation start time and end time data based
            # on the empirical data distributions for the agent
            start_mean, start_std, end_mean, end_std \
                = self.get_stats_data_start_end(df_start, df_end, N, s_params.N)
        else:

            #
            # start time only
            #
            if s_params.do_start:

                # sample start time data from CHAD
                df_start                = self.get_chad_stats_data_start(z, fname_start, s_params)

                # sample mean and standard deviation start time data based on the empirical data
                # distributions for the agent
                start_mean, start_std   = self.get_stats_data_help(df_start, N, s_params.N)

            #
            # end time only
            #
            if s_params.do_end:

                # sample end time data from CHAD
                df_end              = self.get_chad_stats_data_end(z, fname_end, s_params)

                # sample mean and standard deviation end time data based on the empirical data
                # distributions for the agent
                end_mean, end_std   = self.get_stats_data_help(df_end, N, s_params.N)

        # store the moments for the respective activity [time is expressed in hours]
        data = (start_mean, start_std, end_mean, end_std, dt_mean, dt_std)

        return data

    def get_stats_data_dt(self, df, num_people, n_data):

        """
        This function samples the duration data from CHAD from a particular activity and \
        gets the mean and standard deviation of duration for the respective activity \
        for each person in the household.

        :param pandas.core.frame.DataFrame df: duration CHAD data
        :param int num_people: the number of people in the household
        :param int n_data: the minimum number of data points per \
        CHAD-person record used in sampling the CHAD data

        :return: the mean and standard deviation [in hours] for a given activity for \
        each person in the household
        :rtype: numpy.ndarray, numpy.ndarray
        """

        # get a list of values that represent the empirical distribution of the mean, standard deviation, and \
        # coefficient of variation
        x_mean, x_std, x_cv = self.sample(df)

        # keep the distribution of mean values
        y = np.array(x_mean)

        # randomly assign N values for the mean of duration
        x_mean = np.random.choice(x_mean, num_people)

        # assign a coefficient of duration and then use it in assigning a standard deviation for
        # the duration
        if n_data == 1:
            if y.mean() >= LONG_DURATION:
                cv  = CV_LONG
            else:
                cv  = CV_SHORT

            # assign the N calues of standard deviation for duration
            x_std   = cv * x_mean
        else:
            # want to get values between a low and a high
            x_cv    = x_cv[(x_cv >= CV_MIN) & (x_cv <= CV_MAX)]

            # randomly assign N values for the coefficient of variation for duration
            x_cv    = np.random.choice(x_cv, num_people)

            # assign the N values of standard deviation for duration
            x_std   = x_cv * x_mean

        return x_mean, x_std

    def get_stats_data_help(self, df, num_people, n_data):

        """
        This function samples the CHAD data to obtain information \
        on the mean and standard deviation data. This is done by doing \
        the following

        #. creating an empirical distribution for the mean and standard deviation of the data
        #. randomly choosing a value out of the distribution for each agent in the household

        :param pandas.core.frame.DataFrame df: the CHAD statistical data
        :param int num_people: number of people in the household
        :param int n_data: the minimum number of data points per CHAD-person record used in sampling the CHAD data

        :return: the mean and standard deviation [in hours] for a given activity for \
        each person in the household
        :rtype: numpy.ndarray, numpy.ndarray
        """

        # load the empirical distribution based of the mean, standard deviation, and coefficient of variation
        # from the data frame
        x_mean, x_std, x_cv = self.sample(df)

        # choose the means for each person
        x_mean = np.random.choice(x_mean, num_people)

        if n_data == 1:
            # this will be over written for start time and end time
            x_std       = np.mean(x_mean) * np.ones( (num_people,) )
        else:
            # use the longitudinal data
            x_std       = np.random.choice(x_std, num_people)

        return x_mean, x_std

    def get_stats_data_start_end(self, df_start, df_end, num_people, n_data):

        """
        This function samples data for activities that are parametrized \
        by both start time and end time activity-parameters.

        :param pandas.core.frame.DataFrame df_start: the CHAD data for start time [hours]
        :param pandas.core.frame.DataFrame df_end: the CHAD data for end time [hours]
        :param int num_people: the number of people in the household
        :param int n_data:  the number of data points to be considered "longitudinal"

        :return: the mean and standard deviation for the start time and end time respectively
        :rtype: numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray
        """

        # the amount of time [hours] needed
        SPACING     = 2

        # assign the start time and end time mean and standard deviation for each person
        start_mean, start_std, end_mean, end_std \
            = self.get_stats_data_start_end_help( df_start, df_end, num_people, n_data )

        # get indices of overlapping start time and end time configurations
        idx = self.check_spacing(start_mean, start_std, end_mean, end_std, SPACING)

        #while there is a bad parametrization
        while idx.any():

            # number of people who have a bad parametrization
            num = sum(idx)

            # assign the start time and end time mean and standard deviation for each person
            s_mean, s_std, e_mean, e_std \
                = self.get_stats_data_start_end_help(df_start, df_end, num, n_data)

            # assign the start time and time
            start_mean[idx], start_std[idx] = s_mean, s_std
            end_mean[idx], end_std[idx]     = e_mean, e_std

            # get indices of overlapping start time and end time configurations
            idx = self.check_spacing(start_mean, start_std, end_mean, end_std, SPACING)

        return start_mean, start_std, end_mean, end_std

    def get_stats_data_start_end_help(self, df_start, df_end, num_people, n_data):

        """
        This function samples data for activities that are parametrized \
        by both start time and end time activity-parameters.

        :param pandas.core.frame.DataFrame df_start: the CHAD data for start time [hours]
        :param pandas.core.frame.DataFrame df_end: the CHAD data for end time [hours]
        :param int num_people: the number of people in the household
        :param int n_data:  the number of data points to be or not be considered "longitudinal"


        :return: the mean and standard deviation for the start time and end time respectively
        :rtype: numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray
        """

        # obtain the start time mean and standard deviation, respectively, for each agent in the household
        start_mean, start_std   = self.get_stats_data_help(df_start, num_people, n_data)

        # obtain the end time mean and standard deviation, respectively, for each agent in the household
        end_mean, end_std       = self.get_stats_data_help(df_end, num_people, n_data)

        # in order to have a intra-individual variation for start time and end time, when there is no
        # longitudinal data, we use an approximation for intra-individual variation
        if n_data == 1:
            start_std, end_std  = self.pseudo_intraindividual_variation(start_mean, end_mean)

        return start_mean, start_std, end_mean, end_std

    def initialize(self, demo):

        """
        This function initializes each activity in the trial for a given demographic by \
        using CHAD data to parametrize the activity-parameters (i.e., the mean \
        and standard deviation of star time, end time, and duration).

        :param chad_demography.CHAD_demography demo: contains much information about the demographic

        :return: a dictionary containing a tuple of the mean duration, standard deviation of duration, \
        mean start time, standard deviation of start time (in hours, float)
        :rtype: a dictionary of int to numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.
        """

        # the demographic data
        z   = zipfile.ZipFile(demo.fname_zip, mode='r')

        # dictionary of the file names for the statistical data
        fname_stats = demo.fname_stats

        # activity codes for the activities that are done by the demographic
        keys    = demo.keys

        # the sampling parameters for the initialization
        sampling_params = demo.int_2_param

        # adjust_parameter() arguments
        y = dict()

        # for each activity, assign the data about the mean and standard deviation
        # start time, end time, and duration
        for k in keys:

            # store the relevant file names
            f_stats = fname_stats[k]

            # store the sampling parameters for this particular activity
            s_params = sampling_params[k]

            # recall: the times are in hours
            x = self.assign_chad_params(z, f_stats, s_params)

            # store the moments data for each activity in the dictionary
            y[k] = x

        # close the zipfile
        z.close()

        return y

    def initialize_person(self, u, idx):

        """
        This function creates and initializes an agent with the proper parameters for \
        simulation.

        More specifically, the function does

        #. creates the agent
        #. initializes the agent's parameters to the respective values in :attr:`params`

        :param universe.Universe u: the universe the agent will reside in
        :param int idx: the index of the agent within the household

        :return p: the agent
        :rtype: singleton.Singleton
        """

        # create the person
        p = singleton.Singleton(u.home, u.clock, u.schedule)

        # set person to have relevant parameters
        p.set(self.params, idx)

        # initialize the person
        p.location.local    = location.HOME

        # set the state to idle
        p.state.stats       = state.IDLE

        # set the state's start time and end time to the current time [univeral time]
        p.state.t_start     = u.clock.t_univ
        p.state.t_end       = u.clock.t_univ

        return p

    def pseudo_intraindividual_variation(self, start_mean, end_mean):

        """
        This function assigns intraindividual variation for start time and end time based data where
        there is **no** longitudinal data (hence the name "pseudo"). The variation is assigned by
        having the following assumptions:

        #. Given that the mean start time and end time are assigned
        #. Calculate the mean duration based on the mean start time and mean end time
        #. Calculate the variance of the start time and end time with the following assumptions
            * assume that start time and end time are independent
            * variance of start time is equal to the variance of the end time
            * standard deviation of the duration is set to be the coefficient of variation times \
            the previously calculated mean duration

        These assumptions are expressed mathematically below where

        * :math:`X_{start}, X_{end}, X_{\\Delta{t}}` are random variables for the start time, end time, \
        and duration, respectively
        * :math:`\\sigma^2, \\sigma, c_v` are the variance, standard deviation, and coefficient of variation
        * :math:`E[\\cdot], Cov(\\cdot, \\cdot)` are the expected value operator and covariance  operator

        Given :math:`X_{start}` and :math:`X_{end}`,

        Let,

        .. math::
            X_{\\Delta{t}} = X_{end} - X_{start}

        Then,

        .. math::
            \\sigma^2_{\\Delta{t}} = \\sigma^2_{start}  + \\sigma^2_{end} - 2*Cov(X_{start}, X_{end})

        Assuming :math:`X_{start}` and :math:`X_{end}` are independent, then,

        .. math::
            \\sigma^2_{\\Delta{t}} = \\sigma^2_{start}  + \\sigma^2_{end}

        Assuming :math:`\\sigma^2_{start}  = \\sigma^2_{end}`, then,

        .. math::
            \\sigma^2_{\\Delta{t}} = 2\\sigma^2_{start}

        Finally,

        .. math::
             \\sigma_{start} &= \\frac{ \\sigma_{\\Delta{t}} }{ \\sqrt{2} } \\\\
             \\sigma_{start} = \\sigma_{end} &= \\frac{ c_v E[ X_{\\Delta{t}} ] }{ \\sqrt{2} }

        :param numpy.ndarray start_mean: the mean start time [in hours] for each person bing parametrized
        :param numpy.ndarray end_mean: the mean end time [in hours] for each person being parametrized

        :return: standard deviation for start time and end time, respectively for each person being parametrized
        :rytpe: numpy.ndarray, numpy.ndarray
        """

        # the mean duration
        dt_mean = (end_mean - start_mean) % 24

        # assign the coefficient of variation for longer durations
        if dt_mean.mean() >= LONG_DURATION:
            cv  = CV_LONG
        else:
            cv  = CV_SHORT

        # assign the standard deviation for the duration
        dt_std  = cv * dt_mean

        # the standard deviation from our assumptions
        std     = dt_std / np.sqrt(2)

        # assign the start time and end time standard deviation
        start_std, end_std   = std, std

        return start_std, end_std

    def run(self):

        """
        This function runs 1 simulations of the ABMHAP using data from \
        CHAD. The function can handle having more than 1 person in the household.

        More specifically the function does the following for each simulation:

        #. creates the universe
        #. create / initialize the person
        #. run the ABMHAP simulation
        #. store the results / data from the simulation

        :return u: the results of the simulation
        :rtype: universe.Universe
        """

        # create the universe
        u = self.create_universe()

        # create and add person to universe initialized appropriately
        for i in range(self.params.num_people):
            self.add_person_to_universe(u, idx=i)

        # run the ABMHAP simulation
        u.run()

        #
        diary_hhld_list = self.get_diary(u)

        return diary_hhld_list

    # def run_uni(self):
    #
    #     """
    #     This function runs 1 simulations of the ABMHAP using data from CHAD. \
    #     The function can handle having more than 1 person in the household.
    #
    #     More specifically the function does the following for each simulation:
    #
    #     #. creates the universe
    #     #. create / initialize the person
    #     #. run the ABM simulation
    #     #. store the results / data from the simulation
    #
    #     :return u: the results of the simulation
    #     :rtype: universe.Universe
    #     """
    #
    #     # run the simulation
    #     u = self.create_universe()
    #
    #     # create and add person to universe initialized appropriately
    #     for i in range(self.params.num_people):
    #         self.add_person_to_universe(u, idx=i)
    #
    #     # run the ABM simulation
    #     u.run()
    #
    #     return u

    def sample(self, df):

        """
        This function samples the statistical data (of activity moments) from the CHAD diaries.

        The function samples the **distributions** of both the means and the \
        the standard deviations independently of each other.

        :param pandas.core.frame.DataFrame df: a list of statistical data (mean, standard deviation, \
        coefficient of variation) for activity information (duration, start, or end)

        :return: values for the mean, standard deviation, and coefficient of variation, respectively
        :rtype: numpy.ndarray, numpy.ndarray, numpy.ndarray
        """

        # the number of values to sample.
        N = 3 * len(df)

        # sample for mean values
        data_mean   = mg.sample( df['mu'].values, N )

        # sample standard deviation values
        data_std    = mg.sample( df['std'].values, N )

        # sample for coefficient of variation
        # use only finite values of coefficient of variation
        x           = df['cv'].values
        data_cv     = mg.sample( x[np.isfinite(x)], N )

        return data_mean, data_std, data_cv

    # def sample_N(self, df, N, do_solo=False):
    #
    #     """
    #     This function returns CHAD data from entries with either \
    #     single-day data or longitudinal data.
    #
    #     :param pandas.core.frame.DataFrame df: the statistical results
    #     :param bool do_solo: a flag indicating whether to sample people with single-day \
    #     entries only (if True) or not (if False)
    #     :param int N: the minimum amount of events that are needed in sampling the \
    #     activity data
    #
    #     :return: the selected CHAD data
    #     :rtype: pandas.core.frame.DataFrame
    #     """
    #
    #     if do_solo:
    #         x = df[df.N == 1]
    #     else:
    #         x = df[df.N >= N]
    #
    #     return x

    # def sample_dt(self, df, s_params):
    #
    #     """
    #     This function goes through the CHAD activity duration data and gets information that \
    #     have the appropriate characteristics.
    #
    #     .. math::
    #
    #         \\begin{cases}
    #             \\mu_{min} &\\le \\mu \\le \\mu_{max} \\\\
    #             \\sigma &\\le \\sigma_{max}
    #         \\end{cases}
    #
    #     where
    #
    #         * :math:`\\mu` is the mean activity duration [in hours]
    #         * :math:`\\mu_{min}` is the minimum mean activity duration [in hours]
    #         * :math:`\\mu_{max}` is the maximum mean activity duration [in hours]
    #         * :math:`\\sigma` is the standard deviation of activity duration [in hours]
    #         * :math:`\\sigma_{max}` is the maximum standard deviation of activity duration [in hours]
    #
    #     :param pandas.core.frame.DataFrame df: the CHAD statistical data
    #     :param chad_params.CHAD_params s_params: the parameters the limit the sampling of CHAD data
    #
    #     :return: the respective activity duration data
    #     :rtype: pandas.core.frame.DataFrame
    #     """
    #
    #     # the parameters that limit the CHAD data for the activity for duration (mean & standard deviation)
    #     mean_min, mean_max, std_max = s_params.dt_mean_min, s_params.dt_mean_max, s_params.dt_std_max
    #
    #     # get a flag for single activity data only & the minimum number of activity-data to get in sampling
    #     do_solo, N = s_params.do_solo, s_params.N
    #
    #     # get data according to limits on the mean & standard deviation
    #     y = df[ (df['mu'].values >= mean_min) & (df['mu'].values <= mean_max) ]
    #
    #     # sample according to the number of activity-diary entries per person
    #     y = self.sample_N(y, N=N, do_solo=do_solo)
    #
    #     return y

    # def sample_end(self, df, s_params, do_periodic=False):
    #
    #     """
    #     This function goes through the CHAD activity end time data and gets \
    #     information that have the appropriate characteristics.
    #
    #     .. math::
    #
    #         \\begin{cases}
    #             \\mu_{min} &\\le \\mu \\le \\mu_{max} \\\\
    #             \\sigma &\\le \\sigma_{max}
    #         \\end{cases}
    #
    #     where
    #
    #         * :math:`\\mu` is the mean activity end time [hours, periodic time]
    #         * :math:`\\mu_{min}` is the minimum mean activity end time [hours, periodic time]
    #         * :math:`\\mu_{max}` is the maximum mean activity end time [hours, periodic time]
    #         * :math:`\\sigma` is the standard deviation of activity end time [hours]
    #         * :math:`\\sigma_{max}` is the maximum standard deviation of end time[hours]
    #
    #     :param pandas.core.frame.DataFrame df: the statistical end time data
    #     :param chad_params.CHAD_params s_params: the parameters the limit the sampling of CHAD data
    #     :param bool do_periodic: a flag to indicate whether the data for end time should be analyzed \
    #     in periodic form [-12, 12) instead of [0, 24)
    #
    #     :return: the respective end time time data [hours]
    #     :rtype: pandas.core.frame.DataFrame
    #     """
    #
    #     # put the time values in range [-12, 12)
    #     t_mean = df['mu'].values
    #
    #     # the parameters that limit the CHAD data for the activity for end time (mean & standard deviation)
    #     mean_min, mean_max, std_max = s_params.end_mean_min, s_params.end_mean_max, s_params.end_std_max
    #
    #     # get single activity data only
    #     do_solo, N = s_params.do_solo, s_params.N
    #
    #     # if an event may occur over midnight, express the time [-12, 12)
    #     if do_periodic:
    #
    #         # put the time values in range [-12, 12)
    #
    #         # put in periodic time
    #         mean_min    = mg.to_periodic(mean_min)
    #         mean_max    = mg.to_periodic(mean_max)
    #         t_mean      = mg.to_periodic(t_mean)
    #
    #     # get data according to limits on the mean & standard deviation
    #     y = df[ (t_mean >= mean_min) & (t_mean <= mean_max) ]
    #
    #     # sample according to the number of activity-diary entries per person
    #     y = self.sample_N(y, N=N, do_solo=do_solo)
    #
    #     return y


    # def sample_start(self, df, s_params, do_periodic=False):
    #
    #     """
    #     This function goes through the CHAD activity start time data \
    #     and gets information that have the appropriate characteristics.
    #
    #     .. math::
    #
    #         \\begin{cases}
    #             \\mu_{min} &\\le \\mu \\le \\mu_{max} \\\\
    #             \\sigma &\\le \\sigma_{max}
    #         \\end{cases}
    #
    #     where
    #
    #         * :math:`\\mu` is the mean activity start time [hours, periodic time]
    #         * :math:`\\mu_{min}` is the minimum mean activity start time [hours, periodic time]
    #         * :math:`\\mu_{max}` is the maximum mean activity start time [hours, periodic time]
    #         * :math:`\\sigma` is the standard deviation of activity start time [hours]
    #         * :math:`\\sigma_{max}` is the maximum standard deviation of start time[hours]
    #
    #     :param pandas.core.frame.DataFrame df: the statistical start time data
    #     :param chad_params.CHAD_param s_params: the parameters the limit the sampling of CHAD data
    #     :param bool do_periodic: a flag to indicate whether the data should be analyzed in periodic form [-12, 12) \
    #     instead of [0, 24)
    #
    #     :return: the start time time data [in hours]
    #     :rtype: pandas.core.frame.DataFrame
    #     """
    #
    #     # put the time values in range [-12, 12)
    #     t_mean = df['mu'].values
    #
    #     # the parameters that limit the CHAD data for the activity for start time (mean & standard deviation)
    #     mean_min, mean_max, std_max = s_params.start_mean_min, s_params.start_mean_max, s_params.start_std_max
    #
    #     # get single activity data only
    #     do_solo, N = s_params.do_solo, s_params.N
    #
    #     # if an event may occur over midnight, express the time [-12, 12)
    #     if do_periodic:
    #
    #         # put the time values in range [-12, 12)
    #
    #         # put in periodic time
    #         mean_min    = mg.to_periodic(mean_min)
    #         mean_max    = mg.to_periodic(mean_max)
    #         t_mean      = mg.to_periodic(t_mean)
    #
    #     # get data according to limits on the mean & standard deviation
    #     y = df[(t_mean >= mean_min) & (t_mean <= mean_max)]
    #
    #     # sample according to the number of activity-diary entries per person
    #     y = self.sample_N(y, N=N, do_solo=do_solo)
    #
    #     return y

    # def set_std(self, x_mean, x_std, N):
    #
    #     """
    #
    #     :param numpy.ndarray x_mean:
    #     :param numpy.ndarray x_std:
    #     :param int  N:
    #
    #     :return:
    #     :rtype: numpy.ndarray
    #     """
    #
    #     results = np.zeros(x_mean.shape)
    #
    #     if N > 1:
    #         results[:]  = np.mean(x_std)
    #     else:
    #         results[:]  = np.std(x_mean)
    #
    #     return results