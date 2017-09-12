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
This module is responsible for containing parameters that main.py uses to control \
the simulation.

The user should set the parameters in this module **before** running the driver (main.py)

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===========================================
# import
# ===========================================
import sys
sys.path.append('..\\source')

# general mathematical capability
import numpy as np

# agent-based model modules
import my_globals as mg
import occupation, params, scenario, temporal

# ===========================================
# constants
# ===========================================

# the number of minutes in 1 day and the number of minutes in 1 hour, respectively
DAY_2_MIN, HOUR_2_MIN   = temporal.DAY_2_MIN, temporal.HOUR_2_MIN

# -----------------------------------------------------
# functions
# -----------------------------------------------------
def set_no_variation(num_people):

    """
    This function sets the standard deviations in all of the activity-parameters to zero.

    :param int num_people: the number of people in the simulation
    :return: a tuple of the standard deviations of all of the activity-parameters
    """

    sleep_start_std, sleep_end_std  = [np.zeros((num_people,))] * 2
    bf_start_std, bf_dt_std         = [np.zeros((num_people,))] * 2
    lunch_start_std, lunch_dt_std   = [np.zeros((num_people,))] * 2
    dinner_start_std, dinner_dt_std = [np.zeros((num_people,))] * 2
    work_start_std, work_end_std    = [np.zeros((num_people,))] * 2
    commute_to_work_dt_std          = [np.zeros((num_people,))] * 1
    commute_from_work_dt_std        = [np.zeros((num_people,))] * 1

    result = (sleep_start_std, sleep_end_std, bf_start_std, bf_dt_std, lunch_start_std, lunch_dt_std, \
              dinner_start_std, dinner_dt_std, work_start_std, work_end_std, commute_to_work_dt_std, \
              commute_from_work_dt_std)

    return result

# --------------------------------------------
# Default parameters
# --------------------------------------------
# the default number of days in the simulation
NUM_DAYS    = 7

# the default number of additional hours in the simulation
NUM_HOURS   = 8

# the default number of additional minutes in the simulation
NUM_MIN     = 0

# the default start time [minutes] is Day 0 at 16:00
T_START     = temporal.SUNDAY * DAY_2_MIN + 16 * HOUR_2_MIN

# job identifier
JOB_ID      = occupation.STANDARD_JOB

# the number of people in the simulation. In this version of ABMHAP, only one agent
# is allowed per simulation
NUM_PEOPLE  = 1

#
# parametrize the agent. Values are in minutes
#

# the default mean and standard deviation for the sleep start time, respectively
SLEEP_START_MEAN    = 22 * HOUR_2_MIN
SLEEP_START_STD     = 30

# the default mean and standard deviation for the sleep end time, respectively
SLEEP_END_MEAN      = 8 * HOUR_2_MIN
SLEEP_END_STD       = 15

# the default mean and standard deviation of the eat breakfast start time, respectively
BF_START_MEAN       = 8 * HOUR_2_MIN
BF_START_STD        = 10

# the default mean and standard deviation of the eat breakfast duration, respectively
BF_DT_MEAN          = 15
BF_DT_STD           = 10

# the default mean and standard deviation of the eat lunch start time, respectively
LUNCH_START_MEAN    = 12 * HOUR_2_MIN
LUNCH_START_STD     = 15

# the default mean and standard deviation of the eat breakfast duration, respectively
LUNCH_DT_MEAN       = 30
LUNCH_DT_STD        = 10

# the default mean and standard deviation of the eat dinner start time, respectively
DINNER_START_MEAN   = 19 * HOUR_2_MIN
DINNER_START_STD    = 10

# the default mean and standard deviation of the eat dinner duration, respectively
DINNER_DT_MEAN      = 45
DINNER_DT_STD       = 5

# the default mean and standard deviation for the work start time, respectively
WORK_START_MEAN     = 9 * HOUR_2_MIN
WORK_START_STD      = 15

# the default mean and standard deviation for the work end time, respectively
WORK_END_MEAN       = 17 * HOUR_2_MIN
WORK_END_STD        = 5

# the default mean and standard deviation of the commute to work duration, respectively
COMMUTE_TO_WORK_DT_MEAN     = 30
COMMUTE_TO_WORK_DT_STD      = 10

# the default mean and standard deviation of the commute from work duration, respectively
COMMUTE_FROM_WORK_DT_MEAN   = COMMUTE_TO_WORK_DT_MEAN
COMMUTE_FROM_WORK_DT_STD    = COMMUTE_TO_WORK_DT_STD

# the default number of standard deviations to truncate in the normal distribution in the activity-parameters
TRUNC   = 1

# the default file name to save the data
FNAME   = mg.FDIR_MY_DATA + '\\example_output.csv'

# ============================================
# user-defined parameters
# ============================================

#
# simulation parameters
#

# should the simulation print messages to the screen
do_print    = False

# should the simulation plot results at the end of the run
do_plot     = False

# should the simulation save the results of the simulation
do_save     = True

# the file name to save the data
fname       = FNAME

# -------------------------------------------
# time information
# -------------------------------------------

# the number of days
num_days    = NUM_DAYS

# the number of additional hours
num_hours   = NUM_HOURS

# the number of additional minutes
num_min     = NUM_MIN

# the start time [in minutes]
t_start     = T_START

# -------------------------------------------
# set the agent's activity-parameters
# -------------------------------------------

# number of people
num_people = NUM_PEOPLE

# job identifier
job_id      = np.array( [JOB_ID] )

# a flag to indicate whether the standard deviation on the activities should be set to 0 (if True) or not (if False)
no_variation = False

#
# the activity parameters
#

# the mean and standard deviation for the sleep start time, respectively
sleep_start_mean    = np.array([SLEEP_START_MEAN])
sleep_start_std     = np.array([SLEEP_START_STD])

# the mean and standard deviation for the sleep end time, respectively
sleep_end_mean      = np.array([SLEEP_END_MEAN])
sleep_end_std       = np.array([SLEEP_END_STD])

# the mean and standard deviation of the eat breakfast start time, respectively
bf_start_mean       = np.array([BF_START_MEAN])
bf_start_std        = np.array([BF_START_STD])

# the mean and standard deviation of the eat breakfast duration, respectively
bf_dt_mean          = np.array([BF_DT_MEAN])
bf_dt_std           = np.array([BF_DT_STD])

# the mean and standard deviation of the eat lunch start time, respectively
lunch_start_mean    = np.array([LUNCH_START_MEAN])
lunch_start_std     = np.array([LUNCH_START_STD])

# the mean and standard deviation of the eat lunch duration, respectively
lunch_dt_mean       = np.array([LUNCH_DT_MEAN])
lunch_dt_std        = np.array([LUNCH_DT_STD])

# the mean and standard deviation of the eat dinner start time, respectively
dinner_start_mean   = np.array([DINNER_START_MEAN])
dinner_start_std    = np.array([DINNER_START_STD])

# the mean and standard deviation of the eat dinner duration, respectively
dinner_dt_mean      = np.array([DINNER_DT_MEAN])
dinner_dt_std       = np.array([DINNER_DT_STD])

# the mean and standard deviation of the commute to work duration, respectively
commute_to_work_dt_mean     = np.array([COMMUTE_TO_WORK_DT_MEAN])
commute_to_work_dt_std      = np.array([COMMUTE_TO_WORK_DT_STD])

# the mean and standard deviation of the commute from work duration, respectively
commute_from_work_dt_mean   = np.array([COMMUTE_FROM_WORK_DT_MEAN])
commute_from_work_dt_std    = np.array([COMMUTE_FROM_WORK_DT_STD])

# the mean and standard deviation for the work start time, respectively
work_start_mean     = np.array([WORK_START_MEAN])
work_start_std      = np.array([WORK_START_STD])

# the mean and standard deviation for the work end time, respectively
work_end_mean       = np.array([WORK_END_MEAN])
work_end_std        = np.array([WORK_END_STD])

# the number of standard deviations to truncate in the normal distribution in the
# activity-parameters
trunc = np.array([TRUNC])

if no_variation:

    # set the variation to zero
    result = set_no_variation(num_people)

    # store the results in the appropriate variables
    sleep_start_std, sleep_end_std, bf_start_std, bf_dt_std, lunch_start_std, lunch_dt_std, \
    dinner_start_std, dinner_dt_std, work_start_std, work_end_std, commute_to_work_dt_std, \
    commute_from_work_dt_std = result

# ===========================================
# the household parameters
# ===========================================
hhld_param = params.Params(t_start=t_start, num_days=num_days, num_hours=num_hours, num_min=num_min, \
                               sleep_start_mean=sleep_start_mean, sleep_start_std=sleep_start_std, \
                               sleep_end_mean=sleep_end_mean, sleep_end_std=sleep_end_std, \
                               bf_start_mean=bf_start_mean, bf_start_std=bf_start_std, bf_start_trunc=trunc, \
                               bf_dt_mean=bf_dt_mean, bf_dt_std=bf_dt_std, bf_dt_trunc=trunc, \
                               lunch_start_mean=lunch_start_mean, lunch_start_std=lunch_start_std, \
                               lunch_start_trunc=trunc, \
                               lunch_dt_mean=lunch_dt_mean, lunch_dt_std=lunch_dt_std, lunch_dt_trunc=trunc, \
                               dinner_start_mean=dinner_start_mean, dinner_start_std=dinner_start_std, \
                               dinner_start_trunc=trunc, \
                               dinner_dt_mean=dinner_dt_mean, dinner_dt_std=dinner_dt_std, dinner_dt_trunc=trunc, \
                               work_start_mean=work_start_mean, work_start_std=work_start_std, \
                               work_end_mean=work_end_mean, work_end_std=work_end_std, \
                               commute_to_work_dt_mean=commute_to_work_dt_mean, \
                               commute_to_work_dt_std=commute_to_work_dt_std, \
                               commute_from_work_dt_mean=commute_from_work_dt_mean, \
                               commute_from_work_dt_std=commute_from_work_dt_std,\
                               job_id=job_id)
