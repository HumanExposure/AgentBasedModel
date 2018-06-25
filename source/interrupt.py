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
This module contains code for interrupting a current activity.

This module contains class :class:`interrupt.Interrupt`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# agent-based model modules
import activity, need

# ===============================================
# class Interrupt
# ===============================================

class Interrupt(activity.Activity):

    """
    This class allows for the current activity to be interrupted by another activity.
    """

    #
    # constructor
    #
    def __init__(self):

        activity.Activity.__init__(self)

        self.id = activity.INTERRUPT
        
        return

    def advertise(self, p, str_need, act):

        """
        This function calculates the score of an activities advertisement to a Person. This function does the \
        the following:
        
        #. temporarily sets the value of the Need that must be immediately addressed to a low level.
        #. send an advertisement is is made from the potentially interrupting activity
        #. calculate the score from the potentially interrupting activity
        
        :param person.Person p: the person who is being advertised to
        :param int str_need: the id of the Need that needs to be addressed, which \
                                could potentially cause an interrupting event
        :param activity.Activity act: the activity of interest that could immediately \
                            interrupt a current activity

        :return: the value of the advertisement
        :rtype: float
        """

        # original magnitude of the need
        mag_temp = p.needs[str_need].magnitude
        
        # set the magnitude of the interrupting need 
        p.needs[str_need].magnitude = need.MAG_INTERRUPTION
        
        # get the score
        score = act.advertise(p)
        
        # restore the need magnitude to the original amount
        p.needs[str_need].magnitude = mag_temp
        
        return score

    def start(self, p):

        """
        This handles the start of an activity.

        :param person.Person p: the person of interest
        :return: None
        """

        # store a list of the arguments for the end() procedure
        p.state.arg_end.append(p)

        return