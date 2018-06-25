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
This module is responsible for containing parameters that driver.py uses to control \
the simulation. The user should set the parameters in this module **before** \
running the driver :literal:`driver.py`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===========================================
# import
# ===========================================
import sys
sys.path.append('..\\processing')
sys.path.append('..\\source')

# agent-based model modules
import my_globals as mg
import demography as dmg
import trial

# ===========================================
# default constants
# ===========================================

#  the default number of days in the simulation
NUM_DAYS    = 7

# the default number of additional hours in the simulation
NUM_HOURS   = 0

# the default number of additional minutes in the simulation
NUM_MIN     = 0

# the default number of people per household
NUM_PEOPLE  = 1

# default directory to save the data
FPATH       = mg.FDIR_MY_DATA

# default file name to load pre-existing input data
FNAME_LOAD_TRIALS_BASE = None

# ===========================================
# user-defined parameters
# ===========================================

# seed for the random number generator (set to None or a fixed integer for reproducibility)
seed        = None

# -------------------------------------------
# time information
# -------------------------------------------

# the number of days
num_days    = 7

# the number of additional hours
num_hours   = 8

# the number of additional minutes
num_min     = NUM_MIN

# the number of people per household
num_people  = NUM_PEOPLE
# -------------------------------------------
# flags
# -------------------------------------------

# control how the simulation moves through time (False, is the default)
# If True, the simulation uses a strategy to move through time minute by minute, which is slow
# If False, the simulation uses a strategy to move through time by skipping to time steps in which
# a potential computation, calculation, or action could be done. This greatly decreases the simulation \
# by decreasing the total amount of computation.
do_minute_by_minute = False

# should the simulation plot results at the end of the run
do_plot         = False

# should the simulation print messages to the screen
do_print        = True

# should the simulation save the results (both input and output) of the simulation
do_save         = True

# load previously made input
do_load_trials  = False

# -------------------------------------------
# demographic parameters
# -------------------------------------------

# select trial
trial_code      = trial.OMNI

# set the demographic
demographic     = dmg.ADULT_WORK

# -------------------------------------------
# save and load parameters
# -------------------------------------------

# the directory to save the data (output)
fpath   = FPATH

# the directory to load the input
fname_load_trials_base = FNAME_LOAD_TRIALS_BASE

# ==============================================
# initialize the random number generator
# ==============================================

# initialize generator
mg.initialize_random_number_generator(seed)