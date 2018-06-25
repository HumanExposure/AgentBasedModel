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
This module contains code for the need associated with the desire to move from one \
environment to another.

This file contains code for :class:`travel.Travel`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# agent-based model module
import income, location, need, occupation, state, temporal

# ===============================================
# class Travel
# ===============================================

class Travel(need.Need):

    """
    This class governs the need for traveling.

    :param temporal.Temporal clock: the time
    :param int num_sample_points: the number of temporal nodes in the simulation
    """

    #
    # constructor
    #
    def __init__(self, clock, num_sample_points):
        
        need.Need.__init__(self, clock, num_sample_points)
            
        self.id = need.TRAVEL
        
        return

    # ------------------------------------------------------
    # functions
    # ------------------------------------------------------

    def decay(self, p):

        """
        This function decays the satiation. Travel for commuting only decays when the work need is low

        :param person.Person p: the person whose satiation is decaying

        :return: None
        """

        # decay work commute
        self.decay_work_commute(p)

        return

    def decay_work_commute(self, p):

        """
        This decays the satiation level in order to commute to work. For the satiation to decay the \
        person needs the following:

        #. the agent should leave the home to go to work
        #. the agent should leave work to go home

        :param person.Person p: the person of interest

        :return: None
        """
        leave_home  = False
        leave_work  = False

        # do not commute if working at home
        if (p.socio.job.location.local != location.HOME):

            # commute from Home to Work (leave early to take into account commute)
            if (p.location.local == location.HOME):
                leave_home = occupation.is_work_time(p.clock, p.socio.job, is_commute_to_work=True)

            # commute from Work to Home (when it is no longer work time)
            elif (p.location.local == p.socio.job.location.local):
                leave_work = not occupation.is_work_time(p.clock, p.socio.job, is_commute_to_work=False)
        
        # assign the travel magnitude
        if (leave_work or leave_home):
            p.travel.magnitude = need.MAG_COMMUTE

        return

    def initialize(self, p):

        """
        This function initializes the Travel by updating the :class:`scheduler.Scheduler` for Travel

        :param person.Person p: the person of interest

        :return: None
        """

        # decay the need
        self.decay(p)

        # initialize the scheduler
        dt  = p.socio.duration_to_next_commute_event(p.clock)
        p.schedule.update(p.id, need.TRAVEL, dt)

        return

    def perceive(self, clock, job):

        """
        This function gives the satiation for Travel if the Travel need is addressed now.

        :Note: going to work can only happen according to work hours of the job.

        :param temporal.Temporal clock: the time the need to travel is perceived
        :param occupation.Occupation job: the job of the person

        :return mag: the perceived magnitude of the need
        :rtype: float
        """

        # indicate if it is the work time (True) or not (False)
        is_work_time    = occupation.is_work_time(clock, job, is_commute_to_work=True)

        # do not set the work need exactly to zero. This way,
        # if a super important need can interrupt the work activity
        if (is_work_time):
            mag = need.MAG_COMMUTE
        else:
            # it's not time to commute
            mag = 1.0

        return mag
