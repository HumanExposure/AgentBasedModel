chad_parameter_figures notebook
===============================

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

WARNING:

this code may not be useful

This code plots the histograms of the distributions being sampled from
the CHAD data for each activity.

Import

.. code:: ipython3

    import sys
    sys.path.append('..\\source')
    sys.path.append('..\\processing')
    
    # plotting capability
    import matplotlib.pylab as plt
    
    # zipfile capability
    import zipfile
    
    # ABMHAP modules
    
    # general capability
    import my_globals as mg
    import chad_params as cp
    import demography as dmg
    
    import activity, analysis, chad, omni_trial, params

Run

.. code:: ipython3

    # the demographic
    demo = dmg.ADULT_WORK
    
    # sets of activities
    keys_all = mg.KEYS_ACTIVITIES
    
    # the activity codes related to not eating
    keys_not_eat = [mg.KEY_SLEEP, mg.KEY_WORK, mg.KEY_COMMUTE_TO_WORK, mg.KEY_COMMUTE_FROM_WORK]
    
    # the activity codes of the eating activities
    keys_eat = [mg.KEY_EAT_BREAKFAST, mg.KEY_EAT_LUNCH, mg.KEY_EAT_DINNER]
    
    # the chosen group of activities
    keys = keys_all

Loop through each activity and plot the histograms of start time, end
time, and duration. Note: the limitations for each activity depends on
which activity parameters are being sampled

.. code:: ipython3

    # loop through each activity and plot the histograms of start time, end time, and duration
    # Note: the limitations for each activity depends on which activity parameters are being sampled
    for k in keys:
        
        # the CHAD limiting parameters
        s_params = cp.OMNI[k]
        
        # get the data
        stats_start, stats_end, stats_dt, record = analysis.get_verification_info(demo=demo, key_activity=k,
                                                         sampling_params=[s_params])
        # number of the bins
        num_bins = 24
        
        # create subplots
        fig, axes = plt.subplots(2, 2)
    
        # title
        fig.suptitle( activity.INT_2_STR[k] )
        
        #
        # plot the mean start time distribution
        #
        ax = axes[0, 0]
        if k == mg.KEY_SLEEP:
            ax.hist(mg.to_periodic(stats_start.mu.values, do_hours=True), bins=num_bins, color='blue', label='start')
        else:
            ax.hist(stats_start.mu.values, bins=num_bins, color='blue', label='start')
        ax.set_xlabel('hours')
        ax.legend(loc='best')
                    
        #
        # plot the mean end time distribution
        #
        ax = axes[0, 1]
        ax.hist(stats_end.mu.values, bins=num_bins, color='green', label='end')
        ax.set_xlabel('hours')
        ax.legend(loc='best')
    
        #
        # plot the mean duration distribution
        #
        ax = axes[1, 0]
        ax.hist(stats_dt.mu.values, bins=num_bins, color='red', label='duration')
        ax.set_xlabel('hours')
        ax.legend(loc='best')
    
    # show plots
    plt.show()
