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
This module contains code that governs the activities that the agent performs
in order to satisfy its needs.

This module contains the following class: :class:`activity.Activity`.

.. moduleauthor:: Dr. Namdi Brandon
"""


# ===============================================
# import
# ===============================================

# agent-based model modules
import my_globals as mg
import activity, need, temporal

# ===============================================
# constants
# ===============================================

# identifiers for each activity
NO_ACTIVITY         = mg.KEY_IDLE
INTERRUPT           = mg.KEY_INTERRUPT
WORK                = mg.KEY_WORK
SLEEP               = mg.KEY_SLEEP
COMMUTE_TO_WORK     = mg.KEY_COMMUTE_TO_WORK
COMMUTE_FROM_WORK   = mg.KEY_COMMUTE_FROM_WORK
EAT_BREAKFAST       = mg.KEY_EAT_BREAKFAST
EAT_LUNCH           = mg.KEY_EAT_LUNCH
EAT_DINNER          = mg.KEY_EAT_DINNER
EDUCATION           = mg.KEY_EDUCATION

# This dictionary takes the INTEGER representation of an Activity
# category and returns a STRING representation
INT_2_STR = {
    NO_ACTIVITY: 'No Activity',
    WORK: 'Work',
    SLEEP: 'Sleep',
    COMMUTE_TO_WORK: 'Commute to Work',
    COMMUTE_FROM_WORK: 'Commute from Work',
    EAT_BREAKFAST: 'Eat Breakfast',
    EAT_LUNCH: 'Eat Lunch',
    EAT_DINNER: 'Eat Dinner',
    EDUCATION: 'Education',
    INTERRUPT: 'Interrupt',
}

# This dictionary takes the STRING representation of an activity
# category and returns an INTEGER representation
STR_2_INT = { v: k for k, v in INT_2_STR.items() }

# This direcotry takes an interger representation for an activity and
# assigns it a color used for plotting
INT_2_COLOR = {
    NO_ACTIVITY: 'grey',
    WORK: 'brown',
    SLEEP: 'green',
    COMMUTE_TO_WORK: 'red',
    COMMUTE_FROM_WORK: 'cyan',
    EAT_BREAKFAST: 'orange', # black
    EAT_LUNCH: 'purple',
    EAT_DINNER: 'blue',
    EDUCATION: 'pink',
}

# ===============================================
# class Activity
# ===============================================

class Activity(object):

    """
    An activity enables a :class:`person.Person` to address its satiation
    :math:`n(t)`. This class's purpose is to encapsulate general
    capabilities that specific instances of activity will derive from.

    :ivar int category: an unique identifier naming the type of activity.
    :ivar int t_end: the end time of the activity [universal time, seconds]
    :ivar int t_start: the start time of the activity [universal time, seconds]
    :ivar int dt: the duration of the activity [seconds]
    """

    #
    # Constructor
    #
    def __init__(self):

        # activity identifier
        self.id = NO_ACTIVITY

        # start time (universal time, min)
        self.t_start = 0

        # end time (universal time, min)
        self.t_end = self.t_start

        # the duration of an activity
        self.dt = self.t_end - self.t_start    
        
        return

    # ------------------------------------------------------
    #  functions
    # ------------------------------------------------------

    def advertise(self, the_need, dt):

        """
        Calculates the advertised score of doing an activity. Let
        :math:`\\Omega` be the set of all needs addressed by the activity.
        The score :math:`S` is calculated by doing the following
        
        .. math::     
            S = \\begin{cases}
                0  & n(t) > \\lambda \\\\
                \\sum_{j \in \Omega} W_j( n_j(t) ) - W_j( n_j(t + \\Delta{t} )) & n(t) \\le \\lambda
            \\end{cases}
            
        where
            * :math:`t` is the current time
            * :math:`\\Delta{t}` is the duration of the activity
            * :math:`n(t)` is the satiation at time :math:`t`
            * :math:`\\lambda` is the threshold value of the need
            * :math:`W(n)` is the weight function for the particular need

        :param need.Need the_need: the primary need associated with the respective activity
        :param int dt: the duration :math:`\\Delta{t}` of doing the activity [minutes]

        :returns score: the score of the advertisement
        :rtype: float
        """

        # this is the lowest score
        score = 0.0

        # create a clock for the Need perception due the activity when it's finished
        future_clock = temporal.Temporal(the_need.clock.t_univ + dt)

        # the current need association level
        n_now = the_need.magnitude

        # if the  need association is below a threshold, make the advertise the activity's value
        if ( the_need.under_threshold(n_now) ):

            # the resulting need association level when the activity is done
            n_later = the_need.perceive(future_clock)

            # the score from the advertisement
            score = score + ( the_need.weight(n_now) - the_need.weight(n_later) )

        # return the value of the score
        return score

    def advertise_interruption(self):

        """
        Advertise the score if this activity interrupts another activity.
        
        .. note:: 
            This function should be overloaded in derived classes.

        :returns score: the advertised score
        :rtype: float

        """

        # set score to zero
        score = 0.0
        
        return score

    def end(self, p):

        """
        This function handles some of the common logistics in ending a specific activity assuming \
        the activity ends without an interruption.

        Currently the function does the following:
        
        #. reset the :class:`state.State` variable's start time to the current time
        #. reset the :class:`state.State` variable's end time to the current time
         
        :param person.Person p: the person whose activity is ending
        :return: None
        """

        # reset the state's time information to the current time
        p.state.t_start = p.clock.t_univ
        p.state.t_end   = p.state.t_start

        return

    def halt(self,p):

        """
        This function handles some of the common logistics in ending a specific activity due to an \
        interruption.

        Currently the function does the following:
        
        #. reset the :class:`state.State` variable's start time to the current time
        #. reset the :class:`state.State` variable's end time to the current time
        
        :param person.Person p: the person whose activity is being interrupted
        :return: None
        """

        # do the logistics in ending an activity normally (without interruption)
        p.state.t_start = p.clock.t_univ
        p.state.t_end   = p.state.t_start

        return

    def print_id(self):

        """
        This function represents the activity category as a string.

        :return msg: The string representation of the category
        :rtype: str
        """

        # write an error message if the category is not a valid choice
        msg = 'ERROR! %d is not a valid choice for activity.\n' % self.id

        # If the category is a valid choice, return the string form of the category
        # Else, return an error message
        return INT_2_STR.get(self.id, msg)


    def start(self):

        """
        This function starts a specific activity.

        .. note::
            This function is meant to be overloaded by derived activity classes.

        :return: None
        """

        return

    def toString(self):

        """
        This function represents the Activity object as a string.

        :return msg: the string representation of the activity object
        :rtype: str
        """

        # write the identifier
        msg = ''
        msg = msg + 'Activity Type: ' + self.print_id()+ '\n'
        
        return msg
