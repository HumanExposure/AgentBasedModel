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
This module contains code that is is responsible for controlling the scheduler for the simulation. Note \
that the simulation does **not** run continuously in from one adjacent time step to the next. Instead the \
simulation jumps forward in time (i.e. move across multiple time steps in time), stopping only at time steps \
in which an action could occur. The ability to jump forward in time is controlled by the scheduler.

The scheduler will trigger the simulation to stop skipping time steps for the following reasons:

#. an activity should start
#. an activity should end
#. a need is under threshold

This module contains class :class:`scheduler.Scheduler`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# general math capability
import numpy as np

# agent-based model module
import need

# ===============================================
# class Scheduler
# ===============================================

class Scheduler(object):

    """
    This class contains the code for the scheduler. The scheduler is in charge of jumping forward in time and \
    stopping at only potentially relevant time steps. The scheduler keeps track of the needs for every person in \
    in the household and stops at time steps where any person should have an action / need that needs to be \
    addressed.
    
    
    :param temporal.Temporal clock: the time
    :param int num_people: the number of people in the household
    
    :var temporal.Temporal clock: the time
    :var numpy.ndarray A: the schedule matrix of dimension (number of people x number of needs). This matrix \
    contains the times [minutes, universal time] that the simulation should not skip over
    :var int dt: the duration of time between events
    :var int t_old: the time [minutes, universal time] of the prior event
    :var bool do_minute_by_minute: this flag controls whether the schedule should either \
    go through time minute by minute (if True) or jump forward in time (if False). The default \
    is to jump forward in time
    """

    def __init__(self, clock, num_people, do_minute_by_minute=False):

        self.clock = clock

        # the times when a need should be threshold in absolute time or an activity ends
        self.A = np.inf * np.ones( (num_people, need.N) )

        # the duration of time between events
        self.dt = 0

        self.t_old = self.clock.t_univ

        # This flag controls whether the schedule should either go through time minute by minute \
        # or jump forward in time (if False)
        self.do_minute_by_minute    = do_minute_by_minute

        return

    def get_next_event_time(self):

        """
        This function searches the schedule matrix and finds the next time that that model should handle.
        
        .. note::
            This function is only capable of handling **single-occupancy** households.
            
        :return: the next time [minutes, time of day] that the model should address
        :rtype: int
        """

        # the current time
        t_now = self.clock.t_univ

        # get the minimum time per person (minimum time for each row)
        num_people = self.A.shape[0]

        # the data for times that are the minimum times
        A = self.A

        if (num_people == 1):

            # find the relevant indices
            # i.e. get indices of times greater than the current time
            idx = A > t_now

            #
            # move minute by minute
            #
            if self.do_minute_by_minute:
                t_next  = t_now + 1

            #
            # jump forward in time
            #
            else:

                # if there is a time greater than the current time
                if idx.any():
                    # get the next event time
                    t_next = np.min(A[idx])

                else:
                    # nothing scheduled should happen, increase the time by 1
                    t_next = t_now + 1

                # this makes sure that we do not stay in a time loop
                if (t_next == t_now):
                    t_next = t_now + 1

            #
            # update the old scheduled event times
            #
            A[idx == False] = t_next

        else:
            print('\nscheduler.get_next_event_time() is NOT calibrated for populations greater than 1!\n\n')
            t_next = t_now + 1

        # update the duration until the next activity from now
        self.dt     = t_next - t_now

        # update the prior event to be the current time
        self.t_old  = t_now

        return t_next

    def toString(self):

        """
        This function presents the Scheduler object as a string.
        
        :return: a string representation of the object
        """

        msg     = ''
        msg     = msg + 'dt: %d\n' % self.dt
        msg     = msg + 't_old: %d\n' % self.t_old

        return msg

    def update(self, id_person, id_need, dt):

        """
        This function updates the schedule matrix for a given person and need with the duration for the next event, \ 
        for the respective person-need combination.
        
        :param int id_person: the person identifier
        :param int id_need: the need identifier 
        :param int dt: the duration to the next event 
        :return: None 
        """

        self.A[id_person, id_need] = self.clock.t_univ + dt

        return