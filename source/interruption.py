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
This class gives an agent the ability to interrupt a current activity.

This module contains class :class:`interruption.Interruption`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# general math capabilities
import numpy as np

# agent-based module
import activity, meal, need, state, temporal


# ===============================================
# class Interruption
# ===============================================

class Interruption(need.Need):

    """
    This class enables a Person to interrupt a current activity.

    :param temporal.Temporal clock: the clock governing time in the simulation
    :param int num_sample_points: the number of time nodes in the simulation

    :var int category: the category of the interruption Need
    :var int activity_start: the category of the (interrupting) activity to start
    :var int activity_stop: the category of the (interrupted) activity to stop

    """

    #
    # constructor
    #

    def __init__(self, clock, num_sample_points):

        # access the Need association
        need.Need.__init__(self, clock, num_sample_points)

        # store the category of the need association
        self.id = need.INTERRUPTION
        
        # the category of the activity
        self.activity_start = activity.NO_ACTIVITY        
        self.activity_stop  = activity.NO_ACTIVITY
        
        return

    def decay(self, p):

        """
         This function sets the default decrease in the Interruption need

        :param person.Person p: the person of interest

        :return: None
        """

        # do not cause an interruption if not IDLE            
        if (p.state.status != state.IDLE):
            
            # check to see if the work activity needs to be interrupted in order 
            # to start the eat activity
            self.stop_work_to_eat(p)
                      
        return

    def get_time_to_next_work_lunch(self, p):

        """
        This function calculates the amount of time [in minutes] until the agent should
        eat lunch at work.

        :param person.Person p: the person of interest
        :return: the amount of time [minutes] until the next time the agent should \
        eat lunch at work
        """
        DAY_2_MIN   = temporal.DAY_2_MIN

        # problem because work start  gets updated at work end when this

        # get the data about lunch
        m = p.socio.get_meal(meal.LUNCH)

        # default value for duration
        dt = np.inf

        if (m is not None):
            # the time until eating lunch at work
            dt = p.socio.duration_to_work_event(p.clock) + (m.t_start - p.socio.job.t_start) % DAY_2_MIN

        return dt

    def initialize(self, p):

        """
        Initializes the need at the beginning of the simulation.

        :param person.Person p: the person of interest

        :return: None
        """

        # turn off the interruption in the scheduler
        self.decay(p)

        dt = self.get_time_to_next_work_lunch(p)

        # update the schedule
        p.schedule.update(p.id, need.INTERRUPTION, dt)

        return

    def is_lunch_time(self, time_of_day, meals):

        """
        This function indicates whether it is lunch time or not. This is used in the \
        interruption to stop the work activity and begin the eat lunch activity.

        :param int time_of_day: the time of day [minutes]
        :param list meals: a list of the meals (:class:`meal.Meal`) for the agents; some of the \
        entries in the list may be None.

        :return is_lunch: a flag indicating whether it is lunch time
        """

        # default value
        is_lunch = False

        # check to see if it is dinner time
        is_dinner = False

        # for each meal
        for m in meals:

            # take into account some entries may be None
            if (m is not None):

                # lunch time occurs if the current time is after the lunch time
                if (m.id == meal.LUNCH and time_of_day >= m.t_start):
                    is_lunch = True

                if (m.id == meal.DINNER and time_of_day >= m.t_start):
                    is_dinner = True

        # it is "lunch time" (eating lunch at work) only if dinner time has not occurred yet
        is_lunch = is_lunch and not is_dinner

        return is_lunch

    def perceive(self, clock):

        """
        This gives the result if sleep is done now until a later time corresponding to clock.

        :param temporal.Temporal clock: a clock at a future time

        :return out: the perceived interruption magnitude
        """

        # the amount of time (in minutes) it takes to do a perceived
        # activity
        dt = clock.t_univ - self.clock.t_univ

        # a linear gain i(n sleeping
        delta = self.recharge_rate * dt

        # return the perceived hunger level
        out = min( self.magnitude + delta, 1.0)

        return out

    def reset(self):
        """
        This function resets the Interruption need completely in order to re run \
        the simulation. In this reset the history is also reset.

        :return:
        """
        super(Interruption, self).reset()

        # reset the activity to start and stop, respectively
        self.activity_start = None
        self.activity_stop = None

        return

    def reset_minor(self):

        """
        This function resets the interruption need

        :return: None
        """

        # set the need associating magnitude
        self.magnitude = 1.0

        # reset the activity to start and stop, respectively
        self.activity_start = None
        self.activity_stop  = None

        return

    def stop_work_to_eat(self, p):

        """
        This function checks to see if an interruption should occur to allow a person to \
        start the eating activity while doing the work activity

        An agent may stop the work activity to eat lunch if the following conditions are met:

        #. the agent is hungry
        #. the current activity is work
        #. it is lunch time

        :param person.Person p: the person of interest

        :return: None
        """

        do_test = False
        # a flag indicating whether an interrupt should occur
        do_interrupt = False
        
        # eating lunch at work causes an exception

        # is the agent hungry?
        is_hungry = p.hunger.under_threshold(p.hunger.magnitude)

        # is the agent doing the work activity?
        is_working = p.state.activity.id == activity.WORK

        # is it time for lunch? NEED TO FIX THIS
        is_lunch = self.is_lunch_time(p.clock.time_of_day, p.socio.meals)

        #if is_working and is_hungry:
        # min( scheduled hunger time and lunch start time)
        #
        if do_test:
            if is_hungry and is_working:
                f = temporal.print_military_time

                print( 'LUNCH START:\t%s' % f(p.socio.meals[meal.LUNCH].t_start) )

        if ( is_hungry and is_working and is_lunch):

                p.interruption.magnitude        = need.MAG_INTERRUPTION
                p.interruption.activity_start   = activity.EAT_LUNCH
                p.interruption.activity_stop    = activity.WORK
                do_interrupt                    = True

                if do_test:
                    msg = 'just set the interruption'
                    print(msg.upper())
        else:
            p.interruption.magnitude  = 1.0

        p.state.do_interruption = do_interrupt

        return
          

