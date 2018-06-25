
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

This notebook is **only used for development**.

This file does the following: For a given demographic group, plots the
distribution of raw longitudinal or solo data from the Consolidated
Human Activity Database (CHAD) for a given Agent-Based Model of Human
Activity Patterns (ABMHAP) activity

1. Plots the CHAD record data and the mean data (for each unique person)

2. Plot the distribution that the ABM sees after filtering the CHAD data

import

.. code:: ipython3

    import sys
    sys.path.append('..\\source')
    sys.path.append('..\\run_chad')
    
    # plotting capability
    import matplotlib.pylab as plt
    
    # dataframe capability
    import pandas as pd
    
    # ABMHAP modules
    import my_globals as mg
    import chad_demography_adult_work as cdaw
    import chad_demography_adult_non_work as cdanw
    import chad_demography_child_school as cdcs
    import chad_demography_child_young as cdcy
    import chad_params as cp
    import demography as dmg
    
    import activity
    
    from datum import histogram

function

.. code:: ipython3

    def distribution_record(x, alpha=1.0):
        
        # x is the CHAD_demography object
        
        xlabel = 'Time [h]'
        ylabel = 'Relative Frequency'
        
        f = mg.to_periodic
        
        for k in x.keys:    
        
            # find information that is in periodic time
            do_periodic = False
            if k == mg.KEY_SLEEP:
                do_periodic = True
                    
            # try to avoid simultaneous use of the colors red and green
            fig, axes = plt.subplots(2,2)
    
            # title
            fig.suptitle(activity.INT_2_STR[k] )
    
            # file names & data
            fname = chooser[k] + '\\record.csv'
            
            # chad parameters
            cp_param = x.int_2_param[k]
    
            # raw data 
            raw = pd.read_csv(fname)
    
            # abm data
            abm = cp_param.get_record(raw, do_periodic=do_periodic)
    
            #
            # plot the start time
            #
            ax = axes[0, 0]
            ax.set_title('Start')
            
            # the data to plot
            x_raw, x_abm = raw.start.values, abm.start.values
        
            if do_periodic:
                x_raw, x_abm = f(x_raw, do_hours=True), f(x_abm, do_hours=True)
                            
            histogram(ax, x_raw, color='blue', alpha=alpha, label='CHAD')
            histogram(ax, x_abm, color='cyan', alpha=alpha, label='ABM')
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.legend(loc='best')
    
            #
            # plot the end time
            #
            ax = axes[0, 1]
            ax.set_title('End')
            
            # the data to plot
            x_raw, x_abm = raw.end.values, abm.end.values
            
            if do_periodic:
                x_raw, x_abm = f(x_raw, do_hours=True), f(x_abm, do_hours=True)
                        
            histogram(ax, x_raw, color='green', alpha=alpha, label='CHAD')
            histogram(ax, x_abm, color='lightgreen', alpha=alpha, label='ABM')
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.legend(loc='best')
    
            # 
            # plot the duration
            #
            ax = axes[1, 0]
            ax.set_title('Duration')
                    
            histogram(ax, raw.dt.values, color='red', alpha=alpha, label='CHAD')
            histogram(ax, abm.dt.values, color='pink', alpha=alpha, label='ABM')
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.legend(loc='best')
        
        return
    
    def distribution_means(x, alpha=1.0):
        
        # x is CHAD_demography object
        
        xlabel = 'Time [h]'
        ylabel = 'Relative Frequency'
        
        f = mg.to_periodic
                    
        for k in x.keys:
            
            # handle events that occur over midnight
            do_periodic = False        
            if k == mg.KEY_SLEEP:
                do_periodic = True
                
            # try to avoid simultaneous use of the colors red and green
            fig, axes = plt.subplots(2,2)
    
            # title
            fig.suptitle(activity.INT_2_STR[k] )
    
            # file names
            f_path = chooser[k]
            f_start = f_path + '\\stats_start.csv'
            f_end = f_path + '\\stats_end.csv'
            f_dt = f_path + '\\stats_dt.csv'
    
            # ABM names
            cp_param = x.int_2_param[k]
    
            # for solo data
            #cp_param.N = 1
            
            # load the data
            start, end, dt = pd.read_csv(f_start), pd.read_csv(f_end), pd.read_csv(f_dt)
            abm_start, abm_end, abm_dt = cp_param.get_start(start), cp_param.get_end(end), cp_param.get_dt(dt)
    
            #
            # plot the start time
            #
            ax = axes[0, 0]
            ax.set_title('Mean Start')
            
            # the data
            x_raw, x_abm = start.mu.values, abm_start.mu.values
            
            if do_periodic:
                x_raw, x_abm = f(x_raw, do_hours=True), f(x_abm, do_hours=True)
                
            histogram(ax, x_raw, color='blue', alpha=alpha, label='CHAD')
            histogram(ax, x_abm, color='cyan', alpha=alpha, label='ABM')
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.legend(loc='best')
    
            #
            # plot the end time
            #                
            ax = axes[0, 1]
            ax.set_title('Mean End')
            
            # the data
            x_raw, x_abm = end.mu.values, abm_end.mu.values
            
            if do_periodic:
                x_raw, x_abm = f(x_raw, do_hours=True), f(x_abm, do_hours=True)
                
            histogram(ax, x_raw, color='green', alpha=alpha, label='CHAD')
            histogram(ax, x_abm, color='lightgreen', alpha=alpha, label='ABM')
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.legend(loc='best')
    
            # plot the duration
            ax = axes[1, 0]
            ax.set_title('Mean Duration')
            histogram(ax, dt.mu.values, color='red', alpha=alpha, label='CHAD')
            histogram(ax, abm_dt.mu.values, color='pink', alpha=alpha, label='ABM')
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.legend(loc='best')
            
        return

run

.. code:: ipython3

    #
    # choose the demographic
    #
    demo = dmg.CHILD_YOUNG
    
    #
    # load paths
    #
    fin, fout = dmg.INT_2_FIN_FOUT_LARGE[demo]
    
    fpath = fout + '\\longitude'
    
    # choose the fpaths
    chooser = {mg.KEY_SLEEP: fpath + '\\sleep\\all',
               mg.KEY_WORK: fpath + '\\work',
               mg.KEY_EAT_BREAKFAST: fpath + '\\eat_breakfast',
               mg.KEY_EAT_LUNCH: fpath + '\\eat_lunch',
               mg.KEY_EAT_DINNER: fpath + '\\eat_dinner',
               mg.KEY_EDUCATION: fpath + '\\education',
               mg.KEY_COMMUTE_TO_WORK: fpath + '\\commute_to_work',
               mg.KEY_COMMUTE_FROM_WORK: fpath + '\\commute_from_work',
              }
    
    cp_chooser = {mg.KEY_SLEEP: cp.SLEEP,
                  mg.KEY_WORK: cp.WORK,
                  mg.KEY_EAT_BREAKFAST: cp.EAT_BREAKFAST,
                  mg.KEY_EAT_LUNCH: cp.EAT_LUNCH,
                  mg.KEY_EAT_DINNER: cp.EAT_DINNER,
                  mg.KEY_EDUCATION: cp.EDUCATION,
                  mg.KEY_COMMUTE_TO_WORK: cp.COMMUTE_TO_WORK,
                  mg.KEY_COMMUTE_FROM_WORK: cp.COMMUTE_FROM_WORK,              
                 }
    
    demo_chooser = {dmg.ADULT_WORK: cdaw.CHAD_demography_adult_work(),
                    dmg.ADULT_NON_WORK: cdanw.CHAD_demography_adult_non_work(),
                    dmg.CHILD_SCHOOL: cdcs.CHAD_demography_child_school(),
                    dmg.CHILD_YOUNG: cdcy.CHAD_demography_child_young(),}
    
    chad_demo = demo_chooser[demo]

.. code:: ipython3

    #
    # the activity identifiers
    #
    
    # the alpha used for plotting
    alpha = 0.65
    
    # the activities to see
    keys_all  = mg.KEYS_ACTIVITIES
    keys_work = [mg.KEY_COMMUTE_TO_WORK, mg.KEY_WORK, mg.KEY_COMMUTE_FROM_WORK]
    keys_edu  = [mg.KEY_EDUCATION]
    keys_eat  = [mg.KEY_EAT_BREAKFAST, mg.KEY_EAT_LUNCH, mg.KEY_EAT_DINNER]
    
    #keys_temp = [mg.KEY_COMMUTE_TO_WORK, mg.KEY_COMMUTE_FROM_WORK, mg.KEY_EDUCATION]
    keys_temp = keys_eat + [mg.KEY_SLEEP]
    
    # the keys
    keys = chad_demo.keys

plotting

.. code:: ipython3

    #
    # plot the CHAD record distribution
    #
    distribution_record(chad_demo,  alpha=alpha)
    plt.show()

.. code:: ipython3

    #
    # plot the CHAD inter-individual mean distribution
    #
    distribution_means(chad_demo, alpha=alpha)
    plt.show()
