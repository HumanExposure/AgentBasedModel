commute_work notebook
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
    # March 22, 2018

This file goes through the data from the Consoldiated Human Activity
Database (CHAD) and gets information relevent to **commuting to work**,
**commuting from work**, and **working** and processes the data for use
in the Agent-Based Model of Human Activity Patterns (ABMHAP) for the
working adult demographic. More specficially, this file does the
following:

1. This function goes through the CHAD data and finds the commute and
   work-activity data

2. The data is chosen such that events are chosen such that the work
   events are sandwiched between the commute to work and commtue from
   work event

3. The CHAD activity data are seperated into start time, end time,
   duration, and CHAD record data

4. The CHAD activity data is saved into longitudinal data and
   single-activity data

Import

.. code:: ipython3

    import sys
    sys.path.append('..\\source')
    
    # plotting capability
    import matplotlib.pylab as plt
    
    # ABMHAP modules
    import demography as dmg
    import datum

.. code:: ipython3

    %matplotlib notebook

Load

.. code:: ipython3

    #
    # demographic
    #
    # the input file and output file directory
    key = dmg.ADULT_WORK
    
    # the input file and output file directory
    fname_input, fpath_output = dmg.INT_2_FIN_FOUT_LARGE[key]
    
    # load the data
    data = dmg.load(fname_input)

Processing data

.. code:: ipython3

    # analyze the commuting data
    d, d_to_work, d_from_work, d_at_work = datum.analyze_commute(data)

Saving Data

.. code:: ipython3

    # choose to save longitudinal data or single-day data
    #
    # note that N for the LONGITUDINAL DATA is 1
    # this was done becaause there is NOT ENOUGH LONGITUDINAL DATA for adults and working
    #
    chooser = {True: (1, fpath_output + '\\longitude'), 
               False: (1, fpath_output + '\\solo'), } 
    
    # whether to save the longitudinal data (if True) or the single-day data (if False)
    # there is not enough longitudinal data to have a longitudinal model
    do_long = True

.. code:: ipython3

    # save the longitude data 
    do_save = False
    
    if do_save:
    
        N, fpath = chooser[do_long]    
        
        # the directories the data should be saved in
        fpaths = [fpath + '\\commute_to_work', fpath + '\\commute_from_work', fpath + '\\work']
        
        # the dictionaries holding the data
        data_dict = [d_to_work, d_from_work, d_at_work]
        
        # save the data
        for fpath, d in zip(fpaths, data_dict):
            
            stats_dt, stats_start, stats_end, record = d['stats_dt'], d['stats_start'], d['stats_end'], d['data']
            
            if do_long:
                dt, start, end, rec = datum.get_longitude(stats_dt, stats_start, stats_end, record, N=N)
            else:
                dt, start, end, rec = datum.get_solo(stats_dt, stats_start, stats_end, record)
            
            datum.save(fpath, record=rec, stats_dt=dt, stats_start=start, stats_end=end)
            
