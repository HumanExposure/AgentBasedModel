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
This file contains information for creating the default agent that represents a person that lives \
alone in the home. Singleton will be the name of this type of agent.

This module contains :class:`singleton.Singleton`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

import sys
sys.path.append('..\\source')

import collections

# agent-based model modules
import bio, meal, occupation, person, temporal

# ===============================================
# class Singleton
# ===============================================

class Singleton(person.Person):

    """
    Singleton default is a person that has the following characteristics

    #. female
    #. 30 years old
    #. goes to bed at 22:00 and sleeps for 8 hours
    #. lives alone and has no children
    #. works the Standard Job
    #. eats breakfast at 7:30 for 15 minutes, lunch at 12:00 for 30 minutes, \
    and dinner at 19:00 for 45 minutes

    :param home.Home house: the place of residence
    :param temporal.Temporal clock: the clock running in the simulation
    :param scheduler.Scheduler schedule: the schedule for the agent

    """

    # constructor
    def __init__(self, house, clock, schedule):

        # constructor for the parent class
        person.Person.__init__(self, house, clock, schedule)

        #
        # create the biology
        #

        DAY_2_MIN, HOUR_2_MIN  = temporal.DAY_2_MIN, temporal.HOUR_2_MIN

        #
        # get biological parameters
        #

        # the gender
        self.bio.gender             = bio.FEMALE

        # the age [years]
        self.bio.age                = 30

        # the mean sleep start time
        self.bio.sleep_start_mean   = bio.SLEEP_START_MEAN

        # the standard deviation of sleep start time
        self.bio.sleep_start_std    = bio.SLEEP_START_STD

        # the mean sleep end time
        self.bio.sleep_end_mean     = bio.SLEEP_END_MEAN

        # the standard deviation of the sleep end time
        self.bio.sleep_end_std      = bio.SLEEP_END_STD

        # the mean duration for sleep
        dt_sleep    = (self.bio.sleep_end_mean - self.bio.sleep_start_mean + 1 ) % DAY_2_MIN

        # the mean duration of time awake
        dt_awake    = self.bio.calc_awake_duration(self.clock.time_of_day)

        # set the decay rate for Rest
        self.rest.set_decay_rate(dt_awake)

        # set the recharge rate for Rest
        self.rest.set_recharge_rate(dt_sleep)

        #
        # set the job
        #

        # the job identifier
        self.socio.job.id = occupation.STANDARD_JOB

        # set the job
        self.socio.job.set_job_preset()

        # set the alarm for work. This is not used and will be removed in future versions
        self.socio.uses_alarm = False
        self.socio.set_work_alarm(HOUR_2_MIN)

        # set the meals: breakfast, lunch, and dinner, respectively
        self.socio.meals[0].set_meal(id=meal.BREAKFAST, start_mean=meal.BREAKFAST_START_MEAN, \
                                     start_std=meal.BREAKFAST_START_STD, start_trunc=meal.BREAKFAST_START_TRUNC, \
                                     dt_mean=meal.BREAKFAST_DT_MEAN, dt_std=meal.BREAKFAST_DT_STD, \
                                     dt_trunc=meal.BREAKFAST_DT_TRUNC)

        self.socio.meals[1].set_meal(id=meal.LUNCH, start_mean=meal.LUNCH_START_MEAN, start_std=meal.LUNCH_START_STD, \
                                     start_trunc=meal.LUNCH_START_TRUNC, dt_mean=meal.LUNCH_DT_MEAN, \
                                     dt_std=meal.LUNCH_DT_STD, dt_trunc=meal.LUNCH_DT_TRUNC)

        self.socio.meals[2].set_meal(id=meal.DINNER, start_mean=meal.DINNER_START_MEAN, \
                                     start_std=meal.DINNER_START_STD, start_trunc=meal.DINNER_START_TRUNC,\
                                     dt_mean=meal.DINNER_DT_MEAN, dt_std=meal.DINNER_DT_STD, \
                                     dt_trunc=meal.DINNER_DT_TRUNC)

        return

    def print_params(self):

        """
        This function prints the activity-parameter means in chronological order of start time. This \
        results in the ability to print the mean daily routine.

        :return: a representation of the parameters of the agent in increasing values of \
        start time
        :rtype: str
        """

        # constants
        HOUR_2_MIN      = temporal.HOUR_2_MIN

        # the output message
        msg = ''

        # the work-related and commute-related parameters
        work_start      = self.socio.job.t_start
        work_dt         = self.socio.job.dt
        to_work_dt      = self.socio.job.commute_to_work_dt_mean
        from_work_dt    = self.socio.job.commute_from_work_dt_mean

        # the format string (activity name, start time, duration)
        default_format = '%20s\t%.2f\t%.2f\t%0.2f\n'

        # create a dictionary of terms. Make sure the times in an hours format [0, 24)
        x = {'sleep': (self.bio.sleep_start_mean / HOUR_2_MIN, self.bio.sleep_end_mean / HOUR_2_MIN),
             'eat breakfast': (self.socio.meals[0].t_start / HOUR_2_MIN, self.socio.meals[0].dt_mean / HOUR_2_MIN),
             'work': (work_start / HOUR_2_MIN, work_dt / HOUR_2_MIN),
             'eat lunch': (self.socio.meals[1].t_start / HOUR_2_MIN, self.socio.meals[1].dt_mean / HOUR_2_MIN),
             'eat dinner': (self.socio.meals[2].t_start / HOUR_2_MIN, self.socio.meals[2].dt_mean / HOUR_2_MIN),
             'commute to work mean': ((work_start - to_work_dt) / HOUR_2_MIN, to_work_dt / HOUR_2_MIN),
             'commute from work mean': ((work_start + work_dt) / HOUR_2_MIN, from_work_dt / HOUR_2_MIN),
             }

        # sort the entries by increasing values of start time u = (activity name, (start time, duration) )
        od = collections.OrderedDict(sorted(x.items(), key=lambda u: u[1][0]))

        # write the (activity, start time, duration) tuple for most activities
        for k, v in od.items():
            msg = msg + default_format % (k, v[0], v[1], (v[0] + v[1]) % 24)

        return msg

    def set(self, param, idx):

        """
        This function sets the Singleton's parameters.

        The function does the following:

        #. sets the biology
        #. sets the job information
        #. sets the alarm
        #. sets the meal information

        :param params.Params param: parameters describing the household
        :param int idx: the respective index number of the person of interest in the household

        :return: None
        """

        #
        # create the biology
        #
        gender      = param.gender[idx]

        # set the biology
        self.bio.set_sleep_params(start_mean=param.sleep_start_mean[idx], start_std=param.sleep_start_std[idx], \
                                  end_mean=param.sleep_end_mean[idx], end_std=param.sleep_end_std[idx])
        self.bio.gender = gender

        # biologically related need
        dt_awake    = self.bio.calc_awake_duration(self.clock.time_of_day)

        self.rest.set_decay_rate(dt_awake)
        self.rest.set_recharge_rate(self.bio.sleep_dt)

        #
        # social
        #

        #
        # set the job
        #
        self.socio.job.set_job_params(id_job=param.job_id[idx],\
                                      start_mean=param.work_start_mean[idx], start_std=param.work_start_std[idx],\
                                      end_mean=param.work_end_mean[idx], end_std=param.work_end_std[idx], \
                                      commute_to_work_dt_mean=param.commute_to_work_dt_mean[idx], \
                                      commute_to_work_dt_std=param.commute_to_work_dt_std[idx], \
                                      commute_from_work_dt_mean=param.commute_from_work_dt_mean[idx],\
                                      commute_from_work_dt_std=param.commute_from_work_dt_std[idx])

        self.socio.uses_alarm = param.do_alarm[idx]
        self.socio.set_work_alarm(param.dt_alarm[idx])

        #
        # meals
        #

        # get meal parameters
        breakfast   = param.breakfasts[idx]
        lunch       = param.lunches[idx]
        dinner      = param.dinners[idx]

        # set the meals, breakfast, lunch, dinner
        self.socio.meals[0].set_meal(id=meal.BREAKFAST, start_mean=breakfast.start_mean, \
                                     start_std=breakfast.start_std, start_trunc=breakfast.start_trunc, \
                                     dt_mean=breakfast.dt_mean, dt_std=breakfast.dt_std, \
                                     dt_trunc=breakfast.dt_trunc)

        self.socio.meals[1].set_meal(id=meal.LUNCH, start_mean=lunch.start_mean, \
                                     start_std=lunch.start_std, start_trunc=lunch.start_trunc, \
                                     dt_mean=lunch.dt_mean, dt_std=lunch.dt_std, \
                                     dt_trunc=lunch.dt_trunc)

        # set the meals
        self.socio.meals[2].set_meal(id=meal.DINNER, start_mean=dinner.start_mean, \
                                     start_std=dinner.start_std, start_trunc=dinner.start_trunc, \
                                     dt_mean=dinner.dt_mean, dt_std=dinner.dt_std, \
                                     dt_trunc=dinner.dt_trunc)
        return