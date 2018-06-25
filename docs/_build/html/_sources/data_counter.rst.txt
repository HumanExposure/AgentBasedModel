data_counter notebook
=====================

.. code:: ipython3

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
    # March 20, 2018

This file loads the activity-data assigned with each activity for the
respective demographic group. For each activity, then the file counts
the amount of Consolidated Human Acitivyt Databse (CHAD) individuals
from both the single day and the longitudinal entries.

Import

.. code:: ipython3

    import os, sys
    sys.path.append('..\\source')
    sys.path.append('..\\processing')
    
    # plotting capability
    import matplotlib.pylab as plt
    
    # data frame capability
    import pandas as pd
    
    # zipfile capability
    import zipfile
    
    # ABMHAP capability 
    import my_globals as mg
    import chad_demography_adult_non_work as cdanw
    import chad_demography_adult_work as cdaw
    import chad_demography_child_school as cdcs
    import chad_demography_child_young as cdcy
    import demography as dmg
    
    import activity, chad, datum

.. code:: ipython3

    %matplotlib auto


.. parsed-literal::

    Using matplotlib backend: Qt5Agg
    

Functions

.. code:: ipython3

    def load_data(z, fnames):
        
        """
        This function loads the activity parameter data (start time, end time, \
        duration, and CHAD records) for an activity for the demographic.
        
        :param zipfile.Zipfile z: the ZipFile object for a given demographic group
        :param fnames: the file names for CHAD activity-moments data
        :type fnames: dict mapping int to str
        
        :return: the start time, end time, duration, and record data for a \
        given activity
        :rtype: numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray
        """
        
        start = pd.read_csv( z.open( fnames[chad.START], mode='r' ) )
        end = pd.read_csv( z.open( fnames[chad.END], mode='r' ) )
        dt = pd.read_csv( z.open( fnames[chad.DT], mode='r' ) )
        record = pd.read_csv( z.open( fnames[chad.RECORD], mode='r' ) )
        
        return start, end, dt, record
    
    def filter_data(df, the_filter, start_periodic=False, end_periodic=False):
        
        """
        This function takes CHAD data for an activity and filters the CHAD data \
        the satisfy the sampling parameters. This function returns the CHAD data \
        suitable for use in parameterizing ABMHAP.
        
        :param pandas.core.frame.DataFrame df: the record data for a given activity
        :param the_filter: for a given activity code, get the respective parameters \
        for sampling CHAD data    
        :type the_filter: dict mapping int to :class:`chad_params.CHAD_params`
        :param bool start_periodic: whether (if True) or not (if False) the start \
        time should be in a [-12, 12) format
        :param bool end_periodic: whether (if True) or not (if False) the end \
        time should be in a [-12, 12) format
        
        :return: the CHAD data that satisfy the sampling parameters for the following:
        start time moments, end time moments, duration momments, and records 
        :rtype: pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, \
        pandas.core.frame.DataFrame, pandas.core.frame.DataFrame
        """
            
        # the_filter are the sampling paramters for the activity
        
        # the start time and end time data
        x_start, x_end = df.start, df.end
        
        # change the start time data to a [-12, 12) format
        if start_periodic:
            x_start = mg.to_periodic(x_start, do_hours=True)
        
        # change the start time data to a [-12, 12) format
        if end_periodic:
            x_end = mg.to_periodic(x_end, do_hours=True)
        
        # the indices that satisfy the requirements for mean start time, end time, and 
        # and duration respectively
        idx = ( x_start >= the_filter.start_mean_min ) & ( x_start <= the_filter.start_mean_max ) \
        & ( df.end >= the_filter.end_mean_min ) & ( df.end <= the_filter.end_mean_max ) \
        & ( df.dt >= the_filter.dt_mean_min ) & ( df.dt <= the_filter.dt_mean_max ) 
    
        # get the record data that satisfy the proper sampling ranges
        record = df[idx]
        
        # the personal identifier values within the CHAD data
        pid = record.PID.values
        
        # obtain the duraation, start time, and end time values from the filtered CHAD records
        dt, start, end = record.dt.values, record.start.values, record.end.values
    
        # the CHAD data that satisfy the sampling parameters for the start time moments
        stats_start = datum.get_stats(pid, start, do_periodic=start_periodic)
        
        # the CHAD data that satisfy the sampling parameters for the end time moments
        stats_end   = datum.get_stats(pid, end, do_periodic=start_periodic)
        
        # the CHAD data that satisfy the sampling parameters for the duration moments
        stats_dt    = datum.get_stats(pid, dt)
        
        return stats_start, stats_end, stats_dt, record
    
    def get_activity_data(z, fnames, the_filter, start_periodic=False, end_periodic=False):
        
        """
        This function loads CHAD data for an activity and filters the CHAD data \
        the satisfy the sampling parameters. This function returns the CHAD data \
        suitable for use in parameterizing ABMHAP.
        
        :param zipfile.Zipfile z: the ZipFile object for a given demographic group
        :param fnames: the file names for CHAD activity-moments data
        :type fnames: dict mapping int to str
        :param the_filter: for a given activity code, get the respective parameters \
        for sampling CHAD data    
        :type the_filter: dict mapping int to :class:`chad_params.CHAD_params`
        :param bool start_periodic: whether (if True) or not (if False) the start \
        time should be in a [-12, 12) format
        :param bool end_periodic: whether (if True) or not (if False) the end \
        time should be in a [-12, 12) format
        
        :return: the CHAD data that satisfy the sampling parameters for the following:
        start time moments, end time moments, duration momments, and records 
        :rtype: pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, \
        pandas.core.frame.DataFrame, pandas.core.frame.DataFrame
        """
        
        # get the longitudinal data
        start, end, dt, record = load_data(z, fnames)
           
        # filter the records and get the moments 
        stats_start, stats_end, stats_dt, record = \
        filter_data(record, the_filter, start_periodic=start_periodic, end_periodic=end_periodic)
        
        return stats_start, stats_end, stats_dt, record
    
    def get_fnames(demo, k, do_long):
        
        """
        For a demographic, this function obtains the file names of the \
        activity data for longitudinal or single-day data.
        
        :param demography.Demography demo: the demographic of choice to access the CHAD data
        :param int k: the activity code
        :param bool do_long: whether (if True) to load the longitduinal data. If not (False), \
        load the single-day data.
        
        :return: the file names for CHAD activity-moments data for longitudinal data \
        or single-day data
        :rtype: dict of int to str   
        """
        
        # get the file names of the longitudinal data
        fnames = demo.fname_stats[k]
        
        if not do_long:
            # get the file names of the single-day data
            x = [ ( key, value.replace('longitude', 'solo') ) for key, value in fnames.items() ]
            fnames = dict( x )    
            
        return fnames
    
    def plot(data, ax, label):
        
        """
        This function gets data and plots the empiricial cumulative dsitribution \
        function (CDF) of the data.
        
        :param numpy.ndarray data: the data to create a CDF of
        :param matplotlib.axes._subplots.AxesSubplot ax: the subplot that's plotting
        :param str label: the label for the data
        """
        
        # get an empiricial CDF based on the data
        x, y = mg.get_ecdf(data)
       
        # plot the CDF
        ax.plot(x, y, label=label)
        
        # show legend
        ax.legend(loc='best')
        
        return

Run

Load data via demographic

.. code:: ipython3

    # map a demographic type to the respective CHAD_demography object
    chooser = {dmg.ADULT_WORK: cdaw.CHAD_demography_adult_work(),
               dmg.ADULT_NON_WORK: cdanw.CHAD_demography_adult_non_work(), 
               dmg.CHILD_SCHOOL: cdcs.CHAD_demography_child_school(), 
               dmg.CHILD_YOUNG: cdcy.CHAD_demography_child_young()}

.. code:: ipython3

    # choose the demography
    demo_type = dmg.CHILD_SCHOOL
    
    # get the name of the compressed data file
    fname_zip = dmg.FNAME_DEMOGRAPHY[demo_type]
    
    # create the ZipFile object for the respective demographic group
    z = zipfile.ZipFile( fname_zip )
    
    # set the demographic object
    demo = chooser[demo_type]
    
    # store all of the activity-keys for the demographic
    keys = demo.keys
    
    # print flag
    do_print = False

Count the number of CHAD persons for each activity

.. code:: ipython3

    # if true, count the number of people with longitudinal data (at least 2 entries)
    # if false, count the number of people with single data (only 1 entry)
    do_long = True
    
    
    # for each activity in the demographic, count the amount of data
    for k in keys:
        
        # set whether to set the time to periodic time [-12, 12) hours instead of [0, 24) hours
        do_periodic = False
        if k == mg.KEY_SLEEP:
            do_periodic = True
            
        # sampling / filtering params
        the_filter = demo.int_2_param[k]
        
        # get the names of the statistics files
        fnames = get_fnames(demo, k, do_long)    
            
        # load and filter data fitting for the demographic
        start, end, dt, record = get_activity_data(z, fnames, the_filter, start_periodic=do_periodic)    
        
        # print the activity
        if do_print:
            print( activity.INT_2_STR[k] )
        
            # count the number of longitudinal or single-day data, respectively
            if do_long:
                print( start[start.N > 1].shape)
            else:
                print( start[start.N == 1].shape)


.. parsed-literal::

    ..\processing\datum.py:689: RuntimeWarning: invalid value encountered in double_scalars
      cv  = std / np.abs(mu)
    ..\processing\datum.py:689: RuntimeWarning: divide by zero encountered in double_scalars
      cv  = std / np.abs(mu)
    

Plot the data

.. code:: ipython3

    # create the subplots
    fig, axes = plt.subplots(3)
    
    # the title
    fig.suptitle(activity.INT_2_STR[k])
    
    #
    # plot the start time data
    #
    
    # select the subplot
    ax = axes[0]
    
    # the start time data
    plot(start.mu.values, ax, 'start')
    
    #
    # plot the end time data
    #
    
    # select the subplot
    ax = axes[1]
    
    # the end time data
    plot(end.mu.values, ax, 'end')
    
    #
    # plot the duration data
    #
    
    # select the subplot
    ax = axes[2]
    
    # the duration data
    plot(dt.mu.values, ax, 'duration')
    
    # show plots
    plt.show()

