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
This file contains data from the Consolidated Human Activity Database (CHAD). This module contains constants \
necessary to access various files in the CHAD.

This module contains the following classes:

#. :class:`chad.CHAD`
#. :class:`chad.CHAD_RAW`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# general math capability
import numpy as np

# dataframe capability
import pandas as pd

# add date/time and zipfile capabilities
import datetime, zipfile

# ABMHAP modules
import my_globals as mg
import social, temporal

# ===============================================
# constants
# ===============================================

# The directory the compressed CHAD data is in
FDIR_DATA       = '..\\data'

# this is where the uncompressed data lies
FDIR_DATA_LARGE = '..\\data_large'

#
# for the uncompressed files
#

# the file directories
FDIR_DEMOGRAPHY_LARGE       = FDIR_DATA_LARGE + '\\demography'

FDIR_ALL_LARGE              = FDIR_DEMOGRAPHY_LARGE + '\\all'
FDIR_ADULT_LARGE            = FDIR_DEMOGRAPHY_LARGE + '\\adult'
FDIR_ADULT_WORK_LARGE       = FDIR_DEMOGRAPHY_LARGE + '\\adult_work'
FDIR_ADULT_NON_WORK_LARGE   = FDIR_DEMOGRAPHY_LARGE + '\\adult_non_work'
FDIR_CHILD_SCHOOL_LARGE     = FDIR_DEMOGRAPHY_LARGE + '\\child_school'
FDIR_CHILD_YOUNG_LARGE      = FDIR_DEMOGRAPHY_LARGE + '\\child_young'

#
# for the compressed files
#
FDIR_DEMOGRAPHY             = FDIR_DATA + '\\demography'

FNAME_ALL                   = FDIR_DEMOGRAPHY + '\\all.zip'
FNAME_ADULT                 = FDIR_DEMOGRAPHY + '\\adult.zip'
FNAME_ADULT_NON_WORK        = FDIR_DEMOGRAPHY + '\\adult_non_work.zip'
FNAME_ADULT_WORK            = FDIR_DEMOGRAPHY + '\\adult_work.zip'
FNAME_CHILD_SCHOOL          = FDIR_DEMOGRAPHY + '\\child_school.zip'
FNAME_CHILD_YOUNG           = FDIR_DEMOGRAPHY + '\\child_young.zip'

# file name for the CHAD data (questionnaire and events data)
FNAME_CHAD                  = FDIR_DATA + '\\chad.zip'

# file name for the CHAD activity data in zip files
FNAME_COMMUTE_FROM_WORK     = FDIR_DATA_LARGE + '\\commute_from_work.zip'
FNAME_COMMUTE_TO_WORK       = FDIR_DATA_LARGE + '\\commute_to_work.zip'

FNAME_EAT_BREAKFAST         = FDIR_DATA_LARGE + '\\eat_breakfast.zip'
FNAME_EAT_DINNER            = FDIR_DATA_LARGE + '\\eat_dinner.zip'
FNAME_EAT_LUNCH             = FDIR_DATA_LARGE + '\\eat_lunch.zip'

FNAME_EDUCATION             = FDIR_DATA_LARGE + '\\education.zip'
FNAME_SLEEP                 = FDIR_DATA_LARGE + '\\sleep.zip'
FNAME_WORK                  = FDIR_DATA_LARGE + '\\work.zip'

FNAME_OMNI          = { mg.KEY_COMMUTE_FROM_WORK: FNAME_COMMUTE_FROM_WORK,
                        mg.KEY_COMMUTE_TO_WORK: FNAME_COMMUTE_TO_WORK,
                        mg.KEY_EAT_BREAKFAST: FNAME_EAT_BREAKFAST,
                        mg.KEY_EAT_DINNER: FNAME_EAT_DINNER,
                        mg.KEY_EAT_LUNCH: FNAME_EAT_LUNCH,
                        mg.KEY_SLEEP: FNAME_SLEEP,
                        mg.KEY_WORK: FNAME_WORK,
                        }

# the CHAD raw data files within FNAME_CHAD
FNAME_EVENTS    = 'events_071413_mod.csv'
FNAME_QUEST     = 'quest_032913_mod.csv'

#
# file names for statistics.
# they are the the moments (means and standard deviations) of the duration and start time data
# for each person who has longitudinal data
#

# the file names for the CHAD activity-moments data
START   = 1
END     = 2
DT      = 3
RECORD  = 4

FNAME_STATS_DEFAULT = ('stats_dt.csv', 'stats_start.csv')

# file name for statistics from CHAD about longitudinal patterns for commuting to work
FNAME_STATS_COMMUTE_TO_WORK     = {START: 'longitude/commute_to_work/stats_start.csv',
                                   END: 'longitude/commute_to_work/stats_end.csv',
                                   DT: 'longitude/commute_to_work/stats_dt.csv',
                                   RECORD: 'longitude/commute_to_work/record.csv',}

# file name for statistics from CHAD about longitudinal patterns for commuting from work
FNAME_STATS_COMMUTE_FROM_WORK   = {START: 'longitude/commute_from_work/stats_start.csv',
                                   END: 'longitude/commute_from_work/stats_end.csv',
                                   DT: 'longitude/commute_from_work/stats_dt.csv',
                                   RECORD: 'longitude/commute_from_work/record.csv',}

# file name for statistics from CHAD about longitudinal patterns for eating breakfast
FNAME_STATS_EAT_BREAKFAST       = {START: 'longitude/eat_breakfast/stats_start.csv',
                                   END: 'longitude/eat_breakfast/stats_end.csv',
                                   DT: 'longitude/eat_breakfast/stats_dt.csv',
                                   RECORD: 'longitude/eat_breakfast/record.csv',}

# file name for statistics from CHAD about longitudinal patterns for eating dinner
FNAME_STATS_EAT_DINNER          = {START: 'longitude/eat_dinner/stats_start.csv',
                                   END: 'longitude/eat_dinner/stats_end.csv',
                                   DT: 'longitude/eat_dinner/stats_dt.csv',
                                   RECORD: 'longitude/eat_dinner/record.csv',}

# file name for statistics from CHAD about longitudinal patterns for eating lunch
FNAME_STATS_EAT_LUNCH           = {START: 'longitude/eat_lunch/stats_start.csv',
                                   END: 'longitude/eat_lunch/stats_end.csv',
                                   DT: 'longitude/eat_lunch/stats_dt.csv',
                                   RECORD: 'longitude/eat_lunch/record.csv',}

# file name for statistics from CHAD about longitudinal patterns for sleeping
FNAME_STATS_SLEEP               = {START: 'longitude/sleep/all/stats_start.csv',
                                   END: 'longitude/sleep/all/stats_end.csv',
                                   DT: 'longitude/sleep/all/stats_dt.csv',
                                   RECORD: 'longitude/sleep/all/record.csv',}

# file name for statistics from CHAD about longitudinal patterns for working
FNAME_STATS_WORK                = {START: 'longitude/work/stats_start.csv',
                                   END: 'longitude/work/stats_end.csv',
                                   DT: 'longitude/work/stats_dt.csv',
                                   RECORD: 'longitude/work/record.csv',}

# file name for statistics from CHAD about longitudinal patterns for all of the activities
FNAME_STATS_OMNI = { mg.KEY_COMMUTE_FROM_WORK: FNAME_STATS_COMMUTE_FROM_WORK,
                     mg.KEY_COMMUTE_TO_WORK: FNAME_STATS_COMMUTE_TO_WORK,
                     mg.KEY_EAT_BREAKFAST: FNAME_STATS_EAT_BREAKFAST,
                     mg.KEY_EAT_DINNER: FNAME_STATS_EAT_DINNER,
                     mg.KEY_EAT_LUNCH: FNAME_STATS_EAT_LUNCH,
                     mg.KEY_SLEEP: FNAME_STATS_SLEEP,
                     mg.KEY_WORK: FNAME_STATS_WORK,
                     }

# filenames for CHAD records of  for longitudinal data for commuting from work
FNAME_RECORD_COMMUTE_FROM_WORK  = ('longitude/commute_from_work/record.csv',)

# filenames for CHAD records of  for longitudinal data for commuting to work
FNAME_RECORD_COMMUTE_TO_WORK    = ('longitude/commute_to_work/record.csv',)

# filenames for CHAD records of  for longitudinal data for eating breakfast
FNAME_RECORD_EAT_BREAKFAST      = ('longitude/eat_breakfast/record.csv',)

# filenames for CHAD records of  for longitudinal data for eating dinner
FNAME_RECORD_EAT_DINNER         = ('longitude/eat_dinner/record.csv',)

# filenames for CHAD records of  for longitudinal data for eating lunch
FNAME_RECORD_EAT_LUNCH          = ('longitude/eat_lunch/record.csv',)

# filenames for CHAD records of  for longitudinal data for sleeping
FNAME_RECORD_SLEEP              = ('longitude/sleep/all/record.csv',)

# filenames for CHAD records of  for longitudinal data for working
FNAME_RECORD_WORK               = ('longitude/work/record.csv',)

# filenames for CHAD records of  for longitudinal data for all of the activities
FNAME_RECORD_OMNI = { mg.KEY_COMMUTE_FROM_WORK: FNAME_RECORD_COMMUTE_FROM_WORK,
                      mg.KEY_COMMUTE_TO_WORK: FNAME_RECORD_COMMUTE_TO_WORK,
                      mg.KEY_EAT_BREAKFAST: FNAME_RECORD_EAT_BREAKFAST,
                      mg.KEY_EAT_DINNER: FNAME_RECORD_EAT_DINNER,
                      mg.KEY_EAT_LUNCH: FNAME_RECORD_EAT_LUNCH,
                      mg.KEY_SLEEP: FNAME_RECORD_SLEEP,
                      mg.KEY_WORK: FNAME_RECORD_WORK,}

# the columns from the raw CHAD events data to keep
EVENTS_RAW_COLNAMES = ['CHADID', 'PID', 'starttime', 'endtime', 'duration', 'act', 'date']

# the columns from the CHAD events data to keep
EVENTS_COLNAMES     = ['CHADID', 'PID', 'start', 'end', 'dt', 'act', 'date']

# the columns from the raw CHAD questionnaire data to keep
QUEST_COLNAMES      = ['CHADID', 'PID', 'rawid', 'daynum', 'totaldays', 'month', 'daymonth', 'year', 'dayofweek',
                       'wdwe', 'weekend', 'age', 'gender', 'date', 'fulltime', 'employed']

# activity codes for 'X and 'U' found in the raw CHAD data
ACT_X = -1
ACT_U = -2

# ===============================================
# constants based on the CHAD data
# ===============================================

# the minimum and maximum duration of sleep considered [hours]
SLEEP_DT_MIN, SLEEP_DT_MAX          = 4, 12

# the minimum and maximum start time of sleep considered [hours]
SLEEP_START_MIN, SLEEP_START_MAX    = -4, 2 #(periodic time, regular time)

# the minimum and maximum end time of sleep considered [hours]
SLEEP_END_MIN, SLEEP_END_MAX        = 4, 11

# work start time min [hours]
WORK_START_MIN      = 4

# the minimum and maximum duration for the mean duration for a meal
MEAL_DT_MIN, MEAL_DT_MAX = 5./60, 1.5

# the minimum and maximum duration for the mean duration of breakfast
BREAKFAST_DT_MIN, BREAKFAST_DT_MAX  = MEAL_DT_MIN, MEAL_DT_MAX

# the minimum and maximum duration for the mean duration of lunch
LUNCH_DT_MIN, LUNCH_DT_MAX          = MEAL_DT_MIN, MEAL_DT_MAX

# the minimum and maximum duration for the mean duration of dinner
DINNER_DT_MIN, DINNER_DT_MAX        = MEAL_DT_MIN, MEAL_DT_MAX

# lunch start time minimum [hours]
LUNCH_START_MIN     = 11

# dinner start time minimum [hours]
DINNER_START_MIN    = 15.5

# breakfast start min
BREAKFAST_START_MIN = 3

# breakfast end time maximum
BREAKFAST_END_MAX   = LUNCH_START_MIN  - 1./60

# lunch end time maximum
LUNCH_END_MAX       = DINNER_START_MIN - 1./60

# dinner end time maximum
DINNER_END_MAX      = 22

# the commute to school start time minimum and maximum
COMMUTE_TO_SCHOOL_START_MIN     = 5
COMMUTE_TO_SCHOOL_START_MAX     = 10

# the commute to school end time maximum
COMMUTE_TO_SCHOOL_END_MAX       = 11

# the commute from school start time minimum and maximum
COMMUTE_FROM_SCHOOL_START_MIN   = 13
COMMUTE_FROM_SCHOOL_START_MAX   = 17

# the commute from school end time maximum
COMMUTE_FROM_SCHOOL_END_MAX     = 18

# commute to work start time minimum and maximum
COMMUTE_TO_WORK_START_MIN       = 3
COMMUTE_TO_WORK_START_MAX       = 12

# commute to work end time maximum
COMMUTE_TO_WORK_END_MAX         = 13

# commute from work start time minimum and maximum
COMMUTE_FROM_WORK_START_MIN     = 14
COMMUTE_FROM_WORK_START_MAX     = 20

# commute form work end time maximum
COMMUTE_FROM_WORK_END_MAX       = 22

# ===============================================
# class CHAD
# ===============================================

class CHAD(object):

    """
    This object is in charge of accessing the compressed data files from CHAD.

    :param str fname: the directory to the respective compressed data files
    :param str mode: the mode (read, write, or both) the zipfile will work under

    :ivar str fname_zip: the directory to the respective compressed data file (.zip)
    :ivar int mode: the mode (read, write, or both) the zipfile will work under
    :ivar zipfile.Zipfile z: object that holds the zipfile information

    """
    def __init__(self, fname, mode='r'):

        # the directory of the zip file
        self.fname_zip = fname

        # the mode (reading, writing) of accessing the zipfile
        self.mode   = mode

        # access the zip file
        self.z = zipfile.ZipFile(self.fname_zip, mode=mode)

        return

    def activity_times(self, df, act_codes):

        """
        This function finds the  activity data (given by act_codes) in the dataframe df.

        :param pandas.core.frame.DataFrame df: events data
        :param list act_codes: the list of CHAD activity codes specifying 1 general activity
        :return: the activity data for the selected activity codes 
        :rtype: pandas.core.frame.DataFrame
        """

        # find the indices of activities in act_list
        idx = [ (x in act_codes) for x in df.act.values ]

        # the number of corresponding data entries found
        N = np.sum(idx)

        # empty data frame
        result = pd.DataFrame()

        if (N > 0):

            # get the data of the select activities
            temp = df[idx]

            # group activity data by CHADID
            gb = temp.groupby('CHADID')

            # merge adjacent time periods
            result = [ self.sum_time( gb.get_group(u) ) for u in temp.CHADID.unique() ]
            result = pd.concat(result)

        return result

    def get_data(self, fname):

        """
        Gets the decompressed data from the given file

        :param str fname: the name of the file to decompressed

        :return data: the data
        :rtype: pandas.core.frame.DataFrame
        """

        # store data in data frame
        data = pd.read_csv( self.z.open(fname) )

        return data

    def sum_time(self, df):

        """
        This function merges two similar adjacent activities into one activity. This function is used normally for \
        the CHAD events data.
        
        :param pandas.core.frame.DataFrame df: the dataframe corresponding to a specific CHAD identifier
        :return: the dataframe where adjacent activities are merged into one activity
        :rtype: pandas.core.frame.DataFrame
        """

        # get the start values except the first entry
        temp_start  = df.start.values[1:]
        # get the end values except the last entry
        temp_end    = df.end.values[:-1]

        # find indices where the start times and end times are not equal. This indicates that adjacent events are \
        # two different events (not contiguous)
        change  = temp_start != temp_end

        # store the start time, end time for different/ non-contiguous activities
        start   = [df.start.iloc[0]] + temp_start[change].tolist()
        end     = temp_end[change].tolist() + [df.end.iloc[-1]]

        # the duration for the activity
        dt      = (np.array(end) - np.array(start) + 24) % 24

        # the number of entries for different activities
        N = len(start)

        # the CHAD identifier
        chadid  = [df.CHADID.iloc[0]] * N

        # the person identifier
        pid     = [df.PID.iloc[0]] * N

        # the activity code
        act     = [df.act.iloc[0]] * N

        # the date
        date    = [df.date.iloc[0]] * N

        # store the data for the data frame in a a dictionary
        d       = {'CHADID': chadid, 'PID': pid, 'start': start, 'end': end, 'dt': dt, 'act': act, 'date': date}

        # store the data in a data frame with the appropriate column order
        result  = pd.DataFrame(d)[EVENTS_COLNAMES]

        return result

    def toString(self):

        """
        Represent the contents of the compressed file.

        :return: a string representation of the CHAD object
        :rtype: string
        """

        msg = ''

        msg = msg + 'zipfile name:\t' + self.fname_zip + '\n'
        msg = msg + 'contents of zip file\n'
        msg = msg + str( self.z.namelist() )+ '\n'

        return msg

# ===============================================
# class CHAD_RAW
# ===============================================

class CHAD_RAW(CHAD):

    """
    This is a specific instance of :class:`chad.CHAD` that is made for accessing the raw \
    CHAD data for accessing the questionnaire database and the events database.

    :param int min_age: the minimum age [years] for the CHAD data age range
    :param int max_age: the maximum age [years] for the CHAD data age range
    
    :ivar pandas.core.frame.DataFrame quest: the CHAD questionnaire data 
    :ivar pandas.core.frame.DataFrame events: the CHAD events data    
    """

    def __init__(self, min_age=social.ADULT_AGE, max_age=social.MAX_AGE):

        # call the parent class constructor
        CHAD.__init__(self, fname = FNAME_CHAD, mode='r')

        # load the CHAD questionnaire data
        self.quest  = self.get_quest()

        # load the CHAD events data
        self.events = self.get_events()

        # filter by age
        self.get_data_by_age(min_age, max_age)

        # clean the events data
        self.clean_data()

        return

    def clean_data(self):

        """
        This function cleans the data from the loaded CHAD .csv files for the format used for the ABM.
        
        #. clean events
        #. clean dates
        #. set dates
        
        :return: None 
        """

        # clean the events data
        self.clean_events()

        # only keep data with proper dates
        self.clean_dates()

        # convert the dates strings into datetime objects
        self.set_dates()

        return

    def clean_dates(self):

        """
        This function is needed in order to remove data where there are no dates from the dataframes that \
        represent the CHAD questionnaire data and the CHAD events data.

        :return: None
        """

        # find indices where the date is a string (ie, not NaN)
        f = lambda x: np.array( [isinstance(y, str) for y in x] )

        # the indices of dates for the questionnaire and events
        idx_q   = f(self.quest.date.values)
        idx_e   = f(self.events.date.values)

        # update the CHAD questionnaire data
        self.quest  = self.quest[idx_q]

        # update the CHAD events data
        self.events = self.events[idx_e]

        return

    def clean_events(self):

        """
        This cleans the time information in the CHAD events data.
        
        :return: None
        """

        # handle the time information
        self.set_times()

        return

    def convert_activity_code(self, x):

        """
        This function converts the activity code from a string into an integer. It also converts 'X' \
        and 'U' into a numerical value.

        :param string x: the activity code that needs to be converted
        :return: None
        """

        if x == 'X':
            y = ACT_X
        elif( x == 'U'):
            y = ACT_U
        else:
            y = int(x)

        return y

    def convert_military_to_decimal_time(self, x):

        """
        This function converts military time [00 00 - 23 59] to decimal time [0.0 - 24).
        
        :param int x: an integer representation of the military time where 09:00 is represented by 0900.
        
        :return: the time converted into decimal time
        :rtype: float
        """

        # the 1 hour in terms of minutes
        HOUR_2_MIN  = temporal.HOUR_2_MIN

        # amount of hours
        h = x // 100

        # amount of minutes in terms of fractional hours
        m = ( x - h * 100 ) / HOUR_2_MIN

        # the decimal time
        decimal_time = h + m

        return decimal_time

    def get_data_by_age(self, min_age, max_age):

        """
        This function samples the CHAD data by age via the age range inputs.
        
        :param int min_age: the minimum age [years]
        :param int max_age: the maximum age [years]
        :return: None
        """

        # the age
        age = self.quest.age.values

        # the indices
        idx = (age >= min_age) * (age <= max_age)

        # the unique PIDs of people above a certain age
        pid = self.quest.PID[ idx ].unique()

        # group the events by PID
        gb = self.events.groupby('PID')

        # collect the data frames for the events
        y = [gb.get_group(x) for x in pid]

        # set the events and questionnaire data
        self.events = pd.concat(y)
        self.quest  = self.quest[idx]

        return

    def get_events(self):

        """
        This function gets the raw CHAD events data and returns it in the appropriate column order.
        
        :return: the CHAD events data 
        :rtype: pandas.core.frame.DataFrame
        """
        df = self.get_events_raw()

        return df[EVENTS_RAW_COLNAMES]

    def get_events_raw(self):

        """
        This function returns a data frame of the raw events data.
        
        :return data: the raw CHAD events data
        :rtype: pandas.core.frame.DataFrame
        """

        # the raw CHAD events data
        df = pd.read_csv(self.z.open(FNAME_EVENTS), encoding='ISO-8859-1')

        # recall that the activity codes contain numeric and non-numeric data
        df.act = df.act.apply(self.convert_activity_code).values

        # get the PID
        df.PID = df.CHADID.apply(self.get_PID)

        return df

    def get_PID(self, x):

        """
        Given a CHADID, this function returns the PID. The PID is the CHADID stripped of the last character, \
        which is a code for the day record.
        
        :param string x: the CHADID
        :return: the PID
        :rtype: numpy.ndarray
        """

        pid = x[:-1]

        if x[:3] == 'EPA':
            pid = x[:6]

        return pid

    def get_quest(self):

        """
        This function returns a data frame of the raw questionnaire data. However, the data must have the date \
        marked explicitly to be accepted.
        
        :return: the CHAD questionnaire data in the correct column order
        :rtype: pandas.core.frame.DataFrame
        """

        # get the raw questionnaire data
        df = self.get_quest_raw()

        # which indices have the date marked
        idx = np.array( [ isinstance(x, str) for x in df.date.values] )

        # only keep questionnaire data with non NaN entries for dates
        df = df[idx]

        return df[QUEST_COLNAMES]

    def get_quest_raw(self):

        """
        This function returns a data frame of the raw questionnaire data and add the PID information.

        :return: the raw CHAD questionnaire data
        :rtype: pandas.core.frame.DataFrame
        """

        df = self.get_data(FNAME_QUEST)

        # get the PID
        df.PID = df.CHADID.apply(self.get_PID)

        return df

    def set_dates(self):

        """
        This function converts the date information in the CHAD questionnaire and CHAD events datafrmaes \
        from strings to python datetime objects.

        :return: None
        """
        f = lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date()

        self.quest.date     = self.quest.date.apply(f)
        self.events.date    = self.events.date.apply(f)

        return

    def set_times(self):

        """
        This function handles setting the time information for formatting in the CHAD questionnaire and events \
        dataframes
        
        #. converts the time from military time (0000 - 2359] to decimal time [0, 24) in the CHAD \
        evnets and questionnaire data for the start time and end time
        #. converts the duration to hours
        #. drops the military time (start time and end time) and duration (minutes) from the respective \
        data frames
        
        :return: None 
        """
        # converts 1 hour into minutes
        HOUR_2_MIN  = temporal.HOUR_2_MIN

        # convert times from minutes to hours
        self.events['start']    = self.convert_military_to_decimal_time( self.events['starttime'].values )
        self.events['end']      = self.convert_military_to_decimal_time( self.events['endtime'].values )
        self.events['dt']       = self.events['duration'] / HOUR_2_MIN

        # delete columns dealing with the time in minutes
        self.events.drop( ['starttime', 'endtime', 'duration'], axis=1, inplace=True )

        return

# ===============================================
# module functions
# ===============================================
def sample_stats(sample):

    """
    This function takes sample data and returns the mean and the standard deviation.

    :param pandas.core.frame.DataFrame sample: the data to analyze

    :return s_mean: the mean of the sample data
    :return s_std: the standard deviation of the sample data
    :rtype: pandas.core.frame.DataFrame
    :rtype: pandas.core.frame.DataFrame
    """

    # get the mean, standard deviation from a sample from CHAD
    # statistics
    s_mean = sample['mean']
    s_std  = sample['std']
        
    return (s_mean, s_std)

