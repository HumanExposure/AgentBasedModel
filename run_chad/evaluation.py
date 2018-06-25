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
This module is used to for evaluating the accuracy of the Agent-Based Model of Human \
Activity Patterns (ABMHAP) simulation results vs. Consolidated Human Activity Database \
(CHAD) data.
"""

# ===========================================
# import
# ===========================================

# python modules
import sys, zipfile
sys.path.append('..\\source')
sys.path.append('..\\run')

# plotting capability
import matplotlib.pylab as plt

# mathematical capability
import numpy as np

# dataframe capability
import pandas as pd

# statistical capability
import statsmodels as sm

# for smoothing
from scipy import integrate
from scipy import interpolate
from scipy.stats import kde

# ABMHAP modules
import my_globals as mg
import demography as dmg
import analysis, activity, chad, diary, temporal, trial

# ===========================================
# constants
# ===========================================

# # given an activity code, give the name of the corresponding .zip file for the CHAD data
# ACTIVITY_TO_CHAD = {activity.COMMUTE_FROM_WORK: chad.FNAME_COMMUTE_FROM_WORK,
#                 activity.COMMUTE_TO_WORK: chad.FNAME_COMMUTE_TO_WORK,
#                 activity.EAT_BREAKFAST: chad.FNAME_EAT_BREAKFAST,
#                 activity.EAT_DINNER: chad.FNAME_EAT_DINNER,
#                 activity.EAT_LUNCH: chad.FNAME_EAT_LUNCH,
#                 activity.SLEEP: chad.FNAME_SLEEP,
#                 activity.WORK: chad.FNAME_WORK,}
#
# ACTIVITY_TO_DATA = { activity.COMMUTE_FROM_WORK: chad.FNAME_COMMUTE_FROM_WORK,
#                      activity.COMMUTE_TO_WORK: chad.FNAME_COMMUTE_TO_WORK,
#                      activity.EAT_BREAKFAST: chad.FNAME_EAT_BREAKFAST,
#                      activity.EAT_DINNER: chad.FNAME_EAT_DINNER,
#                      activity.EAT_LUNCH: chad.FNAME_EAT_LUNCH,
#                      activity.SLEEP: chad.FNAME_SLEEP,
#                      activity.WORK: chad.FNAME_WORK,
# }

# ===========================================
# functions
# ===========================================

def compare_abm_to_chad(demo, df_list, trial_code, fidx=100, do_save=False, fpath=None):

    """
    This function compares the results of the ABMHAP to the CHAD data by showing by

    #. plotting cumulative distribution functions (CDF) of the predicted (ABMHAP) and \
    observed (CHAD) single-day data for each activity
    #. plotting the residual (that difference between the CDFs) between the predicted \
    (ABMHAP) and observed (CHAD) data for each activity

    :param int demo: the demographic identifier
    :param df_list: the ABMHAP activity diaries to compare
    :type df_list: list of  pandas.core.frame.DataFrame
    :param int trial_code: the trial identifier
    :param int fidx: the figure identifier for the first figure in a series of figures
    :param bool do_save: a flag indicating whether (if True) or not (if False) to save \
    the figures
    :param str fpath: the file path of the figures that are to be saved

    :return:
    """

    # the activity codes
    act_codes = trial.TRIAL_2_ACTIVITY[trial_code]

    # the .zip file for the CHAD data corresponding to the demographic
    fname_zip   = dmg.FNAME_DEMOGRAPHY[demo]

    # open the .zip file
    z           = zipfile.ZipFile(fname_zip, mode='r')

    # for each activity compare the ABMHAP results to the CHAD data
    for act in act_codes:

        # the ABM data (predicted)
        df_abm  = sample_activity_abm(df_list, act)

        #
        # the CHAD single event data (observed)
        #
        fname_record    = chad.FNAME_RECORD_OMNI[act][0]

        # get the single-day data records for the given activity
        df_obs          = get_solo_data(z, fname_record)

        # plot the comparision of the predicted (ABMHAP) and observed data (CHAD)
        fid_last        = compare_abm_to_chad_help(df_abm=df_abm, df_obs=df_obs, act_code=act, fidx=fidx, \
                                                   do_save=do_save, fpath=fpath)
        # the new figure identifier
        fidx            = fid_last + 1

    # close the .zip file
    z.close()

    return

def compare_abm_to_chad_help(df_abm, df_obs, act_code, fidx, do_save, fpath):

    """
    This function compares the results of the ABMHAP to the CHAD data for a given activity by

    #. plotting cumulative distribution functions (CDF) of the predicted (ABMHAP) and \
    observed (CHAD) single-day data for each activity
    #. plotting the residual (that difference between the CDFs) between the predicted \
    (ABMHAP) and observed (CHAD) data for each activity

    :param pandas.core.frame.DataFrame df_abm: the predicted (ABMHAP) data for the respective activity
    :param pandas.core.frame.DataFrame df_obs: the single-day observed (CHAD) data for the respective activity
    :param float act_code: the activity code
    :param int fidx: the figure identifier of the first figure
    :param bool do_save: a flag indicating whether (if True) or not (if False) to save \
    the figures
    :param str fpath: the file path of the figures that are to be saved

    :return: the last figure identifier plotted
    :rtype: int
    """

    # sample with replacement

    # these activities could potential start before midnight and end after midnight
    chooser     = {activity.SLEEP: True, }

    # a flag indicating whether (if True) or not (if False) to represent the time in [-12, 12)
    do_periodic = chooser.get(act_code, False)

    # the number of plots to make in plot()
    # (start, end, dt) * (cdf + inverse_cdf + res + inverse_res + res_scaled + res_scaled_inv )
    n_plots = 6

    # figure ids
    fids = fidx + np.arange(n_plots)

    if not df_abm.empty:

        # the number of samples
        # normally the CHAd dataframe should be much larger than the ABM runs. In the rare event, we run more CHAD
        # simulations than the CHAD observed data, we can still do analysis

        # sample the predicted and observed data
        x_abm   = df_abm.sample( n=len(df_abm), replace=False )

        #
        # need to sample a random person and a random day
        #

        # randomly choose the person to sample
        pid     = np.random.choice( df_obs.PID.unique(), 3 * len(df_obs), replace=True )

        # group the data by pid
        gb      = df_obs.groupby('PID')

        # randomly choose 1 activity event from the person
        x_obs   = pd.concat( [ gb.get_group(x).sample(1) for x in pid ] )

        # the number of times that CDF was sampled
        N = int(1e4) + 1

        # get the duration data
        x_dt, cdf_dt, inv_cdf_dt            = residual_analysis(pred=x_abm.dt.values, obs=x_obs.dt.values, N=N)

        # get the start time data
        x_start, cdf_start, inv_cdf_start   = residual_analysis(pred=x_abm.start.values, obs=x_obs.start.values, \
                                                                N=N, do_periodic=do_periodic)

        # get the end time data
        x_end, cdf_end, inv_cdf_end = residual_analysis(pred=x_abm.end.values, obs=x_obs.end.values, \
                                                              N=N, do_periodic=do_periodic)

        #
        # plot the distribution data for duration, start time, and end time
        #

        # quantile range information
        q = np.linspace(0, 1, N)

        # plot duration results
        figs_dt = plot(x_dt, q, cdf_dt, inv_cdf_dt, act_code, fids=fids, do_hours=False, dname='Duration')

        # plot start time results
        fids = fids + n_plots
        figs_start = plot(x_start, q, cdf_start, inv_cdf_start, act_code, fids=fids, do_hours=True, dname='Start Time')

        # plot end time results
        fids = fids + n_plots
        figs_end = plot(x_end, q, cdf_end, inv_cdf_end, act_code, fids=fids, do_hours=True, dname='End Time')

        # save the plots
        if do_save:
            save_figures(act=act_code, figs_start=figs_start, figs_end=figs_end, figs_dt=figs_dt, fpath=fpath)

    # return the last figure ID plotted
    return fids[-1]
#
# def get_diary_list(u_list):
#
#     """
#     Given all of the simuluation data and creates a list of data frames showing the activity diary for each person \
#     in the simulation.
#
#     :param list u_list: the simulation data (:class:`universe.Universe`) for each household simulation
#     :return:
#     """
#     # each activity diary in the simulation
#     diary_list = list()
#
#     # the time of each step in the simulation [universal time, minutes]
#     for u in u_list:
#
#         # the time in the simulation
#         t = u.hist_time
#
#         # the household diary
#         diary_hhld = [ diary.Diary(t, p.hist_activity, p.hist_local) for p in u.people ]
#
#         diary_list.append( diary_hhld )
#
#     # 'flatten' out the list so that all the diaries are in 1 list
#     df_list = [ item.df for x in diary_list for item in x]
#
#     return df_list

# def get_ecdf(data):
#
#     """
#     This function creates the empirical cumulative distribution function (ECDF) given data
#
#     :param numpy.ndarray data:
#     :return: the ECDF function
#
#     """
#     ECDF = sm.distributions.ECDF
#
#     f = ECDF(data)
#
#     return f

# def get_multi_data(z, fname, N):
#
#     """
#
#     :param zipfile z: the zipfile of the demographic data
#     :param str fname:
#     :return:
#     """
#
#     # the data of the activity of interest
#     df  = pd.read_csv( z.open(fname) )
#
#     # group data by the person identifier
#     gb  = df.groupby('PID')
#
#     # the unique person identifiers
#     pid = df.PID.unique()
#
#     # indices (boolean) of entries with only 1 day
#     idx = np.array( [ len( gb.get_group(x) ) >= N for  x in pid ] )
#
#     # the identifiers of only 1 day data
#     pid_solo = pid[idx]
#
#     # returns true if an entry is within pid_solo
#     f = lambda x: x in pid_solo
#
#     # the solo data
#     # the solo data
#     result = df[ df.PID.apply(f) ]
#
#     return result

def get_solo_data(z, fname):

    """
    This function gets the single-day data from individuals with only single-day records \
     within CHAD.

    :param zipfile z: the zipfile of the demographic data
    :param str fname: the file name for the CHAD individual records data

    :return: the CHAD single-day data
    :rtype: pandas.core.frame.DataFrame
    """

    # the data of the activity of interest
    df  = pd.read_csv( z.open(fname) )

    # group data by the person identifier
    gb  = df.groupby('PID')

    # the unique person identifiers
    pid = df.PID.unique()

    # indices (boolean) of entries with only 1 day
    idx = np.array( [ len( gb.get_group(x) ) == 1 for  x in pid ] )

    # the identifiers of only 1 day data
    pid_solo = pid[idx]

    # returns true if an entry is within pid_solo
    f = lambda x: x in pid_solo

    # the solo data
    result = df[ df.PID.apply(f) ]

    return result

def plot(x, q, cdf, inv_cdf, act_code, fids, do_hours=True, dname=None):

    """
    This function plots the following results of cumulative distribution function (CDF):

    #. CDFs comparing the predicted and observed values
    #. CDFs showing the residual
    #. CDFs showing the scaled residual
    #. Inverted CDFs comparing the predicted and observed values
    #. Inverted CDFs showing the residual
    #. Inverted CDFs showing the scaled residual

    :param numpy.ndarray x: the range of values of the data
    :param numpy.ndarray q: the qunatiles
    :param numpy.ndarray cdf: the cumulative distribution function in units of percentage
    :param numpy.ndarray inv_cdf: the cumulative distribution function in units of time
    :param numpy.ndarray act_code: the activity codes of the respective activities
    :param numpy.ndarray fids: the figure identifiers
    :param bool do_hours: a flag indicating whether to plot the inverted CDF data in hours (if True) \
    or minutes (if false)
    :param str dname: the name of the data to be plotted
    :param float off: the percentage in which to put a vertical line indicating both the bottom and top \
    off-percentage of the data

    :return: a figure containing CDFs comparing the predicted and observed values, \
    a figure containing CDFs showing the residual, \
    a figure containing CDFs showing the scaled residual, \
    a figure containing Inverted CDFs comparing the predicted and observed values, \
    a figure containing Inverted CDFs showing the residual, \
    a figure containing Inverted CDFs showing the scaled residual

    :rtype: matplotlib.figure.Figure, matplotlib.figure.Figure, matplotlib.figure.Figure \
    matplotlib.figure.Figure, matplotlib.figure.Figure, matplotlib.figure.Figure
    """

    # the amount of minutes in 1 hour
    HOUR_2_MIN  = temporal.HOUR_2_MIN

    # the string version of the name
    act_name = activity.INT_2_STR[act_code]

    # if no name for the activity name, assign one
    if dname is None:
        msg = act_name
    else:
        msg = '%s %s' % (act_name, dname)

    # make an iterator for figure identifiers
    fid = iter(fids)

    #
    # plot the cdf analysis
    #

    # plot the CDFs comparing the predicted and observed data
    fig_cdf = plt.figure( next(fid) )
    plot_predicted_observed(x, cdf.pred.values, cdf.obs.values, xlabel='Hours', ylabel='Probability',
                            title=msg + ' CDF')

    # plot the residuals of the CDFs that compared the predicted and observed data
    fig_res = plt.figure( next(fid) )
    plot_residual(x, cdf.res.values, xlabel='Hours', ylabel='Probability', title=msg + ' CDF Residual')

    # plot the scaled residuals of the CDFs that compared the predicted and observed data
    fig_res_scaled = plt.figure(next(fid))
    plot_residual(x, cdf.res_scale.values, xlabel='Hours', ylabel='Standard Deviations', title=msg + ' CDF Residual')

    #
    # plot the inverse cdf analysis
    #

    # make sure the data reflects the wanted units
    if do_hours:
        ylabel, units = 'Hours', 1.0,
    else:
        ylabel, units = 'Minutes', HOUR_2_MIN

    # plot the CDFs comparing the predicted and observed data
    fig_cdf_inv = plt.figure( next(fid) )
    plot_predicted_observed(q, inv_cdf.pred.values * units, inv_cdf.obs.values * units,
                            xlabel='Quantile', ylabel=ylabel, title=msg + ' Inverted CDF')

    # plot the inverted residuals of the CDFs that compared the predicted and observed data
    fig_res_inv = plt.figure( next(fid) )
    plot_residual(q, inv_cdf.res.values * units, xlabel='Qunatile', ylabel=ylabel,
                  title=msg + ' Inverted CDF Residual')

    # plot the inverted scaled residuals of the CDFs that compared the predicted and observed data
    fig_res_inv_scaled = plt.figure( next(fid) )
    plot_residual(q, inv_cdf.res_scale.values, xlabel='Qunatile', ylabel='Standard Deviations',
                  title=msg + ' Inverted CDF Residual')

    return fig_cdf, fig_res, fig_res_scaled, fig_cdf_inv, fig_res_inv, fig_res_inv_scaled


def plot_predicted_observed(x, pred, obs, xlabel, ylabel, title):

    """
    Plot the predicted (ABMHAP) and observed (CHAD) data.

    :param numpy.ndarray x: the x-axis
    :param numpy.ndarray pred: the predicted (ABMHAP) values
    :param numpy.ndarray obs: the observed (CHAD) values from data
    :param str xlabel: the x-axis label
    :param str ylabel: the y-axis label
    :param str title: the title of the figure

    :return:
    """

    # plot the title
    plt.title(title)

    # plot the predicated data
    plt.plot(x, pred, 'b', label='ABM')

    # plot the observed data
    plt.plot(x, obs, 'r', label='Observed')

    # set the y-axis label
    plt.ylabel(ylabel)

    # set the x-axis label
    plt.xlabel(xlabel)

    # set the legend
    plt.legend(loc='best')

    return

def plot_residual(x, res, xlabel='', ylabel='', title='', color='r', label='Residual'):

    """
    This function plots the residual between cumulative distribution functions (CDFs) \
    the ABMHAP and CHAD data.

    :param numpy.ndarray x: the x-axis data
    :param numpy.ndarray res: the residual :math:`r(x)`
    :param str xlabel: the x-axis label
    :param str ylabel: the y-axis label
    :param str title: the title of the plot
    :param str color: the color of the plot
    :param str label: the label of the plot

    :return:
    """

    # plot the title
    plt.title(title)

    # plot the residual data
    plt.plot(x, res, color=color, label=label)

    # plot the y-axis label
    plt.ylabel(ylabel)

    # plot the x-axis label
    plt.xlabel(xlabel)

    # set the legend
    plt.legend(loc='best')

    return

def residual(pred, obs, x):

    """
    This function analyzes the residual between predicted values and observed values. Given the predicted and \
    observed values, this function does the following:

    #. Compute the empirical cumulative distribution function (CDF) between the predicted and observed data \
    in units [quantile vs hours]
    #. Compute the residual in the CDF between observed and predicted data

        .. math::
            r(x) = cdf_{observed}(x) - cdf_{predicted}(x)

    #. Invert the residual so that the CDFs and residuals are in units [minutes vs quantile]

    :param numpy.ndarray pred: the predicted (ABMHAP) values used to make the empirical CDF
    :param numpy.ndarray obs: the observed (CHAD) values used to make the empirical CDF
    :param numpy.ndarray x: the x-values
    :param bool do_scaling: this scales the inverted cdf residual by the standard deviation of the observed values

    :return: the data for the cumulative distribution data (predicted, observed, residual, and scaled residual), \
    the data for the inverted cumulative distribution data (predicted, observed, residual, and scaled residual)
    :rtype: pandas.core.frame.DataFrame, pandas.core.frame.DataFrame
    """

    #
    # CDF
    #

    # smooth probability density functions
    f_obs   = kde.gaussian_kde(obs)
    f_pred  = kde.gaussian_kde(pred)

    # the density vectors
    d_obs   = f_obs(x)
    d_pred  = f_pred(x)

    # the cumalative distribution functions
    cdf_obs     = integrate.cumtrapz(y=d_obs, x=x, initial=0)
    cdf_pred    = integrate.cumtrapz(y=d_pred, x=x, initial=0)

    # the residual in the CDFs
    res         = cdf_obs - cdf_pred
    res_scaled  = res / np.std(cdf_obs)

    #
    # the inverted CDF
    #

    # create functions that represent the inverted cdf
    f_inv_obs   = interpolate.interp1d(x=cdf_obs, y=x)
    f_inv_pred  = interpolate.interp1d(x=cdf_pred, y=x)

    # the probability
    p_max   = min( cdf_obs.max(), cdf_pred.max() )
    p       = np.linspace( 0, p_max, num=len(x) )

    # the inverted of the CDF
    cdf_inv_obs     = f_inv_obs(p)
    cdf_inv_pred    = f_inv_pred(p)

    res_inv         = (cdf_inv_obs - cdf_inv_pred) * (-1)
    res_inv_scaled  = res_inv / np.std(obs)

    #
    # Output
    #

    # combine all of the information into a data frame
    y_data      = {'pred': cdf_pred, 'obs': cdf_obs, 'res': res, 'res_scale': res_scaled}
    y_inv_data  = {'pred': cdf_inv_pred, 'obs': cdf_inv_obs, 'res': res_inv, 'res_scale': res_inv_scaled}

    # the cumulative distribution data
    cdf     = pd.DataFrame(y_data)

    # the inverted cumulative distribution data
    inv_cdf = pd.DataFrame(y_inv_data)

    return cdf, inv_cdf

def residual_analysis(pred, obs, N=int(1e3+1), do_periodic=False):

    """
    This function takes the predicted and observed values and computes the respective cumulative distribution \
    functions (CDFs) in units percentage and the inverted CDF which is the CDF in units of minutes.

    :param numpy.ndarray pred: the predicted values
    :param numpy.ndarray obs: the observed values
    :param int N: the number of points of the CDF vector
    :param bool do_periodic: a flag to see if the time data should be in a [-12, 12) hour format

    :return: the x values, CDF of residual, inverted CDF of residual
    :rtype: numpy.ndarray, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame
    """

    # combine two arrays
    g = lambda x, y: np.array(x.tolist() + y.tolist())

    # offset
    off = 15e-1

    # combine the data
    combo = g(pred, obs)

    # put the data in [-12, 12) format instead of [0, 24) hour format
    if do_periodic:
        combo   = mg.to_periodic(combo)
        pred    = mg.to_periodic( np.array(pred) )
        obs     = mg.to_periodic( np.array(obs) )

    # get the upper and lower bounds of the data
    x_min, x_max = np.min(combo) - off, np.max(combo) + off

    # get the x values in the range of the cdfs
    x = np.linspace(x_min, x_max, num=N)

    # compute the residual
    cdf, inv_cdf = residual(pred=pred, obs=obs, x=x)

    return x, cdf, inv_cdf

def sample_activity_abm(df_list, act):

    """
    Given an activity type, this function looks at each activity diary and samples 1 event of that activity type \
    should that diary have a matching activity-entry.

    .. note::
        Because the work activity technically occurs twice (1 event before lunch and 1 event after lunch), the \
        activity needs to be merged as one event in order for the analysis to be correct.

    :param df_list: the activity diaries
    :type df_list: list of pandas.core.frame.DataFrame
    :param float act: the activity code

    :return: the sampled activities
    :rtype: pandas.core.frame.DataFrame
    """

    acts = list()

    for df in df_list:

        # ignore the last ac
        # get all of the data frame for the select activity

        # ignore the first and last entry in the diary
        data = df[1:-1]

        # get the data for the given activity
        data = data[ data.act == act ]

        # add activity event data to the list
        if not data.empty:

            # take into account that the work "event" consists of two (or more) work activity-diary entries
            if act == activity.WORK:
                x = sample_activitiy_abm_work(data)
            else:
                x = data.sample(1)

            # if there are multiple activities on that day, choose 1 randomly
            acts.append( x )

    # store all of the results in pandas data frame
    if len(acts) == 0:
        df = pd.DataFrame(columns=diary.COLNAMES)
    else:
        df = pd.concat(acts)

    return df

def sample_activitiy_abm_work(df):

    """
    This function is used in order to sample a random day of work activity data from the ABM. This function takes \
    takes into account that 1 work "event" consists of multiple work activity-diary entries.

    .. note::
        This function assumes that df only contains work activity data and is **NOT** empty

    .. note::
        The duration data here is the end of the last event - minus the start of the first event. \
        This is done to mimic how the duration data is stored in CHAD.

    :param pandas.core.frame.DataFrame df: the diary of work activities for an individual

    :return:the sampled work data
    :rtype: pandas.core.frame.DataFrame
    """

    # sample the work activities on a random day
    day = df.day.sample(1).values[0]

    # get all of the activities in that day
    df_day = df[df.day == day]

    # if there is more than 1 activity-entry on the given day
    if len(df_day) == 1:
        x = df_day
    else:
        # choose a specific day
        x = df_day.sample(1)

        # the first event of the day
        x.start = df_day.iloc[0].start

        # the last event of the day
        x.end = df_day.iloc[-1].end
        x.day = df_day.iloc[-1].day

        # duration is the end of the last event - minus the start of the first event
        x.dt = (x.end - x.start) % 24

    return x

def save_figs_dt(figs, fpath):

    """
    This function save plots about the activity duration.

    :param tuple figs: a tuple of figures to save about activity duration data
    :param str fpath: the specific file path in which to plot the data

    :return:
    """

    fnames = ['\\cdf_dt.pkl', '\\res_dt.pkl', '\\res_scaled_dt.pkl', \
              '\\cdf_inv_dt.pkl', '\\res_inv_dt.pkl', '\\res_inv_scaled_dt.pkl']

    fnames = [(fpath + x) for x in fnames]

    # save the figures
    analysis.save_figures(figs, fnames)

    return

def save_figs_end(figs, fpath):
    """
    This function save plots about the activity end time.

    :param tuple figs: a tuple of figures to save about activity end time data
    :param str fpath: the specific file path in which to plot the data
    :return:
    """

    fnames = ['\\cdf_end.pkl', '\\res_end.pkl', '\\res_scaled_end.pkl', \
              '\\cdf_inv_end.pkl', '\\res_inv_end.pkl', '\\res_inv_scaled_end.pkl']

    fnames = [(fpath + x) for x in fnames]

    # save the figures
    analysis.save_figures(figs, fnames)

    return

def save_figs_start(figs, fpath):

    """
    This function save plots about the activity start time.

    :param tuple figs: a tuple of figures to save about activity start time data
    :param str fpath: the specific file path in which to plot the data
    :return:
    """

    fnames = ['\\cdf_start.pkl', '\\res_start.pkl', '\\res_scaled_start.pkl', \
              '\\cdf_inv_start.pkl', '\\res_inv_start.pkl', '\\res_inv_scaled_start.pkl']

    fnames = [(fpath + x) for x in fnames]

    # save the figures
    analysis.save_figures(figs, fnames)

    return

def save_figures(act, figs_start, figs_end, figs_dt, fpath):

    """
    This function saves the plotted figures about duration and start time data of the results from \
    :func:`compare_abm_to_chad`.

    :param int act: the activity code
    :param tuple figs_start: a tuple of figures to save about activity start time data about the random day sampling
    :param tuple figs_end: a tuple of figures to save about activity end time data about the random day sampling
    :param tuple figs_dt: a tuple of figures to save about activity duration data about the random day sampling
    :param str fpath: the general file path to plot the data

    :return:
    """

    # plot the results of the
    fpath_new = fpath + mg.KEY_2_FDIR_SAVE_FIG[act] + mg.FDIR_SAVE_FIG_RANDOM_DAY

    # save the duration and start time data, respectively
    save_figs_start(figs_start, fpath_new)
    save_figs_end(figs_end, fpath_new)
    save_figs_dt(figs_dt, fpath_new)

    return

