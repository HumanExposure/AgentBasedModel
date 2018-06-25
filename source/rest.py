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
This file contains information about the need dealing with Rest.

This module contains class :class:`rest.Rest`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# general mathematical capability
import numpy as np

# agent-based model modules
import my_globals as mg
import need, state, temporal

# ===============================================
# class Rest
# ===============================================

class Rest(need.Need):

    """
    This class contains relevant information about the rest need.

    :param temporal.Temporal clock: this keeps track of the current time. It is linked to the Universe clock.
    :param int num_sample_points: the number of temporal nodes in the simulation
    """

    def __init__(self, clock, num_sample_points):

        need.Need.__init__(self, clock, num_sample_points)

        self.id = need.REST

        # assuming linear increase and decrease of rest
        self.decay_rate                 = 0.0
        self.recharge_rate              = 0.0
        self.suggested_recharge_rate    = 0.0

        return

    def decay(self, status):

        """
        .. warning::
            This function is old and antiquated.
            
        This function decays the Rest satiation. The satiation only decays if the person is \
        **not** asleep. The decay in sleep

        .. math::
            \\delta &= m_{decay} \\Delta{t} \\\\
            n(t + \\Delta{t}) &= n(t) + \\delta

        where
            * :math:`m_{decay}` is the decay rate
            * :math:`\\Delta{t}` is the duration of time in 1 time step of simulation [minutes]
            * :math:`\\delta` is the amount of decay of rest
            * :math:`n(t)` is the satiation at time t
            
        :param int status: the current state of a person
        :return: None
        """

        # decrease the need to sleep if the person is NOT sleeping
        if (status != state.SLEEP):
            # linear decrease
            delta = self.decay_rate * self.clock.dt

            # set the magnitude
            self.magnitude = max(self.magnitude + delta, need.MIN_DEFAULT)

        return

    def decay_new(self, status, dt):

        """
        This function decays Rests' satiation. The satiation only decays if the \
        person is **not** asleep. The decay in sleep is calculated by

        .. math::
            \\delta &= m_{decay} \\Delta{t} \\\\
            n(t + \\Delta{t}) &= n(t) + \\delta
            
        where
            * :math:`t` the current time
            * :math:`\\Delta{t}` is the duration of time to decay the satiation [minutes]
            * :math:`\\delta` the change in the satiation for Rest
            * :math:`m_{decay}` is the decay rate for Rest
            * :math:`n(t)` is the satiation of Rest at time t
    
        :param int status: the current state of a person
        :param int dt: the duration of time :math:`\\Delta{t}` [minutes] used to decay the need
        
        :return: None
        """

        # decrease the need to sleep if the person is NOT sleeping
        if (status != state.SLEEP):

            # linear decrease
            delta = self.decay_rate * (dt)

            # set the magnitude
            self.magnitude = max(self.magnitude + delta, need.MIN_DEFAULT)

        return

    def is_workday(self, p):

        """
        This function indicates whether or not the sleep event resembles that from a person sleeping for \
        a workday.

        :param social.Social socio: the social characteristics of the person of interest
        :return: True, if the sleep event resembles a workday. False, otherwise.
        """

        # default assumes that sleeping duration reflects a workday
        is_non_workday_sleep = False

        # if the person is employed
        if p.socio.job.is_employed:

            # write the time centered around midnight [-12 * HOUR_2_MIN, 12 * HOUR_2_MIN)
            t = mg.to_periodic(self.clock.time_of_day, do_hours=False)

            # store the day fo the week for today and tomorrow
            today       = self.clock.day_of_week
            tomorrow    = (today + 1 + 7) % 7

            # the time to sleep is before midnight
            if (t < 0):
                is_non_workday_sleep = tomorrow not in p.socio.job.work_days
            else:
                # the time to sleep is after midnight
                is_non_workday_sleep = today not in p.socio.job.work_days

        # store if the sleep behavior resembles a workday
        workday_sleep = not is_non_workday_sleep

        return workday_sleep

    def initialize(self, p):

        """
        The purpose of this code is to help initialize Rest's satiation and \
        whatever activity that goes with it, depending on any time the simulation begins.

        .. note::
            This code is a work in progress.

        #. update the sleep start and end time
        #. find out if the person should be asleep
        #. if the Person is asleep,

            * sets the appropriate duration of sleep left to do
            * sets the rest magnitude to threshold
            * sets the rest recharge rate
            * sets the schedule to trigger when when the person is scheduled to wake up
        #. if the Person is not asleep,

            * sets the decay rate
            * set the magnitude
            * sets the schedule to trigger when when the person is scheduled to start sleeping
        #. update the schedule for the rest need
        
        :param person.Person p: the person of interest

        :return: None
        """

        DAY_2_MIN = temporal.DAY_2_MIN

        # update the start and end time
        p.bio.update_sleep_start()
        p.bio.update_sleep_end()

        # expected start time and end times for sleeping
        t_start, t_end  = p.bio.sleep_start, p.bio.sleep_end
        dt              = (t_end - t_start + DAY_2_MIN) % DAY_2_MIN

        # current time [min]
        t = self.clock.time_of_day

        # elapsed time spent since the PREVIOUS wake up event
        dt_elapsed = (t - t_end + DAY_2_MIN) % DAY_2_MIN

        # flag indicating whether or not the agent should be asleep
        # during initialization
        is_asleep = self.should_be_asleep(t_start=t_start, t_end=t_end)

        # suggested recharge rate
        # this is needed for perceive()
        # this is needed for sleep.set_end_time()
        self.set_suggested_recharge_rate(dt)

        if (is_asleep):

            # the amount of time spent asleep so far
            dt_asleep   = (t - t_start + DAY_2_MIN) % DAY_2_MIN

            # the amount of time that will be spent asleep
            dt_sleep    = dt - dt_asleep

            # set the magnitude of sleep
            self.magnitude      = self.threshold
            self.recharge_rate  = (1.0 - self.magnitude) / dt_sleep

            # the next event should be waking up
            dt_schedule = dt_sleep

        else:
            # the decay rate
            self.set_decay_rate(DAY_2_MIN - dt)

            # set the suggested recharge rate to default
            # the current magnitude
            self.magnitude  = max(1.0 + self.decay_rate * dt_elapsed, need.MIN_DEFAULT)

            dt_schedule     = np.round( (self.magnitude - self.threshold) / abs(self.decay_rate) ).astype(int)

        # update the scheduler
        p.schedule.update(p.id, need.REST, dt_schedule)

        return

    def perceive(self, future_clock):

        """
        This functions gives the updated rest magnitude if sleep is done from now until a later time \
        corresponding to clock.

        .. math::
            \\delta = m_{suggested}\\Delta{t}

        where
            * :math:`\\delta` is the amount of change in the satiation for Rest
            * :math:`m_{suggested}` is the suggested recharge rate for Rest
            * :math:`\\Delta{t}` is the duration of time from now until the future time
                    given by future_clock

        :param temporal.Temporal future_clock: a clock corresponding to a future time

        :return: the perceived rest level
        :rtype: float
        """

        # based of characteristics, select proper function.
        # should this be done in the beginning, at initialization?

        dt = future_clock.t_univ - self.clock.t_univ

        # a linear gain in sleeping
        delta = self.suggested_recharge_rate * dt

        return min(self.magnitude + delta, 1.0)

    def reset(self):

        """
        This function resets the values in order for the need to be used in the next simulation
        
        :return: None
        """

        # reset
        super(Rest, self).reset()

        self.decay_rate     = 0.0
        self.recharge_rate  = 0.0
        self.suggested_recharge_rate = 0.0

        return

    def set_decay_rate(self, dt):

        """
        This function sets the decay rate. The decay rate (:math:`m_{decay}`) is assumed \
        to be the slope of a linear function.

        .. math::
            m_{decay} = -\\frac{1 - \\lambda}{\\Delta{t}}

        where
            * :math:`\\Delta{t}` is the duration of time expected to be awake
            * :math:`\\lambda` is the Rest threshold
            * :math:`m_{decay}` is the decay rate for Rest

        :param int dt: the duration of sleep :math:`\\Delta{t}` [minutes]

        :return: None
        """

        # linear rest decay

        # assume dt is the amount of time awake
        self.decay_rate = -1 * (1 - self.threshold) / dt
                
        return
    
    def set_recharge_rate(self, dt):

        """
        This function sets the recharge rate. The recharge rate (:math:`m_{recharge}`) \
        is assumed to be the slope of a linear function.

        .. math::
            m_{recharge} = \\frac{1 - \\lambda}{ \\Delta{t} }

        where
            * :math:`\\Delta{t}` is the duration of sleep
            * :math:`\\lambda` is the threshold for Rest
            * :math:`m_{recharge}` is the recharge rate for Rest


        :param int dt: the duration of sleep after rounding :math:`\\Delta{t}` [minutes]

        :return: None
        """

        # linear recharge rate, avoid integer division
        self.recharge_rate = (1 - self.magnitude) / dt
        
        return

    # def set_rates(self, dt):
    #
    #     """
    #     This function sets the parameters governing the decay rate and the recharge
    #     rate.
    #
    #     :param int dt: the duration of sleep [minutes]
    #     :return: None
    #     """
    #
    #     self.set_decay_rate(dt)
    #     self.set_recharge_rate(dt)
    #
    #     return

    def set_suggested_recharge_rate(self, dt):

        """
        This function sets the "suggested" recharge rate. That is, the rate of recharge assuming exact \
        arithmetic (there is no rounding in time, say to the nearest minute).

        .. math::
            m_{suggested} = \\frac{ 1 - \\lambda }{ \\Delta{t} }

        where
            * :math:`\\Delta{t}` is the duration of sleep
            * :math:`\\lambda` is the Rest threshold
            * :math:`m_{suggested}` is the suggested recharge rate for Rest


        :param int dt: the duration of sleep :math:`\\Delta{t}` [minutes]

        :return: None
        """

        self.suggested_recharge_rate = (1.0 - self.threshold) / dt

        return

    def should_be_asleep(self, t_start, t_end):

        """
        This function finds out if the person should be asleep for the initialization \
        of the ABMHAP algorithm.

        :param int t_start:  start time of sleep [minutes, time of day]
        :param int t_end: end time of sleep [minutes, time of day]

        :return: a flag indicating whether a person should be asleep (if True) or awake (if False)
        :rtype: bool
        """

        do_hours = False

        # set the time to be in [-12 * 60, 12 * 60) instead of [0, 24 * 60)
        x       = mg.to_periodic(self.clock.time_of_day, do_hours=do_hours)
        x_start = mg.to_periodic(t_start, do_hours=do_hours)
        x_end   = mg.to_periodic(t_end, do_hours=do_hours)

        # find out if the person should be asleep
        is_asleep = ( x >= x_start) and (x < x_end)

        return is_asleep

    def toString(self):

        """
        Represent the Rest object as a string

        :return: the representation of the Rest object
        :rtype: str
        """

        msg = ''
        msg = msg + super(Rest, self).toString()
        msg = msg + 'decay rate:\t%f\n' % self.decay_rate
        msg = msg + 'recharge rate:\t%f\n' % self.recharge_rate
        
        return msg

