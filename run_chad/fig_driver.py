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
.. warning::
    This module is antiquated and not used.

This function is used to get the saved pickled plot data and plot them in subplots.

It is used to obtain cumulative distribution functions (CDFs) about the Agent-Based \
Model of Human Activity Patterns (ABMHAP) ABMHAP vs CHAD data for various activities \
and plot subplots with data from various activities instead of just 1
"""

# ===========================================
# import
# ===========================================
import os, sys
sys.path.append('..\\source')

# plotting capability
import matplotlib.pyplot as plt

# mathematical capability
import numpy as np

# ABMHAP modules
import activity, analyzer

# ===========================================
# constants
# ===========================================
FIGURE_DIR = os.path.dirname(os.getcwd()) + '\\my_data\\fig'

# ===========================================
# function
# ===========================================

def plot_cdfs(fdir, fid):

    # get the ABM and CHAD data from the cdf plots for duration and start time, respectively
    x_abm_dt, y_abm_dt, x_chad_dt, y_chad_dt = analyzer.load_plot_data(fdir + '\\cdf_dt.pickle')
    x_abm_start, y_abm_start, x_chad_start, y_chad_start = analyzer.load_plot_data(fdir + '\\cdf_start.pickle')

    # set the figure number
    plt.figure(num=fid)

    # plot the activity duration data in a subplot
    plt.subplot(1, 2, 1)
    plt.plot(x_abm_dt, y_abm_dt, 'b', label='ABM')
    plt.plot(x_chad_dt, y_chad_dt, 'r', label='CHAD')
    plt.title('mean activity duration')
    plt.xlabel('hours')
    plt.ylabel('probability')
    plt.legend(loc='best')

    # plot the start time data in a subplot
    plt.subplot(1, 2, 2)
    plt.plot(x_abm_start, y_abm_start, 'b', label='ABM')
    plt.plot(x_chad_start, y_chad_start, 'r', label='CHAD')
    plt.title('mean activity start time')
    plt.xlabel('hours')
    plt.ylabel('probability')
    plt.legend(loc='best')

    return

def plot_cdfs2(fdirs, fid, nrows, ncols, activity_codes):

    # the number of activities
    n = len(fdirs)

    act_names = [activity.INT_2_STR[x] for x in activity_codes]
    dt_ = list()
    start_list = list()
    # figure indexing starts at 1
    idx = 1 + np.array( range(n) ) * 2

    # get the data
    for fdir in fdirs:
        # get the ABM and CHAD data from the cdf plots for duration and start time, respectively
        dt_.append( analyzer.load_plot_data(fdir + '\\cdf_dt.pickle') )
        start_list.append( analyzer.load_plot_data(fdir + '\\cdf_start.pickle') )

    # set the figure number
    plt.figure(num=fid)

    # plot the data
    for data_abm, data_chad, a, i in zip(dt_, start_list, act_names, idx):

        x_abm_dt, y_abm_dt, x_chad_dt, y_chad_dt = data_abm
        x_abm_start, y_abm_start, x_chad_start, y_chad_start = data_chad

        # plot the activity duration data in a subplot
        plt.subplot(nrows, ncols, i)
        plt.plot(x_abm_dt, y_abm_dt, 'b', label='ABM')
        plt.plot(x_chad_dt, y_chad_dt, 'r', label='CHAD')
        plt.title('mean ' + a + ' duration')
        plt.xlabel('hours')
        plt.ylabel('probability')
        plt.legend(loc='best')

        plt.subplot(nrows, ncols, i+1)
        plt.plot(x_abm_start, y_abm_start, 'b', label='ABM')
        plt.plot(x_chad_start, y_chad_start, 'r', label='CHAD')
        plt.title('mean ' + a + ' start time')
        plt.xlabel('hours')
        plt.ylabel('probability')
        plt.legend(loc='best')

    return

def compare_single_omni(fdirs_single, fdirs_omni, fid, nrows, ncols, activity_codes, do_chad=False):

    """
    Plot a subplot of CDFs of single-activity and full simulation data for start time and duration.

    :param list fdirs_single: the filenames of the pickled single-activity data
    :param list fdirs_omni: the filenames of the pickled for full-simulation data
    :param int fid: figure identifier
    :param int nrows: the number of rows in the suubplot
    :param int ncols: the number of columns in the subplot
    :param list activity_codes: the activity codes to plot
    :param bool do_chad: flag indicating whether or not to plot the CHAD data
    :return:
    """

    # the number of activities
    n = len(fdirs_omni)

    # store the activity names
    act_names = [activity.INT_2_STR[x] for x in activity_codes]

    # lists for duration and start time data for the omni data
    dt_omni_list = list()
    start_omni_list = list()

    # lists for duration and start time data for the solo data
    start_single_list = list()
    dt_single_list= list()

    # figure indexing starts at 1
    idx = 1 + np.array( range(n) ) * 1

    # get the data
    for f_single, f_omni in zip(fdirs_single, fdirs_omni):

        # get the ABM and CHAD data from the cdf plots for duration and start time, respectively
        dt_omni_list.append( analyzer.load_plot_data(f_omni + '\\cdf_dt.pickle') )
        dt_single_list.append(analyzer.load_plot_data(f_single + '\\cdf_dt.pickle'))

        start_omni_list.append(analyzer.load_plot_data(f_omni + '\\cdf_start.pickle'))
        start_single_list.append(analyzer.load_plot_data(f_single + '\\cdf_start.pickle'))

    #
    # plotting parameters
    #

    # linewidth
    l_width = 3

    # labels
    omni_label, single_label, chad_label = 'Global', 'Single', 'CHAD'

    # colors
    omni_color, single_color, chad_color = 'blue', 'red', 'black'

    #
    # plot
    #

    # set the figure number
    plt.figure(num=fid)

    # plot the data
    z = zip(dt_omni_list, start_omni_list, dt_single_list, start_single_list, act_names, idx)
    for dt_omni, start_omni, dt_single, start_single, a, i in z:

        # omni data (duration and start time)
        x_omni_dt, y_omni_dt, x_chad_dt, y_chad_dt = dt_omni
        x_omni_start, y_omni_start, x_chad_start, y_chad_start = start_omni

        # single isolated activity data (duration and start time)
        x_single_dt, y_single_dt, x_chad_dt, y_chad_dt = dt_single
        x_single_start, y_single_start, x_chad_start, y_chad_start = start_single

        #
        # plot the activity duration data in a subplot
        #
        plt.subplot(nrows, ncols, i)
        plt.plot(x_omni_dt, y_omni_dt, color=omni_color, label=omni_label, linewidth=l_width)
        plt.plot(x_single_dt, y_single_dt, color=single_color, label=single_label, linewidth=l_width)

        if do_chad:
            plt.plot(x_chad_dt, y_chad_dt, chad_color, ls='--', label=chad_label, linewidth=l_width)

        plt.title('Mean ' + a + ' Duration')
        plt.xlabel('Hours')
        plt.ylabel('Probability')
        plt.legend(loc='best')

        #
        # Plot the start time
        #
        #plt.subplot(nrows, ncols, i+1)
        plt.subplot(nrows, ncols, i + ncols)
        plt.plot(x_omni_start, y_omni_start, color=omni_color, label=omni_label, linewidth=l_width)
        plt.plot(x_single_start, y_single_start, color=single_color, label=single_label, linewidth=l_width)

        if do_chad:
            plt.plot(x_chad_start, y_chad_start, color=chad_color, ls='--',label=chad_label, linewidth=l_width)

        plt.title('Mean ' + a + ' Start Time')

        if a == activity.INT_2_STR[activity.SLEEP]:
            x_label = 'Hours Before and After Midnight'
        else:
            x_label = 'Hours'

        plt.xlabel(x_label)
        plt.ylabel('Probability')
        plt.legend(loc='best')

    return

# ===========================================
# run
# ===========================================

if __name__ == '__main__':

    # the directories for the all-activity and solo-activities
    figure_dir = FIGURE_DIR
    fdir_omni = figure_dir + '\\omni'
    fdir_solo = figure_dir + '\\solo'

    # get the appropriate parameters for the given activity (trial code and figure directory)
    omni_chooser = {activity.COMMUTE_TO_WORK: (fdir_omni + '\\commute\\to_work'),
               activity.COMMUTE_FROM_WORK: (fdir_omni + '\\commute\\from_work'),
               activity.EAT_BREAKFAST: (fdir_omni + '\\eat\\breakfast'),
               activity.EAT_DINNER: (fdir_omni + '\\eat\\dinner'),
               activity.EAT_LUNCH: (fdir_omni + '\\eat\\lunch'),
               activity.SLEEP: (fdir_omni + '\\sleep'),
               activity.WORK: (fdir_omni + '\\work'),
               }

    solo_chooser = {activity.COMMUTE_TO_WORK: (fdir_solo + '\\commute\\to_work'),
               activity.COMMUTE_FROM_WORK: (fdir_solo + '\\commute\\from_work'),
               activity.EAT_BREAKFAST: (fdir_solo + '\\eat\\breakfast'),
               activity.EAT_DINNER: (fdir_solo + '\\eat\\dinner'),
               activity.EAT_LUNCH: (fdir_solo + '\\eat\\lunch'),
               activity.SLEEP: (fdir_solo + '\\sleep'),
               activity.WORK: (fdir_solo + '\\work'),
               }

    # set the trial codes to plot
    act1 = [activity.SLEEP, activity.WORK, activity.COMMUTE_TO_WORK, activity.COMMUTE_FROM_WORK]
    act2 = [activity.EAT_BREAKFAST, activity.EAT_LUNCH, activity.EAT_DINNER]
    activity_codes = [act1, act2]

    # figure identifiers
    fids = [1000, 2000]

    # plot
    for acts, fid in zip(activity_codes, fids):

        # get the directory
        fdirs1  = [ omni_chooser[x] for x in acts]
        fdirs2  = [ solo_chooser[x] for x in acts]

        # plot the cdfs for the specific activity
        compare_single_omni(fdirs2, fdirs1, fid, nrows=2, ncols=4, activity_codes=acts, do_chad=True)


    #fdir = solo_chooser[activity.COMMUTE_TO_WORK]
    #plot_cdfs(fdir, fid=1)
    # show plot
    plt.show()
