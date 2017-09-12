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
This module contains constants and functions that are used for general use.

This module contains information about the following constants:

#. Identifiers for activity codes
#. File names \ file paths for saving figures for the different demographics
#. File names \ file paths for saving figures for the different activities

.. moduleauthor:: Dr. Namdi Brandon
"""

# -----------------------------------------------
# import
# -----------------------------------------------
# general math capability
import numpy as np

# statistical modeling features
from statsmodels.distributions.empirical_distribution import ECDF

# statistical capability
import scipy.stats as stats

import os, pickle, shutil


# -----------------------------------------------
# constants
# -----------------------------------------------

# these are keys values to be used in dictionaries for the respective activities
KEY_IDLE                = -1
KEY_INTERRUPT           = -100
KEY_COMMUTE_FROM_WORK   = 1
KEY_COMMUTE_TO_WORK     = 2
KEY_EAT_BREAKFAST       = 3
KEY_EAT_DINNER          = 4
KEY_EAT_LUNCH           = 5
KEY_SLEEP               = 6
KEY_WORK                = 7
KEY_EDUCATION           = 8

# keys for all of the activities
KEYS_ACTIVITIES          = (KEY_COMMUTE_FROM_WORK, KEY_COMMUTE_TO_WORK, KEY_EAT_BREAKFAST, KEY_EAT_DINNER, \
                            KEY_EAT_LUNCH, KEY_SLEEP, KEY_WORK)

FDIR_MY_DATA                = '..\\my_data'
FDIR_SAVE_FIG               = FDIR_MY_DATA + '\\fig'

FDIR_SAVE_FIG_DEMOGRAPHIC   = FDIR_SAVE_FIG + '\\demographic'

FDIR_SAVE_FIG_ALL               = FDIR_SAVE_FIG_DEMOGRAPHIC + '\\all'
FDIR_SAVE_FIG_ADULT             = FDIR_SAVE_FIG_DEMOGRAPHIC + '\\adult'
FDIR_SAVE_FIG_ADULT_NON_WORK    = FDIR_SAVE_FIG_DEMOGRAPHIC + '\\adult_non_work'
FDIR_SAVE_FIG_ADULT_WORK        = FDIR_SAVE_FIG_DEMOGRAPHIC + '\\adult_work'
FDIR_SAVE_FIG_CHILD_SCHOOL      = FDIR_SAVE_FIG_DEMOGRAPHIC + '\\child_school'
FDIR_SAVE_FIG_CHILD_YOUNG       = FDIR_SAVE_FIG_DEMOGRAPHIC + '\\child_young'

FDIR_SAVE_FIG_COMMUTE_FROM_WORK = '\\commute_from_work'
FDIR_SAVE_FIG_COMMUTE_TO_WORK   = '\\commute_to_work'
FDIR_SAVE_FIG_EAT_BREAKFAST     = '\\eat_breakfast'
FDIR_SAVE_FIG_EAT_DINNER        = '\\eat_dinner'
FDIR_SAVE_FIG_EAT_LUNCH         = '\\eat_lunch'
FDIR_SAVE_FIG_EDUCATION         = '\\education'
FDIR_SAVE_FIG_SLEEP             = '\\sleep'
FDIR_SAVE_FIG_WORK              = '\\work'

FDIR_SAVE_FIG_RANDOM_DAY        = '\\random_day'
FDIR_SAVE_FIG_WEEKDAY           = '\\weekday'
FDIR_SAVE_FIG_WEEKEND           = '\\weekend'

KEY_2_FDIR_SAVE_FIG = { KEY_COMMUTE_FROM_WORK: FDIR_SAVE_FIG_COMMUTE_FROM_WORK,
                         KEY_COMMUTE_TO_WORK: FDIR_SAVE_FIG_COMMUTE_TO_WORK,
                         KEY_EAT_BREAKFAST: FDIR_SAVE_FIG_EAT_BREAKFAST,
                         KEY_EAT_DINNER: FDIR_SAVE_FIG_EAT_DINNER,
                         KEY_EAT_LUNCH: FDIR_SAVE_FIG_EAT_LUNCH,
                         KEY_EDUCATION: FDIR_SAVE_FIG_EDUCATION,
                         KEY_SLEEP: FDIR_SAVE_FIG_SLEEP,
                         KEY_WORK: FDIR_SAVE_FIG_WORK,}

# the number of statistical events
N_SOLO = 1
N_LONG = 2

# file ending used for batch saves
F_BATCH_ENDING = '_b%04d.pkl'
# -----------------------------------------------
# functions
# -----------------------------------------------

def fill_out_data(t, y):

    """
    This function takes an array of activity start times and activity codes from an activity diary and \
    fills out the activity, minute-by-minute in between two adjacent activities.
    
    :param numpy.ndarray t: the start times in an activity diary
    :param numpy.ndarray y: the activity codes in an activity diary
    :return: 
    """

    # a list of minute by minute times for each start activity
    t_group = group_time(t)

    # a list of minute by minute activity codes for each activity
    y_group = [ y[i] * np.ones(x.shape) for i, x in enumerate(t_group) ]

    # create 1 large numpy array
    y_fill = np.hstack(y_group)

    return y_fill

def fill_out_time(t):

    """
    This function takes an array of activity start times from an activity diary and fills out the time, \
    minute-by-minute in between two adjacent activities
    
    Example, if t = (0, 4, 7) (and :math:`t_{final}=10`) we get the following:
        
         * (0, 1, 2, 3)
         * (4, 5, 6)
         * (7, 8, 9, 10)
    
    :param numpy.ndarray t: the start times in the activity diary [minutes, universal time]
    :return: None
    """

    # a list of minute by minute times for each start activity
    t_group = group_time(t)

    # fill out the times
    t_fill = np.hstack(t_group)

    return t_fill

def from_periodic(t, do_hours=True):

    """
    This function returns the time of day in a 24 hour format. It takes the time :math:`t \\in [-12, 12)` and \
    expresses it at time :math:`x \\in [0, 24)` where 0 represents midnight. The same calculation can be \
    done to represent the time in minutes

    :param float t: the time in hours [-12, 12), or the respective minutes [-12 * 60, 12 * 60)
    :param bool do_hours: a flag to do the calculations in hours (if True)
    :return: the time in [0, 24) or in minutes [0, 24 * 60)
    """

    HOUR_2_MIN = 60

    if do_hours:
        x = t + (t < 0) * (24)
    else:
        x = t + (t < 0) * (24 * HOUR_2_MIN)

    return x

def get_ecdf(data, N=100):

    """
    Given data, this function calculates the probability data from the empirical cumulative \
    distribution function (ECDF).

    :param float data: an array containing the relevant data to get the ECDF of
    :param int N: the amount of samples in calculating the ECDF results

    :return y: the ECDF
    :rtype: float array

    :return x: the values sampled for the ECDF
    :rtype: float array
    """

    # create the distribution function from the data
    ecdf = ECDF(data.flatten())

    # this allows the CDF to transition from  y=0 to y>0 at the minimum x value
    x_min = min(data) - 0.01

    # uniformly get values in the range of the data
    x = np.linspace(x_min, max(data), N)

    # calculate the cdf
    y = ecdf(x)

    return x, y

def group_time(t):

    """
    This function takes data from an activity diary and groups that activity diary into \,
    minute by minute arrays from start to end for each activity (start, start + 1, ... end-1, end)
    
    :param numpy.ndarray t: the start times from an activity diary [minutes, universal time] 
    :return: the grouped start/end pairs for ech activitiy
    :rtype: list
    """
    # take all events except the last
    N = len(t[:-1])

    t_group = [np.arange(t[i], t[i + 1]) for i in range(N)]

    return t_group

def hours_to_minutes(t):

    """
    This function takes a duration of time in hours and converts the time rounded to the nearest minutes.

    :param float t: a duration of time [hours]

    :return: the time in minutes
    """

    HOUR_2_MIN = 60

    x = np.round( t * HOUR_2_MIN ).astype(int)

    return x

def load(fname):

    """
    This function loads data from a .pkl file.

    :param str fname: the file name to be loaded from
    :return: the data unpickled
    """

    # open the file for reading
    fin = open(fname, 'rb')

    # load the data
    x = pickle.load(fin)

    # close the file
    fin.close()

    return x

def sample_normal(std, dx):

    """
    This function samples a normal distribution centered at zero assuming a max and minimum acceptable value [dx, -dx].

    :param float std: the standard deviation
    :param float dx: the amount of total deviation from the mean allowd
    :return:
    """

    # the range of "acceptable variation"
    x_min, x_max = -dx, dx

    # sample for variation centered at zero
    x = stats.norm.rvs(loc=0, scale=std)

    # only accept values that are in the acceptable range
    is_bad_value = (x < x_min) or (x > x_max)

    count = 0

    # sample for "good" behaving variation
    while (is_bad_value and count < 5):

        # re-sample for the variation
        x = stats.norm.rvs(loc=0, scale=std)

        # check for an unacceptable value
        is_bad_value = (x < x_min) or (x > x_max)

        count = count + 1

    # if there is still not a good value, set to zero variation
    if (is_bad_value):
        x = 0

    return x

def save(x, fname):

    """
    This function saves a python variable by pickling it.

    :param x: the data to be saved
    :param str fname: the file name of the saved file. It must end with .pkl

    """

    # create the directory for the save file if it does not exist
    os.makedirs(os.path.dirname(fname), exist_ok=True)

    # open the file for writing
    fout = open(fname, 'wb')

    # save the file as a binary
    pickle.dump(x, fout)

    # close the file
    fout.close()

    return

def save_zip(out_file, source_dir):

    """
    This function compresses an entire directory as a zip file.

    :param str out_file: the filename of the save zip file with out the .zip extension
    :param str source_dir: the directory to be compressed
    :return: the name of the compressed directory
    """

    # create the file path to the save file if it does not exist
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    # zip the source directory
    x = shutil.make_archive(out_file, 'zip', source_dir)

    return x

def set_distribution(lower, upper, mu, std):

    """
    This function sets the truncated normal probability distribution.

    :param int lower: the lower bound in number of standard deviation from the mean
    :param int upper: the upper bound in number of standard deviation from the mean
    :param int mu: the mean
    :param int std: the standard deviation
    
    :return: the function for the truncated normal distribution
    """

    f = stats.truncnorm(lower, upper, loc=mu, scale=std).rvs

    return f

def set_distribution_dt(lower, upper, mu, std, x_min):

    """
    This function set the truncated normal probability distribution subject to the fact that there \
    is an assigned lowest value.
    
    If the lowest value of the normal distribution is lower than the lowest \
    allowed value, change the distribution so that the standard deviation allows the distribution to not be \
    lower than the lowest allowed value.

    :param int lower: the lower bound in number of standard deviation from the mean
    :param int upper: the upper bound in number of standard deviation from the mean
    :param int mu: the mean
    :param int std: the standard deviation
    :param int x_min: the lowest allowed value
    
    :return: the function for the truncated normal distribution, the standard deviation of the distribution 
    :rtype: tuple
    """

    # the lowest value assuming a truncated normal distribution
    y_min = mu - lower * std

    # if the lowest value assuming a truncated normal distribution is smaller than the lowest allowed value,
    # change the distribution to have the same mean but a different standard deviation so that the
    # lowest value from the new distribution is the lowest possible value
    if (y_min < x_min):
        # the new standard deviation
        the_std = np.floor( (mu - x_min) / lower ).astype(int)

    else:
        the_std = std

    # set the truncated normal distribution
    f = set_distribution(lower, upper, mu, the_std)

    return f, the_std

def to_periodic(t, do_hours=True):

    """
    This function returns the time of day in a periodic format. It takes the time :math:`t \\in [0, 24)` and \
    expresses it at time :math:`x \\in [-12, 12)` where 0 represents midnight.

    :param float t: the time in hours [0, 24)
    :param bool do_hours: a flag to do the calculations in hours (if True) or minutes if False

    :return: the time in [-12, 12) or minutes [-12 * 60, 12 * 60)
    :rtype: float
    """

    HOUR_2_MIN = 60

    if do_hours:
        x = t + (t >= 12) * (-24)
    else:
        # do the calculation in minutes
        x = t + (t >= 12 * HOUR_2_MIN) * (-24 * HOUR_2_MIN)

    return x

