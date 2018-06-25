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

#. set the user-defined parameters of the simulation in :literal:`main_params.py`
#. run the code via

    \> :literal:`python main.py`

.. moduleauthor:: Dr. Namdi Brandon
"""

#
# In order to run the debugger do the following in windows:
# python -m pdb main.py

# ===========================================
# import
# ===========================================

# to access python files in the parent directory
import sys, time
sys.path.append('..\\source')
sys.path.append('..\\plotting')

# for plotting
import matplotlib.pylab as plt

# agent-based model modules
import my_globals as mg
import main_params, plotter, scenario

# ===============================================
# functions
# ===============================================

def plot(p, d=None):

    """
    This function plots figures related to the results of the simulation. Specifically, \
    it does the following for the given agent:

    #. plots the histograms about the activity data
    #. plots cumulative distribution functions (CDFs) of the activity data
    #. plots how the satiation changes over time for the all of the needs
    #. plots how the weight function values change over time for all of the needs

    .. note::
        The satiation and weight function plots will **not** be correct unless the simulation \
        was set to run minute by minute. That is, main_params.do_minute_by_minute is set to **True**.

    :param person.Person p: the agent whose information is going to be plotted
    :param diary.Diary d: the activity diary of the respected agent

    :return:
    """

    # print plotting message to screen
    print('plotting...')

    # if the activity diary is not already created, create the activity diary
    if d is None:
        d = p.get_diary()
    #
    # plot activity data
    #

    # all of the activities used in the simulation as well as idle time
    act_all = d.df.act.unique()

    # the activities used in the simulation, not including the idle time
    keys = act_all[act_all != mg.KEY_IDLE]

    # plot the histograms
    plotter.plot_activity_histograms(d, keys)

    # plot the cumulative distribution function
    plotter.plot_activity_cdfs(d, keys)

    #
    # plot how satiation and weights evolve over time
    #

    # start day
    start = d.df.day.iloc[0]

    # end day
    end = d.df.day.iloc[-1]

    # plot how both satiation and weights change over time
    plotter.plot_satiation_and_weight(p, start_day=start, end_day=end)

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

    # the person being simulated
    agent = scene.u.people[0]

    # get the activity diary from the results of the simulation
    act_diary = agent.get_diary()

    #
    # print the diary
    #
    if do_print:
        print( act_diary.toString() )

    #
    # save the output diary
    #
    if do_save:
        mg.save_diary_to_csv(act_diary.df, main_params.fname)

    #
    # plot results of the simulation for each activity
    #
    if do_plot:

        # plot the results
        plot(agent, act_diary)

        # show the plot
        plt.show()
