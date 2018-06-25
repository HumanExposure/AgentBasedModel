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
# March 22, 2018

"""
This module contains functions that analyze the raw data from the Consolidated Human Activity \
Database (CHAD) to be processed/ filtered for use by the Agent-Based Model of Human Activity \
Patterns (ABMHAP).

This function primarily encapsulates functions to analyze data to be used as an \
imported module. However, it may also be run as a main file.
"""

# ===========================================
# import
# ===========================================
import datetime, os, sys
sys.path.append('..\\source')

# mathematical capability
import numpy as np

# dataframe capability
import pandas as pd

# for grouping capability
from itertools import groupby

# ABMHAP modules
import my_globals as mg
import chad, chad_code, social

# ===========================================
# functions
# ===========================================

def analyze_commute(data):

    """
    This function analyzes the commuting data to get information about BOTH \
    commuting to work, commuting from work, **AND** working. The data are chosen from \
    entries where a work event is sandwiched between a commuting to work event and a \
    commuting from work event. The commuting data and working data are processed and \
    filtered for use for ABMHAP.

    :param chad.CHAD_RAW data: the raw CHAD data

    :return: the raw CHAD commuting data also the data of people with both commute and work data,\
    statistical data of commuting to work, statistical data of commuting from work, \
    statistical data of working.

    :rtype: dictionary, dictionary, dictionary, dictionary
    """

    print('loading commuting data...')

    # get the raw commute data
    raw_comm = data.activity_times(data.events, chad_code.COMMUTE)

    # get the raw work data
    raw_work = data.activity_times(data.events, chad_code.WORK)

    # get the identifier's of people we have data for commuting and working
    pid_comm = raw_comm.PID.unique()

    # check to see if the PID is in the commuting identifiers
    f = lambda x: x in pid_comm

    # index of work PIDs that are in commute data
    idx     = raw_work.PID.apply(f)
    temp    = raw_work[idx]

    print('merging data...')

    # longitudinal commuting and working data, respectively
    merge_comm   = merge(raw_comm)
    merge_work   = merge(temp)

    # get the data of people with BOTH commute and work data
    merged = pd.concat([merge_comm, merge_work]).sort_values(['CHADID', 'start'])

    print('separate data into commuting to work, commuting from work, and being at work...')

    # the commuting data for going to work and going from work
    to_work, from_work, at_work = get_commute_data(merged)

    # indices for individuals for commuting to work
    idx_to      = filter_commute(to_work, chad.COMMUTE_TO_WORK_START_MIN, chad.COMMUTE_TO_WORK_START_MAX, \
                                 chad.COMMUTE_TO_WORK_END_MAX)

    # indices for individuals for commuting from work
    idx_from    = filter_commute(from_work, chad.COMMUTE_FROM_WORK_START_MIN, chad.COMMUTE_FROM_WORK_START_MAX, \
                                 chad.COMMUTE_FROM_WORK_END_MAX)

    # indices for individuals who have both commuting to and from work
    idx         = idx_to & idx_from

    to_work, from_work, at_work = to_work[idx], from_work[idx], at_work[idx]

    print('statistical results...')

    # store the commuting data
    # this is odd: why use merged with 'long'
    d = {'raw': raw_comm, 'long': merged}

    # analyze the moments for commuting to work, commuting from work, and being at work
    d_to_work   = get_moments(to_work, start_periodic=False)
    d_from_work = get_moments(from_work, start_periodic=False)
    d_at_work   = get_moments(at_work, start_periodic=False)

    return d, d_to_work, d_from_work, d_at_work

def analyze_commute_school(data):

    """
    This function analyzes the commuting to school data to get information \
    to get data about commuting to school and commuting from school. The \
    commuting to school data are processed and filtered for use for ABMHAP.

    :param chad.CHAD_RAW data: the raw CHAD data

    :return: the raw CHAD commuting data also the CHAD commuting data modified to handle \
    over night events, statistical data of commuting to school, statistical data of \
    commuting from school

    :rtype: dictionary, dictionary, dictionary
    """

    # the acceptable of CHAD activity codes
    codes = chad_code.COMMUTE + chad_code.COMMUTE_EDU

    raw = data.activity_times(data.events, codes)

    # merged commuting events that occur over midnight
    df = merge(raw)

    # the commuting to school data
    to_school = df[ (df.start >= chad.COMMUTE_TO_SCHOOL_START_MIN) \
                    & (df.start <= chad.COMMUTE_TO_SCHOOL_START_MAX) \
                    & (df.end <= chad.COMMUTE_TO_SCHOOL_END_MAX) ]

    # the commuting from school data
    from_school = df[ (df.start >= chad.COMMUTE_FROM_SCHOOL_START_MIN) \
                      & (df.start <= chad.COMMUTE_FROM_SCHOOL_START_MAX) \
                      & (df.end <= chad.COMMUTE_FROM_SCHOOL_END_MAX) ]

    # store the commuting data
    d = {'raw': raw, 'merged': df}

    # analyze the moments for commuting to school, commuting from school
    d_to_school     = get_moments(to_school, start_periodic=False)
    d_from_school   = get_moments(from_school, start_periodic=False)

    return d, d_to_school, d_from_school

def analyze_eat(data):

    """
    This function analyzes the CHAD data for eating in order to get information \
    on eating breakfast, eating lunch, and eating dinner data. The data \
    are processed and filtered for use for ABMHAP for the respective activities.

    :param chad.CHAD_RAW data: the raw CHAD data

    :return: statistical data of eating breakfast, statistical data of eating lunch, \
    statistical data of eating dinner

    :rtype: dictionary, dictionary, dictionary
    """

    print('loading raw eat-activity data...')

    # raw CHAD eating data
    raw = data.activity_times(data.events, chad_code.EAT)

    # separate the raw data into the respective meals
    breakfast, lunch, dinner = get_meals(raw)

    # merge data with overnight activities
    print('merging the meals data...')
    breakfast_long  = merge(breakfast)
    lunch_long      = merge(lunch)
    dinner_long     = merge(dinner)

    print('analyzing the moments for the meals...')

    # get the statistical data for breakfast, lunch, and dinner
    d_breakfast = get_moments(breakfast_long, start_periodic=False)
    d_lunch     = get_moments(lunch_long, start_periodic=False)
    d_dinner    = get_moments(dinner_long, start_periodic=False)

    return d_breakfast, d_lunch, d_dinner

def analyze_education(data):

    """
    This function analyzes the CHAD data for schooling in order to get information on \
    going to school. \
    The data are processed and filtered for use for ABMHAP for the school activity, \
    namely school data are only taken if the event is considered "fulltime", \
    (i.e., having a long enough duration) in order to avoid part-time school events.

    :param chad.CHAD_RAW data: the raw CHAD data

    :return: the CHAD schooling data for "fulltime" educational data.

    :rtype: dictionary
    """

    print('loading raw education-activity data...')

    # raw CHAD data with education
    raw = data.activity_times(data.events, chad_code.EDUCATION)

    # puts events that occur over midnight as 1 event
    print('merging the education data...')
    merged      = merge(raw)

    # fulltime data
    print('getting fulltime education data...')
    full        = get_fulltime_data(merged, start_min=3)

    # get data about the moments
    print('analyzing moments for education...')

    # get the statistical information for fulltime event data
    d_merged    = get_moments(full, start_periodic=False)

    return d_merged

def analyze_moments(df, start_periodic=False):

    """
    This function analyzes the data for each person by calculating the moments for \
    duration, start time, and end time for the following three cases.

    #. General (weekday and weekend)
    #. Weekday
    #. Weekend

    :param pandas.core.frame df: the data in the form of CHAD records to analyze

    :return: the statistical moments data for the following: \
    general duration, general start time, general end time, \
    weekday duration, weekday start time, weekday end time, \
    weekend duration, weekend start time, weekend end time

    :rtype: pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, \
    pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, \
    pandas.core.frame.DataFrame, pandas.core.frame.DatFrame, pandas.core.frame.DataFrame
    """

    #
    # statistics
    #

    # the CHAD personal identifiers, and the date values
    pid, date           = df.PID.values, df.date.values

    # the duration, start time, and end time values, respectively
    dt, start, end      = df.dt.values, df.start.values, df.end.values

    #
    # general (weekday and weekend data combined)
    #

    # the statistical analysis about the moments data for the duration
    stats_dt    = get_stats(pid, dt)

    # the statistical analysis about the moments data for the start time
    stats_start = get_stats(pid, start, do_periodic=start_periodic)

    # the statistical analysis about the moments data for the end time
    stats_end   = get_stats(pid, end, do_periodic=start_periodic)

    #
    # weekday
    #
    do_weekend      = False

    # the statistical analysis about the moments of weekday data for the duration
    stats_wd_dt     = get_stats_weekend(pid=pid, data=dt, date=date, start=start, end=end, \
                                        do_weekend=do_weekend)

    # the statistical analysis about the moments of weekday data for the start time
    stats_wd_start  = get_stats_weekend(pid=pid, data=start, date=date, start=start, end=end, \
                                        do_weekend=do_weekend, do_periodic=start_periodic)

    # the statistical analysis about the moments of weekday data for the end time
    stats_wd_end    = get_stats_weekend(pid=pid, data=end, date=date, start=start, end=end, \
                                        do_weekend=do_weekend, do_periodic=start_periodic)
    # weekend
    do_weekend      = True

    # the statistical analysis about the moments of weekend data for the duration
    stats_we_dt     = get_stats_weekend(pid=pid, data=dt, date=date, start=start, end=end, do_weekend=do_weekend)

    # the statistical analysis about the moments of weekend data for the start time
    stats_we_start  = get_stats_weekend(pid=pid, data=start, date=date, start=start, end=end, \
                                        do_weekend=do_weekend, do_periodic=start_periodic)

    # the statistical analysis about the moments of weekend data for end time
    stats_we_end    = get_stats_weekend(pid=pid, data=end, date=date, start=start, end=end, \
                                        do_weekend=do_weekend, do_periodic=start_periodic)

    return stats_dt, stats_start, stats_end, stats_wd_dt, stats_wd_start, stats_wd_end, \
           stats_we_dt, stats_we_start, stats_we_end

def analyze_sleep(data):

    """
    This function analyzes the CHAD data for sleeping in order to get information \
    on sleeping. The data are processed and filtered for use for ABMHAP for the \
    sleep activity.

    :param chad.CHAD_RAW data: the raw CHAD data

    :return: the statistical data on CHAD sleep data
    :rtype: dictionary
    """

    # the CHAD events data
    events = data.events

    # load raw data
    print('loading sleep data...')
    raw = data.activity_times(events, chad_code.SLEEP)

    # merge data across one day and the next (for events occurring over midnight)
    print('calculating merged data...')
    merged = merge(raw)

    # periodicity assumption
    print('calculating the periodicity assumption...')
    period      = periodicity_sleep(merged)

    # limit the periodic
    df  = period

    # filter out the bad data and keep the good data
    idx = (mg.to_periodic(df.start) >= chad.SLEEP_START_MIN) & (mg.to_periodic(df.start) <= chad.SLEEP_START_MAX) \
          & (df.end >= chad.SLEEP_END_MIN) & (df.end <= chad.SLEEP_END_MAX) \
          & (df.dt >= chad.SLEEP_DT_MIN) & (df.dt <= chad.SLEEP_DT_MAX)

    print('calculating the moments...')

    # get the sleep data with the good events data
    sleep   = period[idx]

    # analyze the statistics of the sleep events
    d_sleep = get_moments(sleep, start_periodic=True)

    return d_sleep

def analyze_work(data):

    """
    This function analyzes the CHAD data for working. The data are processed and \
    filtered for use for ABMHAP for the work activity. Data in only chosen if the \
    person surveyed in CHAD is marked as fulltime employed. This function does a statistical \
    analysis of the following:

    #. raw work data
    #. longitudinal data
    #. fulltime work data

    .. warning::
        This function may be antiquated and not currently used. Instead see :func:`analyze_commute` \
        for obtaining work information.

    :param chad.CHAD_RAW data: the raw CHAD data

    :return: statistical data on CHAD work data on the following: raw CHAD data, \
    raw CHAD data after being processed for overnight activities, raw CHAD data \
    after being processed for data from people employed fulltime

    :rtype: dictionary, dictionary, dictionary
    """

    # get the fulltime work only
    x = chad_code.WORK

    # the raw CHAD events data
    events = data.events

    # the raw CHAD questionnaire data
    quest = data.quest

    # group the events data by PID
    gb = events.groupby('PID')

    # the CHADIDs that are fulltime workers
    idx = (quest.fulltime == 'Y') & (quest.employed == 'Y')

    # get the corresponding PID for fulltime workers
    u = quest.PID[idx].unique()

    # get all of the events data for fulltime workers
    y = [gb.get_group(i) for i in u]
    df = pd.concat(y)

    print('loading work data...')

    # load the raw data
    raw = data.activity_times(df, x)

    # merging data
    print('calculating merged data...')

    # merge data from overnight activities
    merged = merge(raw)

    # merge multiple multiple work events occurring in one day as one event
    print('calculating fulltime data...')

    # get full time data
    full = get_fulltime_data(merged, start_min=chad.WORK_START_MIN)

    print('analyzing moments...')
    do_periodic = False

    # statistical information based on the raw CHAD data
    d_raw       = get_moments(raw, start_periodic=do_periodic)

    # statistical information based on the raw CHAD data after being processed
    # for overnight activities
    d_merged    = get_moments(merged, start_periodic=do_periodic)

    # statistical information based on data from CHAD from people identified
    # as employed full time
    d_full      = get_moments(full, start_periodic=do_periodic)

    return d_raw, d_merged, d_full

def filter_commute(df, start_min, start_max, end_max):

    """
    This function finds indices of the data that satisfy the filters \
    placed on the commuting data by limiting the data to be within the start \
    time range and end time range.

    :param pandas.core.frame.DataFrame df: the commuting data
    :param float start_min: the minimum start time [hours]
    :param float start_max: the maximum start time [hours]
    :param float end_max: the maximum end time [hours]

    :return: indices of the commuting data that satisfy the filtering
    :rtype: numpy.ndarray
    """

    idx      = (df.start >= start_min) & (df.start <= start_max) & (df.end <= end_max)
    idx      = idx.values

    return idx

def get_commute_data(df_all):

    """
    This function finds the following commuting data for BOTH commuting to work AND commuting \
    from work.

    :param pandas.core.frame.DataFrame df_all: the dataframe containing commuting and work data
    :return: the commute to work data, the commute from work data, the work activity data
    """

    gb      = df_all.groupby('CHADID')
    chadid  = df_all.CHADID.unique()

    # store the data for commuting to work and from work respectively
    to_work, from_work, act_work = list(), list(), list()

    # loop through the entries for each day
    for x in chadid:

        # get the data for the CHADID
        df = gb.get_group(x)

        idx = np.array([y in chad_code.COMMUTE for y in df.act])

        # index of commute
        ic = np.argwhere(idx == True)

        # index of work
        iw = np.argwhere(idx == False)

        b = False
        if (len(ic) >= 2):
            # check to see if at least 1 work event is sandwiched between the first and last commutes
            b = (iw > ic[0]).any() and (iw < ic[-1]).any()
        if (b):
            # add the first commute event as commute to work
            to_work.append(df.iloc[ic[0]])
            # add the last commute event as commute from work
            from_work.append(df.iloc[ic[-1]])
            # add the work activity as the time between work
            act_work.append(df.iloc[iw[0]].act[0])

    # collect data about commuting to and from work
    to_work     = pd.concat(to_work)
    from_work   = pd.concat(from_work)

    # calculate work as the time between two commute events
    at_work     = to_work.copy()
    at_work.end = from_work.end.values
    at_work.dt  = (at_work.end - at_work.start + 24) % 24
    at_work.act = np.array(act_work)

    return to_work, from_work, at_work

def get_data_help(idx, stats_dt, stats_start, stats_end, record):

    """
    This function returns statistical information from the activity duration, \
    start time, end time, and the CHAD records from the given indices.

    :param numpy.ndarray idx: the indices of the CHAD individuals to \
    keep in the statistical data
    :param pandas.core.frame.DataFrame stats_dt: the statistical moments for the \
    activity duration
    :param pandas.core.frame.DataFrame stats_start: the statistical moments for \
    the start time activity duration
    :param pandas.core.frame.DataFrame stats_end: the statistical moments for \
    the end time activity duration
    :param pandas.core.frame.DataFrame record: the CHAD records for a given \
    activity

    :return: the statistical data on duration, start time, and end time; \
    the CHAD record data from the chosen individuals given by the indices.

    :rtype: pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, \
    pandas.core.frame.DataFrame
    """

    # this function is used to get data in order to help the get_solo() and get_longitude() data

    # the duration data to keep
    dt      = stats_dt[idx]

    # the start time data to keep
    start   = stats_start[idx]

    # the end time data to keep
    end     = stats_end[idx]

    # the person identifiers of the individuals of the kept CHAD data
    pid     = dt.PID.unique()

    f       = lambda x: x in pid

    # get the indices from the records of the individuals to keep
    idx     = record.PID.apply(f)

    # get the records
    rec     = record[idx]

    return dt, start, end, rec

def get_end_date(date, start, end):

    """
    This function finds the date that an activity ends.

    :param date: the date the activities start
    :type: numpy.ndarray of datetime.timedelta
    :param numpy.ndarray start: the start time of the activities
    :param numpy.ndarray end: the end time of activities

    :return: the end date for an activity
    :rtype: numpy.ndarray of datetime.timedelta
    """

    # convert the start time and end time to be expressed in hours as [-12, 12)
    start_p = mg.to_periodic(start)
    end_p   = mg.to_periodic(end)

    # this means an event started before midnight and ended starting at midnight( the next day)
    idx_polarity    = np.sign(start_p * end_p) == -1
    date_end        = date + (idx_polarity) * datetime.timedelta(days=1)

    return date_end

def get_fulltime_data(df, start_min=chad.WORK_START_MIN):

    """
    This function finds the data from CHAD that pertain to individuals that \
    are working fulltime. That is, activities starting with with a minimum \
    given mean start time.

    :param pandas.core.frame.DataFrame df: the CHAD work data
    :param float start_min: the minimum start time to be accepted [0, 24)

    :return: the data frame of the workers
    :rtype: pandas.core.frame.DataFrame
    """

    # groub the dataframe by CHADID (CHAD identifier)
    gb = df.groupby('CHADID')

    # the unique CHADIDs
    chadid = df.CHADID.unique()

    # the list of new data frames
    df_list = list()

    # loop through the CHADIDs
    for i in chadid:

        # get data from the particular CHADID
        df = gb.get_group(i)

        # turn scalars into numpy arrays
        start = np.array(df.iloc[0].start)

        # only take data starting at the minimum start time
        if (start >= start_min):

            # turn scalars into numpy arrays
            end = np.array(df.iloc[-1].end)
            dt = (end - start + 24) % 24

            # need to pass non-scalars into the dictionary
            chadid = [df.CHADID.iloc[0]]

            # person id
            pid = [df.PID.iloc[0]]

            # activity code
            act = [df.act.iloc[0]]

            # date
            date = [df.date.iloc[0]]

            d = {'CHADID': chadid, 'PID': pid, 'start': start, 'end': end, 'dt': dt, \
                 'act': act, 'date': date}

            # create new data frame
            df_list.append(pd.DataFrame(d))

    # make into 1 single data frame
    result = pd.concat(df_list)[chad.EVENTS_COLNAMES]

    return result

def get_longitude(stats_dt, stats_start, stats_end, record, N=2):

    """
    This function gets the longitudinal CHAD statistical data for \
    duration, start time, and end time. This function also gets \
    the CHAD record data from the respective statistical data.

    :param pandas.core.frame.DataFrame stats_dt: the statistical moments for the \
    activity duration
    :param pandas.core.frame.DataFrame stats_start: the statistical moments for \
    the start time activity duration
    :param pandas.core.frame.DataFrame stats_end: the statistical moments for \
    the end time activity duration
    :param pandas.core.frame.DataFrame record: the CHAD records for a given \
    activity
    :param int N: the minimum number of activities to be considered \
    longitudinal

    :return: longitudinal data for statistical moments for activity duration, \
    start time, and end time also longitudinal CHAD records
    :rtype: pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, \
    pandas.core.frame.DataFrame, pandas.core.frame.DataFrame
    """

    # get longitudinal data
    idx = stats_dt.N >= N

    # get the data that correspond to the indices of the longitudinal statistical record
    dt, start, end, rec = get_data_help(idx, stats_dt=stats_dt, stats_start=stats_start, stats_end=stats_end, \
                                        record=record)

    return dt, start, end, rec

def get_meals(df):

    """
    This function takes in eating data and separates that data into meals: breakfast, \
    lunch, and dinner by filtering the data by minimum and maximum start time, \
    end time, and duration.

    :param pandas.core.frame.DataFrame df: CHAD data on the eating data

    :return: breakfast data, lunch data, and dinner data
    :rtype: pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, \
    pandas.core.frame.DataFrame
    """

    # filter out data that will be considered as a breakfast event
    breakfast = df[ (df.start >= chad.BREAKFAST_START_MIN) & (df.end <= chad.BREAKFAST_END_MAX) \
                   & (df.end != 0) \
                   & (df.dt >= chad.BREAKFAST_DT_MIN) & (df.dt <= chad.BREAKFAST_DT_MAX) ]

    # filter out data that will be considered as a lunch event
    lunch = df[ (df.start >= chad.LUNCH_START_MIN) & (df.end <= chad.LUNCH_END_MAX) \
               & (df.dt >= chad.LUNCH_DT_MIN) & (df.dt <= chad.LUNCH_DT_MAX) \
               & (df.end != 0) ]

    # filter out data that will be considered as a dinner event
    dinner = df[ (df.start >= chad.DINNER_START_MIN) & (df.end <= chad.DINNER_END_MAX) \
                 & (df.end >= chad.DINNER_START_MIN) & (df.end != 0) \
                 & (df.dt >= chad.DINNER_DT_MIN) & (df.dt <= chad.DINNER_DT_MAX) ]

    return breakfast, lunch, dinner

def get_moments(x, start_periodic):

    """
    This function calculates data about the moments of start time, end time, and duration \
    weekday + weekend data, weekday data, weekend data. Also there are the CHAD records for \
    the following situations: daily data, weekday data, and weekend data.

    :param pandas.core.frame.DataFrame x: the CHAD data to be analyzed
    :param bool start_periodic: a flag indicating whether start times should be analyzed \
    in [-12, 12) if true or [0, 24) if false

    :return: a dictionary of statistical moments for the following data: duration, \
    start time, end time, weekday duration, weekday start time, weekday end time, \
    weekend duration, weekend start time, weekend end time. Also there are the following \
    CHAD records: daily records, weekend records, weekday records.

    :rtype: dictionary of pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, \
    pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, \
    pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, \
    pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame
    """

    # analyze the moments
    stats_dt, stats_start, stats_end, stats_wd_dt, stats_wd_start, stats_wd_end, stats_we_dt, stats_we_start, \
    stats_we_end = analyze_moments(x, start_periodic=start_periodic)

    # get the boolean indices of weekend data
    idx = get_weekend_index_df(x)

    d = {'stats_dt': stats_dt, 'stats_start': stats_start, 'stats_end': stats_end, \
         'stats_wd_dt': stats_wd_dt, 'stats_wd_start': stats_wd_start, 'stats_wd_end': stats_wd_end, \
         'stats_we_dt': stats_we_dt, 'stats_we_start': stats_we_start, 'stats_we_end': stats_we_end, \
         'data': x, 'data_weekend': x[idx], 'data_weekday': x[~idx]}

    return d

def get_skipped_meals(df):

    """
    For each person identified within CHAD, this function goes through activity \
    data and finds, on a workday, and finds whether or not the individual \
    skipped a meal (i.e., skipped breakfast, lunch, and/ or dinner).

    .. warning::
        This function is antiquated and not used.

    :param pandas.core.frame.DataFrame df: CHAD activity data

    :return: the activity data of people within CHAD where a meal was skipped
    :rtype: pandas.core.frame.DataFrame
    """

    # group by PID
    gb_pid = df.groupby('PID')

    # group by CHADID
    gb_chadid = df.groupby('CHADID')

    # identifiers for PID and CHADID, respectively
    u_pid = df.PID.unique()

    # check to see if the given activity (x) is a work activity
    f_workday = lambda x: x in chad_code.WORK

    # check to see if the given activity (x) is an eat activity
    f_eat = lambda x: x in chad_code.EAT

    # list of data frames
    df_list = list()

    # loop through data for each person
    for x in u_pid:

        # get the data for the individual
        df_pid = gb_pid.get_group(x)

        # the number of days of data
        n_days = len(df_pid.CHADID.unique())

        # reset info for workdays, and skipped meals
        workdays = np.zeros(n_days)

        breakfast_skipped   = np.zeros(n_days)
        lunch_skipped       = np.zeros(n_days)
        dinner_skipped      = np.zeros(n_days)

        # reset the index
        ii = 0

        # loop over data for each day
        for y in df_pid.CHADID.unique():

            # get the activities for the day
            df_chadid       = gb_chadid.get_group(y)

            # is the current day a workday
            is_workday      = df_chadid.act.apply(f_workday).any()

            # store results
            workdays[ii]    = is_workday

            # get eating events
            idx     = df_chadid.act.apply(f_eat).values
            meals   = df_chadid[idx]
            breakfast, lunch, dinner = get_meals(meals)

            # look at skipping meals
            breakfast_skipped[ii]   = len(breakfast) == 0
            lunch_skipped[ii]       = len(lunch) == 0
            dinner_skipped[ii]      = len(dinner) == 0

            # update index
            ii = ii + 1

            # store information about the specific individual

        # the CHADID
        chadid = df_pid.CHADID.unique()

        # the number of days of data for the individual
        N = len(chadid)

        # the person identifier
        pid = [df_pid.PID.iloc[0]] * N

        # the skipping meals data to be stored for the individual
        d = {'CHADID': chadid, 'PID': pid, 'workday': workdays, 'breakfast_skipped': breakfast_skipped, \
             'lunch_skipped': lunch_skipped, 'dinner_skipped': dinner_skipped}

        # store the result about the individual
        df_list.append(pd.DataFrame(d))

    # store the results for all of the data
    result = pd.concat(df_list)

    return result

def get_solo(stats_dt, stats_start, stats_end, record):

    """
    This function gets the single-day (i.e. from individuals with only 1 entry) \
    CHAD statistical data for \
    duration, start time, and end time. This function also gets \
    the CHAD record data from the respective statistical data.

    :param pandas.core.frame.DataFrame stats_dt: the statistical moments for the \
    activity duration
    :param pandas.core.frame.DataFrame stats_start: the statistical moments for \
    the start time activity duration
    :param pandas.core.frame.DataFrame stats_end: the statistical moments for \
    the end time activity duration
    :param pandas.core.frame.DataFrame record: the CHAD records for a given \
    activity

    :return: single-day data for statistical moments for activity duration, \
    start time, and end time also longitudinal CHAD records
    :rtype: pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, \
    pandas.core.frame.DataFrame, pandas.core.frame.DataFrame
    """

    # get the indices of individuals with only 1 data point
    idx = stats_dt.N == 1

    # get the solo data
    dt, start, end, rec = get_data_help(idx, stats_dt=stats_dt, stats_start=stats_start, stats_end=stats_end, \
                                        record=record)

    return dt, start, end, rec

def get_stats(pid, data, do_periodic=False):

    """
    This function gets the statistics about an activity-parameter (start time, end time, \
    or duration) and stores the following data within a dataframe:

    #. person identifier (PID)
    #. the number of events (N)
    #. the mean (mu)
    #. the standard deviation (std)
    #. the coefficient of variation (cv)

    :param pid: the identifiers for the individuals within CHAD for a given activity
    :type pid: numpy.ndarray of str
    :param numpy.ndarray data: the CHAD records for a given activity
    :param bool do_periodic: a flag whether (if True) or not (if False) time of day \
    should be expressed in [-12, 12)

    :return: the statistical results from an activity-parameter (start time, end time, \
    or duration)
    :rtype: pandas.core.frame.DataFrame
    """

    # dataframe list for the created data
    df_list = list()

    # for each person within the data
    for p in np.unique(pid):

        # get the correct indices, and the corresponding data
        idx = pid == p
        x   = data[idx]

        if do_periodic:

            # display time in [-12, 12) instead of [0, 24)
            x = mg.to_periodic(x)

        # get the stats for the individual
        mu, std, cv, N = get_stats_individual(x)

        # store the information
        d = {'PID': p, 'N': N, 'mu': mu, 'std': std, 'cv': cv}
        df_list.append(d)

    # column names
    cols = ['PID', 'N', 'mu', 'std', 'cv']

    # store the data in a data frame
    df = pd.DataFrame(df_list)[cols]

    return df

def get_stats_individual(x):

    """
    This function gets the data from the records and returns the following.

    #. the mean (mu)
    #. the standard deviation (std)
    #. the coefficient of variation (cv)
    #. the number of events (N)

    :param numpy.ndarray x: the individual records data

    :return: the mean, standard deviation, coefficient of variation, \
    and  number of entries

    :rtype: numpy.ndarray, numpy.ndarray, numpy.ndarray, int
    """

    # the mean
    mu  = x.mean()

    # the standard deviation
    std = x.std()

    # the coefficient of variation
    cv  = std / np.abs(mu)

    # the number of entries
    N   = len(x)

    return (mu, std, cv, N)

def get_stats_weekend(pid, data, date, start, end, do_weekend=True, do_periodic=False):

    """
    This function calculates the stats about the moments of the activity \
    that occur on a weekends OR weekedays.

    :param pid: the personal identifiers in the CHAD data
    :type pid: numpy.ndarray of str
    :param data: the CHAD records of the activity data
    :param date: the dates of the activity data
    :type date: numpy.ndarray of datetime.timedelta
    :param numpy.ndarray start: the start time of the activity data
    :param numpy.ndarray end: the end time of the activity data
    :param bool do_weekend: a flag whether (if True) to use data that occurs on the \
    weekend or (if False) and the weekday
    :param bool do_periodic: a flag whether (if True) or not (if False) time of day \
    should be expressed in [-12, 12)

    :return: the statistical data for an activity-parameter (i.e. start time, \
    end time, and duration) that occurs on the weekend or weekday
    :rtype: pandas.core.frame.DataFrame
    """

    # indices corresponding to days that are a weekend
    idx = get_weekend_index(date, start, end)

    # get index corresponding to a weekday
    if not do_weekend:
        idx = idx == False

    # if there is data, calculate it, else do nothing
    if idx.any():
        df = get_stats(pid[idx], data[idx], do_periodic)
    else:
        df = pd.DataFrame()

    return df

def get_weekend_index(date, start, end):

    """
    This function gets the indices of activity information \
    of the weekend data.

    :param date: the date of the activity information
    :type date: numpy.ndarray of datetime.timedelta
    :param numpy.ndarray start: the start time of the activity information
    :param numpy.ndarray end: the end time of the activity information

    :return: this function gets the indices of activities that occur \
    during the weekend

    :rtype: numpy.ndarray of bool
    """

    # Monday is a zero
    weekend = [5, 6]

    # get the day an event ends
    date_end = get_end_date(date, start, end)

    # the days that are a weekend
    idx = np.array([x.weekday() in weekend for x in date_end])

    return idx

def get_weekend_index_df(df):

    """
    This function gets the boolean indices of weekend data from a dataframe.

    :param pandas.core.frame.DataFrame df: CHAD activity record data

    :return: the boolean indices of weekend data
    :rtype: numpy.ndarray of bool
    """

    idx = get_weekend_index(df.date.values, df.start.values, df.end.values)

    return idx

def histogram(ax, x, bins=None, color='b', label='', alpha=1.0):

    """
    This function plots a histogram of the data where the y axis corresponds \
    to the relative frequency.

    :param ax: the plotting axis (plt or from axes)
    :type ax: matplotlib.figure.Figure
    :param numpy.ndarray x: the data to be plotted
    :param numpy.ndarray bins: the bins for the histogram
    :param str color: the color for the histogram
    :param str label: the label of the data
    :param float alpha: the alpha for plotting

    :return:
    """

    if (len(x) != 0):
        weights = np.zeros(x.shape) + 1 / x.size
    else:
        x = np.array([0])
        weights = np.array([1])

    # create the bins
    if bins is None:
        x_min   = x.min()
        x_max   = x.max()
        dx      = x_max - x_min
        N       = dx * 4 + 1
        bins    = np.linspace(x_min, x_max, N)

    # plot histogram
    ax.hist(x, weights=weights, bins=bins, color=color, label=label, alpha=alpha)

    return

def merge(df_full):

    """
    For each person in the activity data, the function does the following:

    #. groups the contiguous daily activity data
    #. merges data that occur over midnight into one event

    :param pandas.core.frame.DataFrame df_full: the full set of the activity data

    :return: a data frame that merges activities that occur over midnight
    :rtype: pandas.core.frame.DataFrame
    """

    # unique person identifiers
    pid = df_full.PID.unique()

    # group by unique person identifiers
    gb = df_full.groupby('PID')

    df_list_merged = list()

    # for each person, merge the data
    for p in pid:

        # get the data of person p
        df = gb.get_group(p)

        # splits the data into groups of sequential days
        df_list = sequential_data(df)

        # merge the activity events that start before midnight and end after midnight
        x = [merge_end_of_day(s) for s in df_list]

        # add to list
        df_list_merged.append(pd.concat(x))

    result = pd.concat(df_list_merged)

    return result

def merge_end_of_day(df):

    """
    This function takes longitudinal data and merges the data if the data \
    starts before midnight and ends after midnight.

    :param pandas.core.frame.DataFrame df: the activity records data

    :return: activity events that start before midnight and end after midnight
    :rtype: pandas.core.frame.DataFrame
    """

    # find indices where the end time is at midnight
    idx = df.end.values == 0

    # add a False for the last day. We will seek to merge the final day in the longitudinal sequence
    idx = np.array(idx[:-1].tolist() + [False])

    #
    # get indices of days that should be merged
    #

    # the start of the event
    idx_start = np.where(idx == True)[0]

    # the end of the event
    idx_end = idx_start + 1

    # indices of events that will be merged
    idx_merged = np.array(idx)
    idx_merged[idx_end] = True

    # the data that will not be merged
    df_old = df[idx_merged == False]

    # create the merged data
    df_merge        = pd.DataFrame(df.iloc[idx_start])
    df_merge.end    = df.iloc[idx_end].end.values
    df_merge.dt     = df.iloc[idx_start].dt.values + df.iloc[idx_end].dt.values

    # create a new data frame of the merged and non-merged data
    df_new = pd.concat([df_merge, df_old]).sort_values(['date', 'start'])

    return df_new

def periodicity_CHADID(df):

    """
    This function combines entries for sleep with the periodicity assumption for a \
    given day (CHADID).

    If there are two events starting at 0:00 and ending in the morning AND \
    another event starting in the evening and ending at 0:00 on the SAME DAY, \
    we combine the two events into one event. We assume that the person goes to sleep \
    on the same start time and wakes up at the same time (periodicity assumption).

    :param pandas.core.frame.DataFrame df: sleep events for 1 CHADID

    :return: return sleep data with the periodicity assumption for 1 CHADID
    :rtype: pandas.core.frame.DataFrame

    """

    # create an empty list
    df_list = list()

    # if the list contains only 1 or 0 entries
    if ( len(df) <= 1 ):
        result  = pd.DataFrame(df)[chad.EVENTS_COLNAMES]
    else:

        # store the activity
        act     = [df.iloc[0].act]
        # store the data
        date    = [df.iloc[0].date]
        # store the CHADID
        chadid  = [df.iloc[0].CHADID]
        # store the PID
        pid     = [df.iloc[0].PID]

        # for each entry
        for i in range(len(df)):

            # store the start time
            start = df.iloc[i].start

            # if the current entry does not end with 0, keep the entry
            if df.iloc[i].end != 0:
                end = df.iloc[i].end
            else:
                # if the entry ends with zero, take the value of the first entry
                end = df.iloc[0].end

            # calculate the duration
            dt      = [mg.from_periodic(end - start, do_hours=True)]

            # set the start and end time for entry into dataframe
            start   = [start]
            end     = [end]

            # create dictionary for the new entry
            d = {'CHADID': chadid, 'PID': pid, 'start': start, 'end': end, 'dt': dt, \
                 'act': act, 'date': date}

            # add the entry to the list
            df_list.append(pd.DataFrame(d))

            # if the entry includes the periodicity assumption, throw away the top entry
            if not (df.iloc[i].end != 0):
                df_list.pop(0)

        # store the results as a dataframe
        result = pd.concat(df_list)[chad.EVENTS_COLNAMES]

    return result

def periodicity_PID(df):

    """
    Perform the periodicity assumption for a given person by its \
    person identifier (PID).

    :param pandas.core.frame.DataFrame df: the sleep data of a person with 1 PID

    :return: sleep data with the periodicity assumption
    :rtype: list of pandas.core.frame.DataFrame
    """

    # the data list
    df_list = list()

    # group data by CHADID
    gb      = df.groupby('CHADID')

    # for each CHADID and use the periodicity assumption
    df_list.append( [ periodicity_CHADID( gb.get_group(y) ) for y in df.CHADID.unique() ] )

    # flatten out the list
    df_list = [subitem for item in df_list for subitem in item]

    return df_list

def periodicity_sleep(data):

    """
    Perform the periodicity assumption (i.e., expressing time as [-12, 12)) for an \
    entire dataset of multiple entries.

    :param pandas.core.frame.DataFrame data: the sleep data over many individuals

    :return: sleep data with the periodicity assumption
    :rtype: pandas.core.frame.DataFrame
    """

    # group data frame by PID
    gb_pid = data.groupby('PID')

    # list of data frames
    df_list = list()

    # loop through each PID
    for x in data.PID.unique():

        # get data for the PID
        df = gb_pid.get_group(x)

        # set the periodicity for sleep for the PID
        df_list.append(periodicity_PID(df))

        # flatten out the df_list
    df_list = [subitem for item in df_list for subitem in item]

    # create one data frame
    result = pd.concat(df_list)

    return result

def save(fpath, record, stats_dt, stats_start, stats_end):

    """
    This function saves the following information as a .csv file:

    #. the statistical moments data for the activity duration ('stats_dt.csv')
    #. the statistical moments data for the activity start time ('stats_start.csv')
    #. the statistical moments data for the activity end time ('stats_end.csv')
    #. the statistical moments data for the activity records ('record.csv')

    :param str fpath: the file directory in which to save the data
    :param pandas.core.frame.DataFrame record: the CHAD records for a given \
    activity
    :param pandas.core.frame.DataFrame stats_dt: the statistical moments for the \
    activity duration
    :param pandas.core.frame.DataFrame stats_start: the statistical moments for \
    the start time activity duration
    :param pandas.core.frame.DataFrame stats_end: the statistical moments for \
    the end time activity duration

    :return:
    """

    # the name of the files
    fname_dt        = fpath + '\\stats_dt.csv'
    fname_start     = fpath + '\\stats_start.csv'
    fname_end       = fpath + '\\stats_end.csv'
    fname_record    = fpath + '\\record.csv'

    # flag used to save the row index in .csv files
    do_row_index = False

    # the data to save
    data = [stats_dt, stats_start, stats_end, record]

    # the file names of the respective data
    fnames  = [fname_dt, fname_start, fname_end, fname_record]

    # save the data to .csv files
    for fname, df in zip(fnames, data):

        # create the directory for the save file if it does not exist
        os.makedirs(os.path.dirname(fname), exist_ok=True)

        # save the dataframe as a .csv file
        df.to_csv(fname, index=do_row_index)

    return

def sequential_data(df):

    """
    For a given PID, this function groups the data in terms of sets of data \
    for consecutive days. This function \
    assumes that all the data given is for a given (generalized) activity.

    .. note::
        In the data, it is not necessarily the case that if there are multiple days of consecutive activity, \
        that all of them form 1 contiguous period. Ex. It is possible to have entries Jan 1, Jan 2, Jan 3, Feb 10, \
        Feb 11. This function will group the data into 2 groups when this occurs.

    :param pandas.core.frame.DataFrame df: the data of a specific PID for an activity
    :return: a list of dataframes for sequential longitudinal-data
    :rtype: list of pandas.core.frame.DataFrame
    """

    # the number of events
    N = df.shape[0]

    if (N <= 1):
        s = [df]
    else:
        # get labels indicating sequential days
        b = sequential_days(df.date.values, df.start.values, df.end.values)

        # keys are the sequence identifier [0, 1, 2] in the above example
        keys = [k for k, g in groupby(b)]

        # a list of sets of longitudinal data for a given PID
        s = [df[b == k] for k in keys]

    return s

def sequential_days(date, start=None, end=None):

    """
    This creates label indicating sequential days. This is done by writing a sequence \
    where each group of consecutive dates have a label starting at 0.

    .. note::
        the following sequence of dates [0, 0, 1,1, 3, 4, 5, 10], would have the \
        following sequence [0, 0, 0, 0, 1, 1, 1, 2]

    :param date: the date of the activity data
    :type date: numpy.ndarray datetime.timedelta
    :param numpy.ndarray start: the start time of the activity data
    :param numpy.ndarray end: the end time of the activity data

    :return: a sequence whose indices indicates sequential dates for an activity
    :rtype: numpy.ndarray
    """

    dt_min = datetime.timedelta(days=0)
    dt_max = datetime.timedelta(days=1)

    # return true if the events occur on consecutive days
    f = lambda x: [(later - now >= dt_min) & (later - now <= dt_max) for now, later in zip(x[:-1], x[1:])]

    if (start is not None) and (end is not None):

        # get the date that the activity ends
        date_end = get_end_date(date, start, end)

        # find where the dates are the same or in a consecutive series
        idx = np.array(f(date_end))
    else:
        idx = np.array(f(date))

    # write sequence where each group of consecutive dates have a label starting at 0
    # the following sequence of dates [0, 0, 1,1, 3, 4, 5, 10], would have the following sequence
    # [0, 0, 0, 0, 1, 1, 1, 2]
    b = np.array([0] + np.cumsum(idx == False).tolist())

    return b


# ===========================================
# run
# ===========================================

if __name__ == '__main__':

    # get all data
    data = chad.CHAD_RAW(min_age=social.ADULT_AGE, max_age=social.MAX_AGE)

    # the activity to look at
    x = [chad_code.SLEEP]

    # the minimum duration
    dt_min = 4

    # load raw data
    print('loading sleep data...')
    raw = data.activity_times( data.events, x)

    # THIS IS NOT longitudinal data
    merged = merge(raw)

    # sleep data
    slumber = merged[merged.dt >= dt_min]

    # get data about the moments
    stats_dt, stats_start, stats_wd_dt, stats_wd_start, stats_we_dt, stats_we_start = analyze_moments(slumber)

