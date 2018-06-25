sleep_new notebook
==================

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
    # March 22, 2018

This file goes through the data from the Consoldiated Human Activity
Database (CHAD) and gets information relevent to **sleeping** and
processes the data for use in the Agent-Based Model of Human Activity
Patterns (ABMHAP) for each demographic. More specficially, this file
does the following:

For a given demographic,

1. This function goes through the CHAD data and finds the sleep-activity
   data

2. The CHAD activity data are seperated into start time, end time,
   duration, and CHAD record data

3. The CHAD activity data is saved into longitudinal data and
   single-activity data

Import

.. code:: ipython3

    import sys
    sys.path.append('..\\source')
    
    # plotting capability
    import matplotlib.pylab as plt
    
    # ABMHAP modules
    import demography as dmg
    import my_globals as mg
    import datum

.. code:: ipython3

    %matplotlib notebook

Load

.. code:: ipython3

    #
    # demographic
    # 
    demo = dmg.CHILD_YOUNG
    
    # the input file and output file directory
    fname_input, fpath_output = dmg.INT_2_FIN_FOUT_LARGE[key]
    
    # load the data
    data = dmg.load(fname_input)

Process data

.. code:: ipython3

    # analyze the data
    d_slumber = datum.analyze_sleep(data)

.. code:: ipython3

    # get the statistical data
    d = d_slumber
    
    slumber, stats_dt, stats_start, stats_end = d['data'], d['stats_dt'], d['stats_start'], d['stats_end']
    
    slumber_we, stats_we_dt, stats_we_start, stats_we_end = \
    d['data_weekend'], d['stats_we_dt'], d['stats_we_start'], d['stats_we_end']
    
    slumber_wd, stats_wd_dt, stats_wd_start, stats_wd_end = \
    d['data_weekday'], d['stats_wd_dt'], d['stats_wd_start'], d['stats_wd_end']

save the data

.. code:: ipython3

    # the minimum number of activity entries per individual to be considered longitudinal
    N_long = 2
    
    # there is not much longitudinal information of pre-school children
    if demo in [dmg.CHILD_YOUNG]:
        N_long = 1
        
    # choose to save longitudinal data or single-day data    
    chooser = {True: (N_long, fpath_output + '\\longitude'), 
               False: (1, fpath_output + '\\solo'), } 
    
    # whether to save the longitudinal data (if True) or the single-day data (if False)
    do_long = True

.. code:: ipython3

    # save the and solo data
    do_save = False
    
    if do_save:
        
        N, fpath = chooser[do_long]
        
        if do_long:        
            data_all = datum.get_longitude(stats_dt, stats_start, stats_end, slumber, N=N)
            data_weekend = datum.get_longitude(stats_we_dt, stats_we_start, stats_we_end, slumber_we, N=N)
            data_weekday = datum.get_longitude(stats_wd_dt, stats_wd_start, stats_wd_end, slumber_wd, N=N)
        else:
            data_all = datum.get_solo(stats_dt, stats_start, stats_end, slumber)
            data_weekend = datum.get_solo(stats_we_dt, stats_we_start, stats_we_end, slumber_we)
            data_weekday = datum.get_solo(stats_wd_dt, stats_wd_start, stats_wd_end, slumber_wd)
        
        # the directories the data should be saved in    
        fpath = fpath + '\\sleep'
        fpaths = [ fpath + '\\all', fpath + '\\non_workday', fpath + '\\workday' ]
            
        # the dictionaries holding the data
        data_list = [data_all, data_weekend, data_weekday]
        
        # save the data
        for fpath, d in zip(fpaths, data_list):
            
            stats_dt, stats_start, stats_end, record = d
            datum.save(fpath, record=record, stats_dt=stats_dt, stats_start=stats_start, stats_end=stats_end)
    
