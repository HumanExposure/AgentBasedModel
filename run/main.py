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
# August 14, 2017

"""
This is code is runs the simulation for the Agent-Based Model of Human Activity Patterns \
(ABMHAP) module of the Life Cycle Human Exposure Model (LC-HEM) project.

In order to run the code, do the following:

#. set the user-defined parameters of the simulation in main_params.py
#. run the code via
    \> python main.py

.. note::
    In order to run the debugger do the following in windows:

    \> python -m pdb main.py

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===========================================
# import
# ===========================================

# to access python files in the parent directory
import os, sys, time
sys.path.append('..\\source')

# for plotting
import matplotlib.pylab as plt

# agent-based model modules
import my_globals as mg
import activity, diary, main_params, occupation, params, scenario, temporal

# ===============================================================================
# RUN
# ===============================================================================

def get_diary(u):

    """
    This function output the result of the simulation in terms of an activity diary.

    :param universe.Universe u: the governing engine of the simulation
    :return: the activity diary describing the behavior of the agent
    :rtype: diary.Diary
    """

    # the agent
    p = u.people[0]

    # the indices of simulation data
    idx = u.clock.hist_time != -1
    idx = idx.flatten()

    # the time
    t           = u.clock.hist_time[idx].flatten()

    # the array of the activities
    hist_act    = p.hist_activity[idx]

    # the array of the locations
    hist_loc    = p.hist_local[idx]

    # make the time continuous
    t_all   = mg.fill_out_time(t)

    # fill out the time in between events to get data that corresponds to contiguous time
    act_all = mg.fill_out_data(t, hist_act)

    # fill out the location data in between events that corresponds to contiguous time
    loc_all = mg.fill_out_data(t, hist_loc)

    # create the activity diary
    d = diary.Diary(t=t_all, act=act_all, local=loc_all)

    return d

def plot_cdfs(d, keys):

    """
    This function plots the cumulative distribution function of start time, end time, and duration for \
    each activity in the the simulation.

    :param diary.Diary d: the results of the simulation
    :param list keys: list of activities to graph
    :return:
    """

    for k in keys:

        df = d.df[d.df.act == k]

        fig, axes = plt.subplots(2, 2)

        # title
        fig.suptitle(activity.INT_2_STR[k])

        # plot the start time distribution
        N = 1e3
        ax = axes[0, 0]
        if k == mg.KEY_SLEEP:
            x, y = mg.get_ecdf( mg.to_periodic(df.start.values), N)
        else:
            x, y = mg.get_ecdf(df.start.values, N)

        ax.plot(x, y, color='blue', label='start')
        ax.set_xlabel('hours')
        ax.legend(loc='best')

        # plot the end time distribution
        ax = axes[0, 1]
        x, y = mg.get_ecdf(df.end.values, N)
        ax.plot(x, y, color='green', label='end')
        ax.set_xlabel('hours')
        ax.legend(loc='best')

        # plot the duration distribution
        ax = axes[1, 0]
        x, y = mg.get_ecdf(df.dt.values, N)
        ax.plot(x, y, color='red', label='duration')
        ax.set_xlabel('hours')
        ax.legend(loc='best')

    return


def plot_histograms(d, keys):

    """
    This function plots the histograms of start time, end time, and duration for each activity in \
    the the simulation.

    :param diary.Diary d: the results of the simulation
    :param list keys: list of activities to graph
    :return:
    """

    for k in keys:

        df = d.df[d.df.act == k]
        num_bins = 24
        fig, axes = plt.subplots(2, 2)

        fig.suptitle(activity.INT_2_STR[k])
        # title

        # plot the start time distribution

        ax = axes[0, 0]
        if k == mg.KEY_SLEEP:
            ax.hist(mg.to_periodic(df.start.values), bins=num_bins, color='blue', label='start')
        else:
            ax.hist(df.start.values, bins=num_bins, color='blue', label='start')
        ax.set_xlabel('hours')
        ax.legend(loc='best')

        # plot the end time distribution
        ax = axes[0, 1]
        ax.hist(df.end.values, bins=num_bins, color='green', label='end')
        ax.set_xlabel('hours')
        ax.legend(loc='best')

        # plot the duration distribution
        ax = axes[1, 0]
        ax.hist(df.dt.values, bins=num_bins, color='red', label='duration')
        ax.set_xlabel('hours')
        ax.legend(loc='best')

    return

def save_output(df, fname):

    """
    This function saves the output of the simulation.

    :param pandas.core.frame.DataFrame df: the activity-diary output of the simulation
    :param str fname: the file name of the saved file. It must end with ".csv"
    """

    # the conversion of 1 hour into minutes
    HOUR_2_MIN  = temporal.HOUR_2_MIN

    # copy the data frame to avoid changing the original data in df
    data        = df.copy()

    # convert the end time in minutes.
    # Add the + 1 minute to the end time so that 16:00 - 16:59 becomes 16:00 - 17:00
    end         = mg.hours_to_minutes( data.end ) + 1

    # convert the end time into hours
    data.end    = end / HOUR_2_MIN

    # create the directory for the save file if it does not exist
    os.makedirs(os.path.dirname(fname), exist_ok=True)

    # save the data
    data.to_csv(fname, index=False)

    return

# ===============================================
# run
# ===============================================

if __name__ == '__main__':

    # close all open plots
    plt.close('all')

    #
    # set up the parameters
    #

    # print messages to string if True, do not if False
    do_print    = main_params.do_print

    # print plots of the data if True, do not if False
    do_plot     = main_params.do_plot

    # print the output to the screen
    do_print    = main_params.do_print

    # save the output flag if True, do not if False
    do_save     = main_params.do_save

    # the household parameters for the simulation
    hhld_param  = main_params.hhld_param

    # set up the simulation
    scene       = scenario.Solo(hhld_param)

    #
    # run the simulation
    #

    # start timing
    tic = time.time()

    # run the simulation
    scene.run()

    # stop timing
    toc = time.time()

    # calculate the elapsed duration
    dt_elapsed = toc - tic

    # print the elapsed simulation time
    print('elapsed time: %.2f[s]' % dt_elapsed)

    # get the activity diary from the results of the simulation
    d = get_diary(scene.u)

    # print the diary
    if do_print:
        print( d.toString() )

    # save the output diary
    if do_save:
        save_output(d.df, main_params.fname)

    # plot results of the simulation for each activity
    if do_plot:
        print('plotting...')

        # all of the activities used in the simulation as well as idle time
        act_all = d.df.act.unique()

        # the activities used in the simulation, not including the idle time
        keys = act_all[ act_all != mg.KEY_IDLE ]

        # plot the histograms
        plot_histograms(d, keys)

        # plot the cumulative distribution function
        plot_cdfs(d, keys)

        # show the plot
        plt.show()