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
This module contains info needed for the occupation of a Person. In addition, this file also contains functions \
useful for the module itself.

This module contains class :class:`occupation.Occupation`.

This module contains constants relevant to the occupational information:

* job identifiers
* job categories
* default start time information
* default end time information
* default commuting to work information
* default commuting from work information
* default summer vacation (from school) information

.. moduleauthor:: Dr. Namdi Brandon
"""

# ----------------------------------------------------------
# import
# ----------------------------------------------------------

# general math capability
import numpy as np

# agent-based model modules
import my_globals as mg
import location, temporal

# ----------------------------------------------------------
# constants
# ----------------------------------------------------------

# job IDs
NO_JOB          = 0
STANDARD_JOB    = 1
GRAVE_SHIFT     = 2
STUDENT         = 3

# job categories
NO_TIME     = 0
FIXED_SHIFT = 1     # the worker works on a fixed shift. Has to be there
                    # at t_start and
                    # leaves at t_end. If the employee shows up late, the employee
                    # still leaves at the end of the shift
            
FIXED_DURATION = 2  # always work for a fixed duration of time.
                    # it doesn't matter as much if you are late

# default mean occupation start time [minutes]
START_MEAN          = 9 * temporal.HOUR_2_MIN
START_MEAN_SCHOOl   = 8 * temporal.HOUR_2_MIN
START_STD           = 0

END_MEAN            = 17 * temporal.HOUR_2_MIN
END_MEAN_SCHOOL     = 15 * temporal.HOUR_2_MIN
END_STD             = 0

# default commuting time
COMMUTE_TO_WORK_DT_MEAN     = 30
COMMUTE_TO_WORK_DT_STD      = 0

COMMUTE_FROM_WORK_DT_MEAN   = 60
COMMUTE_FROM_WORK_DT_STD    = 0

# the amount of standard deviations before truncation when sampling work start and end times
WORK_START_TRUNC    = 1
WORK_END_TRUNC      = 1

# the amount of standard deviations before truncation when sampling commuting start and end times
COMMUTE_TO_WORK_DT_TRUNC        = 1
COMMUTE_FROM_WORK_DT_TRUNC      = 1

# minimum amount of time to commute [minutes]
DT_COMMUTE_MIN = 5

# summer vacation start [weeks]
SUMMER_VACATION_START   = temporal.SUMMER  * temporal.SEASON_2_WEEK + 2
SUMMER_VACTION_END      = temporal.FALL * temporal.SEASON_2_WEEK

# This dictionary takes the INTEGER representation of a the job identifier and
# returns a STRING representation
INT_2_STR_ID = {
    NO_JOB: 'No Job',
    STANDARD_JOB: 'Standard Job',
    GRAVE_SHIFT: 'Grave Shift',
    STUDENT: 'Student',
}

# This dictionary takes the STRING representation of a the job identifier and
# returns an INTEGER representation
STR_2_INT_ID = { v: k for k, v in INT_2_STR_ID.items() }

# This dictionary takes the INTEGER representation of a the Occupation category and
# returns a STRING representation
INT_2_STR_CAT = {
    NO_TIME: 'No time',
    FIXED_SHIFT: 'Fixed Shift',
    FIXED_DURATION: 'Fixed Duration',
}

# This dictionary takes the STRING representation of a the Occupation category and
# returns an INTEGER G representation
STR_2_INT_CAT = { v: k for k, v in INT_2_STR_CAT.items() }

# ===============================================
# class
# ===============================================

class Occupation(object):

    """
    This class contains information relevant to an occupation of a Person.

    :var int category: the category of the job
    :var int id: the identifier for the job
    
    :var int commute_to_work_dt_mean: the mean duration to commute to work [minutes]
    :var int commute_to_work_dt_std: the standard deviation to commute to work [minutes]
    :var int commute_to_work_dt: the duration to commute to work [minutes]
    :var int commute_to_work_dt_trunc: the number of standard deviation in the commute to work \
    duration distribution
    
    :var int commute_to_work_start: the start time for the commute to work activity [minutes]
    :var int dt_commute: the duration of the commute [minutes]
    :var int dt: the duration of the work activity [minutes]
    
    :var int commute_from_work_dt_mean: the mean duration to commute from work [minutes]
    :var int commute_from_work_dt_std: the standard deviation to commute from work [minutes]
    :var int commute_from_work_dt: the duration to commute from work [minutes]
    :var int commute_from_work_dt_trunc: the number of standard deviations in the commute from work \
    duration distribution
    
    :var int t_start_mean: the mean start time for the job [minutes, time of day]
    :var int t_start_std: the standard deviation of the start time for the job
    :var int t_start: the start time for the job [minutes, time of day]
    :var int t_start_univ: the start time for the job [minutes, universal time]
    :var int work_start_trunc: the number of standard deviations in the work start time distribution    
    :var int day_start: the day the work activity start [minutes]
    
    :var int t_end_mean: the mean end time for the job [minutes, time of day]
    :var int t_end_std: the standard deviation of the end time for the job
    :var int t_end: the end time for the job [minutes, time of day]
    :var int t_end_univ: the end time for the job [minutes, universal time]
    :var int work_end_trunc: the number of standard deviations in the work end time distribution
    

    :var bool is_employed: this is a flag saying whether this is a job or not
    :var bool is_same_day: This is a flag to see whether the start time and end time of a job are \
                            on the same day. If so, True. Else, False. If a person has :const:`NO_JOB`, the flag \
                            is set to True
                            
    :var location.Location 'location': the location of the Occupation        
    :var float wage: the yearly wage for that job [U.S. dollars]
    :var list work_days: a list of ints, giving the days the job starts
    
    :var f_commute_to_work_dt: the commute to work duration distribution
    :var f_commute_from_work_dt: the commute from work duration distribution
    :var f_work_start: the work start time distribution
    :var f_work_end: the work end time distribution
    """

    #
    # Constructor 
    #
    def __init__(self):

        # the occupation ID
        self.id = NO_JOB

        # the category of Job type
        self.category = NO_TIME

        # commute to work duration
        self.commute_to_work_dt_mean    = None
        self.commute_to_work_dt_std     = None
        self.commute_to_work_dt         = None

        # commute from work duration
        self.commute_from_work_dt_mean  = None
        self.commute_from_work_dt_std   = None
        self.commute_from_work_dt       = None

        self.commute_to_work_dt_trunc   = COMMUTE_TO_WORK_DT_TRUNC
        self.commute_from_work_dt_trunc = COMMUTE_FROM_WORK_DT_TRUNC

        # the start time for work
        self.t_start_mean   = None
        self.t_start_std    = None
        self.t_start        = None
        self.t_start_univ   = 0

        # the end time for work
        self.t_end_mean     = None
        self.t_end_std      = None
        self.t_end          = None
        self.t_end_univ     = 0

        # the number of stnadard deviation for the work start time and end time distributions, respectively
        self.work_start_trunc   = WORK_START_TRUNC
        self.work_end_trunc     = WORK_END_TRUNC

        # the duration of the commute
        self.dt_commute = None
        # the start time for commuting to work
        self.commute_to_work_start = None
        # the duration of working
        self.dt = None

        # the days of the week that I start working
        self.work_days = None   # the days you start your job

        # the wage of the occupation
        self.wage = 0

        # a flag indicating whether or not an agent is unemployed or not
        self.is_employed = None

        # a flag indicating whether or not, work starts and ends on the same day
        self.is_same_day = None

        # the location of the job
        self.location = None

        # set the job to a preset one
        self.set_job_preset()

        # these are the probability distributions for sampling start and end times for work
        self.f_work_start   = None
        self.f_work_end     = None

        # the probability distribution for sampling commute to work and commute from work duration
        self.f_commute_to_work_dt   = None
        self.f_commute_from_work_dt = None

        # the day the work activity starts
        self.day_start  = 0
        return

    def is_summer_vacation(self, week_of_year):

        """
        This function returns True if the agent should not go to school due to summer vacation. False, otherwise.
        
        :param int week_of_year: the week of the year 
        :return: 
        """

        x = (self.id == STUDENT) and (week_of_year in range(SUMMER_VACATION_START, SUMMER_VACTION_END) )

        return x

    def print_category(self):

        """
        This function represents the Occupation category as a string

        :return: the string representation of a Occupation category
        :rtype: str
        """

        # the error message if category is an invalid choice
        msg = 'ERROR! %d is an invalid choice for the type of job category!\n' % self.category

        # if the category is valid, express it as a string. If not, write the error message
        return INT_2_STR_CAT.get(self.category, msg)

    def print_id(self):

        """
        This function writes the Occupation id as a string

        :return: a string representation of the job ID
        :rtype: str
        """

        # the error message if id is an invalid choice
        msg = 'ERROR! %d is an invalid choice for the type of job id!\n' % self.id

        # if the id is valid, express it as a string. If not, write the error message
        return INT_2_STR_ID.get(self.id, msg)

    def set_commute_distribution(self):

        """
        This function sets the following: 
        
        * commute to work duration distribution 
        * commute from work duration distribution.
         
        :return: None 
        """

        # create the commute to work distribution
        f_to_work, self.commute_to_work_dt_std = mg.set_distribution_dt(-self.commute_to_work_dt_trunc, \
                self.commute_to_work_dt_trunc, self.commute_to_work_dt_mean, self.commute_to_work_dt_std, \
                x_min=DT_COMMUTE_MIN)

        # create the commute from work distribution
        f_from_work, self.commute_from_work_dt_std = mg.set_distribution_dt(-self.commute_from_work_dt_trunc, \
                self.commute_from_work_dt_trunc, self.commute_from_work_dt_mean, self.commute_from_work_dt_std, \
                x_min=DT_COMMUTE_MIN)

        # set the distributions
        self.f_commute_to_work_dt   = f_to_work
        self.f_commute_from_work_dt = f_from_work

        return

    def set_is_job(self):

        """
        This function checks to see if the current job is actually a job (eg. that it is not \
        :const:`NO_JOB`).

        Sets self.is_job to True if the Occupation is :const:`NO_JOB`, returns False otherwise

        :return: None
        """

        # if an occupation id is named in this dictionary, set it to False
        # otherwise, set everything else to True
        switcher = {
            NO_JOB: False,
        }

        self.is_job = switcher.get(self.id, True)

        return

    def set_is_same_day(self):

        """
        This function sets a flag indicating whether or not a job starts and ends \
        on the same day. The function sets :mod:`is_same_day` to True if the Occupation start time and end time \
        are within the same day. False, otherwise.

        :return: None
        """

        # the amount of minutes in 1 day
        DAY_2_MIN = temporal.DAY_2_MIN

        # the duration of the job
        dt = (self.t_end - self.t_start) % DAY_2_MIN

        # if the job ends before midnight
        if (self.t_start + dt < DAY_2_MIN):
            self.is_same_day = True
        else:
            self.is_same_day = False

        return

    def set_job_params(self, id_job, start_mean, start_std, end_mean, end_std, commute_to_work_dt_mean,\
                       commute_to_work_dt_std, commute_from_work_dt_mean, commute_from_work_dt_std):

        """
        This function sets the Occupation parameters.
        
        :param int id_job: the job identifier 
        :param int start_mean: the mean start time for the occupation
        :param int start_std: the standard deviation of the start time for the occupation
        :param int end_mean: the mean end time for the occupation
        :param int end_std: the standard deviation for the end time
        :param int commute_to_work_dt_mean: the mean commute to work duration
        :param int commute_to_work_dt_std: the standard deviation of the commute to work duration
        :param int commute_from_work_dt_mean: the mean commute from work duration
        :param int commute_from_work_dt_std: the standard deviation to commute from work duration
        
        :return: None
        """

        # how many minutes in one day
        DAY_2_MIN   = temporal.DAY_2_MIN

        # set the id number
        self.id     = id_job

        # this sets the job to one of the presets
        self.set_job_preset()

        # if the occupation is a job
        if self.id != NO_JOB:

            # set information about job start time
            self.t_start_mean   = start_mean
            self.t_start_std    = start_std
            self.t_start        = self.t_start_mean

            # set information about job end time
            self.t_end_mean     = end_mean
            self.t_end_std      = end_std
            self.t_end          = self.t_end_mean

            # set the work distribution functions
            self.set_work_distribution()

            # commute to work duration
            self.commute_to_work_dt_mean    = commute_to_work_dt_mean
            self.commute_to_work_dt_std     = commute_to_work_dt_std
            self.commute_to_work_dt         = self.commute_to_work_dt_mean

            # commute from work duration
            self.commute_from_work_dt_mean  = commute_from_work_dt_mean
            self.commute_from_work_dt_std   = commute_from_work_dt_std
            self.commute_from_work_dt       = self.commute_from_work_dt_mean

            # set the commuting distribution functions
            self.set_commute_distribution()

            # for easy recall, set the commute to work start time
            self.commute_to_work_start = (self.t_start_mean - self.commute_to_work_dt_mean + DAY_2_MIN) % DAY_2_MIN

            # job duration
            self.dt = (self.t_end_mean - self.t_start_mean) % DAY_2_MIN

        return

    def set_job_preset(self):

        """
        Sets Occupation to one of the following preset jobs:
        
        * :const:`NO_JOB`
        * :const:`STANDARD_JOB`
        * :const:`STUDENT`

        :return: None
        """

        msg = ''
        if self.id == NO_JOB:
            self.set_no_job()

        elif (self.id == STANDARD_JOB):
            self.set_standard_job()

        elif (self.id == STUDENT):
            self.set_student()

        else:
            # the error message if the job-identifier is an invalid choice
            msg = msg + 'ERROR! %d is in INVALID choice for id_job in set_job_preset()!\n' % self.id
            print(msg)

        return

    def set_no_job(self):

        """
        Set the Occupation to having no job.

        :param occupation.Occupation job: the job of which to set the attributes

        :return: None
        """

        self.id = NO_JOB

        # set the job category
        self.category = NO_TIME

        self.commute_to_work_dt_mean = 0
        self.commute_to_work_dt_std = 0
        self.commute_to_work_dt = 0

        self.commute_from_work_dt_mean = 0
        self.commute_from_work_dt_std = 0
        self.commute_from_work_dt = 0

        self.set_commute_distribution()

        # the start time of the job [time of day, minutes]
        self.t_start_mean = 0
        self.t_start_std = 0
        self.t_start = 0

        self.t_end_mean = 0
        self.t_end_std = 0
        self.t_end = 0

        self.set_work_distribution()

        # for easy recall
        self.commute_to_work_start = 0

        # set job duration
        self.dt = 0

        # set the flag indicating whether or not the job starts and end on the same day
        self.is_same_day = True

        # set work days to none
        self.work_days = ()

        # set to no wage
        self.wage = 0.0

        # set employment flag
        self.is_employed = False

        # set the location to home
        self.location = location.Location(location.NORTH, location.HOME)

        return

    def set_standard_job(self):

        """
        This function sets the Occupation to the standard job.

        * has fixed shift of 9:00 - 17:00
        * Monday through Friday 
        * wage of $40,000 
        * 30 minute commute to work
        * 60 minute commute from work

        :param occupation.Occupation job: the job of which to set the attributes

        :return: None
        """

        DAY_2_MIN       = temporal.DAY_2_MIN

        self.id         = STANDARD_JOB

        # set the occupation type to a fixed shift
        self.category   = FIXED_SHIFT

        # the start time of the job [time of day, minutes]
        self.t_start_mean   = START_MEAN
        self.t_start_std    = START_STD
        self.t_start        = self.t_start_mean

        self.t_end_mean = END_MEAN
        self.t_end_std  = END_STD
        self.t_end      = self.t_end_mean

        self.f_work_start   = None
        self.f_work_end     = None

        self.set_work_distribution()

        # the commute time [minutes]
        # commute duration to and from work
        self.commute_to_work_dt_mean    = COMMUTE_TO_WORK_DT_MEAN
        self.commute_to_work_dt_std     = COMMUTE_TO_WORK_DT_STD
        self.commute_to_work_dt         = self.commute_to_work_dt_mean

        self.commute_from_work_dt_mean  = COMMUTE_FROM_WORK_DT_MEAN
        self.commute_from_work_dt_std   = COMMUTE_FROM_WORK_DT_STD
        self.commute_from_work_dt       = self.commute_from_work_dt_mean

        # for easy recall
        self.commute_to_work_start = (self.t_start_mean - self.commute_to_work_dt_mean + DAY_2_MIN ) % DAY_2_MIN

        # set the probability distribution for commute to work and commute from work
        self.set_commute_distribution()

        # occupation duration 8:00 hours
        self.dt             = (self.t_end - self.t_start) % DAY_2_MIN

        # set the flag indicating that the job starts and ends on the same day
        self.set_is_same_day()

        # set the work days
        self.work_days = (temporal.MONDAY, temporal.TUESDAY, temporal.WEDNESDAY, temporal.THURSDAY, temporal.FRIDAY)

        # set the wage in U.S. dollars
        self.wage = 40000.0

        # set the is_employed flag
        self.is_employed = True

        # set the job location
        self.location = location.Location(location.NORTH, location.OFF_SITE)

        return

    def set_student(self):

        """
        This function sets the Occupation to the standard job.

        * Fixed shift of 8:00 - 15:00
        * Monday through Friday 
        * wage of $0
        * 30 minute commute to school
        * 60 minute commute from school

        :param occupation.Occupation job: the job of which to set the attributes

        :return: None
        """

        DAY_2_MIN       = temporal.DAY_2_MIN

        self.id         = STUDENT

        # set the occupation type to a fixed shift
        self.category   = FIXED_SHIFT

        # the start time of the job [time of day, minutes]
        self.t_start_mean   = START_MEAN
        self.t_start_std    = START_STD
        self.t_start        = self.t_start_mean

        self.t_end_mean = END_MEAN
        self.t_end_std  = END_STD
        self.t_end      = self.t_end_mean

        self.f_work_start   = None
        self.f_work_end     = None

        self.set_work_distribution()

        # the commute time [minutes]
        # commute duration to and from work
        self.commute_to_work_dt_mean    = COMMUTE_TO_WORK_DT_MEAN
        self.commute_to_work_dt_std     = COMMUTE_TO_WORK_DT_STD
        self.commute_to_work_dt         = self.commute_to_work_dt_mean

        self.commute_from_work_dt_mean  = COMMUTE_FROM_WORK_DT_MEAN
        self.commute_from_work_dt_std   = COMMUTE_FROM_WORK_DT_STD
        self.commute_from_work_dt       = self.commute_from_work_dt_mean

        # for easy recall
        self.commute_to_work_start = (self.t_start_mean - self.commute_to_work_dt_mean + DAY_2_MIN ) % DAY_2_MIN

        # set the probability distribution for commute to work and commute from work
        self.set_commute_distribution()

        # occupation duration 8:00 hours
        self.dt             = (self.t_end - self.t_start) % DAY_2_MIN

        # set the flag indicating that the job starts and ends on the same day
        self.set_is_same_day()

        # set the work days
        self.work_days = (temporal.MONDAY, temporal.TUESDAY, temporal.WEDNESDAY, temporal.THURSDAY, temporal.FRIDAY)

        # set the wage in U.S. dollars
        self.wage = 0.00

        # set the is_employed flag
        self.is_employed = True

        # set the job location
        self.location = location.Location(location.NORTH, location.OFF_SITE)

        return

    def set_work_distribution(self):

        """
        This function sets the following distributions for work:
        
        * work start time distribution
        * work end time distribution
        
        :return: None 
        """

        self.f_work_start   = mg.set_distribution(-self.work_start_trunc, self.work_start_trunc, \
                                                  self.t_start_mean, self.t_start_std)

        self.f_work_end     = mg.set_distribution(-self.work_end_trunc, self.work_end_trunc, \
                                                  self.t_end_mean, self.t_end_std)
        return

    def toString(self):

        """
        Represents the Occupation object as a string

        :return msg: The representation of the Occupation object as a string
        :rtype: str
        """

        msg = ''

        # the occupation identifier
        msg = msg + 'Job ID:\t%s\n' % self.print_id()

        # the occupation category
        msg = msg + 'Category:\t%s\n' % self.print_category()

        # the wage
        msg = msg + 'Wage:\t$ %.2f\n' % self.wage

        # the current job start day flag
        msg = msg + 'Current Start Day:\t%d\n' % self.day_start

        # the start time in military time
        msg = msg + 'Start time:\t' + temporal.print_military_time( self.t_start ) + '\n'

        # the duration in military time
        msg = msg + 'Duration:\t' + temporal.print_military_time( self.dt ) + '\n'

        # the end time in military time
        msg = msg + 'End time:\t' + temporal.print_military_time( self.t_end ) + '\n'

        # the commute duration in military time
        msg = msg + 'Commute to work time:\t' + temporal.print_military_time(self.commute_to_work_dt_mean) + '\n'
        msg = msg + 'Commute from work time:\t' + temporal.print_military_time(self.commute_from_work_dt_mean) + '\n'

        # the days of the week that the job starts
        msg = msg + 'Work days:\t' + str( self.work_days ) + '\n'

        # whether or not the job starts and end on the same day
        msg = msg + 'Start and End on the same day?:\t' + str( self.is_same_day ) + '\n'

        # a flag indicating employment
        msg = msg + 'Is employed?:\t' + str( self.is_employed) + '\n'

        # the location
        msg = msg + 'Location\n'
        msg = msg + self.location.toString()
        
        return msg

    def update_commute_from_work_dt(self):

        """
        Pull a commute from work duration from the respective distribution.
        
        :return: None 
        """

        # sample the duration
        dt                          = self.f_commute_from_work_dt(1)[0]
        self.commute_from_work_dt   = np.round(dt).astype(int)

        return

    def update_commute_to_work_dt(self):

        """
        Pull a commute to work duration from the respective distribution. Also, update the commute to work \
        start time place holder.
        
        :return: None 
        """

        # sample the duration
        dt                          = self.f_commute_to_work_dt(1)[0]
        self.commute_to_work_dt     = np.round(dt).astype(int)

        # update the commute to work start time place holder
        self.update_commute_to_work_start()

        return

    def update_commute_to_work_start(self):

        """
        Update the commute to work start time.
        
        :return: None 
        """

        # the amount of minutes in 1 day
        DAY_2_MIN   = temporal.DAY_2_MIN

        # this is just a parameter for ease of use
        self.commute_to_work_start = (self.t_start - self.commute_to_work_dt + DAY_2_MIN) % DAY_2_MIN

        return

    def update_work_start(self):

        """
        Update the work start time.
        
        :return: None 
        """

        # the amount of minutes in 1 day
        DAY_2_MIN       = temporal.DAY_2_MIN

        # sample the work start time
        t               = self.f_work_start(1)[0]
        self.t_start    = np.round(t).astype(int) % DAY_2_MIN

        # update the work duration
        self.update_work_dt()

        # update the commute to work start time place holder
        self.update_commute_to_work_start()

        # update the day to start
        self.day_start += 1

        return

    def update_work_dt(self):

        """
        Update the work duration
        
        :return: None
        """

        DAY_2_MIN = temporal.DAY_2_MIN

        self.dt = (self.t_end - self.t_start + 1) % DAY_2_MIN

        return

    def update_work_end(self):

        """
        Update the work end time.
        
        :return: None 
        """

        # the amount of minutes in 1 day
        DAY_2_MIN   = temporal.DAY_2_MIN

        # sample the work end time
        t           = self.f_work_end(1)[0]
        self.t_end  = np.round(t).astype(int) % DAY_2_MIN

        # update the work duration
        self.update_work_dt()

        return


# --------------------------------------------------------------
# OUTSIDE of class Occupation definition.
# Module functions
# --------------------------------------------------------------


def is_work_time(clock, job, is_commute_to_work=False):

    """
    Given a clock and a job, this function says whether the clock's time corresponds \
    to a time to be at work **or** a time to commute to work.

    If :math:`\\Delta{t} > 0`, it indicates when it's time to commute to work.

    :param temporal.Temporal clock: the time
    :param occupation.Occupation job: the job to inquiry
    :param bool is_commute_to_work: a flag indicating whether we are interested in calculating if it is \
                            time to commute to work

    :return: a flag indicating if it is / is not work time (or commute time if is_commute_to_work is True)
    :rtype: bool
    """

    # if we are commuting to work, set the job start time to be the commute start time
    if (is_commute_to_work):

        # do calculations for the commute time

        # the original start time
        t_start = job.t_start

        # the start time to be the time the commute begins
        job.t_start = job.commute_to_work_start

    # find out if it's time to work
    is_time = is_work_time_help(clock, job)

    # restore the commute to work start time
    if is_commute_to_work:

        # reset the value
        job.t_start = t_start


    return is_time

def is_work_time_help(clock, job):

    """
    Given a clock and a job, this function says whether the clock's time corresponds to
    a time at work.

    :param temporal.Temporal clock: the time
    :param occupation.Occupation job: the job to inquiry

    :return: is_work_time: a flag indicating if the time (clock) corresponds to a work time
    :rtype: bool
    """

    # set the flag to output to False
    is_work_time = False

    # store the time of day [minutes]
    time_of_day = clock.time_of_day

    # store the day of the week
    today = clock.day_of_week

    # store the next day of the week
    tomorrow  = (today + 1) % 7

    # store the previous day of the week
    yesterday = (today + 6) % 7

    # find out if it is time to be at work, if employed
    if ( job.is_employed ):

        # supposed to be a workday when not on summer vacation
        check_work_day  = ( not job.is_summer_vacation(clock.week_of_year) ) and job.is_same_day

        if check_work_day:

            # set is_work_time to true if today is a workday and the time of day is between
            # the start time and the end time
            if (today in job.work_days) and (clock.day >= job.day_start) and (time_of_day >= job.t_start) \
                    and (time_of_day < job.t_end):

                is_work_time = True

    # return whether or not is is time for work
    return is_work_time

def set_grave_shift(job):

    """
    This function sets the Occupation to a grave shift.

    * shift job from  22:00 to 6:00 
    * Monday through Friday
    * 30 minute commute to work
    * 60 minute commute from work
    * wage of $40,0000.

    :param occupation.Occupation job: the job of which to set the attributes

    :return: None
    """

    HOUR_2_MIN      = temporal.HOUR_2_MIN

    # identifier
    job.id          = GRAVE_SHIFT

    # set the job category
    job.category    = FIXED_SHIFT

    # set the start time to be 22:00
    job.t_start     = 22 * HOUR_2_MIN

    # set the job duration
    job.dt          = 8 * HOUR_2_MIN

    # set the end time
    job.set_t_end()

    # set the flag indicating whether or not the job starts and ends on the same day
    job.set_is_same_day()

    # set the work days
    job.work_days = (temporal.MONDAY, temporal.TUESDAY, temporal.WEDNESDAY, temporal.THURSDAY, temporal.FRIDAY)

    # set the wage in U.S dollars
    job.wage = 40000.0

    # set the employment flag
    job.is_employed = True

    # set the location
    job.location = location.Location(location.NORTH, location.OFF_SITE)

    # set the commute
    job.commute_to_work_dt_mean     = COMMUTE_TO_WORK_DT_MEAN
    job.commute_from_work_dt_mean   = COMMUTE_TO_WORK_DT_MEAN

    job.commute_to_work_dt      = job.commute_to_work_dt_mean
    job.commute_from_work_dt    = job.commute_from_work_dt_mean

    job.set_commute_distribution()
    job.set_work_distribution()
    return
    
def set_no_job(job):

    """
    Set the Occupation to having no job.

    :param occupation.Occupation job: the job of which to set the attributes

    :return: None
    """

    # the job identifier
    job.id          = NO_JOB

    # set the job category
    job.category    = NO_TIME

    # set start time
    job.t_start = 0

    # set job duration
    job.dt = 0

    # set end time
    job.set_t_end()

    # set the flag indicating whether or not the job starts and end on the same day
    job.set_is_same_day()

    # set work days to none
    job.work_days = ()

    # set to no wage
    job.wage = 0.0

    # set employment flag
    job.is_employed = False

    # set the location to home
    job.location = location.Location(location.NORTH, location.HOME)

    # set to no commute
    job.commute_to_work_dt_mean     = 0
    job.commute_from_work_dt_mean   = 0

    job.commute_to_work_dt   = job.commute_to_work_dt_mean
    job.commute_from_work_dt = job.commute_from_work_dt_mean

    job.set_commute_distribution()
    job.set_work_distribution()

    return
    
def set_standard_job(job):

    """
    This function sets the Occupation to the standard job.

    * fixed shift of 9:00 - 17:00
    * Monday through Friday 
    * wage $40,000 
    * 30 minute commute to work
    * 60 minute commute from work

    :param occupation.Occupation job: the job of which to set the attributes

    :return: None
    """

    DAY_2_MIN, HOUR_2_MIN   = temporal.DAY_2_MIN, temporal.HOUR_2_MIN

    # identifier
    job.id          = STANDARD_JOB

    # set the occupation type to a fixed shift
    job.category    = FIXED_SHIFT

    # start at 9:00
    job.t_start     = 9 * HOUR_2_MIN
    job.t_end       = 17 * HOUR_2_MIN

    # occupation duration 8:00 hours
    job.dt = (job.t_end - job.t_start) % DAY_2_MIN

    # set the end time
    job.set_t_end()

    # set the flag indicating that the job starts and ends on the same day
    job.set_is_same_day()

    # set the work days
    job.work_days = (temporal.MONDAY, temporal.TUESDAY, temporal.WEDNESDAY, temporal.THURSDAY, temporal.FRIDAY)

    # set the wage in U.S. dollars
    job.wage = 40000.0

    # set the is_employed flag
    job.is_employed = True

    # set the job location
    job.location = location.Location(location.NORTH, location.OFF_SITE)

    # set the commute
    job.commute_to_work_dt_mean     = COMMUTE_TO_WORK_DT_MEAN
    job.commute_from_work_dt_mean   = COMMUTE_TO_WORK_DT_MEAN

    job.commute_to_work_dt      = job.commute_to_work_dt_mean
    job.commute_from_work_dt    = job.commute_from_work_dt_mean

    job.set_commute_distribution()
    job.set_work_distribution()

    return

def set_student(job):

    """
    This function sets a job to the preset values of student occupation.

    * fixed shift of 08:00 - 15:00
    * Monday through Friday
    * wage of $0
    * 30 minute commute to school
    * 60 minute commute from school
    
    :param occupation.Occupation job: the job to set
     
    :return: None 
    """

    # the number of minutes in 1 day, the number of minutes in 1 hour
    DAY_2_MIN, HOUR_2_MIN = temporal.DAY_2_MIN, temporal.HOUR_2_MIN

    # job identifier
    job.id          = STUDENT

    # set the occupation type to a fixed shift
    job.category    = FIXED_SHIFT

    job.t_start     = START_MEAN_SCHOOl
    job.t_end       = END_MEAN_SCHOOL

    # occupation duration 8:00 hours
    job.dt = (job.t_end - job.t_start) % DAY_2_MIN

    # set the end time
    job.set_t_end()

    # set the flag indicating that the job starts and ends on the same day
    job.set_is_same_day()

    # set the work days
    job.work_days = (temporal.MONDAY, temporal.TUESDAY, temporal.WEDNESDAY, temporal.THURSDAY, temporal.FRIDAY)

    # set the wage in U.S. dollars
    job.wage = 0.0

    # set the is_employed flag
    job.is_employed = True

    # set the job location
    job.location = location.Location(location.NORTH, location.OFF_SITE)

    # set the commute
    job.commute_to_work_dt_mean     = COMMUTE_TO_WORK_DT_MEAN
    job.commute_from_work_dt_mean   = COMMUTE_TO_WORK_DT_MEAN

    job.commute_to_work_dt          = job.commute_to_work_dt_mean
    job.commute_from_work_dt        = job.commute_from_work_dt_mean

    job.set_commute_distribution()
    job.set_work_distribution()

    return

