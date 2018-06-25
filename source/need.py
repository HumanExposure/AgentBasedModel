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
This module contains information about governing the various needs that agents have in the simulation.

This module contains the class :class:`need.Need`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# general math package
import numpy as np

# ===============================================
# constants
# ===============================================

# the needs value also corresponds to a position in the matrix

# Major needs. These needs do NOT depend on the state of other needs
REST    = 0
INCOME  = 1
HUNGER  = 2

# Minor needs. These needs may depend on the state of other need
TRAVEL          = 3
INTERRUPTION    = 4

# This dictionary takes the INTEGER representation of a the Need category and
# returns a STRING representation
INT_2_STR = {
    REST: 'Rest',
    INCOME: 'Income',
    HUNGER: 'Hunger',
    TRAVEL: 'Travel',
    INTERRUPTION: 'Interruption',
}

# total number of needs
N = len( INT_2_STR.items() )

# This dictionary takes the STRING representation of a Need category and
# returns an INTEGER representation
STR_2_INT = { v: k for k, v in INT_2_STR.items() }


# this function is the minimum satiation under normal conditions.
# since this value is > 0, the program may allow emergency situations by
# allowing the satiation to decrease under this amount
MIN_DEFAULT         = 1e-10

# this sets the magnitude of a interrupting need
MAG_INTERRUPTION    = 1e-11

# The magnitude of the need association when it is time to be at work/ school
MAG_WORK            = max(1e-9, MIN_DEFAULT)

# the travel need's satiation for commuting. This should be less than the magnitude for work
MAG_COMMUTE         = max( MAG_WORK/2, MIN_DEFAULT)

# default threshold for need
THRESHOLD           = 0.2

# used in weight function to avoid division by 0
EPS                 = 1e-12

# this is to take care of machine precision errors
# when checking the magnitude of the satiation to the threshold
EPS_THRESHOLD       = 1e-13

# ===============================================
# class Need
# ===============================================

class Need(object):

    """
    This class holds general information about needs.

    :param temporal.Temporal clock: the clock governing time in the simulation
    :param int num_sample_points: the number of time nodes in the simulation

    :var int category: the need- identifier
    :var temporal.Temporal clock: keeps track of the time
    :var float history: an array containing the magnitude level :math:`[0,1]` of the need at all \
                        sample times.

    :var float magnitude: the magnitude of the need (the satiation)
    :var int t0: this keeps track of the last time the need was addressed
    :var float threshold: the threshold of the need
    """

    #
    # constructor
    #
    def __init__(self, clock, num_sample_points):


        # initialize the category to -1
        self.id = -1

        # set the clock
        self.clock = clock

        # set the previous time a need was addressed to 0
        self.t0 = 0

        # set the threshold
        self.threshold = THRESHOLD

        # set the magnitude
        self.magnitude = 1.0
        # this stores the history at all sample_points (in time)
        self.history  = np.zeros( ( num_sample_points,1 ) )
        return

    def decay(self):

        """
        This calculates the amount of decay over a time step.

        .. note::
            This function is meant to be overridden.

        :return: None
        """

        return

    def initialize(self):

        """
        This function initializes the state of the need at the very beginning of simulation.

        .. note::
            This function is meant to be overridden.

        :return: None
        """

        return

    def print_category(self):

        """
        This function represents the category as a string.

        :return: the string representation of the category
        :rtype: str
        """

        # The error message if an invalid choice of category is assigned
        msg = 'ERROR! %d is an Invalid choice of need.Neeed.id!\n' % self.id

        # return the string representation of the category if the category is valid. If the category is NOT valid,
        # return the error message
        return INT_2_STR.get(self.id, msg)

    def reset(self):

        """
        This function resets the values in order for the need to be used in the next simulation. This function \
        does the following:
        
        #. sets the satiation to 1.0
        #. sets the history to zero
        
        :return: None
        """

        # set the magnitude
        self.magnitude = 1.0

        # this stores the history at all sample_points (in time)
        self.history[:] = 0

        return

    def toString(self):

        """
        This function represents the Need object as a string.

        :return msg: the string representation of the Need object
        :rtype: str
        """

        msg = ''
        msg = msg + 'Category:\t' + self.print_category() + '\n'
        msg = msg + 'Threshold:\t%f\n' % self.threshold
        msg = msg + 'Magnitude:\t%f\n' % self.magnitude

        return msg

    def under_threshold(self, n):

        """
        Compares the value of anNeed's satiation to the threshold.

        :param float n: the satiation

        :return: True if the satiation is less than or equal to the threshold, False otherwise
        :rtype: bool
        """

        # need to do a comparison within a tolerance in order to take account of
        # inexact arithmetic and loss of precision when the need level is subtracted
        # by a small number over many time steps
        return (n <= self.threshold + EPS_THRESHOLD)

    def weight(self, n):

        """
        This function calculates the weight function of a need.

        :param float n: the satiation

        :return: the weight due to the  need
        :rtype: float
        """

        # the weight
        w = 1.0 / (n + EPS)

        return w
