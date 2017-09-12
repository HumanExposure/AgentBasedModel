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
This module contains information about the activity dealing with sleeping. This class is :class:`activity.Activity` \
that gives a :class:`person.Person` the ability to eat and satisfy the need :class:`rest.Rest`.

This file contains class :class:`sleep.Sleep`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# -------------------------
# import
# -------------------------

# general math functions
import numpy as np

# agent-based model modules
import activity, need, state, temporal

# ===============================================
# class
# ===============================================


class Sleep(activity.Activity):

    """
    This class is responsible for the act of sleeping, which satisfies the need :class:`rest.Rest`.
    """

    # constructor
    def __init__(self):

        activity.Activity.__init__(self)

        self.id = activity.SLEEP

        return
     
    #--------------------------------
    #  Functions
    #---------------------------------

    def advertise(self, p):

        """
        This function calculates the score of an activity advertisement to a Person

        :param person.Person p: the person being advertised to
        
        :return: the value of the advertisement
        :rtype: float
        """

        DAY_2_MIN   = temporal.DAY_2_MIN

        # the estimated duration of the sleep event
        dt = (p.bio.sleep_end - p.bio.sleep_start) % DAY_2_MIN

        # calculate the score
        score = super(Sleep, self).advertise(p.rest, dt)

        return score

    def end(self, p):

        """
        This handles the end of the sleep activity.

        :param person.Person p: the person of interest

        :return: None
        """

        self.end_sleep(p)

        super(Sleep, self).end(p)

        return

    def end_sleep(self, p):

        """
        This function addresses logistics with a person waking up from sleep

        #. free the asset from use
        #. set the state of the person to idle (:const:`state.IDLE`)
        #. update the satiation
        #. update the start time and end time
        #. set the decay rate
        #. update the schedule for the rest need

        :param person.Person p: the person of interest
        :return: None
        """

        #
        # free the asset
        #
        p.state.asset.free()

        #
        # update the person
        #
        # change the status of the Person
        p.state.status = state.IDLE

        # the amount of time spent sleeping (including rounding)
        dt = p.state.t_end - p.state.t_start + 1

        # the amount of gain of need during sleeping
        # a linear gain in sleep
        delta = p.rest.recharge_rate * dt
        
        # update the Person's Rest Need
        p.rest.magnitude = min(p.rest.magnitude + delta, 1.0)

        # update the sleep parameters
        p.bio.update_sleep_start()
        p.bio.update_sleep_end()
        
        # update the rates

        # the amount of time expected to be awake
        dt_awake = p.bio.calc_awake_duration(p.clock.time_of_day)

        # set the recharge rate
        p.rest.set_suggested_recharge_rate(p.bio.sleep_dt)

        # set the decay rate
        p.rest.set_decay_rate(dt_awake)
        # update the scheduler
        # the amount of time until tired again
        p.schedule.update(p.id, need.REST, dt_awake)

        return

    def is_workday(self, p):

        """
        This function indicates whether or not the sleep event resembles that from a person sleeping for \
        a workday.

        :param person.Person p: the person of interest
        :return: True, if the sleep event resembles a workday. False, otherwise.
        """

        # constants
        HOUR_2_MIN = temporal.HOUR_2_MIN

        # default assumes that sleeping duration reflects a workday
        is_non_workday_sleep = False

        if p.socio.job.is_employed:

            # write the time centered around midnight [-12 * HOUR_2_MIN, 12 * HOUR_2_MIN)
            time_of_day = p.clock.time_of_day
            t = time_of_day + (time_of_day >= 12 * HOUR_2_MIN) * (-24 * HOUR_2_MIN)

            # store the day fo the week for today and tomorrow
            today = p.clock.day_of_week
            tomorrow = (today + 1 + 7) % 7

            # the time to sleep is before midnight
            if (t < 0):
                is_non_workday_sleep = tomorrow not in p.socio.job.work_days
            else:
                # the time to sleep is after midnight
                is_non_workday_sleep = today not in p.socio.job.work_days

        # store if the sleep behavior resembles a workday
        workday_sleep = not is_non_workday_sleep

        return workday_sleep

    def set_end_time(self, p):

        """
        This function returns the end time of sleeping

        The end time :math:`t_{end}` is set as follows

        .. math::
            :nowrap:

            \\[
            \\begin{cases}
                \\Delta{t} &= \\frac{ 1 - n(t) }{ m_{suggested} } \\\\
                t_{end} &= t + \\Delta{t}
            \\end{cases}
            \\]

        where
            * :math:`\\Delta{t}` is the duration of sleep
            * :math:`m_{suggested}` is the suggested recharge rate
            * :math:`n(t)` is the magnitude of sleep at time t

        :param person.Person p: the person of interest

        :return t_end: the end time of the sleep event [minutes, universal time]
        :rtype: int
        """

        do_test = True

        # the natural sleep end time

        # suggested recharge rate assumes current magnitude is at threshold

        # the default length of sleep; make sure it is an integer
        if (p.clock.initial_step):
            dt = (1 - p.rest.magnitude) / p.rest.recharge_rate
        else:
            dt = (1 - p.rest.magnitude) / p.rest.suggested_recharge_rate

        # round the time to the nearest minute
        dt = np.round(dt).astype(int)

        # the default time to wake up, if uninterrupted
        t_end = p.state.t_start + dt

        if do_test:
            if (dt <= 0):
                uu = 1

        return t_end

    def start(self, p):

        """
        This handles the start of the sleep activity.

        :param person.Person p: the person of interest

        :return: None
        """

        self.start_sleep(p)

        # store a list of the arguments for the end() procedure
        p.state.arg_end.append(p)

        return

    def start_sleep(self, p):

        """
        This handles what happens when a Person goes to sleep.

        #. The asset's status is updated.
        #. The Person's state is set to the sleep state (:const:`state.SLEEP`)
        #. The end time is calculated
        #. The recharge rate is set (according to whether or not it is a workday / non-workday)

        :param person.Person p: the person of interest

        :return: None
        """

        HOUR_2_MIN, DAY_2_MIN = temporal.HOUR_2_MIN, temporal.DAY_2_MIN
        #
        # update the asset
        #

        p.state.asset.update()

        #
        # update the person
        #

        # set the state of the Person to SLEEP
        p.state.status = state.SLEEP

        # changing the rates
        if not p.clock.initial_step:
            # changing the suggested rate makes sure the agent sleeps in
            dt = (p.bio.sleep_end - p.clock.time_of_day) % DAY_2_MIN
                
            p.rest.set_suggested_recharge_rate(dt)

        # set the start time of the current state
        p.state.t_start = p.clock.t_univ

        # calculate the end time of sleep
        p.state.t_end = self.set_end_time(p)

        # the duration of the sleep event
        dt = p.state.t_end - p.state.t_start + 1

        # set the recharge rate
        p.rest.set_recharge_rate(dt)

        # set the scheduler to the wake up time for rest
        p.schedule.update(p.id, need.REST, dt)

        return

    def toString(self):
        """
        This function represents the Sleep object as a string

        :return msg: the representation of the Sleep object
        :rtype: str
        """
        msg = ''
        msg = msg + 'Activity Type: ' + self.print_id()+ '\n'
        return msg


