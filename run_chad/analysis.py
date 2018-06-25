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
# February 15, 2017

"""
This file contains capability for analyzing results from the comparisons between CHAD \
(Consolidated Human Activity Database) data and the performance of ABMHAP (Agent-Based \
Model of Human Activity Patterns).

.. moduleauthor:: Dr. Namdi Brandon


.. warning::
    This modules is old and may or may not be used.
"""

# ===========================================
# import
# ===========================================
import os, pickle, sys, zipfile
sys.path.append('..\\source')
sys.path.append('..\\run')
sys.path.append('..\\processing')

# general math capabilities
import numpy as np

# for dataframe manipulation
import pandas as pd

# ABMHAP modules
import my_globals as mg
import demography as dmg
import chad, temporal

# ===========================================
# functions
# ===========================================


def get_error(chad_raw, chad_stats, col_name, abm_all, do_cyclical = False):

    """

    .. warning::
        I do not think this function is used.

    :param pandas.core.frame.DataFrame chad_raw: the CHAD activity data being compared to

    :param pandas.core.frame.DataFrame chad_stats: the relevant statistics for the CHAD activity
                                    of the person (PID) being modeled

    :param str col_name: the name of the column of the CHAD data being compared

                    :example: col_name = "dt" would allow access for chad_raw["dt"]

    :param abm_all: the ABM simulation data for the simulated person's activity
                    with respected to the quantity from col_name.

                    :example: if col_name = "dt", then abm_all should contain the duration data

    :param bool do_cyclical: indicates when to cast data in a "cyclical" form. As in,
                            [0, 24 * HOURS_2_MIN - 1] [minutes]

    :return: the L2 (sum of squares) absolute error for each agent, \
    the L2 (sum of squares) relative error for each agent
    :rtype: float array, float array
    """

    # the number of sampled CHAD people being modeled
    num_samples = len(abm_all)
    
    # absolute and relative error vectors
    aerr_abm = -1 * np.ones( (num_samples, 1) )
    rerr_abm = np.array( aerr_abm ) 

    # do the error analysis for dt
    for i in range( num_samples ):
    
        # the abm activity duration [min]
        data_abm = abm_all[i]
    
        if (do_cyclical):
            # put the ABM time in terms of time of day [min]
            data_abm = data_abm % temporal.DAY_2_MIN
    
        # number of data points per sample
        N = len(data_abm)
    
        # CHAD activity duration [hours]
        chad_data = chad_raw.loc[ chad_raw.PID == chad_stats.PID.iloc[i] ]
    
        # convert CHAD data to minutes
        data = np.round( chad_data[col_name].values * temporal.HOUR_2_MIN )
    
        # It is possible that the ABM simulation starts with the Agent 
        # in a non-IDLE state. Thus the ABM may have an additional 
        # partially executed event.
        # If so, ignore that data point
        if ( len(data_abm) - 1 == len(data) ):
            data_abm = data_abm[1:]
        
        # flatten the abm data for analysis
        data_abm = data_abm.flatten()
        
        # error vectors (absolute error is in minutes)        
        aerr = 1.0 * abs( data - data_abm )
        rerr = aerr / data
    
        # get the L2 error
        aerr_abm[i] = np.sqrt( np.dot(aerr, aerr) ) / N
        rerr_abm[i] = np.sqrt( np.dot(rerr, rerr) ) / N
        
    return aerr_abm, rerr_abm


def get_moments(abm_data):

    """
    This function takes in all of the ABMHAP simulation data [in minutes] for a particular activity and returns \
    the moments (mean and standard deviation) [hours] for each person in the simulation.

    :param list abm_data: the list of ABMHAP of activity data in minutes per person

    :return: the mean and standard deviation for each person in the simulation
    :rtype: numpy.ndarray, numpy.ndarray
    """

    HOUR_2_MIN  = temporal.HOUR_2_MIN

    # store the data as hours
    mu  = [ np.mean(x)/HOUR_2_MIN for x in abm_data ]
    std = [ np.std(x)/HOUR_2_MIN for x in abm_data ]

    mu  = np.array(mu)
    std = np.array(std)

    return mu, std

def get_proper_data(df_dt, df_start, df_record, x):

    """
    This function gets the duration, start time, and record data for a given activity

    .. warning::
        This function may not be  used.

    :param pandas.core.frame.DataFrame df_dt: the duration statistical data for a given activity
    :param pandas.core.frame.DataFrame df_start: the start time statistical data for a given activity
    :param pandas.core.frame.DataFrame df_record: the CHAD records for the given activity
    :param chad_params.CHAD_params x: the parameters that limit sampling the CHAD data
    :return:
    """

    # get the boolean indices for the data that lies within the sampling parameters
    b1  = (df_start['mu'] >= x.start_mean_min).values
    b2  = (df_start['mu'] <= x.start_mean_max).values
    b3  = (df_start['std'] <= x.start_std_max).values

    # should I add filtering for the standard deviation?

    # only true at indices if both b1 and b2 are true
    b       = b1 * b2 * b3
    start   = df_start[b]

    # get the boolean indices for the data that lies within the sampling parameters
    b1  = (df_dt['mu'] >= x.dt_mean_min).values
    b2  = (df_dt['mu'] <= x.dt_mean_max).values
    b3  = (df_dt['std'] <= x.dt_std_max).values

    # only true at indices if both b1 and b2 are true
    b   = b1 * b2 * b3
    dt  = df_dt[b]

    # get persons identifiers that correspond to the sampling parameters for start time and duration
    pid = list( set(start.PID.unique()) & set(dt.PID.unique()) )

    # get the records of people who are used in the empirical distribution of BOTH start times AND durations
    f       = lambda x: x in pid
    idx     = df_record.PID.apply(f)
    record  = df_record[idx]

    return dt, start, record

    return x

def get_verification_info(demo, key_activity, sampling_params, fname_stats=None):

    """
    This function gets the CHAD parameters for each household

    .. note::
        Sometimes record dataframe can be null. I should remove the sampling of the record code **and** \
        output

    :param int demo: the demographic identifier
    :param int key_activity: the identifier for the activity (from my_globals)
    :param list sampling_params: the parameters that the limit the \
    sampling of the CHAD data
    :type sampling_params: list of :class:`chad_params.CHAD_params`

    :return: the activity moments of the start time data from CHAD used to verify the ABMHAP, \
    the activity moments of the end time data from CHAD used to verify the ABMHAP, \
    the activity moments of the duration data from CHAD used to verify the ABMHAP, \
    the activity records data from CHAD used to verify the ABMHAP

    :rtype: pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, \
    pandas.core.frame.DataFrame, pandas.core.frame.DataFrame
    """

    # get the zipfile name of the demographic
    fname_zip = dmg.FNAME_DEMOGRAPHY[demo]

    # open zip file of demographic data
    z = zipfile.ZipFile(fname_zip, mode='r')

    # get the verification file names
    if fname_stats is None:
        fname_stats     = chad.FNAME_STATS_OMNI[key_activity]
        fname_record    = chad.FNAME_RECORD_OMNI[key_activity][0]
    else:
        fname_record    = fname_stats[chad.RECORD]

    #
    # load the the data
    #

    # get the CHAD file names
    fname_start, fname_end , fname_dt = fname_stats[chad.START], fname_stats[chad.END], fname_stats[chad.DT]

    # load the data
    df_start    = pd.read_csv( z.open(fname_start) )
    df_end      = pd.read_csv( z.open(fname_end) )
    df_dt       = pd.read_csv( z.open(fname_dt) )
    df_record   = pd.read_csv( z.open(fname_record) )

    # close zip file
    z.close()

    # sample by df_dt, df_start
    # sampling parameters from the first household
    s_params = sampling_params[0]

    # if doing a trial containing multiple activities (aka, contains a list instead of a \
    # chad_param.CHAD_params object)
    if  ( type(s_params) is dict):
        s_params    = s_params[key_activity]

    if s_params.do_start:
        df_start    = s_params.get_start(df_start)

    if s_params.do_end:
        df_end      = s_params.get_end(df_end)

    if s_params.do_dt:
        df_dt       = s_params.get_dt(df_dt)

    do_periodic = False
    if key_activity == mg.KEY_SLEEP:
        do_periodic = True

    # get the CHAD records
    df_record = s_params.get_record(df_record, do_periodic)

    return df_start, df_end, df_dt, df_record

def save_figures(figs, fnames):

    """
    This function saves figures in a python pickle file, so that the data \
    may be accessed again.

    :param list figs: figures for duration and start time for an activity
    :type figs: list of figures
    :param list fnames: file names to save the data in figs
    :type fnames: list of str
    :param str fdir: the directory in which to save the files

    :return:
    """

    # save the files
    for fig, fname in zip(figs, fnames):

        # create the save file directory if it does not exist
        os.makedirs(os.path.dirname(fname), exist_ok=True)

        # save the figure
        pickle.dump(fig, open(fname, 'wb'))

    return