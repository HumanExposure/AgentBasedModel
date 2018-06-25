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
The purpose of this module is to assign parameters necessary to run the Agent-Based \
Model of Human Activity Patterns (ABMHAP). This module also have constants used in \
default runs.

This module contains class :class:`params.Params`.

 .. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# for an ordered dictionary
import collections

# mathematical capability
import numpy as np

# agent-based model modules
import my_globals as mg
import activity, bio, meal, occupation, temporal

# ===============================================
# constants
# ===============================================

#
# defaults for household parameters
#

# the step size in the simulation
DT = 1

NUM_PEOPLE  = 1
NUM_DAYS    = 1

NUM_HOURS   = 0
NUM_MIN     = 0

# default start time is Sunday, Day 0 at 06:00
T_START = (temporal.SUNDAY * temporal.DAY_2_MIN) + 16 * temporal.HOUR_2_MIN

# will need to add meal information
# make a default mean object in meal

# ===============================================
# class Params
# ===============================================

class Params(object):

    """
    This class contains the parameters that are needed to parametrize a household.

    .. note::
        Some of the class attributes are **not** really used and need to be phased out in future versions of the \
        model. Some of these attribtues are:
        
        * :attr:`dt`
        * :attr:`do_alarm`
        * :attr:`dt_alarm`
        
    :param int dt: the step size [in minutes] in the simulation. **This is antiquated \
    and will be removed in future versions.**
    :param int num_people: the number of people in the household
    :param int num_days: the number of days in the simulation
    :param int num_hours: the number of additional hours in the simulation
    :param int num_min: the number of additional minutes in the simulation
    :param int t_start: the start time [in minutes] in the simulation
    
    :param list gender: the gender of each person in the household    
    :param list sleep_start_mean: the mean sleep start time [in minutes, time of day] for each person in \
    the household
    :param list sleep_start_std: the standard deviation of sleep start time [in minutes] for each person in the \
    household            
    :param list sleep_end_mean: the mean sleep end time [in minutes, time of day] for each person in the household
    :param list sleep_end_std: the standard deviation of the sleep end time [in minutes] for each person in \
    the household
            
    
    :param list job_id: the occupation identifier for each person in the household
    :param list do_alarm: a flag indicating whether or not a person uses an alarm for each person in the household
    :param list dt_alarm: the duration of time [in minutes] before an alarm goes off before its respective event
    
    :param numpy.ndarray bf_start_mean: the mean breakfast start time for each person in the household \
    [minutes, time of day]
    :param numpy.ndarray bf_start_std: the standard deviation for breakfast start time for each person in the \
    household [minutes] 
    :param numpy.ndarray bf_start_trunc: the number of standard deviations used in the breakfast start time \
    distribution for each person
    
    :param numpy.ndarray bf_dt_mean: the mean breakfast duration for each person in the household [minutes]
    :param numpy.ndarray bf_dt_std: the standard deviation for breakfast duration for each person in the \
    household [minutes] 
    :param numpy.ndarray bf_dt_trunc: the number of standard deviations used in the breakfast duration \
    distribution for each person
        
    :param numpy.ndarray lunch_dt_mean: the mean lunch duration for each person in the household [minutes]
    :param numpy.ndarray lunch_dt_std: the standard deviation for lunch duration for each person in the \
    household [minutes] 
    :param numpy.ndarray lunch_dt_trunc: the number of standard deviations used in the lunch duration \
    distribution for each person
    
    :param numpy.ndarray lunch_start_mean: the mean lunch start time for each person in the household \
    [minutes, time of day]
    :param numpy.ndarray lunch_start_std: the standard deviation for lunch start time for each person in the \
    household [minutes] 
    :param numpy.ndarray lunch_start_trunc: the number of standard deviations used in the lunch start time \
    distribution for each person
        
    :param numpy.ndarray dinner_start_mean: the mean dinner start time for each person in the household \
    [minutes, time of day]
    :param numpy.ndarray dinner_start_std: the standard deviation for dinner start time for each person in the \
    household [minutes] 
    :param numpy.ndarray dinner_start_trunc: the number of standard deviations used in the dinner start time \
    distribution for each person
    
    :param numpy.ndarray dinner_dt_mean: the mean dinner duration for each person in the household [minutes]
    :param numpy.ndarray dinner_dt_std: the standard deviation for dinner duration for each person in the \
    household [minutes] 
    :param numpy.ndarray dinner_dt_trunc: the number of standard deviations used in the dinner duration \
    distribution for each person
    
    :param numpy.ndarray work_start_mean: the mean work start time for each person in the household \
    [minutes, time of day] 
    :param numpy.ndarray work_start_std: the standard deviation of work start time for each person in the \
    household [minutes]
    :param numpy.ndarray work_end_mean: the work end time for each person in the household [minutes, time of day]
    :param numpy.ndarray work_end_std: the work standard deviation for each person in the household \
    [minutes, time of day]
    
    :param numpy.ndarray commute_to_work_dt_mean: the mean duration for commuting to work [minutes] for each \
    person in the household
    :param numpy.ndarray commute_to_work_dt_std: the standard deviation for commuting to work [minutes] for each \
    person in the household
    :param numpy.ndarray commute_from_work_dt_mean: the mean duration for commuting from work [minutes] for each \
    person in the household
    :param numpy.ndarray commute_from_work_dt_std: the standard deviation for commuting from work [minutes] for \
    each person in the household
    
    :var int dt: the step size [in minutes] in the simulation **(this is antiquated and will be removed \
    in future versions)**
    :var int num_people: the number of people in the household
    :var int num_days: the number of days in the simulation
    :var int num_hours: the number of additional hours in the simulation
    :var int num_min: the number of additional minutes in the simulation
    :var int t_start: the start time [in minutes] in the simulation
    
    :var list gender: the gender of each person in the household    
    :var list sleep_start_mean: the mean sleep start time [in minutes, time of day] for each person in \
    the household
    :var list sleep_start_std: the standard deviation of sleep start time [in minutes] for each person in the \
    household            
    :var list sleep_end_mean: the mean sleep end time [in minutes, time of day] for each person in the household
    :var list sleep_end_std: the standard deviation of the sleep end time [in minutes] for each person in \
    the household            
    
    :var list job_id: the occupation identifier for each person in the household
    :var list do_alarm: a flag indicating whether or not a person uses an alarm for each person in the household
    :var list dt_alarm: the duration of time [in minutes] before an alarm goes off before its respective event
    
    :var list breakfasts: the breakfast meal objects for each person in the household
    :var list lunches: the lunch meal objects for each person in the household
    :var list dinners: the dinner meal objects for each person in the household
    
    :var numpy.ndarray work_start_mean: the mean work start time for each person in the household \
    [minutes, time of day] 
    :var numpy.ndarray work_start_std: the standard deviation of work start time for each person in the \
    household [minutes]
    :var numpy.ndarray work_end_mean: the work end time for each person in the household [minutes, time of day]
    :var numpy.ndarray work_end_std: the work standard deviation for each person in the household \
    [minutes, time of day]
    
    :var numpy.ndarray commute_to_work_dt_mean: the mean duration for commuting to work [minutes] for each person \
    in the household
    :var numpy.ndarray commute_to_work_dt_std: the standard deviation for commuting to work [minutes] for \
    each person in the household
    :var numpy.ndarray commute_from_work_dt_mean: the mean duration for commuting from work [minutes] for \
    each person in the household
    :var numpy.ndarray commute_from_work_dt_std: the standard deviation for commuting from work [minutes] for each \
    person in the household
    """

    def __init__(self, num_people, num_days, num_hours, num_min,
                 do_minute_by_minute, t_start=T_START, dt=1, gender=None,
                 sleep_start_mean=None, sleep_start_std=None,  sleep_end_mean=None, sleep_end_std=None,
                 job_id=None, do_alarm=None,
                 dt_alarm=None,
                 bf_start_mean=None, bf_start_std=None, bf_start_trunc=None,
                 bf_dt_mean=None, bf_dt_std=None, bf_dt_trunc=None,
                 lunch_start_mean=None, lunch_start_std=None, lunch_start_trunc=None,
                 lunch_dt_mean=None, lunch_dt_std=None , lunch_dt_trunc=None,
                 dinner_start_mean=None, dinner_start_std=None, dinner_start_trunc=None,
                 dinner_dt_mean=None, dinner_dt_std=None, dinner_dt_trunc=None,
                 work_start_mean=None, work_start_std=None, work_end_mean=None, work_end_std=None,
                 commute_to_work_dt_mean=None, commute_to_work_dt_std=None, commute_from_work_dt_mean=None,
                 commute_from_work_dt_std=None):

        # parametrize the sleep start, end, and duration

        #
        # timing
        #
        self.do_minute_by_minute = do_minute_by_minute

        self.dt         = dt
        self.num_days   = num_days
        self.num_hours  = num_hours
        self.num_min    = num_min
        self.t_start    = t_start
        self.set_num_steps()

        # population
        self.num_people         = num_people
        self.gender             = self.init_help( gender, (bio.MALE,) * self.num_people )

        # sleep info
        self.sleep_start_mean   = self.init_help(sleep_start_mean, (bio.SLEEP_START_MEAN,) * self.num_people)
        self.sleep_start_std    = self.init_help(sleep_start_std, (bio.SLEEP_START_STD,) * self.num_people)

        self.sleep_end_mean     = self.init_help(sleep_end_mean, (bio.SLEEP_END_MEAN,) * self.num_people)
        self.sleep_end_std      = self.init_help(sleep_end_std, (bio.SLEEP_END_STD,) * self.num_people)

        # work info
        self.work_start_mean    = self.init_help(work_start_mean, (occupation.START_MEAN,) * self.num_people)
        self.work_start_std     = self.init_help(work_start_std, (occupation.START_STD,) * self.num_people)

        self.work_end_mean      = self.init_help(work_end_mean, (occupation.END_MEAN,) * self.num_people)
        self.work_end_std       = self.init_help(work_end_std, (occupation.END_STD,) * self.num_people)

        # commute to and from work info
        self.commute_to_work_dt_mean    = self.init_help( commute_to_work_dt_mean, \
                                                             (occupation.COMMUTE_TO_WORK_DT_MEAN,) * self.num_people )
        self.commute_to_work_dt_std     = self.init_help( commute_to_work_dt_std, \
                                                             (occupation.COMMUTE_TO_WORK_DT_STD,) * self.num_people )

        self.commute_from_work_dt_mean = self.init_help(commute_from_work_dt_mean, \
                                                      (occupation.COMMUTE_FROM_WORK_DT_MEAN,) * self.num_people)

        self.commute_from_work_dt_std = self.init_help(commute_from_work_dt_std, \
                                                     (occupation.COMMUTE_FROM_WORK_DT_STD,) * self.num_people)
        # meals info
        self.breakfasts = self.init_meal(m_id=meal.BREAKFAST, start_mean=bf_start_mean, start_std=bf_start_std, \
                                         start_trunc=bf_start_trunc, dt_mean=bf_dt_mean, dt_std=bf_dt_std, \
                                         dt_trunc=bf_dt_trunc)

        self.lunches = self.init_meal(m_id=meal.LUNCH, start_mean=lunch_start_mean, start_std=lunch_start_std, \
                                          start_trunc=lunch_start_trunc, dt_mean=lunch_dt_mean, \
                                          dt_std=lunch_dt_std, dt_trunc=lunch_dt_trunc)

        self.dinners = self.init_meal(m_id=meal.DINNER, start_mean=dinner_start_mean, start_std=dinner_start_std, \
                                          start_trunc=dinner_start_trunc, dt_mean=dinner_dt_mean, \
                                          dt_std=dinner_dt_std, dt_trunc=dinner_dt_trunc)

        #
        # other info
        #
        self.job_id     = self.init_help( job_id, (occupation.STANDARD_JOB, ) * self.num_people )
        self.do_alarm   = self.init_help( do_alarm, (False,) * self.num_people )
        self.dt_alarm   = self.init_help( dt_alarm, (1 * temporal.HOUR_2_MIN,) * self.num_people )

        return

    def get_info_mean(self):

        """
        This function stores information about the mean values of the activity-parameters.

        :return: a message about the the mean values
        :rtype: str
        :return: a list of activity codes in the chronological order in time of day
        :rtype: list
        """

        # the amount of minutes in 1 hour
        HOUR_2_MIN = temporal.HOUR_2_MIN

        msg = ''

        msg = msg + 'Mean data [hours] (start\tduration\tend)\n'

        z = zip(self.sleep_start_mean, self.sleep_end_mean, self.breakfasts, self.work_start_mean,
                self.work_end_mean, self.lunches, self.dinners, self.commute_to_work_dt_mean,
                self.commute_from_work_dt_mean)

        # the format string (activity name, start time, duration)
        default_format = '%20s\t%.2f\t%.2f\t%0.2f\n'

        #  or each person in the household, loop through the parameters
        for sleep_start_mean, sleep_end_mean, breakfast, work_start_mean, work_end_mean, lunch, \
            dinner, to_work_dt, from_work_dt in z:

            # create a dictionary of terms. Make sure the times in an hours format [0, 24)
            x = {mg.KEY_SLEEP: (sleep_start_mean / HOUR_2_MIN, sleep_end_mean / HOUR_2_MIN),
                 mg.KEY_EAT_BREAKFAST: (breakfast.start_mean / HOUR_2_MIN, breakfast.dt_mean / HOUR_2_MIN),
                 mg.KEY_WORK: (work_start_mean / HOUR_2_MIN, work_end_mean / HOUR_2_MIN),
                 mg.KEY_EAT_LUNCH: (lunch.start_mean / HOUR_2_MIN, lunch.dt_mean / HOUR_2_MIN),
                 mg.KEY_EAT_DINNER: (dinner.start_mean / HOUR_2_MIN, dinner.dt_mean / HOUR_2_MIN),
                 mg.KEY_COMMUTE_TO_WORK: ((work_start_mean - to_work_dt) / HOUR_2_MIN, to_work_dt / HOUR_2_MIN),
                 mg.KEY_COMMUTE_FROM_WORK: (work_end_mean / HOUR_2_MIN, from_work_dt / HOUR_2_MIN),
                 }

            # sort the entries by increasing values of start time u = (activity name, (start time, duration) )
            od = collections.OrderedDict(sorted(x.items(), key=lambda u: u[1][0]))

            # write the (activity, start time, duration) tuple for most activities
            keys = list()
            for k, v in od.items():
                msg = msg + default_format % (activity.INT_2_STR[k], v[0], v[1], (v[0] + v[1]) % 24)
                keys.append(k)

        return msg, keys

    def get_info_std(self, keys_ordered=None):

        """
        This function stores information about the standard deviation values of the activity-parameters.

        :param list keys_ordered: this is a list of the names of the activities that are in the \
        same order as the information about the means

        :return: a message about the the standard deviation values
        :rtype: str
        """

        # the amount of minutes in 1 hour
        HOUR_2_MIN = temporal.HOUR_2_MIN

        msg = ''

        msg = msg + 'Standard deviation data [hours] (start\tduration\tend)\n'

        z = zip(self.sleep_start_std, self.sleep_end_std, self.breakfasts, self.work_start_std,
                self.work_end_std, self.lunches, self.dinners, self.commute_to_work_dt_std,
                self.commute_from_work_dt_std)

        # the format string (activity name, start time, duration)
        default_format = '%20s\t%.2f\t%.2f\t%0.2f\n'

        #  or each person in the household, loop through the parameters
        for sleep_start_std, sleep_end_std, breakfast, work_start_std, work_end_std, lunch, \
            dinner, to_work_dt, from_work_dt in z:

            # create a dictionary of terms. Make sure the times in an hours format [0, 24)
            x = {mg.KEY_SLEEP: (sleep_start_std / HOUR_2_MIN, np.NaN, sleep_end_std / HOUR_2_MIN),
                 mg.KEY_EAT_BREAKFAST: (breakfast.start_std / HOUR_2_MIN, breakfast.dt_std / HOUR_2_MIN, np.NaN),
                 mg.KEY_WORK: (work_start_std / HOUR_2_MIN, np.NaN, work_end_std / HOUR_2_MIN),
                 mg.KEY_EAT_LUNCH: (lunch.start_std / HOUR_2_MIN, lunch.dt_std / HOUR_2_MIN, np.NaN),
                 mg.KEY_EAT_DINNER: (dinner.start_std / HOUR_2_MIN, dinner.dt_std / HOUR_2_MIN, np.NaN),
                 mg.KEY_COMMUTE_TO_WORK: (np.NaN, to_work_dt / HOUR_2_MIN, np.NaN),
                 mg.KEY_COMMUTE_FROM_WORK: (np.NaN, from_work_dt / HOUR_2_MIN, np.NaN),
                 }

            # sort the entries by increasing values of start time u = (activity name, (start time, duration) )
            od = collections.OrderedDict(sorted(x.items(), key=lambda u: u[1][0]))

            # write the (activity, start time, duration) tuple for most activities
            if keys_ordered is None:
                for k, v in od.items():
                    msg = msg + default_format % (activity.INT_2_STR[k], v[0], v[1], v[2])
            else:
                # the order of the keys in the ordered dictionary
                keys = [k for k, v in od.items()]
                vals = [v for k, v in od.items()]
                for k in keys_ordered:
                    idx = keys.index(k)
                    v = vals[idx]
                    msg = msg + default_format % (activity.INT_2_STR[k], v[0], v[1], v[2])

        return msg

    def init_help(self, val, default_val):

        """
        This function assigns a default value to an attribute in case it was not assigned already. This is, \
        function is particularly useful if the value to be assigned is an array depending on :attr:`num_people`. \
        More specifically,
        
        * if val is not None, return val
        * if val is None, return the default value (default_val)
        
        :param val: the value to be assigned
        :param default_val: the default value to assign in case val is None

        :return: the non-None value
        """

        # if val is none, assign the default value
        if val is None:
            val = default_val

        return val

    def init_meal(self, m_id, start_mean=None, start_std=None, start_trunc=None, dt_mean=None, \
                      dt_std=None, dt_trunc=None):

        """
        This function returns the data for each person in the household for the respective meal \
        given by "m_id":

        * if specific parameters have been assigned, create meals with the respective parameters
        * if specific parameters have not been assigned, create meals with the default meal parameters for \
        each meal
        
        :param int m_id: the identifier of meal type
        :param numpy.ndarray start_mean: the mean start time for the meal for each person in the household
        :param numpy.ndarray start_std: the standard deviation of start time for the meal for each person in \
        the household
        :param numpy.ndarray start_trunc: the amount of standard deviations allowed before truncating the \
        start time distribution for each person in the household

        :param numpy.ndarray dt_mean: the mean duration for the meal for each person in the household
        :param numpy.ndarray dt_std: the standard deviation for the meal for each person in the household
        :param numpy.ndarray dt_trunc: the amount of standard deviations allowed before truncating the \
        duration distribution for each person in the household

        :return: the meals for each person in the household
        :rtype: list
        """

        # this is a dictionary of the default parameters for each meal
        default = {meal.BREAKFAST: (meal.BREAKFAST_START_MEAN, meal.BREAKFAST_START_STD, meal.BREAKFAST_START_TRUNC, \
                                    meal.BREAKFAST_DT_MEAN, meal.BREAKFAST_DT_STD, meal.BREAKFAST_DT_TRUNC),

                   meal.LUNCH: (meal.LUNCH_START_MEAN, meal.LUNCH_START_STD, meal.LUNCH_START_TRUNC, \
                                meal.LUNCH_DT_MEAN, meal.LUNCH_DT_STD, meal.LUNCH_DT_TRUNC),

                   meal.DINNER: (meal.DINNER_START_MEAN, meal.DINNER_START_STD, meal.DINNER_START_TRUNC, \
                                 meal.DINNER_DT_MEAN, meal.DINNER_DT_STD, meal.DINNER_DT_TRUNC),
                   }

        # if data was not specifically assigned to a person, assign the default values for the meal
        # for each person in the household
        if (start_mean is None) and (start_std is None)  and (start_trunc is None) and (dt_mean is None) and \
                (dt_std is None) and (dt_trunc is None):

            # start time (s) and duration (d) parameters
            s_mean, s_std, s_trunc, d_mean, d_std, d_trunc = default[m_id]

            the_meal    = meal.Meal(id=m_id, start_mean=s_mean, start_std=s_std, start_trunc=s_trunc, \
                                    dt_mean=d_mean, dt_std=d_std, dt_trunc=d_trunc)

            meals       = (the_meal,) * self.num_people

        # enter the assigned parameters for the meal for each person in the household
        else:
            z = zip(start_mean, start_std, start_trunc, dt_mean, dt_std, dt_trunc)

            meals = [ meal.Meal(id=m_id, start_mean=s_mean, start_std=s_std, start_trunc=s_trunc, \
                                    dt_mean=d_mean, dt_std=d_std, dt_trunc=d_trunc) \
                      for (s_mean, s_std, s_trunc, d_mean, d_std, d_trunc) in z ]

        return meals

    def init_meal_old(self, id, start_mean=None, start_std=None, dt_mean=None, dt_std=None):

        """
        This function returns the data for each person in the household for the respective meal given by "id".

        .. warning::
            This function may be **not** used because it is antiquated.
            
        :param int id: the id of meal type
        :param numpy.ndarray start_mean: the mean start time for the meal for each person in the household
        :param numpy.ndarray dt_mean: the mean duration for the meal for each person in the household
        :param numpy.ndarray dt_std: the mean standard deviation for the meal for each person in the household

        :return: the meals for each person in the household
        :rtype: list
        """

        # the default parameters for each meal
        default = {meal.BREAKFAST: (meal.BREAKFAST_START_MEAN, meal.BREAKFAST_START_STD, \
                                    meal.BREAKFAST_DT_MEAN, meal.BREAKFAST_DT_STD),
                   meal.LUNCH: (meal.LUNCH_START_MEAN, meal.LUNCH_START_STD, \
                                meal.LUNCH_DT_MEAN, meal.LUNCH_DT_STD),
                   meal.DINNER: (meal.DINNER_START_MEAN, meal.DINNER_START_STD, \
                                 meal.DINNER_DT_MEAN, meal.DINNER_DT_STD),
                   }

        # default parameters for the meal
        if (start_mean is None) and (dt_mean is None) and (dt_std is None):

            start_mean, start_std, dt_mean, dt_std = default[id]
            the_meal    = meal.Meal(id=id, start_mean=start_mean, start_std=start_std, dt_mean=dt_mean, dt_std=dt_std)
            meals       = (the_meal,) * self.num_people

        # enter the parameters for the meal
        else:
            meals = [ meal.Meal(id=id, start_mean=s_mean, start_std=s_std, dt_mean=d_mean, dt_std=d_std)
                            for (s_mean, s_std, d_mean, d_std) in zip(start_mean, start_std, dt_mean, dt_std) ]

        return meals

    def set_no_variation(self):

        """
        This function sets all of the standard deviations of the activity-parameters to zero for all
        agents being simulated.

        :return:
        """

        # zero minutes
        zero = np.zeros( (self.num_people,), dtype=int )

        # work
        self.work_start_std = np.array(zero)
        self.work_end_std   = np.array(zero)

        # commute from work
        self.commute_from_work_dt_std   = np.array(zero)

        # commute to work
        self.commute_to_work_dt_std     = np.array(zero)

        # sleep
        self.sleep_start_std    = np.array(zero)
        self.sleep_end_std      = np.array(zero)

        # eat meals
        for meals in zip(self.breakfasts, self.lunches, self.dinners):
            for m in meals:
                m.start_std = 0
                m.dt_std    = 0

        return

    def set_num_steps(self):

        """
        This function calculates and sets the number of time steps ABMHAP will run.

        .. note::
            This function may be antiquated.

        :rtype: None
        """

        # convert the number of days into minutes
        t_days = self.num_days * temporal.DAY_2_MIN

        # convert the number of hours into minutes
        t_hours = self.num_hours * temporal.HOUR_2_MIN

        # the total amount of time
        total_time = t_days + t_hours + self.num_min

        # the total number of steps
        self.num_steps = total_time // self.dt

        return

    def tester(self):

        """
        .. warning::
            This function is just for testing. It checks to see whether the expected dinner time is before \
            the expected end time for work.

        :return:
        """

        HOUR_2_MIN  = temporal.HOUR_2_MIN

        z = zip(self.work_start_mean, self.work_dt_mean, self.dinners)

        is_problem = False

        msg = ''

        for work_start, work_dt, dinner in z:

            work_end = ( work_start + work_dt ) / HOUR_2_MIN
            dinner_start = dinner.t_start / HOUR_2_MIN

            if ( dinner_start < work_end):
                is_problem = True

        if (is_problem):
            msg = msg + 'EXPECT A PROBLEM\n'
            msg = msg + 'dinner starts before work ends '

        return msg

    def toString(self):

        """
        This function represents the Params object as a string. For now, it prints \
        the tuple (start time, duration, end time) in hours[0, 24] for the following activities:

        #. eat breakfast
        #. commute to work
        #. work
        #. eat lunch
        #. commute from work
        #. eat dinner
        #. sleep

        in order of start time. The commute activities only have duration information.

        :return: the parameter information
        """

        # write information about the mean values
        msg, keys_ordered   = self.get_info_mean()

        # write information about the standard deviation values
        msg     = msg + '\n' + self.get_info_std(keys_ordered)

        return msg

