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
This is module contains code for governing the need to work/ be schooled.

This module contains the class :class:`income.Income`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# agent-based model module
import need, occupation, state

# ===============================================
# class Income
# ===============================================

class Income(need.Need):

    """
    This class governs the need dealing with work / school. Recall that income mathematically \
    resembles a step function.

    :param temporal.Temporal clock: the time
    :param int num_sample_points: the number of temporal node points in the simulation
    """

    #
    # constructor
    #
    def __init__(self, clock, num_sample_points):

        need.Need.__init__(self, clock, num_sample_points)

        self.id = need.INCOME

        return

    def decay(self, p):

        """
        This function decays the magnitude of the need. Income only decays after the job start time.
        
        #. Find out if it is time to work
        #. If it's time to work, set the satiation :math:`n_{income} = \eta_{work}`

        :param person.Person p: the person of interest

        :return: None
        """

        # is it time for work?
        is_work_time = occupation.is_work_time(p.clock, p.socio.job)

        # decay by income need dropping to WORK_MAG
        if (is_work_time):
            self.magnitude = need.MAG_WORK

        return

    def initialize(self, p):

        """
        This function is used to initialize the agent's income need at the beginning of the simulation. \
        This function initializes the Person to be at the workplace (:const:`location.OFF_SITE`) if it is work time. \
        This function does the following:
        
        #. decay the income satiation
        #. if the person is supposed to be at work

            * set the person to the workplace location
            * else, set the amount of time until the next work event
        #. update the scheduler for the income need

        :param person.Person p: the person of interest
        :return: None
        """

        # set the current need level
        self.decay(p)

        # if supposed to be at work, change to the appropriate location
        # THIS IS WEIRD because the work.start() function should take care of this
        # HOWEVER, there is a location requirement in the advertise() function
        # NEED TO ADD ANOTHER LAYER to make sure there is no conflict
        if ( self.under_threshold(self.magnitude) ):
            p.location.local = p.socio.job.location.local
            dt = 0
        else:
            # update the scheduler
            dt = p.socio.duration_to_work_event(p.clock)

        # update the schedule
        p.schedule.update(p.id, need.INCOME, dt)

        return
    
    def perceive(self, clock, job):

        """
        This gives the satiation of income **if** the income need is addressed now.

        #. find out if the time associated with clock implies a work time for the person
        #. If it should be work time
            * the perceived satiation is :math:`\eta_{work} \le \lambda`
            * else, the perceived satiation is :math:`1.0`
        
        :param temporal.Temporal clock: the future time the activity the should be perceived to be done
        :param occupation.Occupation job: the job

        :return: the satiation at the perceived time
        :rtype: float
        """

        # flag indicating whether it is work time or not
        is_work_time = occupation.is_work_time(clock, job)
                
        # do not set the work need exactly to zero. This way,
        # if a super important need can interrupt the work activity
        if (is_work_time):
            mag = need.MAG_WORK
        else:
            mag = 1.0

        return mag
