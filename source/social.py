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
This module contains code that governs the social behavior/ characteristics relevant \
to a Person (:class:`person.Person`).

This module contains class :class:`social.Social`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

#  general math capability
import numpy as np

# agent-based model modules
import my_globals as mg
import meal, occupation, temporal

# ===============================================
# constants
# ===============================================

# school age
SCHOOL_AGE  = 5

# the minimum age for an adult
ADULT_AGE   = 18

# no one has lived this long
MAX_AGE     = 130

# not using infants
MIN_AGE     = 1

# ===============================================
# class Social
# ===============================================

class Social(object):

    """
    This class contains all of the relevant information governing the person's \
    social behavior.

    .. note::
        The current version of ABMHAP does not have any "alarm" functionality / capability. The remnants of any \
        code that governs the use of an alarm  will be removed in future updates.
        
    :param int age: the age of the person [years]
    :param int num_meals: the number of meals per day

    :var bool is_child: this flag is True if the person is a child, False otherwise
    :var occupation.Occupation job: the information pertaining the the job
    :var int num_meals: the number of meals per day a person will eat
    :var list meals: a list of the meals that a person eats (:class:`meal.Meal`)
    :var meal.Meal current_meal: the meal that is currently being eaten **or** if the person is not eating a meal, \
    it is the upcoming meal
    :var meal.Meal next_meal: the meal that is after the meal indicated by :mod:`current_meal`
    :var bool uses_alarm: indicates whether or not a person uses an alarm to wake up
    :var bool is_alarm_set: indicates whether or not an alarm is set for the current day
    :var int t_alarm: the time an alarm is supposed to go off [minutes, time of day]
    """

    #
    # constructor
    #
    def __init__(self, age, num_meals=3):
        
        # child / adult
        self.is_child = None
        self.set_child_flag(age)

        # job info
        self.job = occupation.Occupation()
        
        # meals
        self.num_meals  = num_meals
        self.meals      = [ meal.Meal() for _ in range(self.num_meals) ]

        self.current_meal   = None
        self.next_meal      = None
        # does the Person ever set an alarm. Currently, there is no real alarm capability
        self.uses_alarm = False
        
        # this depends on whether a Person uses an alarm and 
        # whether the day is a work day
        # Currently, there is no real alarm capability
        self.is_alarm_set   = False
        self.t_alarm        = 7 * temporal.HOUR_2_MIN

        return

    def duration_to_next_commute_event(self, clock):

        """
        This function is called in in order to calculate the amount of time until the next commute event by \
        doing the following.

        #. If the agent is unemployed, return infinity 
        #. If the time indicates that the agent should be currently working, set the duration to be the \
        length of time remaining at work
        #. If the time indicates that the agent should be currently commuting to work, set the duration to be \
        the duration until the commute to work should start
        #. If the time indicates that the agent should be currently commuting from work, set the duration to be \
        the amount of time until the commute from work should end
        #. Else, calculate the amount of time until the next commute to work event
        
        .. note::
            The only reason this code is place here is because the work activity and the commute activity use it.

        :param temporal.Temporal clock: the current time
        :return: the duration in time [mintues] until the next commute event
        :rtype: int
        """

        DAY_2_MIN = temporal.DAY_2_MIN

        # if the person is unemployed, set the duration to infinity
        if not self.job.is_employed:
            dt = np.inf

        else:
            # should the agent be working
            work_time               = occupation.is_work_time(clock, self.job, is_commute_to_work=False)

            # is it time for the person to be commuting to work
            commute_to_work_time    = occupation.is_work_time(clock, self.job, is_commute_to_work=True)

            # is it time to commute from work
            t = max(0, clock.t_univ - self.job.commute_from_work_dt )
            temp_clock = temporal.Temporal()
            temp_clock.t_univ = t
            temp_clock.set_time()
            commute_from_work_time = occupation.is_work_time(temp_clock, self.job, is_commute_to_work=False)

            # if the agent is currently working, set the duration to be the length of time remaining at work
            if (work_time):
                t_end   = self.job.t_end
                dt      = ( t_end - clock.time_of_day + DAY_2_MIN ) % DAY_2_MIN

            # if the person should be commuting to work, set the duration to be the length of time remaining until
            # the commute starts
            elif(commute_to_work_time):
                t_start = self.job.commute_to_work_start
                dt      = ( t_start - clock.time_of_day + DAY_2_MIN)  % DAY_2_MIN

            # if the person should be commuting from work, set the time to be the time when the commute should end
            elif(commute_from_work_time):
                t_start = self.job.t_end
                dt      = (t_start + self.job.commute_from_work_dt - self.clock.time_of_day + DAY_2_MIN ) % DAY_2_MIN

            # else, calculate the amount of time until the next commute event
            else:
                # time until the next work event
                dt = self.duration_to_work_event(clock) - self.job.commute_to_work_dt

        return dt

    def duration_to_next_meal(self, t_univ):

        """
        This function calculates the amount of time until the next meal.
        
        :param int t_univ: the current time [minutes, universal time]
        
        :return: the duration to the next meal [minutes]
        :rtype: int
        :return: the scheduled next meal
        :rtype: meal.Meal                
        """

        #
        # find the next meal
        #

        # get the start time (universal time) for all meals
        t_start_all     = np.array( [ m.t_start_univ for m in self.meals] )

        # get the duration in time from the start time of each meal from the current time
        dt_all          = t_start_all - t_univ
        dt              = np.min(dt_all) # all dt's should be positive

        # index of the next meal
        idx         = np.where(dt_all == dt)[0][0]
        next_meal   = self.meals[idx]

        return dt, next_meal

    def duration_to_work_event(self, clock):

        """
        This function is called in in order to calculate the amount of time until the next work event.

        #. If the person is employed, the duration to the next meal is set to infinity
        #. If the current time is a workday before the time work starts,

            * set the duration to the amount of time until the start of work
        #. Else,

            * set the duration until the next work event 
        
        .. note::
            The only reason this code is place here is because the work activity and the commute activity use it.

        :param temporal.Temporal clock: the current time
        
        :return: the duration [minutes] until the next minutes
        :rtype: int
        """

        DAY_2_MIN, WEEK_2_DAY   = temporal.DAY_2_MIN, temporal.WEEK_2_DAY

        # the time [minutes, time of day] that a job starts
        t_start = self.job.t_start

        # if the person is unemployed, set the duration to infinity
        if not self.job.is_employed:
            dt = np.inf
        else:
            # if sampling on a workday before the work event starts
            if (clock.day_of_week in self.job.work_days) and (clock.time_of_day <= t_start):
                dt = (t_start - clock.time_of_day) % DAY_2_MIN
            else:

                # future days (1 being tomorrow, 2 being the day after tomorrow)
                z = np.arange(1, WEEK_2_DAY)

                idx = [(clock.day_of_week + i) % WEEK_2_DAY in self.job.work_days for i in z]
                idx = np.array(idx)

                # the number of days until the next workday
                dt_day = z[np.argmax(idx)]

                # time until the next work event
                dt = dt_day * DAY_2_MIN - clock.time_of_day + t_start

        return dt

    def get_current_meal(self, time_of_day):

        """
        This function gets the closest meal to the time of day.

        :param int time_of_day: the time of day
        :return: return the meal
        :rtype: meal.Meal        
        """

        DAY_2_MIN   = temporal.DAY_2_MIN

        # the number of meals
        N = self.num_meals

        # an array where the True values shows the index of the current meal
        idx = np.zeros(N, dtype=bool)

        # loop through each meal
        for q in range(N):

            # get the index for the next meal
            i = self.meals[q].id
            j = (i + 1) % N
            k = (i - 1) % N

            # store the time of day , current meal, next meal, and meal after next the start time
            t, ti, tj, tk = time_of_day, self.meals[i].t_start, self.meals[j].t_start, self.meals[k].t_start

            # meal time is from the start time until the midpoint between the two meals
            # ex: t_max(bf) = t_start(bf) + ( t_start(lunch) - t_start(bf) ) / 2
            # t_min(bf) = t_start(dinner) + ( t_start(bf) - t_start(dinner) ) /2

            # doing math around zero.
            if (tj < ti):
                # change time to periodic time [-DAY_2_MIN / 2, DAY_2_MIN)
                tj = mg.to_periodic(tj, do_hours=False)
                ti = mg.to_periodic(ti, do_hours=False)

                # take the average
                top = np.floor( (ti + tj) / 2 ).astype(int)

                # convert to normal time [0, DAY_2_MIN)
                top = mg.from_periodic(top, do_hours=False)

            else:
                top = np.floor( (ti + tj) / 2 ).astype(int)

            # do math around zero
            if (tk > ti):
                # change time to periodic time [-DAY_2_MIN / 2, DAY_2_MIN)
                ti = mg.to_periodic(ti, do_hours=False)
                tk = mg.to_periodic(tk, do_hours=False)

                # take the average
                bot = np.floor( (tk + ti) / 2 ).astype(int)

                # convert to normal time [0, DAY_2_MIN)
                bot = mg.from_periodic(bot, do_hours=False)
            else:
                bot = np.floor( (tk + ti) / 2 ).astype(int)

            dt_max  = (top - bot) % DAY_2_MIN
            dt0     = (t - bot) % DAY_2_MIN
            dt1     = (top - t) % DAY_2_MIN

            idx[i] = (dt0 <= dt_max) and (dt1 < dt_max) and (dt1 > 0)

        # the current index
        if idx.any():
            ii = np.where(idx == True)[0][0]
            the_meal = self.meals[ii]
        else:
            the_meal = None

        return the_meal

    def get_meal(self, id_meal):

        """
        Get the specific meal given by a meal identifier.
        
        :param int id_meal: the meal identifier
        :return: the meal given by the id
        :rtype: meal.Meal
        """

        x = None

        for m in self.meals:
            if (m.id == id_meal):
                x = m

        return x

    def get_next_meal(self, clock):

        """
        This function gets the next meal. The meal must occur after the current time.

        :param temporal.Temporal clock: the current time

        :return: the next meal
        :rtype: meal.Meal
        """


        # this makes sure that the current meal is not the next meal
        # however, it is still not completely correct because the current meal only depends on time. It's the
        # meal closest to the current time forwards and backwards

        # the expected amount of time (minutes) to the next meal from
        # the current time

        # calculate the amount of time until each meal, respectively
        t_start = np.array([m.t_start_univ for m in self.meals])
        dt      = t_start - clock.t_univ

        # the index of the nearest meal is Social.meals
        idx = np.where(dt == min(dt))[0]
        idx = idx[0]

        # the next meal
        the_meal = self.meals[idx]

        return the_meal

    def print_child_status(self):

        """
        This function represents the child status as a string.

        :return msg: the child/ adult status
        :rtype: str
        """

        if (self.is_child):
            msg = 'Child'
        else:
            msg = 'Adult'

        return msg

    def set_child_flag(self, age):

        """
        Sets the flag indicating whether a person is a child.

        :param int age: the age of the person [years]

        :return: None
        """

        if (age < ADULT_AGE):
            self.is_child = True
        else:
            self.is_child = False
        return

    def set_job(self, job_id, dt=0):

        """
        This function sets the job and the alarm time (if used) that corresponds to the job. The alarm  is set, \
        if a person is using the alarm.

        .. note::
            The current version of ABMHAP has no alarm capability.

        :param int job_id: job identifier
        :param int dt: the amount of time before the job start.

        :return: None
        """

        self.job.id = job_id
        self.job.set_job()
        self.set_work_alarm(dt)
        
        return

    def set_work_alarm(self, dt=0):

        """
        This sets the alarm time due to work. If a person uses an alarm, the alarm \
        is set to be "dt" minutes before work time.

        .. note::
            The current version of ABMHAP has no alarm capability.

        :param int dt: the amount of time to wake up before the work event [minutes]

        :return: None
        """

        DAY_2_MIN = temporal.DAY_2_MIN

        if (self.uses_alarm):
            t = (self.job.t_start - dt + DAY_2_MIN) % DAY_2_MIN
            self.t_alarm = t

        return

    def test_func(self, time_of_day, the_meal):

        """
        This is used for testing.
        
        .. note::
            This function has no real purpose and will be deleted in future versions.
            
        :param int time_of_day: the time of day in minutes 
        :param meal.Meal the_meal: a meal object 
        :return: None
        """

        print('time of day: %.2f\tmeal: %s' % (time_of_day/60, meal.INT_2_STR[the_meal.id] ) )
        print('bf: %.2f\tlunch: %.2f\tdinner: %.2f' \
              % (self.meals[meal.BREAKFAST].t_start /60, self.meals[meal.LUNCH].t_start/60, \
                 self.meals[meal.DINNER].t_start/60) )

        return

    def toString(self):

        """
        Represents the Social object as a string.

        :return: the representation of the Social object
        :rtype: str
        """

        msg = ''

        msg = msg + self.print_child_status() + '\n'
        msg = msg + self.job.toString()

        return msg

