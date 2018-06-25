eat_new notebook
================

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
Database (CHAD) and gets information relevent to **eating breakfast**,
**eating lunch**, and **eating dinner** and processes the data for use
in the Agent-Based Model of Human Activity Patterns (ABMHAP) for each
demographic. More specficially, this file does the following:

For a given demographic,

1. This function goes through the CHAD data and finds the eat-activity
   data

2. The CHAD activity data are seperated into start time, end time,
   duration, and CHAD record data for the meals: breakfast, lunch, and
   dinner

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
    import datum

.. code:: ipython3

    %matplotlib notebook

Load data

.. code:: ipython3

    #
    # the demographic
    #
    key = dmg.CHILD_YOUNG
    
    # the input file and output file directory
    fname_input, fpath_output = dmg.INT_2_FIN_FOUT_LARGE[key]
    
    # load the data
    data = dmg.load(fname_input)

Process the data

.. code:: ipython3

    # analyze the eat-activity data
    d_breakfast, d_lunch, d_dinner = datum.analyze_eat(data)

Plot the distribution

.. code:: ipython3

    #
    # plot the distribution
    #
    d = d_dinner
    
    temp = d['data']
    
    ylabel = 'Relative Frequency'
    xlabel = 'Time [h]'
    
    fig, axes = plt.subplots(2,2)
    
    # start time
    ax = axes[0,0]
    
    datum.histogram(ax, temp.start.values, color='b', label='start')   
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.legend(loc='best')
    
    # end time
    ax = axes[0, 1]
    datum.histogram(ax, temp.end.values, color='g', label='end')
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.legend(loc='best')
    
    
    # duration
    ax = axes[1, 0]
    datum.histogram(ax, temp.dt.values, color='r', label='duration')
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)      
    ax.legend(loc='best')
    
    plt.show()

Save the data

.. code:: ipython3

    # choose to save longitudinal data or single-day data
    chooser = {True: (2, fpath_output + '\\longitude'), 
               False: (1, fpath_output + '\\solo'), } 
    
    # whether to save the longitudinal data (if True) or the single-day data (if False)
    do_long = False

.. code:: ipython3

    #
    # save the data 
    
    do_save = False
    
    if do_save:
    
        N, fpath = chooser[do_long]
        
        # the directories the data should be saved in
        fpaths = [fpath + '\\eat_breakfast', fpath + '\\eat_lunch', fpath + '\\eat_dinner']
        
        # the dictionaries holding the data
        data_dict = [d_breakfast, d_lunch, d_dinner]
        
            
        # save the data
        for fpath, d in zip(fpaths, data_dict):
            
            stats_dt, stats_start, stats_end, record = d['stats_dt'], d['stats_start'], d['stats_end'], d['data']
            
            if do_long:
                dt, start, end, rec = datum.get_longitude(stats_dt, stats_start, stats_end, record, N=N)
            else:
                dt, start, end, rec = datum.get_solo(stats_dt, stats_start, stats_end, record)
            
            datum.save(fpath, record=rec, stats_dt=dt, stats_start=start, stats_end=end)
            

