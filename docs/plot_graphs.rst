plot_graphs notebook
====================

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

This notebook plots graphs comparing results from the Agent-Based Model
of Human Activity Patterns (ABMHAP) to the data from the Consolidated
Human Activity Database (CHAD).

1. plots the graphs of a distribution of the mean values of the agent
   and compares it to the distribution of CHAD mean values from the
   longitudinaal data for each activity start time, end time, and
   duration. The plots are the following:

2. plots the graphs of a distribution of 1 randomly chosen day from each
   agent and compares it to the distribution of CHAD single-day data for
   each activity start time, end time, and duration. The plots are the
   following:

   a. the CDF plots of the ABMHAP distribution and CHAD distribution
   b. the inveted CDF plots of the ABMHAP distribution and CHAD
      distribution
   c. the inverted residual plots of the ABMHAP distribution and CHAD
      distribution
   d. the scaled inverted residual plots of the ABMHAP distribution and
      CHAD distribution

3. The results of the figures are saved in a suite of .pkl files

Import

.. code:: ipython3

    import os, sys
    sys.path.append('..\\source')
    sys.path.append('..\\processing')
    
    # plotting capbailities
    import matplotlib.pylab as plt
    
    # ABMHAP capabilities
    import my_globals as mg
    import chad_demography_adult_non_work as cdanw
    import chad_demography_adult_work as cdaw
    import chad_demography_child_school as cdcs
    import chad_demography_child_young as cdcy
    import demography as dmg
    import evaluation as ev
    
    import activity, analysis, analyzer, zipfile

.. code:: ipython3

    %matplotlib auto

load the data

.. code:: ipython3

    #
    # load the data
    #
    
    #
    # Get filename to load the data
    #
    
    # get the file name
    f_data_ending = '\\12_07_2017\\n8192_d364'
    
    # the file path directory to load the data
    fpath = mg.FDIR_MY_DATA + f_data_ending
    
    # the full file name for loading the data
    fname_load_data = fpath + '\\data_child_young.pkl'
    
    print('Loading data from:\t%s' % fname_load_data)
    
    # clear variables
    fname, fpath = None, None
    
    # load the data
    x = mg.load(fname_load_data)
    
    # get all of the data frames
    df_list = x.get_all_data()        
    
    # demographic
    demo = x.demographic

parameters for saving the data

.. code:: ipython3

    #
    # Get directory to save the figrues in
    #
    
    # file directory for saving the data
    fpath = mg.FDIR_SAVE_FIG + f_data_ending
    
    # map the demographic to the correct file directory
    chooser_fout = {dmg.ADULT_WORK: fpath + '\\adult_work',
           dmg.ADULT_NON_WORK: fpath + '\\adult_non_work',
           dmg.CHILD_SCHOOL: fpath + '\\child_school',
           dmg.CHILD_YOUNG: fpath + '\\child_young',
          }
    
    # get the file directory to save the data
    fpath_save_fig = chooser_fout[demo]
    
    print('The directory to save the data:\t%s' % fpath_save_fig)
    
    # clear variables
    fpath = None

the plotting parameters

.. code:: ipython3

    #
    # plotting flags
    #
    
    # calculates the plots
    do_plot = True
    
    # save the figures
    do_save_fig = False
    
    # show the plots
    do_show = False
    
    # show extra print messages
    do_print = False

.. code:: ipython3

    #
    # demography
    #
    
    # map the demograph;y identifiyer to the demographics object
    chooser = {dmg.ADULT_WORK: cdaw.CHAD_demography_adult_work(),
               dmg.ADULT_NON_WORK: cdanw.CHAD_demography_adult_non_work(),
               dmg.CHILD_SCHOOL: cdcs.CHAD_demography_child_school(),
               dmg.CHILD_YOUNG: cdcy.CHAD_demography_child_young(),
              }
    
    # choose the demography
    chad_demo = chooser[demo]

plot

.. code:: ipython3

    # CHAD parameters
    chad_param_list = chad_demo.int_2_param
    
    # get the activity codes for a given trial
    act_codes = chad_demo.keys
    
    # the directories for the respective activities. This is used for saving the figures
    fdirs = analyzer.get_verify_fpath(fpath_save_fig, act_codes)
    
    if fpath_save_fig is None:
        do_save_fig = False
    
    # offset, used for figure identifiers
    off = 0
    
    # number of days in the simulation
    n_days = len( df_list[0].day.unique() )
    
    fid = 0
    
    for act, fpath in zip(act_codes, fdirs):
    
        print( activity.INT_2_STR[act])
        if (do_print):
            msg = 'starting analysis for the ' + activity.INT_2_STR[act] + ' activity ...'
            print(msg)
    
        # this is to see if the analysis of the moments for start time needs to be in [-12, 12)
        # instead of [0, 24) format
        chooser     = {activity.SLEEP: True, }
        do_periodic = chooser.get(act, False)
    
        # get the CHAD data
        # this is here to access the data frames from t.initialize()    
        f_stats = chad_demo.fname_stats[act]
        
        # the sampling parameters for 1 household
        s_params = chad_demo.int_2_param[act]    
        
        # get the CHAD data
        chad_start, chad_end, chad_dt, chad_record = \
            analysis.get_verification_info(demo=demo, key_activity=act, fname_stats=f_stats, \
                                           sampling_params=[s_params] )    
            
        # plot the ABMHAP data
        df_abm         = ev.sample_activity_abm(df_list, act)
        abm_start_mean = df_abm.start.values
        abm_end_mean   = df_abm.end.values
        abm_dt_mean    = df_abm.dt.values        
    
        # create the plots
        if (do_plot):
    
            print(fpath)
            #if s_params.do_start:
            fid = fid + 1
            analyzer.plot_verify_start(act, abm_start_mean, chad_start['mu'].values, fid=fid, \
                                       do_save_fig=do_save_fig, fpath=fpath)
    
            #if s_params.do_end:
            fid = fid + 1
            analyzer.plot_verify_end(act, abm_end_mean, chad_end['mu'].values, fid=fid, \
                                     do_save_fig=do_save_fig, fpath=fpath)
    
            #if s_params.do_dt:
            fid = fid + 1
            analyzer.plot_verify_dt(act, abm_dt_mean, chad_dt['mu'].values, fid=fid, \
                                     do_save_fig=do_save_fig, fpath=fpath)
    
    if do_show:
        plt.show()
    else:
        plt.close('all')

Validation

.. code:: ipython3

    # get the CHAD sampling parameters for the given demographioc
    chad_param_list = x.chad_param_list
    
    # get the sampling parameters
    s_params = chad_param_list[0]
    
    # get the figure index
    fidx = 100
    
    # save flag
    do_save = False
    
    print(fpath_save_fig)

Compare random events

.. code:: ipython3

    # the activity codes
    act_codes = chad_demo.keys
    #act_codes = [mg.KEY_WORK]
    
    # open the data
    z = zipfile.ZipFile(chad_demo.fname_zip, mode='r')
    
    # this flag allows the code to pick a random record from the longitudinal data (if True)
    # or single-day data (if False)
    do_random_long = False
    
    # for each activity, plot the corresponding plots
    for act in act_codes:
        
        print( activity.INT_2_STR[act] )
        
        
        # periodic time flag [-12, 12)
        do_periodic = False
        
        # if the activity occurs over midnight (if True), set the 
        # 
        if act == activity.SLEEP:
            do_periodic = True
        
        # sample the ABM data
        df_abm  = ev.sample_activity_abm(df_list, act)
            
        # get the CHAD data
        # this is here to access the data frames from t.initialize()    
        f_stats = chad_demo.fname_stats[act]
    
        # get the file name data of the single name data
        if do_random_long == False:
            for k in f_stats.keys():
                f_stats[k] = f_stats[k].replace('longitude', 'solo')            
                
        # the sampling parameters for 1 household
        s_params = chad_demo.int_2_param[act]    
    
        # get the CHAD data
        stats_start, stats_end, stats_dt, record = \
            analysis.get_verification_info(demo=demo, key_activity=act, fname_stats=f_stats, \
                                           sampling_params=[s_params])
            
        # grouby the CHAD records by identifier
        gb  = record.groupby('PID')
        pid = record.PID.unique()    
        
        # return true if x is in pid
        f = lambda x: x in pid
        
        # indices of records within 'pid'
        i = record.PID.apply(f)
        
        # get the CHAD observations
        df_obs = record[i]    
        
        # get teh CHAD records that satisfy the sampling parameters for the given activity
        df_obs_new = s_params.get_record(df_obs, do_periodic)
        
        # get the single day observations
        print(fpath_save_fig)
        fid_last    = ev.compare_abm_to_chad_help(df_abm=df_abm, df_obs=df_obs_new, act_code=act, fidx=fidx, \
                                                  do_save=do_save, fpath=fpath_save_fig)
        fidx        = fid_last + 1
    
    z.close()
    
    print('finished plotting...')
    
    # show the plots
    if do_show:
        plt.show()
    else:
        # clear all of the plots
        plt.close('all')
    
    fpath = None
