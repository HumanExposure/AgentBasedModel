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
This module contains code that governs the activity that gives a person the ability \
to go to work/ school.

This file contains :class:`work.Work`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# agent-based model modules
import activity, location, meal, need, occupation, state, temporal

# ===============================================
# class Work
# ===============================================

class Work(activity.Activity):

    """
    This class allows a person to work / go to school in order to satisfy the need \
    :class:`income.Income`.
    """

    #
    # constructor
    #
    def __init__(self):

        activity.Activity.__init__(self)

        self.id = activity.WORK
        
        return
     
    #------------------------------------------------------
    #  Functions
    #------------------------------------------------------

    def advertise(self, p):

        """
        This function calculates the score of the advertised work activity to a person

        :param person.Person p: the person of interest

        :return score:
        :rtype: float
        """

        DAY_2_MIN   = temporal.DAY_2_MIN

        # this is the lowest score
        score = 0.0

        # create a clock for the Need perception due the Activity when it's finished
        dt = (p.socio.job.t_end - p.clock.time_of_day) % DAY_2_MIN

        future_clock = temporal.Temporal(p.clock.t_univ + dt)

        # the current need level and the resulting need level if an Activity is done
        n_now = p.income.magnitude

        # if the Income need is under a threshold, send a score
        if ( p.income.under_threshold(n_now) ):

            n_later = p.income.perceive(future_clock, p.socio.job)
            score   = score + ( p.income.weight(n_now) - p.income.weight(n_later) )

        return score

    def end(self,p):

        """
        This function handles the end of an activity

        :param person.Person p: the person of interest
        :return: None
        """
        self.end_work(p)

        super(Work, self).end(p)

        return

    def end_work(self, p):

        """
        This function sets the variables pertaining to coming back from work by doing the following:

        #. free the asset from use
        #. set the asset's state to :const:`state.IDLE`
        #. set the Income satiation to 1
        #. decay the need Travel
        #. sample the new work start time
        #. sample the new work end time
        #. update the scheduler to take into account the next work event

        :param person.Person p: the person of interest

        :return: None
        """

        # this function frees the asset
        p.state.asset.free()

        # reset the state
        p.state.status = state.IDLE

        # update the Person's Income Need
        p.income.magnitude = 1.0

        # decay the travel need
        p.travel.decay(p)

        # update the work parameters
        p.socio.job.update_work_start()
        p.socio.job.update_work_end()

        # calculate the next work event
        # does not necessarily have to be the next day
        # get the next start time
        dt = p.socio.duration_to_work_event(p.clock)

        p.schedule.update(p.id, need.INCOME, dt)

        return


    def halt(self, p):

        """
        This function handles an interruption of an Activity.

        :param person.Person p: the person of interest
        :return: None
        """
        
        self.halt_work(p)

        super(Work, self).halt(p)

        return

    def halt_work(self, p):

        """
        This function interrupts the work behavior by doing the following:

        #. frees the current asset
        #. the asset's state is set to :const:`state.IDLE`
        #. the Interruption satiation is set to 1.0
        #. the Interruption's activity start/ stop

        :Note: No benefits of working are given while being interrupted

        :param person.Person p: the person of interest
        :return: None
        """

        # free the asset
        p.state.asset.free()

        # reset the the state
        p.state.status = state.IDLE

        # set up the satiation for Interruption to 1.0
        p.interruption.magnitude        = 1.0

        # set the Interrpution start and stop activity no activity
        p.interruption.activity_start   = activity.NO_ACTIVITY
        p.interruption.activity_stop    = activity.NO_ACTIVITY

        return

    def set_end_time(self, p):

        """
        Calculates the end time of work.

        :param person.Person p: the person of interest

        :return t_end: the end time [minutes, universal time]
        :rtype: int
        """

        # the current time (universal time)
        t_now = p.clock.t_univ

        # if (we do shift work)
        #     work to the end of the shift no matter, if the work activity
        #     starts early or late
        #
        # else if (work for a fixed duration fo time)
        #     always work for a fixed duration of time
        #     "work until the job gets done"

        if (p.socio.job.category == occupation.FIXED_SHIFT):

            # the beginning of the day (universal time)
            t_day = t_now - (t_now % temporal.DAY_2_MIN)

            # the time the job is supposed to start (universal time)
            t_start = t_day + p.socio.job.t_start

            # the time the job is supposed to end (universal time)
            t_end = t_start + p.socio.job.dt

        elif (p.socio.job.category == occupation.FIXED_DURATION):

            # work for a fixed duration of time starting now
            t_end = t_now + p.socio.job.dt

        return t_end

    def start(self, p):

        """
        This handles the start of an Activity

        :param person.Person p: the person of interest
        :return: None
        """
        self.start_work(p)

        # store a list of the arguments for the end() procedure
        p.state.arg_end.append(p)

        return

    def start_work(self, p):

        """
        This function starts the work activity

        * updates that asset's status and number of users
        * changes the location of the Person
        * updates that person's status
        * calculates the end time of the work activity
        * update the scheduler for the Income satiation
        * update the scheduler for the Travel satiation
        * set the day for the work period

        :param person.Person p: the person of interest
        :return: None
        """

        DAY_2_MIN = temporal.DAY_2_MIN

        # set the location of the Person to be at work
        p.location.local = location.OFF_SITE

        # update the person's state
        p.state.status = state.WORK

        # set the start time of the current state
        p.state.t_start = p.clock.t_univ

        # calculate the end time of working
        dt              = (p.socio.job.t_end - p.clock.time_of_day) % DAY_2_MIN
        p.state.t_end   = p.clock.t_univ + dt

        # update the asset
        p.state.asset.update()

        # update the scheduler
        p.schedule.update(p.id, need.INCOME, dt)
        p.schedule.update(p.id, need.TRAVEL, dt)

        # update the interruption schedule
        dt = (p.socio.meals[meal.LUNCH].t_start - p.clock.time_of_day)
        if dt < 0:
            dt = 1
        p.schedule.update(p.id, need.INTERRUPTION, dt)

        # set the day for current work period
        p.socio.job.day_start = p.clock.day

        return

    def test_func(self, p):


        """
        .. note::
            This function is **NOT** used.

        :param person.Person p: the person of interest
        :return:
        """
        DAY_2_MIN   = temporal.DAY_2_MIN

        msg = ''
        #msg = '---------------------------------\n'

        f   = temporal.print_military_time
        #msg = msg + '%s\t\t %d\n' % (f(self.clock.time_of_day), self.clock.time_of_day)


        msg = msg + state.INT_2_STR[p.state.status] + '\n'

        for k, v in p.needs.items():
            msg = msg + ( '%s: %.2f\n' % (need.INT_2_STR[k], v.magnitude) )

        y = [ f(x % DAY_2_MIN) for x in p.schedule.A[0]]

        msg = msg + '%s: ' % y
        print(msg)
        print(p.schedule.A[0])
        return