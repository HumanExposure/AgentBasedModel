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
# March 22, 2017

"""
For a given activity, this code compares how well the ABMHAP matches the CHAD data. \
This is useful for the quality assurance and quality control (QAQC). This code \
compares the distributions of mean activity-start-time and mean activity duration \
for the respective activity.

.. warning::
    I will need to update this definition
"""

# ===========================================
# import
# ===========================================

import sys
sys.path.append('..\\source')
sys.path.append('..\\run')

# for data compression
import pickle

# mathematical capability
import numpy as np

# dataframe capability
import pandas as pd

# plotting capability
import matplotlib.pylab as plt

# ABMHAP modules
import my_globals as mg
import driver_params as dp

import activity, analysis, driver, evaluation, temporal, trial

# ===========================================
# functions
# ===========================================

# def filter_activity(df, value_min, value_max, idx=None):
#
#     """
#     .. warning::
#         This function is **NOT** used
#
#     :param df:
#     :param value_min:
#     :param value_max:
#     :param idx:
#     :return:
#     """
#
#     # get the values in the correct range
#     if idx is None:
#         idx = (df >= value_min) & (df <= value_max)
#
#     # store the values in the correct range. Those values outside the range will be given NaN
#     x = df[idx].values
#
#     # only keep the values in the range
#     y = [ u[np.isfinite(u)] for u in x]
#
#     return y, idx

# def find_skipped_activty(df):
#
#     """
#     This function returns the indices of people where there was at least 1 skipped activity.
#
#     :param pandas.core.frame.DataFrame df: the data frame of data for a particular activity
#
#     :return idx: the indices (boolean) of people where there was a skipped activity
#     :rtype: numpy.ndarray
#     """
#
#     # the boolean indices of the rows of data with at least 1 NaN
#     idx = [np.isnan(x).sum() > 0 for x in df.values]
#     idx = np.array(idx)
#
#     return idx

def get_activity_data(df, act):

    """
    This function returns the activity data from an activity diary \
    of given respective agent.

    :param pandas.core.frame.DataFrame df: the activity diary
    :param int act: ABMHAP activity code

    :return: an activity diary containing information from the given activity
    :rtype: pandas.core.frame.DataFrame
    """

    # the number of minutes in 1 hour
    HOUR_2_MIN = temporal.HOUR_2_MIN

    # get all of the data for a certain activity
    y = df[df.act == act]

    # Since the work activity occurs as two-events, choose the event to be the start of the first activity-entry \
    # and the end of the last-activity entry of the day

    temp = []

    if ( len(y) != 0 ) and ( act == activity.WORK ):

        # group things by day
        gb = y.groupby('day')

        for day in y.day.unique():
            x       = gb.get_group(day)
            start   = x.start.min()
            end     = x.end.max()
            dt      = end - start + 1.0/HOUR_2_MIN
            loc     = x['loc'].values[0]

            # fill on the data for the particular day
            d = {'day': day, 'act': act, 'start': start, 'dt': dt, 'end': end, 'loc': loc}

            # store the results
            temp.append(d)

        y = pd.DataFrame(temp, columns=df.columns.values)

    return y


# def get_chad_stats_data(trial_code):
#
#     """
#     This function obtains the CHAD statistical data about activity and durations and start times about the
#     activities done within a particular trial.
#
#     .. warning::
#         This code must be **removed** because it is not used
#
#     :param int trial_code: the code on what trial to analyze
#     :return: a list of pandas data frame pairings for stats for duration and stats, respectively
#     :rtype: list
#     """
#
#     # get the CHAD data bout the moments
#     stats_chooser = {trial.COMMUTE_TRIAL: chad.FNAME_STATS_COMMUTE,
#                      #trial.EAT_TRIAL: chad.FNAME_STATS_EAT
#                      }
#
#     zip_chooser = { trial.SLEEP_TRIAL:  chad.FNAME_SLEEP,
#                     trial.EAT_BREAKFAST: chad.FNAME_EAT_BREAKFAST,
#                     trial.EAT_LUNCH: chad.FNAME_EAT_LUNCH,
#                     trial.EAT_DINNER: chad.FNAME_EAT_DINNER,
#                     trial.WORK_TRIAL:  chad.FNAME_WORK,
#                     }
#
#     # file names for the stats information
#     # floor the trial code to get the general trial
#     fname_stats = stats_chooser.get( trial_code, chad.FNAME_STATS_DEFAULT)
#
#     # the zip file CHAD information for the activity
#     fname_zip = zip_chooser[ trial_code ]
#
#     # create a CHAD object to access the necessary CHAD sleep data
#     c = chad.CHAD(fname_zip)
#
#     # get a list of pandas data frame tuples of stats data for duration and start time, respectively( df_dt, df_start)
#     y = [ get_chad_stats_data_PID( c.get_data(x[0]), c.get_data(x[1]) ) for x in fname_stats]
#
#     return y

# def get_chad_stats_data_PID(stats_dt, stats_start):
#
#     """
#     .. warning::
#         This function is **NOT** used
#
#     This function returns duration and start time data on entries of people that are **both** in the duration
#     data **and** start time.
#
#
#     :param pandas.core.frame.DataFrame stats_dt: CHAD data on statistical moments for duration
#     :param pandas.core.frame.DataFrame stats_start: CHAD data on statistical moments for start time
#
#     :return df_dt: the moments for the duration
#     :return df_start: the moments for the start time
#
#     :rtype: pandas.core.frame.DataFrame
#     :rtype: pandas.core.frame.DataFrame
#     """
#
#     # need to get the intersection of CHAD data
#     dt      = stats_dt.loc[stats_dt.PID.isin(stats_start.PID)]
#     start   = stats_start.loc[stats_start.PID.isin(stats_dt.PID)]
#
#     # sort both data frames by PID ("person identifier")
#     df_dt       = dt.sort_values(['PID'])
#     df_start =   start.sort_values(['PID'])
#
#     return df_dt, df_start

def get_moments(abm_list, do_periodic=False):

    """
    This function calculates both the mean and the standard deviation for start time, end time, and \
    duration for a given activity for each agent simulated.

    :param abm_list: the activity diary for a given activity for each agent
    :type abm_list: list of pandas.core.frame.DataFrame
    :param bool do_periodic: this flag indicates whether (if True) or not (if False) to do the \
    analysis on a time scale that is [-12, 12). This is useful for activities that may occur \
    over midnight.

    :return: information containing the the mean and standard deviation information for start time, \
    end time, and duration for the simulated agents for a given activity
    :rtype: numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray, \
    numpy.ndarray, numpy.ndarray
    """

    # calculate the mean start time and end time for each agent
    if do_periodic:
        # convert the start time and end time from [0, 24) time to [-12, 12) hour time if
        # needed
        abm_start_mean  = np.array([df.start.apply(mg.to_periodic).mean() for df in abm_list])
        abm_end_mean    = np.array([df.end.apply(mg.to_periodic).mean() for df in abm_list])
    else:
        abm_start_mean  = np.array([df.start.mean() for df in abm_list])
        abm_end_mean    = np.array([df.end.mean() for df in abm_list])

    # calculate the mean duration for each agent
    abm_dt_mean         = np.array([df.dt.mean() for df in abm_list])

    # caluclate the standard deviation for start time, end time, and duration for each agent
    abm_start_std   = np.array([df.start.std() for df in abm_list])
    abm_end_std     = np.array([df.end.std() for df in abm_list])
    abm_dt_std      = np.array([df.dt.std() for df in abm_list])

    return abm_start_mean, abm_start_std, abm_end_mean, abm_end_std, abm_dt_mean, abm_dt_std


# def get_residuals(abm_dt_mean, abm_start_mean, chad_dt, chad_start, p_min=0.0, p_max=1.0):
#
#     """
#     This function calculates the cumulative density function (CDF) residuals for the ABM simulations with respect
#     to the CHAD data
#
#     :param numpy.ndarray abm_dt_mean: the mean duration times on an activity in the ABM simulations
#     :param numpy.ndarray abm_start_mean: the mean start times on an activity in the ABM simulations
#     :param numpy.ndarray chad_dt: the mean duration times on an activity in the CHAD
#     :param numpy.ndarray chad_start: the mean start times on an activity in the CHAD
#     :param float p_min: the lowest percentile in the cdf to compare
#     :param float p_max: the highest percentile in the cdf to compare
#     :return:
#     """
#
#     res_dt      = residual_cdf(abm_dt_mean, chad_dt, p_min, p_max)
#     res_start   = residual_cdf(abm_start_mean, chad_start, p_min, p_max)
#
#     return res_dt, res_start

def get_simulation_data(df_list, act):

    """
    This function obtains the simulation data for a given activity from each each agent in the
    simulation.

    :param df_list: the activity diaries for each agent in the entire simulation
    :type df_list: list of pandas.core.frame.DataFrame
    :param int act: the ABMHAP activity code

    :return: the activity diary containing information for the respective activity \
    for each agent simulated
    :return: list of pandas.core.frame.DataFrame
    """
    x = [get_activity_data(df, act) for df in df_list]

    return x

# def get_test(df_list, act, do_periodic=False):
#
#     # the data for each household
#     abm_list = get_simulation_data(df_list, act)
#
#     # get the moments
#     abm_dt_mean, abm_dt_std, abm_start_mean, abm_start_std = get_moments(abm_list, do_periodic)
#
#     # the number of times each activity occurred
#     counts = [ len(x) for x in abm_list]
#
#     return abm_dt_mean, abm_dt_std, abm_start_mean, abm_start_std, counts

# def get_abm_record(abm_list, msg):
#     """
#     This function gets a record of events for each person in the abm_list
#
#     :param abm_list:
#     :param msg:
#     :return:
#     """
#     df = pd.DataFrame.from_records( [ df[msg].ravel() for df in abm_list ] )
#
#     return df

# def get_trial_info(trial_code):
#
#     """
#     This function obtains the relevant parameters specific to the activities used in the respective trial
#
#     The function returns the following in a tuple:
#
#     * the activity code
#     * the CHAD-activity sampling parameters for "good" data
#     * the file name for the CHAD activity data zip file
#
#     :param int trial_code: the specific trial identifier
#     :rtype: tuple
#     """
#
#     # get a tuple of (activity code, chad-activity parameters code, and CHAD zip file name )
#     chooser = { trial.COMMUTE_FROM_WORK: chad_params.COMMUTE_FROM_WORK,
#                 trial.COMMUTE_TO_WORK: chad_params.COMMUTE_TO_WORK,
#                 trial.EAT_BREAKFAST: chad_params.EAT_BREAKFAST,
#                 trial.EAT_LUNCH: chad_params.EAT_LUNCH,
#                 trial.EAT_DINNER: chad_params.EAT_DINNER,
#                 trial.SLEEP: chad_params.SLEEP,
#                 trial.WORK: chad_params.WORK,
#                 trial.OMNI: chad_params.OMNI,
#                 }
#
#     return chooser[trial_code]

def get_verify_fpath(fdir, act_codes):

    """
    This function returns the directories corresponding to the specified activity codes \
    where figures of activities will be stored for a specific simulation.

    :param fdir: the file path to the directory of the figure data for a specific simulation.

    :param str act_codes: the ABMHAP activity codes for a given activity
    :type act_codes: list of int

    :return: the directories corresponding to the specified activity codeds where figures \
    of the activities will be stored
    :rtype: list of str

    """
    if fdir is None:
        fdirs = [None] * len(act_codes)
    else:
        fdirs = [ (fdir + mg.KEY_2_FDIR_SAVE_FIG[x] ) for x in act_codes]

    return fdirs

# def handle_nans(data):
#
#     """
#     This function takes in the activity data of a simulation and returns the activity data without \
#     NaNs (which represent "skipped" activities)
#
#     :param numpy.ndarray data: the activity data of many individuals over various simulations
#
#     :return new_data: the data without NaNs
#
#
#     :rtype: numpy.ndarray, numpy.ndarray
#     """
#
#     # take only the non-empty activities that are not NaNs
#     y = [ x[ np.isfinite(x) ] for x in data]
#
#     # do not add empty lists/ cases where all activities are NaN
#     new_data = [x for x in y if len(x) != 0]
#
#     return new_data

def load_plot_data(fname):

    """
    This function loads the data from pickled (.pkl) figures. This assumes that the figures plotted the
    ABM data first and then the CHAD data.

    :param str fname: the filename of the saved figure (.pkl)

    :return: the x and y data for the ABM and CHAD data, respectively
    :rtype: numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray
    """

    # load the data from the pickled figure
    fig = pickle.load( open(fname, mode='rb') )
    lines = fig.axes[0].lines

    # store the appropriate data from ABM and CHAD, respectively
    [x_abm, y_abm]      = lines[0].get_data()
    [x_chad, y_chad]    = lines[1].get_data()

    return x_abm, y_abm, x_chad, y_chad


# def plot_abm_chad_histo(x_abm, x_chad, xlabel, title, bins):
#
#     """
#     This function plots a histogram of the ABM data with the respective CHAD data
#
#     :param numpy.ndarray x_abm: an array containing the ABM values to plot from each simulation
#     :param numpy.ndarray x_chad: an array containing the CHAD values to plot
#     :param str xlabel: the x-axis label
#     :param str title:  the plot title
#     :param int fig_id: the figure identifier number
#     :param numpy.ndarray bins: an array of bin data needed in plt.hist()
#
#
#     :return: None
#     """
#
#     # ABM
#     plt.hist(x_abm, bins, alpha=0.5, normed=True, label='abm')
#
#     # chad stats
#     plt.hist(x_chad, bins, alpha=0.5, normed=True, label='CHAD')
#
#     plt.xlabel( xlabel )
#     plt.ylabel( 'pdf' )
#     plt.title( title )
#     plt.legend()
#
#     return

# def plot_activity_counts(counts, act, nbins=20):
#
#     """
#
#     :param list counts: the number of times the activity was done for each person in the simulation
#     :param float act: the activity code
#     :param int nbins: the number of bins for plotting the histogram
#     :return:
#     """
#
#     # calculate relative frequencies
#     x = np.array(counts)
#
#     # plot the data in a histogram
#     # the weights give fractions for relative frequency
#     if ( len(x) != 0):
#         weights = np.zeros(x.shape) + 1 / x.size
#     else:
#         x = np.array( [0])
#         weights = np.array( [1])
#
#     plt.hist(x, weights=weights, bins=nbins)
#
#     plt.title( activity.INT_2_STR[act] )
#     plt.ylabel('Relative Frequency')
#     plt.xlabel('Counts')
#
#     return

def plot_cdf(data_abm, data_chad, xlabel, title):

    """
    This function plots the CDF for data related to the ABM and CHAD

    :param numpy.ndarray data_abm: the ABM data to be plotted
    :param numpy.ndarray data_chad: the CHAD data to be plotted
    :param str xlabel: the x-axis label
    :param str title: the title of the plot

    :return:
    """

    x_abm, y_abm    = mg.get_ecdf(data_abm)
    x_chad, y_chad  = mg.get_ecdf(data_chad)

    plt.plot(x_abm, y_abm, color='blue', label='ABM')
    plt.plot(x_chad, y_chad, color='red', label='CHAD')
    plt.ylabel('probability')
    plt.xlabel(xlabel)
    plt.title(title)
    plt.legend()

    return

def plot_cdf_new(data_abm, data_chad, fid, title, xlabel, do_periodic=False):

    """
    This function plots the cumulative distribution function (CDF) comparing \
    the ABM and CHAD data for a given activity

    :param numpy.ndarray data_abm:
    :param numpy.ndarray data_chad:
    :param int fid: the figure identifier
    :param str title: the title of the figure
    :param str xlabel: the label of the x-axis
    :param bool do_periodic: this flag indicates whether (if True) or not (if False) to convert \
    the data to a time scale that is [-12, 12). This is useful for activities that may occur \
    over midnight.

    :return: the figure of the CDF
    :rtype: matplotlib.figure.Figure
    """

    # plot duration info
    fig = plt.figure(num=fid)

    if do_periodic:
        d_abm   = mg.to_periodic(data_abm)
        d_chad  = mg.to_periodic(data_chad)
    else:
        d_abm   = data_abm
        d_chad  = data_chad

    # plot if the dataset is not empty
    if data_abm.size != 0:
        plot_cdf(d_abm, d_chad, xlabel=xlabel, title=title)

    return fig

# def plot_cdfs(activity_code, abm_dt, abm_start, chad_dt, chad_start, id_dt, id_start):
#
#     """
#      This function plots the CDF comparing the ABM and CHAD data for both activity duration and activity start time
#
#     :param float activity_code: the activity code
#     :param numpy.ndarray abm_dt: the activity mean duration from the ABM simulations
#     :param numpy.ndarray abm_start: the activity mean start time from the ABM simulations
#     :param numpy.ndarray chad_dt: the sampled CHAD duration moments
#     :param numpy.ndarray chad_start: the sampled CHAD start time moments
#     :param int id_dt: the figure identifier of the duration information
#     :param int id_start:  the figure identifier of the start time information
#     :return: the figures of the cdf of duration and start time respectively
#     """
#
#     # plot duration info
#     fig_dt = plt.figure(num=id_dt)
#     title = 'Mean ' + activity.INT_2_STR[activity_code] + ' Duration'
#
#     if abm_dt.size != 0:
#         plot_cdf(abm_dt, chad_dt, xlabel='duration [h]', title=title)
#         plt.legend()
#
#     # plot start time info
#     fig_start = plt.figure(num=id_start)
#
#     # this selects which start time should be written in periodic scale t in (-12, 12] if True
#     # the default is False
#     chooser = { activity.SLEEP: True}
#
#     do_periodic = chooser.get( activity_code, False)
#
#     if do_periodic:
#         temp_abm    = mg.to_periodic(abm_start)
#         temp_chad   = mg.to_periodic(chad_start)
#     else:
#         temp_abm    = abm_start
#         temp_chad   = chad_start
#
#     if temp_abm.size != 0:
#         plot_cdf(temp_abm, temp_chad, xlabel='start time [h]', title=title)
#         plt.legend()
#
#     title = 'Mean ' + activity.INT_2_STR[activity_code] + ' Start Time'
#     plt.title(title)
#
#
#     return fig_dt, fig_start

# def plot_data(err, x, cdf, title, xlabel, fig1, fig2, col):
#
#     # plot a histograms for duration. Use the relative error
#
#     plt.figure(fig1)
#     histo = plt.hist(err, bins=30, color=col)
#     plt.title(title)
#     plt.xlabel(xlabel)
#     plt.ylabel('count')
#
#     # plot the empirical cumulative distribution formulation
#     style = col + '.'
#
#     plt.figure(fig2)
#     plt.step(x, cdf, style)
#     plt.title('cdf ' + title)
#     plt.xlabel(xlabel)
#     plt.ylabel('probability')
#
#     plt.show()
#
#     return

# def plot_histograms(activity_code, abm_dt, abm_start, chad_dt, chad_start, id_dt, id_start):
#
#     """
#     This function plots the histograms comparing the ABM and CHAD data for both activity and duration and \
#     activity start time.
#
#     :param int activity_code: the activity code
#     :param numpy.ndarray abm_dt: the activity mean duration from the ABM simulations
#     :param numpy.ndarray abm_start: the activity mean start time from the ABM simulations
#     :param numpy.ndarray chad_dt: the sampled CHAD duration means
#     :param numpy.ndarray chad_start: the sampled CHAD start time means
#
#     :return: the figures of the duration and star ttime and histograms, respectively
#
#     """
#
#     # plot the mean sleep duration distribution for ABM and CHAD
#     bins = np.linspace(0, 24, 48)
#     title = 'Mean ' + activity.INT_2_STR[activity_code] + ' Duration Distribution'
#
#     fig_dt = plt.figure(num=id_dt)
#     plot_abm_chad_histo(abm_dt, chad_dt, xlabel='[hours]', title=title, bins=bins)
#
#     # this selects which start time should be written in periodic scale t in (-12, 12] if True
#     # the default is False
#     chooser = {activity.SLEEP: True}
#
#     # copy the array
#     abm_start = np.array(abm_start)
#
#     if chooser.get(activity_code, False):
#         bins = np.linspace(-12, 12, 48)
#         abm_start = abm_start + (abm_start > 12) * (-24)
#
#     title = 'Mean ' + activity.INT_2_STR[activity_code] + ' Start Time Distribution'
#     fig_start = plt.figure(num=id_start)
#     plot_abm_chad_histo(abm_start, chad_start, xlabel='[hours]', title=title, bins=bins)
#
#     # return the figures
#     return fig_dt, fig_start

# def residual_cdf(data_abm, data_chad, p_min=0, p_max=1.0):
#
#     """
#     This function compares the residual of the cumalative density function (CDF) of the CHAD data with the ABM data.
#     The residual is calculated as the difference in area under the CDF curves divided by the area under the
#     CHAD cdf curve.
#
#
#     :param numpy.ndarray data_abm: the data from the ABM simulation
#     :param numpy.ndarray data_chad: the data of the moments from CHAD
#     :param float p_min: the lowest percentile in the cdf to compare
#     :param float p_max: the highest percentile in the cdf to compare
#     :return: the relative error measure
#     :rtype: float
#     """
#
#     x_abm, y_abm    = mg.get_ecdf(data_abm)
#     x_chad, y_chad  = mg.get_ecdf(data_chad)
#
#     idx_abm     = (y_abm >= p_min) * (y_abm <= p_max)
#     idx_chad    = (y_chad >= p_min) * (y_chad <= p_max)
#
#     A_abm   = scipy.integrate.simps(y_abm[idx_abm], x_abm[idx_abm])
#     A_chad  = scipy.integrate.simps(y_chad[idx_chad], x_chad[idx_chad])
#
#     res = abs(A_chad - A_abm) / A_chad
#
#     return res

# def save_plots_cdf(fig_dt, fig_start, fdir):
#
#     """
#     This function saves the plots (cumulative distribution function )CDF plots for duration and start time) \
#     in a python pickle file, so that the data may be accessed again.
#
#     :param fig_dt: the CDF of the activity duration data
#     :param fig_start: the CDF of the activity start time data
#     :param str fdir: the directory in which to save the files
#
#     :return:
#     """
#
#     # the figures
#     figs = [ fig_dt, fig_start ]
#
#     # the file names
#     fnames = ['cdf_dt.pickle', 'cdf_start.pickle']
#     fnames = [(fdir + '\\' + x) for x in fnames]
#
#     # save the plots
#     analysis.save_figures(figs, fnames)
#
#     return

# def save_plots_histo(fig_dt, fig_start, fdir):
#
#     """
#     This function saves the plots (histogram for duration and start time) in a python pickle file, \
#     so that the data may be accessed again.
#
#     :param fig_dt: the histogram of the activity duration data
#     :param fig_start: the histogram of the activity start time data
#     :param str fdir: the directory in which to save the files
#
#     :return:
#     """
#
#     # the figures
#     figs = [fig_dt, fig_start]
#
#     # the file names
#     fnames = ['hist_dt.pickle', 'hist_start.pickle']
#     fnames = [(fdir + '\\' + x) for x in fnames]
#
#     # save the plots
#     analysis.save_figures(figs, fnames)
#
#     return




def plot_verify_dt(act, data_abm, data_chad, fid, do_save_fig=False, fpath=''):

    """
    This function plots the cumulative distribution function (CDFs) in order to compare \
    the duration data for the given activity from the ABMHAP simulation to the CHAD data.

    :param int act: the ABMHAP activity data
    :param numpy.ndarray data_abm: the ABMHAP duration data
    :param numpy.ndarray data_chad: the CHAD duration data
    :param int fid: the figure identifier
    :param bool do_save_fig: a flag indicating whether (if True) or not (if False) \
    to save the figure
    :param str fpath: the file path to the directory in which to save the figure

    :return:
    """

    # only plot data for start time that exists
    dt      = data_abm[ np.isfinite(data_abm) ]

    # plot the histogram of the distribution
    title   = activity.INT_2_STR[act] + ' Duration'
    xlabel  = 'Hours'

    # plot the CDFs
    fig = plot_cdf_new(dt, data_chad, fid, title=title, xlabel=xlabel, do_periodic=False)

    # save the figure
    if (do_save_fig):
        fname = fpath + '\\dt.pkl'
        analysis.save_figures([fig], [fname])

    return

def plot_verify_end(act, data_abm, data_chad, fid, do_save_fig=False, fpath=''):

    """
    This function plots the cumulative distribution function (CDFs) in order to compare \
    the end time data for the given activity from the ABMHAP simulation to the CHAD data.

    :param int act: the ABMHAP activity data
    :param numpy.ndarray data_abm: the ABMHAP end time data
    :param numpy.ndarray data_chad: the CHAD end time data
    :param int fid: the figure identifier
    :param bool do_save_fig: a flag indicating whether (if True) or not (if False) \
    to save the figure
    :param str fpath: the file path to the directory in which to save the figure

    :return:
    """

    # only plot data for start time that exists
    end     = data_abm[ np.isfinite(data_abm) ]

    # plot the histogram of the distribution
    title   = activity.INT_2_STR[act] + ' End Time'
    xlabel  = 'Hours'

    # if the activity occurs over midnight, convert the data into a [-12, 12) hour format
    do_periodic = False
    if act == activity.SLEEP:
        do_periodic = True

    # plot the CDFs of the end time
    fig = plot_cdf_new(end, data_chad, fid, title=title, xlabel=xlabel, do_periodic=do_periodic)

    # save figure
    if (do_save_fig):
        fname = fpath + '\\end.pkl'
        analysis.save_figures([fig], [fname])

    return

def plot_verify_start(act, data_abm, data_chad, fid, do_save_fig=False, fpath=''):

    """
    This function plots the cumulative distribution function (CDFs) in order to compare \
    the start time data for the given activity from the ABMHAP simulation to the CHAD data.

    :param int act: the ABMHAP activity data
    :param numpy.ndarray data_abm: the ABMHAP start time data
    :param numpy.ndarray data_chad: the CHAD start time data
    :param int fid: the figure identifier
    :param bool do_save_fig: a flag indicating whether (if True) or not (if False) \
    to save the figure
    :param str fpath: the file path to the directory in which to save the figure

    :return:
    """

    # only plot data for start time that exists
    start   = data_abm[ np.isfinite(data_abm) ]

    # plot the histogram of the distribution
    title   = activity.INT_2_STR[act] + ' Start Time'
    xlabel  = 'Hours'

    # if the activity occurs over midnight, convert the data into a [-12, 12) hour format
    do_periodic = False
    if act == activity.SLEEP:
        do_periodic = True

    # plot the CDFs
    fig = plot_cdf_new(start, data_chad, fid, title=title, xlabel=xlabel, do_periodic=do_periodic)

    # save the figure
    if (do_save_fig):
        fname = fpath + '\\start.pkl'
        analysis.save_figures( [fig], [fname])

    return

# def plot_verify(act, abm_dt_mean, abm_start_mean, chad_dt, chad_start, counts, do_histogram=False,
#                 off=0, do_save_fig=False, fpath=''):
#
#     num_plots = 5
#
#     # the figure identification numbers
#     id1, id2, id3, id4, id5 = off + np.array(list(range(num_plots)))
#
#     dt = np.array(abm_dt_mean)
#     start = np.array(abm_start_mean)
#
#     # if there is no activity data, store the duration as 0
#     dt[ np.isnan(dt) ] = 0
#
#     # only plot data for start time that exists
#     start = start[ np.isfinite(start) ]
#
#     # plot the histogram of the distribution
#     if do_histogram:
#         histo_dt, histo_start = plot_histograms(act, dt, start, chad_dt['mu'].values,
#                                                 chad_start['mu'].values, id_dt=id1, id_start=id2)
#
#     # plot the CDFs of the distributions
#     cdf_dt, cdf_start = plot_cdfs(act, dt, start, chad_dt['mu'].values,
#                                   chad_start['mu'].values, id_dt=id3, id_start=id4)
#
#     plt.figure(num=id5)
#     plot_activity_counts(counts, act)
#
#     # update offset
#     off = off + num_plots
#
#     # save the plots
#     if (do_save_fig):
#
#         if do_histogram:
#             save_plots_histo(histo_dt, histo_start, fdir=fpath)
#
#         save_plots_cdf(cdf_dt, cdf_start, fdir=fpath)
#
#     return off

# def write_abm_data(activity_code, df_dt, df_start):
#
#     """
#     This function writes the ABM data to a file.
#
#     :param int activity_code: the identifier for an activity
#     :param pandas.core.frame.DataFrame df_dt: the activity duration information for the ABM
#     :param pandas.core.frame.DataFrame df_start: the activity start time information for the ABM
#
#     :return:
#     """
#
#     # activity name
#     act_name = activity.INT_2_STR[activity_code]
#
#     # parent directory
#     dir_parent = os.path.dirname(os.getcwd())
#
#     # write the ABM data into the appropriate directory
#     fdir = dir_parent + str('\\data')
#
#     fname = fdir + '\\abm_' + act_name + '_dt.csv'
#     df_dt.to_csv(fname)
#
#     fname = fdir + '\\abm_' + act_name + '_start.csv'
#     df_start.to_csv(fname)
#
#     return

def run(num_process, num_hhld, num_batch):

    """
    This function runs the simulations.

    :param int num_process: the number of processors (cores)
    :param int num_hhld: the number of households per core per batch
    :param int num_batch: the number of batches

    :return: the results of the simulation
    :rtype: driver_result.Driver_Result
    """

    fname_trials, fname_data = driver.run_everything(num_process, num_hhld, num_batch)

    x = mg.load(fname_data)

    return x

def verify(trial_code, demo, chad_param_list, df_list, do_plot, do_print=False, fdir=None):

    """
    This code compares the results of the ABM to the CHAD data by comparing the cumulative distribution function \
    (CDF) of the duration and start times predicted by the ABM and that of respective CDFs from the CHAD data.

    :param int trial_code: the trial code identifier
    :param int demo: the demographic identifier
    :param chad_param_list: that limit the CHAD parameters sampling in initializing the households
    :type chad_param_list: list of :class:`chad_params.CHAD_params`
    :param df_list: contains the activity diaries for each household
    :type df_list: list of pandas.core.frame.DataFrame

    :param bool do_plot: a flag to indicate whether (True) or not (False) to plot
    :param bool do_print: a flag to indicate whether (True) or not (False) to print various messages to the screen
    :param list fdir: a list of file directories needed to save the figures
    :return:
    """

    # get the activity codes for a given trial
    act_codes = trial.TRIAL_2_ACTIVITY[trial_code]

    # the directories for the respective activities. This is used for saving the figures
    fdirs = get_verify_fpath(fdir, act_codes)

    # figure identifier
    fid = 0

    for act, fpath in zip(act_codes, fdirs):

        if (do_print):
            msg = 'starting analysis for the ' + activity.INT_2_STR[act] + ' activity .....'
            print(msg)

        # this is to see if the analysis of the moments for start time needs to be in [-12, 12)
        # instead of [0, 24) format
        chooser     = {activity.SLEEP: True, }
        do_periodic = chooser.get(act, False)

        # get the CHAD data
        # this is here to access the data frames from t.initialize()
        chad_start, chad_end, chad_dt, chad_record = \
            analysis.get_verification_info(demo=demo, key_activity=act, sampling_params=chad_param_list)

        # the sampling parameters for 1 household
        s_params                = chad_param_list[0]

        # get the raw ABM data
        abm_list = get_simulation_data(df_list, act)

        # the ABM moments
        abm_start_mean, abm_start_std, abm_end_mean, abm_end_std, abm_dt_mean, abm_dt_std \
            = get_moments(abm_list, do_periodic)

        # create the plots
        if (do_plot):

            if s_params.do_start:
                fid = fid + 1
                plot_verify_start(act, abm_start_mean, chad_start['mu'].values, fid=fid, do_save_fig=False, fpath='')

            if s_params.do_end:
                fid = fid + 1
                plot_verify_end(act, abm_end_mean, chad_end['mu'].values, fid=fid, do_save_fig=False, fpath='')

            if s_params.do_dt:
                fid = fid + 1
                plot_verify_dt(act, abm_dt_mean, chad_dt['mu'].values, fid=fid, do_save_fig=False, fpath='')

    return

# ======================================================
# RUN
# ======================================================

if __name__ == '__main__':


    # this flag indicates whether (if True) or not (if False) simulation data will be loaded from a pre-existing file
    # or generated
    do_load = False

    #
    # get the data
    #

    if do_load:

        # load the simulation data

        # load the simulation data from a pre-existing file
        fname = dp.fpath + '\\2018_03_29\\n0004_d007\\data_adult_work.pkl'
        x = mg.load(fname)

        print('loaded data from %s' % fname)
    else:

        # create the data
        condition   = dp.do_save
        msg         = 'The driver_params must have the save flag set to TRUE in order to run!'

        # assert condition
        assert condition, msg

        num_process, num_hhld, num_batch = driver.get_cmd_line_params()

        # run the simulation
        x = run(num_process, num_hhld, num_batch)

    #
    # set up the figures
    #

    # the general directory to save figures
    figure_dir = mg.FDIR_SAVE_FIG

    # the directory for the isolated activity and global activity runs, respectively
    fdir_solo = figure_dir + '\\solo'
    fdir_omni = figure_dir + '\\omni'

    # flags
    do_plot     = True

    #
    # choose activity with the corresponding trial to test the data
    #
    trial_code = trial.EAT_BREAKFAST

    # get the appropriate parameters for the given activity (trial code and figure directory)
    chooser = { trial.COMMUTE_TO_WORK: fdir_solo + '\\commute\\to_work',
                trial.COMMUTE_FROM_WORK: fdir_solo + '\\commute\\from_work',
                trial.EAT_BREAKFAST: fdir_solo + '\\eat\\breakfast',
                trial.EAT_DINNER: fdir_solo + '\\eat\\dinner',
                trial.EAT_LUNCH: fdir_solo + '\\eat\\lunch',
                trial.SLEEP: fdir_solo + '\\sleep',
                trial.WORK: fdir_solo + '\\work',
                trial.OMNI: fdir_omni,
                }

    # get the trial code and figure directory (used for saving figures)
    fig_dir = chooser[trial_code]


    #
    # Run some analysis
    #

    # obtain data from each simulation
    df_list = x.get_all_data()

    evaluation.compare_abm_to_chad(x.demographic, df_list, trial_code)

    # show the plots
    if (do_plot):
        plt.show()
