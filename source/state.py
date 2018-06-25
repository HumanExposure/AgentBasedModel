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
This module contains code that governs information relevant to a person's state.

This module contains class :class:`state.State`.
"""

# ===============================================
# import
# ===============================================
import sys

# ===============================================
# constants
# ===============================================

IDLE_TEMP   = -1        # the Person is Idle this time step and has gone through
                        # the advertisement stage and ending up without an activity
IDLE        = 0         # the Person/ Asset is free to do any Action
SLEEP       = 1         # the Person is asleep
TRANSIT     = 2         # the Person is awake and in the process of traveling from the
                        # home to another location and vice versa
WORK        = 3         # the Person is awake and at a location other than the home
BUSY        = 4         # the Person/ Asset performing an Activity that CANNOT be done
                        # with another Activity simultaneously
BUSY_MULTI  = 5         # the Person / Asset  performing an Activity that CAN be
                        # done with another Activity simultaneously

# This dictionary takes the INTEGER representation of an state status and
# returns the STRING representation
INT_2_STR = {
    IDLE_TEMP: 'Temporary Idle',
    IDLE: 'Idle',
    SLEEP: 'Sleep',
    WORK: 'Work',
    TRANSIT: 'Transit',
    BUSY: 'Busy',
    BUSY_MULTI: 'Busy_Multi',
}

# This dictionary takes the STRING representation of an state status and
# returns the INTEGER representation
STR_2_INT = { v: k for k, v in INT_2_STR.items() }

# ===============================================
# class State
# ===============================================

class State (object):

    """
    This class contains information relevant to a person state

    :param int status: the status of the person

    :var activity.Activity 'activity': the particular activity of the asset
    :var list arg_start: the list of arguments for the start() function
    :var list arg_end: the list of arguments for the end() function
    :var asset.Asset 'asset': the Asset that is being used
    :var list asset_list:
    :var bool is_init: this is a flag indicating whether or not the agent is in the initialization state. \
    This state only occurs during the first step of the simulation.
    :var int status: the status of a person
    :var int t_end: the end time of a state [minutes, universal time]
    :var int t_start: the start time of the current state [minutes, universal time]
    :var int round_dt: the amount of minutes [-1, 0, 1] to round an activity duration
    :var float dt_frac: the fraction of a minutes subtracted from rounding down from the true projected \
    activity duration
    :var bool do_interruption: a flag indicating whether the person is interrupting an ongoing activity
    """

    #
    # constructor
    #
    
    def __init__(self, status=IDLE):
        
        self.status     = status
        self.t_start    = 0
        self.t_end      = self.t_start
        
        self.asset      = None
        self.asset_list = []
        
        self.activity   = None
        self.arg_start  = []
        self.arg_end    = []
        
        # this shows that if the Person is in the initialization state
        #self.is_init = False

        # the amount of minutes [-1, 0, 1] to round an activity duration
        self.round_dt = 0

        # the fraction of a minute subtracted from rounding down from the true projected activity duration
        self.dt_frac = 0.0

        self.do_interruption = False
        return

    def end_activity(self):

        """
        This function ends an activity.

        :return: None
        """

        if( self.activity is None):
            self.status = IDLE
        else:
            self.run_activity(self.arg_end, self.activity.end)

        # reset the end() and argument list
        self.asset      = None
        self.activity   = None
        self.arg_end    = []

        return

    def halt_activity(self, p):

        """
        This function runs the halt activity. The function is used by interruptions \
        to stop an activity **immediately** without giving benefits to the need that the \
        halted activity addressed.

        :param person.Person p: the person of interest
        :return: None
        """

        self.arg_start = [p]

        # if currently not doing an activity
        if self.activity is None:
            # do nothing
            uu = 1

        # run the new activity
        self.run_activity(self.arg_start, self.activity.halt)

        self.asset      = None
        self.activity   = None
        self.arg_start  = None
        self.arg_end    = []
        self.do_interruption    = False

        return

    def print_activity(self):

        """
        The string representation of the activity. This function handles the \
        possibility of the activity being None.

        :return: the representation of the activity
        :rtype: str
        """

        msg = ''
        if (self.activity is None):
            msg = msg + str(None)
        else:
            msg = msg + self.activity.toString()

        return msg

    def print_asset(self):

        """
        This function represents the asset as a string. This function handles \
        the possibility of the asset being None.

        :return: the representation of the asset
        :rtype: str
        """

        msg = ''
        if (self.asset is None):
            msg = msg + str(None)
        else:
            msg = msg + self.asset.toString()

        return msg

    def print_status(self):

        """
        This function represents the status as a string.

        :return: the representation of the status
        :rtype: str
        """

        # the error message
        msg = 'ERROR! %d is an Invalid choice of STATE.status!\n' % self.status

        return INT_2_STR.get(self.status, msg)

    def reset(self, t_univ):

        """
        Reset the state object to the default behavior at the beginning of the simulation.

        :param int t_univ: the time of the beginning of the simulation in universal time [seconds]
        :return: None
        """

        self.status     = IDLE
        self.t_start    = t_univ
        self.t_end      = t_univ

        self.asset = None
        self.asset_list = []

        self.activity = None
        self.arg_start = []
        self.arg_end = []

        # this shows that if the Person is in the initialization state
        #self.is_init = False

        # the amount of minutes [-1, 0, 1] to round an activity duration
        self.round_dt = 0

        # the fraction of a minute subtracted from rounding down from the true projected activity duration
        self.dt_frac = 0.0

        self.do_interruption = False

        return

    def reset_rounding_parameters(self):

        """
        This function resets the rounding parameters to zero.

        :return: None
        """

        self.round_dt   = 0
        self.dt_frac    = 0.0

        return

    def reset_time_status(self, t_start, status=IDLE):

        """
        This function resets the time information to the current time and \
        sets the status. This function is usually used at the end of an activity.

        :param int t_start: the start time [minutes, universal time]
        :param int status: the status of the person

        :return: None
        """

        self.status     = status
        self.t_start    = t_start
        self.t_end      = self.t_start

        return

    def run_activity(self, arg, func):

        """
        This function allows an activity to start, end, or halt

        :param list arg:  arguments for the func() function
        :param function func:  arguments for the func() function

        :return: None
        """
        # The +1 is due to the self argument
        narg = 1 + len(arg)

        # an error message
        msg = ''
        msg = msg + 'ERROR! %d is an invalid number of arguments for the chosen function!\n' % narg

        # func -> activity.end(p)
        # choose the correct function
        # offset is doe to func(self, arg)
        if ( narg == 1):
            func()
        elif ( narg == 2):
            func(arg[0]) # this is the function that is usually selected
        elif ( narg == 3):
            func(arg[0], arg[1])
        elif( narg == 4):
            func(arg[0], arg[1], arg[2])
        else:
            func = sys.stdout.write(msg)

        return

    def start_activity(self):

        """
        This function starts an activity

        :return: None
        """

        self.run_activity(self.arg_start, self.activity.start)
        
        # reset arguments for activity.start()
        self.arg_start = None

        return


    def toString(self):

        """
        This function represents the State object as a string.

        :return: the representation of the State object
        :rtype: str
        """

        msg = ''
        msg = msg + 'State:\t' + self.print_status() + '\n'
        msg = msg + 't_start:\t%d\n' % self.t_start
        msg = msg + 't_end:\t%d\n' % self.t_end
        msg = msg + 'current Asset being used:\n' + self.print_asset() + '\n'
        msg = msg + 'current Activity being used:\n' + self.print_activity() + '\n'
        
        return msg
