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
This module contains information and functions for plotting various data related to the algorithm. In short,
this module is a plotting library for the algorithm.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===========================================
# import
# ===========================================
import sys, pickle
sys.path.append('..\\source')

# plotting capabilities
import matplotlib.pylab as plt

# mathematical capabilities
import numpy as np

# data frame capability
import pandas as pd

# agent-based model modules
import my_globals as mg
import activity, need, temporal

# ===========================================
# import
# ===========================================
def calc_weight(x, threshold=need.THRESHOLD):

    """
    This function calculates the weight value corresponding to a given value \
    of satiation and threshold value.

    :param numpy.ndarray x: the satiation values from an agent
    :param float threshold: the threshold value for a need

    :return: an array of the weight values
    """

    # the weights
    w = np.zeros(x.shape)

    # the index of non-zero value weights
    i = x <= (threshold + need.EPS_THRESHOLD)

    #  calculate the non-zero value weights
    w[i] = 1 / ( x[i] + need.EPS)

    return w

def calc_log_weight(w):

    """
    This function calculates the log10 of the weights. To avoid the possibility of getting an \
    error due to taking log10(w=0), we zero-valued weight values to None.

    :param numpy.ndarray w: the values of the weights of a corresponding need

    :return: the log10 for the non-zero values of the weights
    """

    # copy the value of the weights of a corresponding need
    y   = np.array(w)

    # indices of zero values of weights
    i   = y == 0

    # set zero-valued weights to None in order to avoid taking log10(0)
    y[i]    = None

    # take the log10 of the weights
    y   = np.log10(y)

    return y


def get_figure_data(fpaths, fpath_figure_save, fname, fnames_load=None, do_single_day=False):

    """
    This function gets figure data from the subplots of cumulative distribution functions (CDFs)
    of activity-parameters (start time, end time, and duration).

    :param fpaths: a list of file paths of the figure data for each activity to load
    :type fpaths: list of str
    :param str fpath_figure_save: the file path to save the figure
    :param str fname: the file name (no file path) to save the data
    :param fnames_load: the ending of the file names of the figure files to load (start time, end time, duration)
    :type fnames_load: list of str
    :param bool do_single_day: a flag indicating whether to load single-day (if True) or \
    longitudinal(if False) figure data

    :return: the x and y values of the lines in the figure for start time, end time, and duration plots
    :rtype: list, str
    """

    # file names load
    if fnames_load is None:
        fname_start, fname_end, fname_dt = '\\start.pkl', '\\end.pkl', '\\dt.pkl'
    else:
        fname_start, fname_end, fname_dt = fnames_load

    # change the file path to reflect whether or not to load single-day data
    if do_single_day:
        fpaths_temp = [(x + '\\random_day') for x in fpaths]
    else:
        fpaths_temp = fpaths

    #
    # store the file names
    #

    # the file names to load the start time data
    fnames_start    = [(x + fname_start) for x in fpaths_temp]

    # the file names to load the end time data
    fnames_end      = [(x + fname_end) for x in fpaths_temp]

    # the file names to load the duration data
    fnames_dt       = [(x + fname_dt) for x in fpaths_temp]

    # the file name for saving the combined subplot
    fname_subplot   = fpath_figure_save + fname

    #
    # load the figure data
    #

    # load the figure data for start time data
    data_list_start = [load_fig_data(x) for x in fnames_start]

    # load the figure data for end time data
    data_list_end   = [load_fig_data(x) for x in fnames_end]

    # load the figure data for duration data
    data_list_dt    = [load_fig_data(x) for x in fnames_dt]

    # store the data about the figures: start time, end time, and duration
    data_list_all   = [data_list_start, data_list_end, data_list_dt]

    return data_list_all, fname_subplot

def get_satiation_and_weight(p, start_day, end_day):

    """
    This function obtains the satiation values and weight values for the agent during the simulation over the
    range of the selected days.

    :param person.Person p: the agent whose satiation and weight values are to be plotted
    :param int start_day: the day to start plotting
    :param int end_day: the day to end plotting

    :return: a tuple of an array of the selected time (in hours), a list of the satiation values, and \
    a list of the weights for the respective times
    """

    # the amount of minutes in 1 day
    DAY_2_MIN = temporal.DAY_2_MIN

    # get the indices that have data
    idx = p.H[:, 0] != -1

    # the times during the simulation
    t = p.clock.hist_time[idx]

    # convert the start and end times from days into minutes
    start = start_day * DAY_2_MIN
    end = end_day * DAY_2_MIN

    # the indices between the selected times
    ii = (t >= start) & (t < end)

    # the times shown in a 24 hour scale
    tau = (t[ii] / temporal.HOUR_2_MIN)

    # the satiation values for the selected times
    n_rest      = p.H[idx, need.REST]
    n_hunger    = p.H[idx, need.HUNGER]
    n_income    = p.H[idx, need.INCOME]
    n_travel    = p.H[idx, need.TRAVEL]

    # store the satiation values and weights
    n_list = [ n[ii] for n in (n_rest, n_hunger, n_income, n_travel) ]
    w_list = [ calc_weight(x) for x in n_list ]

    return tau, n_list, w_list

def load_fig_data(fname):

    """
    Load figure data.
    :param str fname: the file name of the figure to load. The file must be a .pkl file.

    :return: the x and y values of the lines in the figure
    :rtype: list
    """

    # load the data from the pickled figure
    fig = pickle.load(open(fname, mode='rb'))

    # close the plot
    plt.close(fig)

    # the lines of the plot data
    lines = fig.axes[0].lines

    # the figure data
    data = [x.get_data() for x in lines]

    return data

def plot_activity_cdfs(d, keys):

    """
    This function plots the cumulative distribution function of start time, end time, and duration for \
    each activity in the the simulation.

    :param diary.Diary d: the results of the simulation
    :param list keys: list of activities to graph
    :return:
    """

    # for each activity (key)
    for k in keys:

        # get diary information for the given activity
        df = d.df[d.df.act == k]

        # create subplots
        fig, axes = plt.subplots(2, 2)

        # title
        fig.suptitle(activity.INT_2_STR[k])

        # number of samples for empirical cumulative distribution function (CDF)
        N = 1e3

        # the labels for the subplots
        labels = ('start', 'end', 'duration')

        # the colors for the subplots
        colors = ('blue', 'green', 'red')

        # the axes for the subplots
        ax_list = ( axes[0, 0], axes[0, 1], axes[1, 0] )

        # the data for the subplots
        data_list = ( df.start.values, df.end.values, df.dt.values)

        # plot each subplot
        for ax, data, color, label in zip(ax_list, data_list, colors, labels):

            # use periodic time if start time can span over midnight
            if label == 'start' and k == mg.KEY_SLEEP:
                data = mg.to_periodic(data, do_hours=True)

            # calculate the empirical CDF
            x, y = mg.get_ecdf(data, N)

            # plot the values, set the x-axis label, set the legend
            ax.plot(x, y, color=color, label=label)

            # set the x-axis label
            ax.set_xlabel('hours')

            # set the legend
            ax.legend(loc='best')

    return

def plot_activity_histograms(d, keys):

    """
    This function plots the histograms of start time, end time, and duration for each activity in \
    the the simulation.

    :param diary.Diary d: the results of the simulation
    :param list keys: list of activities to graph
    :return:
    """

    for k in keys:

        # get diary information about the given activity
        df = d.df[d.df.act == k]

        # the number of bins (set to 24 to reflect 24 hours in a day)
        num_bins = 24

        # create subplots
        fig, axes = plt.subplots(2, 2)

        # title
        fig.suptitle(activity.INT_2_STR[k])

        # the labels for the subplots
        labels = ('start', 'end', 'duration')

        # the colors for the subplots
        colors = ('blue', 'green', 'red')

        # the axes for the subplots
        ax_list = (axes[0, 0], axes[0, 1], axes[1, 0])

        # the data for subplots
        data_list = (df.start.values, df.end.values, df.dt.values)

        # for each subplot, plot the data
        for ax, data, color, label in zip(ax_list, data_list, colors, labels):

            # use periodic time if the start time can span over midnight
            if label == 'start' and k == mg.KEY_SLEEP:
                data = mg.to_periodic(data, do_hours=True)

            # plot the values
            ax.hist(data, bins=num_bins, color=color, label=label)

            # set the x-axis label
            ax.set_xlabel('hours')

            # set the legend
            ax.legend(loc='best')

    return

def plot_count(data, keys, do_abs=True, title=None):

    """
    This function plots a histogram showing the amount of times each activity was done \
    in an ABMHAP simulation.

    :param pandas.core.frame.DataFrame data: the activity diary
    :param list keys: the activity codes
    :param bool do_abs: whether (if True) to plot a histogram of the number \
    of agents or (if False) to plot a histogram of percentage of agents
    :param str title: the title of the plot

    :return:
    """

    # number of activities
    N = len(keys)

    # set the rows and columns
    nrows = int(np.ceil(np.sqrt(N)))
    ncols = nrows

    # create the subplot
    f, axes = plt.subplots(nrows, ncols, sharex=False, sharey=False)

    for i, k in enumerate(keys):

        row = i // nrows
        col = i % ncols

        ax = axes[row, col]
        total = np.zeros(len(data.diaries))

        for i, y in enumerate(data.diaries):
            df = y[0].df

            if k == mg.KEY_WORK:
                count = len(df[df.act == k].day.unique())
            else:
                count = df[df.act == k].day.count()

            total[i] = count

        if do_abs:
            weights = None
        else:
            weights = np.zeros(total.shape) + 1 / total.size

            # plot the histogram for the activity
        ax.hist(total, weights=weights, color=activity.INT_2_COLOR[k], label=activity.INT_2_STR[k])

        if do_abs:
            ylabel = 'Number of Agents'
        else:
            ylabel = 'Percentage of Agents'

        # set the x-axis limits
        ax.set_xlim(total.min() - 1, total.max() + 1)
        ax.legend(loc='best')

        ax.set_ylabel(ylabel)
        ax.set_xlabel('Count')

    if title is None:
        title = 'Activity Distribution'

    f.suptitle(title)

    return


def plot_history(t,  y_list, labels, colors, linestyles, ylabel, linewidth=None):

    """
    This function plots information related to data related to needs (such as satiation and \
    weight function values) over time.

    :param numpy.ndarray t: the time values [hours] of interest
    :param list y_list: the satiation values for each need over time
    :param list labels: the labels that corresponds to the respective need
    :param list colors: the colors that corresponds to the respective need
    :param list linestyles: the line styles that corresponds to the respective need
    :param str ylabel: the y-axis label
    :param int linewidth: the line width for each line

    :return:
    """

    # plot the satiation
    for y, label, color, linestyle in zip(y_list, labels, colors, linestyles):
        plt.plot(t, y, label=label, color=color, lw=linewidth, ls=linestyle)

    # the days within the specified times
    days = np.unique( np.floor(t / 24) )

    # plot a vertical line to separate the days
    for day in days:
        plt.axvline(day * 24, color='k', ls='--', lw=linewidth)

    # plot a vertical line after the last day
    plt.axvline((days[-1] + 1) * 24, color='k', ls='--', lw=linewidth)

    # set the x-axis label, y-axis label, and the legend
    plt.xlabel('Hour')
    plt.ylabel(ylabel)
    plt.legend(loc='best')

    return

def plot_longitude(data, titles, linewidth=1):

    """
    This function plots the day-to-day variation of activity duration for each activity \
    over time from an ABMHAP simulation. This is done for each demographic in order \
    to compare their differences and daily behavior. Within each subplot, an agent \
    representing a respective demographic has its activity behavior is plotted
    in a log10 scale over time.

    :param data: the activity diaries of the agents to plot. Each agent represents \
    a different demograhic.
    :type data: list of pandas.core.frame.DataFrame
    :param titles: the names of the demographics that are being plot
    :type titles: list of str
    :param float linewidth: the line width of the plot lines

    :return:
    """

    # the number of rows and columns in the subplots
    nrows, ncols = 2, 2

    #
    # create axes
    #
    f, axes = plt.subplots(nrows, ncols, sharex=True, sharey=True)

    #
    # plot
    #

    # plot the subplots for each demographic
    K = [plot_longitude_help(ax, separate_activities_into_days(data[i]), linewidth) \
         for i, ax in enumerate(f.axes)]

    # the activities
    K0 = K[0]

    # choose the activities
    keys = [activity.INT_2_STR[k] for k in K0]

    # show the legend
    f.legend(f.axes[0].lines, keys, 'best')

    # set the subplot titles
    fontsize_title = 18
    ticksize = 14
    for i, ax in enumerate(f.axes):
        ax.set_title(titles[i], fontsize=fontsize_title)
        ax.tick_params(axis='both', labelsize=ticksize)

    # set the main title
    f.suptitle('Daily Activity Duration', fontsize=fontsize_title)

    # write axes for x and y
    df = data[0]
    xlabel, ylabel = 'Day', 'Duration [minutes]'
    x_min, x_max = df.day.values[0], df.day.values[-1]

    #
    # set the x and y axes for each subplot
    #
    fontsize_label = 18
    ax = axes[0, 0]
    ax.set_ylabel(ylabel, fontsize=fontsize_label)

    ax = axes[1, 0]
    ax.set_xlabel(xlabel, fontsize=fontsize_label)
    ax.set_xlim(x_min, x_max)
    ax.set_ylabel(ylabel, fontsize=fontsize_label)

    ax = axes[1, 1]
    ax.set_xlabel(xlabel, fontsize=fontsize_label)

    return

def plot_longitude_help(ax, df, linewidth=1):

    """
    This function plots the day-to-day variation of activity duration for each activity \
    over time from an ABMHAP simulation. Within each subplot, an agent has its activity \
    behavior is plotted in a log10 scale over time.

    :param matplotlib.figure.Figure ax: the subplot object
    :param pandas.core.frame.DataFrame df: the activity diary of an agent
    :param float linewidth: the line width of the plot lines

    :return:
    :rtype: list of int
    """

    # colors for plotting
    colors = activity.INT_2_COLOR

    # the days in the simulation
    days = df.day.unique()

    # the activities that were done by the person in the simulation
    keys = [k for k in df.act.unique() ]

    # group activities by day
    gb = df.groupby('day')

    # loop through each activity and plot the duration over time
    for k in keys:

        # the duration data
        y = np.zeros(days.shape)

        for i, d in enumerate(days):

            # get the daily activity data
            temp = gb.get_group(d)
            temp = temp[temp.act == k]

            # if there the respective activity does not happen that day, return NaN
            # this allows python to avoid plotting the activity on that specific day
            if temp.size == 0:
                dt = np.nan

            # the duration is counted as work end - work start, like in the ABM
            # perhaps this should change to summing the durations themselves
            elif (k == mg.KEY_WORK):
                # dt = temp.end.values[-1] - temp.start.values[0] # original
                dt = temp.dt.values.sum()

            else:
                dt = temp.dt.values.sum()

            # convert the time into minutes (not hours)
            y[i] = temporal.HOUR_2_MIN * dt

        # plot the data for the kth activity
        ax.plot(days, y, '-*', label=activity.INT_2_STR[k], color=colors[k], linewidth=linewidth)
        # ax.plot(days, y, '-', label=activity.INT_2_STR[k], color=colors[k], linewidth=linewidth)
        ax.set_ylim(1e0, 1e3)
        ax.set_yscale('log')

    return keys

def plot_satiation_and_weight(p, start_day, end_day, fid_satiation=100, fid_weight=101):

    """
    This function plots the satiation values and weight values for the agent during the simulation.

    .. warning::
        This function is best used when the simulation moves through time minute by minute. If not,
        the slopes in both the satiation and weight plots will **not** be accurate.

    :param person.Person p: the agent whose satiation and weight values are to be plotted
    :param int start_day: the day to start plotting
    :param int end_day: the day to end plotting
    :param int fid_satiation: the figure identifier for the satiation plot
    :param int fid_weight: the figure identifier for the weights plot

    :return:
    """

    # get the times, satiation values, and weight function values from the agent
    t, n_list, w_list = get_satiation_and_weight(p, start_day, end_day)

    #
    # plotting parameters
    #

    # line width for each line in the plot
    linewidth   = 1.0

    # the labels
    labels      = ('Rest', 'Hunger', 'Income', 'Travel')

    # the colors
    colors      = (None, 'darkorange', 'darkviolet', 'green')

    # the line styles
    linestyles  = ['-', '--', '-.', ':']

    #
    # plot the satiation value over time
    #

    # create the figure
    plt.figure(fid_satiation)

    # plot the satiation history
    plot_history(t, n_list, labels, colors, linestyles, ylabel='Satiation', linewidth=linewidth)

    #
    # plot the value of the weight function over time
    #
    plt.figure(fid_weight)

    # calculate the log10 of the weights
    log_w_list = [ calc_log_weight(w) for w in w_list ]

    # plot the weight history
    plot_history(t, log_w_list, labels, colors, linestyles, ylabel='Weight', linewidth=linewidth)

    return

def separate_activities_into_days(data):

    """
    This function finds the activities tha occur over midnight and breaks down \
    creates a new activity diary in which an activity occurring over midnight \
    is split into two activities: one activity entry ending at midnight, and \
    one activity entry starting at midnight.

    :param pandas.core.frame.DataFrame data: the activity diary of an agent

    :return: the new activity diary
    :rtype: pandas.core.frame.DataFrame
    """

    # one minute in hours
    one_min = 1 / temporal.HOUR_2_MIN

    # copy the data frame
    df = data.copy()

    # convert start time and duration to periodic time [-12, 12)
    df.start    = mg.to_periodic(df.start, do_hours=True)
    df.end      = mg.to_periodic(df.end, do_hours=True)

    # index for rollover of activities from one day to the next
    idx = (df.start.values < 0) * (df.end.values >= 0)

    # when an activity starts and ends on the same day
    df_same_day = df[~idx]

    # when an activity starts on one day and ends the next day
    df_next_day = df[idx]

    # the column labels
    # columns = df_next_day.columns

    x_list = list()
    for i in range(len(df_next_day)):
        x = df_next_day.iloc[i]

        day, start, end, act, loc = np.array([x.day]), np.array([x.start]), np.array([x.end]), \
                                    np.array([x.act]), np.array([x['loc']])

        d1 = {'day': day, 'start': start, 'end': [-one_min], 'dt': (-one_min - start + one_min), \
              'act': act, 'loc': loc}

        d2 = {'day': day + 1, 'start': [0], 'end': end, 'dt': (end - 0 + one_min), 'act': act, 'loc': loc}

        x1 = pd.DataFrame(d1, columns=data.columns)
        x2 = pd.DataFrame(d2, columns=data.columns)

        x_list.append(x1)
        x_list.append(x2)

    # create the dataframe with multiple days
    df_two_day = pd.concat(x_list)

    # concatenate arrays
    df_new = pd.concat([df_same_day, df_two_day])

    # sort values
    df_new = df_new.sort_values(by=['day', 'start'])

    return df_new