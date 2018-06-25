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
This module contains information about governing the need Hunger.

This module contains the class Hunger (:class:`hunger.Hunger`).

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# general math capability
import numpy as np

# agent-based model modules
import need, temporal

# ===============================================
# class Hunger
# ===============================================

class Hunger(need.Need):

    """
    This class governs the behavior of the need Hunger need. When Hunger is unstatisfied,
    the agent feels compelled to eat a meal in order to satisfy the need. Mathematically \
    speaking, Hunger is modeled as linear-behaving need.

    :param temporal.Temporal clock: the time
    :param int num_sample_points: the number of temporal nodes in the simulation

    :ivar int category: the category of the need
    :ivar float decay_rate: the decay rate of the Hunger need [need/minute]
    :ivar float recharge_rate: the recharge rate of the Hunger need [need/min]
    :ivar float suggested_recharge_rate: an approximate recharge rate used to calculate the end time of an \
    event before rounding
    """

    #
    # constructor
    #
    def __init__(self, clock, num_sample_points):
        
        need.Need.__init__(self, clock, num_sample_points)

        self.id = need.HUNGER
        
        # these values may change due to different influences, meals

        # the decay rate
        self.decay_rate = 0.0

        # the true recharge rate once the end time is known
        self.recharge_rate = 0.0

        # an approximate recharge rate. It is used to calculate the end time of an event
        self.suggested_recharge_rate = 0.0

        return

    def decay(self, status):

        """
        This function decreases the satiation in Hunger by doing the following:
        
        .. math::
          n(t + 1) = n(t) + m_{decay}                        

        .. warning::
            This function may be antiquated and **not used**
            
        :param int status: indicates the current status of the person's state (not-used)
        :return: None
        """

        # linear decrease in hunger
        delta = self.decay_rate * self.clock.dt

        # set the magnitude of hunger
        self.magnitude = max(self.magnitude + delta, need.MIN_DEFAULT)

        return

    def decay_new(self, dt):

        """
        This function sets the default decrease in the Hunger need.        

        .. math::
            n(t + \Delta{t}) = n(t) + m_{decay}\,\Delta{t}

        where
            * :math:`t` is the current time
            * :math:`\\Delta{t}` is the duration of time to decay the satiation [minutes]
            * :math:`n(t)` is the satiation for Hunger at time :math:`t`
            * :math:`m_{decay}` the decay rate for Hunger

        :param int dt: the duration of time [minutes] :math:`\\Delta{t}` used to decay the need
        :return: None
        """

        # linear decrease in hunger
        delta = self.decay_rate * dt

        # set the magnitude of hunger
        self.magnitude = max(self.magnitude + delta, need.MIN_DEFAULT)

        return

    def initialize(self, p):

        """
        This function initializes the the Hunger need at the first step of the simulation. The function \
        checks to see whether or not the current time implies that there should be an eating event. The \
        Hunger object is set to the respective state.

        This function does the following exactly:
        
        #. initialize all of the meals
        #. check to see if a meal should be occurring at the current time

        #. if no meals should be occurring

            * figure out the next meal
            * calculate the decay rate for hunger until the next meal
            * calculate the amount of time until the next meal :math:`\Delta{t}`
            * set the current meal
            * update the schedule for the hunger need to be the time the next meal starts

        #. if a meal should be occurring

            * get the index of the meal that should be occurring
            * set the current meal
            * calculate the final time of the meal
            * calculate the duration until the end of the next meal :math:`\Delta{t}`
            * set the recharge rate
            * update the scheduler for the hunger need to be the time the current meal should end

        #. initialize the start time for each meal
                    
        :param person.Person p: the person whose hunger need is being initialized
        :return: None
        """

        # duration to next meal
        DAY_2_MIN   = temporal.DAY_2_MIN

        # initialize the meals
        for m in p.socio.meals:
            m.initialize(p.clock.t_univ)

        # check to see if a meal should be occurring at the current time
        do_meals = self.is_meal_time_all(p.clock.time_of_day, p.socio.meals)

        if ( True not in do_meals ):
            # assuming that the current time is NOT for eating

            # get the next meal
            dt, the_meal = p.socio.duration_to_next_meal(p.clock.t_univ)
            dt = None

            # set the decay rate
            self.set_suggested_recharge_rate(the_meal.dt)
            self.set_decay_rate(the_meal.t_start)

            # the amount of time until eating the next meal
            dt = np.round( (self.magnitude - self.threshold) / abs(self.decay_rate) ).astype(int)

            # set the current meal
            p.socio.current_meal = the_meal

            # update the scheduler
            p.schedule.update(p.id, need.HUNGER, dt)
        else:

            # index of the the current meal
            idx = do_meals.index(True)

            # set the current meal
            p.socio.current_meal = p.socio.meals[idx]

            # the final time of the eating event
            t_end = p.socio.meals[idx].t_start + p.socio.meals[idx].dt

            # the time duration of the first eating event
            dt = (t_end - p.clock.time_of_day + DAY_2_MIN) % DAY_2_MIN

            # set the magnitude
            self.magnitude = self.threshold

            # set the recharge rate
            self.recharge_rate = (1 - self.magnitude )/ dt

            # update the scheduler
            p.schedule.update(p.id, need.HUNGER, dt)

        # initialize t_start_univ for meals
        time_of_day     = p.clock.time_of_day

        for m in p.socio.meals:

            # the meal will happen later in the day
            if (m.t_start >= time_of_day):
                t_day  = p.clock.day * DAY_2_MIN
            else:
                # the meal will happen tomorrow
                t_day = (p.clock.day + 1) * DAY_2_MIN

            m.t_start_univ      = t_day + m.t_start
            m.day               = p.clock.day

        return

    def is_meal_time(self,t, the_meal):

        """
        This checks whether or not it is time for a meal.

        :param int t: time of day [minutes]
        :param meal.Meal the_meal: the respective meal to see whether the current time implies \
                            that an eating event should happen

        :return: True if the current time is within the time to eat. False, otherwise
        :rtype: bool
        """

        DAY_2_MIN   = temporal.DAY_2_MIN

        # the start time
        t_start = the_meal.t_start

        # the end time
        t_end   = t_start + the_meal.dt

        # the amount of time since the start of the meal
        u       = (t - t_start + DAY_2_MIN) % DAY_2_MIN

        # the duration of the meal
        u_end   = (t_end - t_start + DAY_2_MIN) % DAY_2_MIN

        # if u == u_end, the meal has ended
        return (u < u_end)

    def is_meal_time_all(self, t, meals):

        """
        This function checks every meal and sees whether or not the current time \
        implies that there should be an eventing event for a respective meal.


        :param int t: the current time of day [minutes]
        :param list meals: a list of meals that a person has

        :return: a list of boolean flags indicating True or False, indicating whether or not an \
        eating event should occur for the respective meal

        :rtype: list
        """
        return [self.is_meal_time(t, m) for m in meals]

    def perceive(self, future_clock):

        """
        This gives the result if eat is done now until a later time corresponding to clock.

        :param temporal.Temporal future_clock: a clock at a future time

        :return out: the perceived hunger need association level
        :rtype: float
        """

        # the amount of time (in minutes) it takes to do a perceived
        # activity
        dt = future_clock.t_univ - self.clock.t_univ

        # a linear gain in eating
        delta = self.suggested_recharge_rate * dt

        # return the perceived hunger level
        out = min( self.magnitude + delta, 1.0)

        return out

    def reset(self):

        """
        This function resets the values in order for the need to be used in the next simulation.

        :return:
        """

        super(Hunger, self).reset()

        # the decay rate
        self.decay_rate     = 0.0
        self.recharge_rate  = 0.0
        self.suggested_recharge_rate = 0.0

        return

    def set_decay_rate(self, t_start):

        """
        This function calculates the decay rate of hunger to the next meal.

        :param int dt: the amount of time :math:`\\Delta{t}` to the next meal [minutes]
        :param int t_start: the start time [in minutes] of the next meal
        :return: None
        """

        # the amount of minutes in a day
        DAY_2_MIN = temporal.DAY_2_MIN

        # the time until the start of the next meal
        dt = (t_start - self.clock.time_of_day + DAY_2_MIN) % DAY_2_MIN

        # set the decay rate. Avoid integer division

        if dt == 0:
            self.decay_rate = -1
        else:
            self.decay_rate = -1 * (1.0 - self.threshold) / dt

        return

    def set_decay_rate_new(self, dt):

        """
        This function calculates the decay rate of hunger to the next meal.

        :param int dt: the amount of time :math:`\\Delta{t}` to the next meal [minutes]
        :return: None
        """

        # set the decay rate. Avoid integer division
        if dt == 0:
            self.decay_rate = -1.0
        else:
            self.decay_rate = -1.0 * (1.0 - self.threshold) / dt

        return

    def set_recharge_rate(self, dt):

        """
        This function calculates the recharge rate of hunger due to eating the current meal.

        :param int dt: the amount of time :math:`\\Delta{t}` it takes to finish a meal [minutes]

        :return: None
        """

        # set the recharge rate
        self.recharge_rate = (1.0 - self.magnitude) /dt

        return

    def set_suggested_recharge_rate(self, dt):

        """
        This function sets the suggested recharge rate assuming a **linear function** behavior

        The suggested recharge rate is based on the duration of the sleeping event \
        and the threshold. The sleep duration is based on the biological data (no rounding).

        :param int dt: The duration of time :math:`\\Delta{t}` of the eating event [minutes]
        :return: None
        """

        self.suggested_recharge_rate = (1.0 - self.threshold) / dt

        return

    def toString(self):

        """
         Represents the Hunger object as a string.

        :return msg:  the string representation of the huger object
        :rtype: str
        """

        msg = ''

        # write the values from Hunger
        msg = msg + super(Hunger, self).toString()

        # write the decay rate
        msg = msg + 'decay rate:\t%f\n' % self.decay_rate

        # write the recharge rate
        msg = msg + 'recharge rate:\t%f\n' % self.recharge_rate
         
        return msg
        