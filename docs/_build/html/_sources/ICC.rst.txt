
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

This code is **NOT** part of the Agent-Based Model of Human Activity
Patterns (ABMHAP). This code does some calculations on calculating the
Intraclass coefficient (ICC) statistic.

import

.. code:: ipython3

    import os, sys
    sys.path.append('..\\source')
    sys.path.append('..\\processing')
    
    # math capabilities
    import numpy as np
    
    # data frame capability
    import pandas as pd
    
    # ABMHAP capabilities
    import my_globals as mg
    import chad_demography_adult_non_work as cdanw
    import chad_demography_adult_work as cdaw
    import chad_demography_child_school as cdcs
    import chad_demography_child_young as cdcy
    import demography as dmg
    
    import activity, analyzer

functions

.. code:: ipython3

    # can be used with NaNs
    
    def ICC(df, do_print=False):
        
        n_rows, n_cols = df.shape
        
        mu_cols  = df.mean()
        var_cols = df.var()
        
        # the number of non Nans per column
        count_cols = np.array( [ sum(~df[x].isnull()) for x in df.columns] )
        
        mu_rows  = df.transpose().mean()
        var_rows = df.transpose().var()
        
        # the number of non Nans per row
        count_rows = np.array( [ sum(~df.transpose()[x].isnull()) for x in df.transpose().columns] )
            
        # total number of non NaNs
        n_total = np.sum(count_cols)
        
        
        #
        # total variation
        #
    
        # total mean
        mu_total = np.dot(count_cols, mu_cols)/count_cols.sum()
    
        # each non NaN value - mean
        temp = df.values.flatten()[ ~df.isnull().values.flatten() ] - mu_total
    
        # sum of squares error
        SS_total = np.dot(temp, temp)
    
        # degrees of freedom
        df_total = n_total - 1
    
        # mean square error
        MS_total = SS_total / df_total
        
        #
        # between group (row) variation
        #
        temp = mu_rows - mu_total
        
        SS_rows = np.outer(temp, temp).diagonal().dot(count_rows)
    
        # degrees of freedom
        df_rows = n_rows - 1
    
        # mean square
        MS_rows = SS_rows / df_rows
        
        #
        # between group (column) variation
        #
        temp = mu_cols - mu_total
        
        SS_cols = np.outer(temp, temp).diagonal().dot(count_cols)
    
        # degrees of freedom
        df_cols = n_cols - 1
    
        # mean square
        MS_cols = SS_cols / df_cols
    
        #
        # error
        #
        SS_e = 0
        for i in range(n_rows):
            for j in range(n_cols):
                if not df.isnull().iloc[i, j]:
                    SS_e += (df.iloc[i, j] - mu_rows[i] - mu_cols[j] + mu_total)**2
        
        # degrees of freedom
        df_e = (n_rows - 1)*(n_cols - 1)
        
        MS_e = SS_e / df_e
        
        #
        # variability
        #
    
        variability_rows = (MS_rows - MS_e) / n_cols
        variability_cols = (MS_cols - MS_e) / n_rows
        variability_e = MS_e
    
        variability_total = (variability_rows + variability_cols + variability_e)
    
        icc_rows = variability_rows / variability_total
        icc_cols = variability_cols / variability_total
        
        msg = ''
        if do_print:        
            msg = msg + ( 'SS_total:\t%.2f\t\tMS_total:\t%.2f\n' % (SS_total, MS_total) )
            msg = msg + ( 'SS_rows:\t%.2f\t\tMS_rows:\t%.2f\n'% (SS_rows, MS_rows) )
            msg = msg + ( 'SS_cols:\t%.2f\t\tMS_cols:\t%.2f\n' % (SS_cols, MS_cols) )
            msg = msg + ( 'SS_e:\t\t%.2f\t\tMS_e:\t\t%.2f\n' % (SS_e, MS_e) )
            msg = msg + ( 'ICC_rows:\t%.3f\n' % icc_rows )
            msg = msg + ( 'ICC_cols:\t%.3f\n' % icc_cols )
            
        return msg
    
    def anova_help(df, do_print=False):
        
        n_rows, n_cols = df.shape
    
        mu_cols = df.mean().values
        var_cols = df.var().values
    
        count_cols = np.array( [ sum(~df[x].isnull()) for x in df.columns] )
        n_total = np.sum(count_cols)
    
        #
        # total variation
        #
    
        # total mean
        mu_total = np.dot(count_cols, mu_cols)/count_cols.sum()
    
        # each non NaN value - mean
        temp = df.values.flatten()[ ~df.isnull().values.flatten() ] - mu_total
    
        # sum of squares error
        SS_total = np.dot(temp, temp)
    
        # degrees of freedom
        df_total = n_total - 1
    
        # mean square error
        MS_total = SS_total / df_total
        
        #
        # total variation within each group
        #
        SS_w = 0
        for i, x in enumerate(df.columns):
            z = df[x]
            temp = z[~z.isnull()] - mu_cols[i]
            SS_w += np.dot(temp, temp)
    
        # degrees of freedom
        df_w = n_total - n_cols
    
        # mean square
        MS_w = SS_w / df_w     
        
        #
        # total variation within each group
        #
        SS_w = 0
        for i, x in enumerate(df.columns):
            z = df[x]
            temp = z[~z.isnull()] - mu_cols[i]
            SS_w += np.dot(temp, temp)
    
        # degrees of freedom
        df_w = n_total - n_cols
    
        # mean square
        MS_w = SS_w / df_w     
    
        #
        # total variation between the groups
        #
        temp = mu_cols - mu_total
        SS_b = np.outer(temp, temp).diagonal().dot(count_cols)
    
        # degrees of freedom
        df_b = n_cols - 1
    
        # mean square
        MS_b = SS_b / df_b
        
        if do_print:
            print('SS_total:\t%.2f\t\tMS_total:\t%.2f' % (SS_total, MS_total)  )
            print('SS_w:\t\t%.2f\t\tMS_w:\t\t%.2f'% (SS_w, MS_w) )
            print('SS_b:\t\t%.2f\t\tMS_b:\t\t%.2f' % (SS_b, MS_b) )
            
        return

run

.. code:: ipython3

    # get the file name
    fpath_load_data = mg.FDIR_MY_DATA + '\\03_29_2017\\n1024_d364'
    fname_load_data = fpath_load_data + '\\data_adult_work.pkl'
    print(fname_load_data)


.. parsed-literal::

    ..\my_data\03_29_2017\n1024_d364\data_adult_work.pkl
    

.. code:: ipython3

    # load the driver_result object
    x = mg.load(fname_load_data)
    
    df_list = x.get_all_data()
    
    demo = x.demographic

.. code:: ipython3

    chooser = {dmg.ADULT_WORK: cdaw.CHAD_demography_adult_work(),
               dmg.ADULT_NON_WORK: cdanw.CHAD_demography_adult_non_work(),
               dmg.CHILD_SCHOOL: cdcs.CHAD_demography_child_school(),
               dmg.CHILD_YOUNG: cdcy.CHAD_demography_child_young(),
              }
    chad_demo = chooser[demo]

.. code:: ipython3

    # how to acces a data frame
    #d = x.diaries[0][0] 0th dirary of the houses, the 0th person of that house
    #df = d.df

.. code:: ipython3

    
    FPATH = mg.FDIR_SAVE_FIG + '\\namdi_test'
    
    fpath = FPATH
    
    # plotting flags
    do_plot = True
    do_save_fig = False

.. code:: ipython3

    fdir = fpath
    do_print = True

.. code:: ipython3

    # get the activity codes for a given trial
    #act_codes = chad_demo.keys
    
    # testing
    act_codes = [mg.KEY_SLEEP]

.. code:: ipython3

    #
    # Run the ICC for each activity
    #
    
    # the directories for the respective activities. This is used for saving the figures
    fdirs = analyzer.get_verify_fpath(fdir, act_codes)
    
    if fdir is None:
        do_save_fig = False
    
    # offset, used for figure identifiers
    off = 0
    
    # number of days in the simulation
    n_days = len( df_list[0].day.unique() )
    
    fid = 0
    
    f = mg.to_periodic
    
    msg = ''
    
    print('Columns:\tagents')
    print('Rows:\t\tdays')
    
    for act in act_codes:
    
        if (do_print):
            msg = '---------------------------------\n'
            msg = msg + 'starting analysis for the ' + activity.INT_2_STR[act] + ' activity ...\n'
            msg = msg + '---------------------------------'
            print(msg)
    
        # this is to see if the analysis of the moments for start time needs to be in [-12, 12)
        # instead of [0, 24) format
        chooser     = {activity.SLEEP: True, }
        do_periodic = chooser.get(act, False)
            
        # get the raw ABM data
        abm_list = analyzer.get_simulation_data(df_list, act)
    
        # the ABM moments
        #abm_start_mean, abm_start_std, abm_end_mean, abm_end_std, abm_dt_mean, abm_dt_std \
        #    = analyzer.get_moments(abm_list, do_periodic)
    
        # the number of times each activity occurred
        counts = np.array( [len(dd) for dd in abm_list] )
        
        # ICC            
        if do_periodic:
            y_start = [ f(dd.start.values, do_hours=True) for dd in abm_list if not dd.empty]
            y_end   = [ f(dd.end.values, do_hours=True) for dd in abm_list if not dd.empty]
                
        else:
            y_start = [ dd.start.values for dd in abm_list if not dd.empty ]
            y_end   = [ dd.end.values for dd in abm_list if not dd.empty ]
    
        y_dt        = [ dd.dt.values for dd in abm_list if not dd.empty]
        
        
        df_start = pd.DataFrame(y_start).T
        df_end   = pd.DataFrame(y_end).T
        df_dt    = pd.DataFrame(y_dt).T
            
        print('\nstart time statistics')
        msg = ICC(df_start, do_print=True)
        print(msg)
        
        print('\nend time statistics')
        msg = ICC(df_end, do_print=True)
        print(msg)
        
        print('\nduration statistics')
        msg = ICC(df_dt, do_print=True)
        print(msg)


.. parsed-literal::

    Columns:	agents
    Rows:		days
    ---------------------------------
    starting analysis for the Sleep activity ...
    ---------------------------------
    
    start time statistics
    SS_total:	491114.08		MS_total:	1.32
    SS_rows:	51.02		MS_rows:	0.14
    SS_cols:	440340.49		MS_cols:	430.44
    SS_e:		50722.57		MS_e:		0.14
    ICC_rows:	0.000
    ICC_cols:	0.896
    
    
    end time statistics
    SS_total:	490638.27		MS_total:	1.32
    SS_rows:	121.54		MS_rows:	0.33
    SS_cols:	456284.18		MS_cols:	446.03
    SS_e:		34232.55		MS_e:		0.09
    ICC_rows:	0.000
    ICC_cols:	0.930
    
    
    duration statistics
    SS_total:	980343.86		MS_total:	2.63
    SS_rows:	162.99		MS_rows:	0.45
    SS_cols:	894262.38		MS_cols:	874.16
    SS_e:		85918.49		MS_e:		0.23
    ICC_rows:	0.000
    ICC_cols:	0.912
    
    

