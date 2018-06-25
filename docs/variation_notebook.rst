
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

This code does some variation calculations. However, this code is
**NOT** part of the Agent-Based Model of Human Activity Patterns
(ABMHAP) and should not be added to the ABMHAP code package.

Import

.. code:: ipython3

    import sys, zipfile
    sys.path.append('..\\source')
    sys.path.append('..\\run_chad')
    sys.path.append('..\\processing')
    
    # math functions
    import matplotlib.pylab as plt
    import numpy as np
    import pandas as pd
    
    # ABMHAP modules
    import chad_demography_adult_non_work as cdanw
    import chad_demography_adult_work as cdaw
    import chad_demography_child_school as cdcs
    import chad_demography_child_young as cdcy
    import demography as dmg
    import my_globals as mg
    import evaluation as ev
    
    import activity, analyzer, chad, omni_trial, params

function declarations

.. code:: ipython3

    def get_longitude_data(t, z, fname_stats, s_params):
        
        # get the specific filenames
        fname_start, fname_end, fname_dt = fname_stats[chad.START], fname_stats[chad.END], fname_stats[chad.DT]
        
        # the data for the start time, end time, and duration
        long_start    = t.get_chad_stats_data_start(z, fname_start, s_params)
        long_end      = t.get_chad_stats_data_end(z, fname_end, s_params)
        long_dt       = t.get_chad_stats_data_dt(z, fname_dt, s_params)
        
        return long_start, long_end, long_dt
    
    def get_plot_data(data_id, solo_start, solo_end, solo_dt, long_start, long_end, long_dt, df_abm, record, do_periodic):
        
        chooser_data = {chad.START: (solo_start['mu'].values, long_start['mu'].values, df_abm.start.values, \
                                     record.start.values),\
                        chad.END: (solo_end['mu'].values, long_end['mu'].values, df_abm.end.values, record.end.values), \
                        chad.DT: (solo_dt['mu'].values, long_dt['mu'].values, df_abm.dt.values, record.dt.values), }
    
        solo, long, abm, rec = chooser_data[data_id]
    
        if (data_id != chad.DT) and do_periodic:
            rec = mg.to_periodic(rec, do_hours=True)
            abm = mg.to_periodic(abm, do_hours=True)
        
        return solo, long, abm, rec
    
    def get_record_data(z, fname_stats, do_periodic):
        
        f_record = fname_stats[chad.RECORD]
        
        raw = pd.read_csv( z.open(f_record) )
        record = s_params.get_record(raw, do_periodic=do_periodic)    
        
        return record
    
    def get_solo_data(t, z, fname_stats, s_params):
        
        f_start, f_end, f_dt, f_record = [fname_stats[x].replace('longitude', 'solo') \
                                      for x in (chad.START, chad.END, chad.DT, chad.RECORD)]
    
        # store the original value
        N_old = s_params.N
    
        # set the value to 1 to obtain the solo results
        s_params.N = 1
    
        solo_start = t.get_chad_stats_data_start(z, f_start, s_params)
        solo_end = t.get_chad_stats_data_end(z, f_end, s_params)
        solo_dt = t.get_chad_stats_data_dt(z, f_dt, s_params)
    
        # reset to the original value
        s_params.N = N_old
        
        return solo_start, solo_end, solo_dt
    
    def variance(X):
        
        mu_total = X.mean()
        mu_A     = np.mean(X, axis=1)
        mu_B     = np.mean(X, axis=0)
    
        n_A   = len(mu_A)
        n_B   = len(mu_B)
    
        temp = (X - mu_total).flatten()
    
        # total sum of squares
        SS_total = np.dot(temp, temp)
    
        # sum of squares of rows
        SS_A  = n_B * np.dot(mu_A - mu_total, mu_A - mu_total)
    
        # sum of squares of columns
        SS_B  = n_A * np.dot(mu_B - mu_total, mu_B - mu_total)
    
        # sum of squares of rows and columns
        SS_AB = SS_total - (SS_A + SS_B)
    
        return SS_total, SS_A, SS_B, SS_AB

.. code:: ipython3

    %matplotlib auto


.. parsed-literal::

    Using matplotlib backend: Qt5Agg
    

run

.. code:: ipython3

    chooser = { dmg.ADULT_WORK: cdaw.CHAD_demography_adult_work(),
                    dmg.ADULT_NON_WORK: cdanw.CHAD_demography_adult_non_work(),
                    dmg.CHILD_SCHOOL: cdcs.CHAD_demography_child_school(),
                    dmg.CHILD_YOUNG: cdcy.CHAD_demography_child_young(),
                    }

set up the trial

.. code:: ipython3

    # default parameters
    p = params.Params(num_people=1, num_days=1, num_hours=0, num_min=0, do_minute_by_minute=False)
    
    # choose demographic
    demo = dmg.ADULT_WORK
    chad_demo = chooser[demo]
    
    # trial
    t = omni_trial.Omni_Trial(p, chad_demo.int_2_param, demo)

.. code:: ipython3

    t.initialize()

get the abm data

.. code:: ipython3

    #
    # load the data
    #
    
    #
    # Get filename to load the data
    #
    
    # get the file name
    f_data_ending = '\\11_21_2017\\n8192_d364'
    
    fpath = mg.FDIR_MY_DATA + f_data_ending
    
    fname_load_data = fpath + '\\data_adult_work.pkl'
    
    print('Loading data from:\t%s' % fname_load_data)
    
    # clear variables
    fname, fpath = None, None
    
    # load the data
    x = mg.load(fname_load_data)
    
    # get all of the data frames
    df_list = x.get_all_data()        
    
    # demographic
    demo = x.demographic


.. parsed-literal::

    Loading data from:	..\my_data\11_21_2017\n8192_d364\data_adult_work.pkl
    

set the activities

.. code:: ipython3

    # choose the key that represents an activity
    keys = [ mg.KEY_COMMUTE_TO_WORK]
    #keys = chad_demo.keys
    
    # the demographic data
    z = zipfile.ZipFile(chad_demo.fname_zip, mode='r')
    
    # dictionary of the file names for the statistical data
    fname_stats = chad_demo.fname_stats
    

get the longitudinal data

.. code:: ipython3

    for k in keys:    
        msg = 'key: %s' % activity.INT_2_STR[k]
        print(msg)
        
        do_periodic = False
        if k == mg.KEY_SLEEP:
            do_periodic = True
            
        # store the relevant file names
        f_stats = fname_stats[k]
        
        # store the sampling paramters for this activity
        s_params = chad_demo.int_2_param[k]    
        
        #
        # get the data
        
        #
        # get the longitudinal data
        long_start, long_end, long_dt = get_longitude_data(t, z, f_stats, s_params)
        
        # get the solo data
        solo_start, solo_end, solo_dt = get_solo_data(t, z, f_stats, s_params)
        
        # the CHAD single day records
        record = get_record_data(z, f_stats, do_periodic)
        
        # get the raw ABM data
        abm_list = analyzer.get_simulation_data(df_list, k)
    
        # sample the ABM data
        df_abm  = ev.sample_activity_abm(df_list, k)    
        
        # print
        if s_params.do_start:
            print('start: %d\tN: %d' % (len(long_start), s_params.N) )
        if s_params.do_end:
            print('end: %d\tN: %d' % (len(long_end), s_params.N) )        
        if s_params.do_dt:
            print('dt: %d\tN: %d' % (len(long_dt), s_params.N) )       
        
        #
        # plot the graphs
        #
        print('Plotting...')
        x_plots = [(s_params.do_start, chad.START), (s_params.do_end, chad.END), (s_params.do_dt, chad.DT) ]
        
        for (do_plot, data_id) in x_plots:
            
            if (do_plot):
        
                # get data for plotting
                solo, long, abm, rec = get_plot_data(data_id, solo_start, solo_end, solo_dt, long_start, long_end, long_dt, \
                                                     df_abm, record, do_periodic)
    
                # get the ecdf data    
                (x_solo,  y_solo), (x_long, y_long), (x_abm, y_abm), (x_rec, y_rec) = \
                [ ( mg.get_ecdf(d, N=1000)) for d in (solo, long, abm, rec) ]
                
                # plot the longitude means vs solo means
                plt.figure()
                plt.title('Longitude vs Solo "means"')
                plt.plot(x_long, y_long, label='long')
                plt.plot(x_solo, y_solo, label='solo')
                plt.legend(loc='best')
                            
                # plot the random abm data vs random single-day data
                plt.figure()
                plt.title('Random ABM vs Random Single-day')
                plt.plot(x_abm, y_abm, label='abm')
                plt.plot(x_rec, y_rec, label='chad record')
                plt.legend(loc='best')
                
                # plot the random abm record vs longitudinal means
                plt.figure()
                plt.title('Random ABM Record vs Longitudinal Means')
                plt.plot(x_abm, y_abm, label='abm')
                plt.plot(x_long, y_long, label='long')
                plt.legend(loc='best')
                
                # plot the random abm data vs random single-day data
                plt.figure()
                plt.title('Random Single-day vs Solo "mean"')
                plt.plot(x_rec, y_rec, label='chad record')
                plt.plot(x_solo, y_solo, label='solo mean')
                plt.legend(loc='best')
                
    plt.show()


.. parsed-literal::

    key: Commute to Work
    start: 1736	N: 1
    end: 1769	N: 1
    dt: 1577	N: 1
    Plotting...
    

ANOVA

"cheap" calculation variation

.. code:: ipython3

    temp = abm_list
    
    
    if data_id == chad.START:
        xx = [ v.start.values for v in temp]
    elif data_id == chad.END:
        xx = [ v.end.values for v in temp]
    else:
        xx = [ v.dt.values for v in temp]
    
    df = pd.DataFrame(xx)

.. code:: ipython3

    mu_agent = np.array( [ df.iloc[i].mean() for i in range(len(df)) ] )
    std_agent = np.array( [ df.iloc[i].std() for i in range(len(df)) ] )
    
    var_intra = std_agent.mean()
    var_inter = mu_agent.std()

.. code:: ipython3

    #
    # the amount of variation
    #
    print('intra var: %.2f\t\tinter var: %.2f' % (var_intra, var_inter))


.. parsed-literal::

    intra var: 0.07		inter var: 0.24
    

brute force calculation

.. code:: ipython3

    # get the indicies of non NaN entries for each row
    idx = [ ~pd.isnull( df.iloc[i] ) for i in range( len(df)) ]
    
    # the number of non NaN entries for each row
    jdx = np.array( [ sum(xx) for xx in idx] )
    
    # the minimum number to sample
    n_min = jdx.min()
    
    print('The number of events to sample in the ABM: %d' % n_min)


.. parsed-literal::

    The number of events to sample in the ABM: 260
    

.. code:: ipython3

    # sample each non NaN value 
    d = [ df.iloc[i][ idx[i] ].sample(n_min).values for i in range( len(idx) ) ]
    
    # store the data
    data = pd.DataFrame(d)

.. code:: ipython3

    #
    # calculate the variance
    #
    
    # calculate the variance
    SS_total, SS_agent, SS_act, SS_agent_act = variance(data.values)
    
    # scale the variance by the total variance
    ss_agent, ss_act, ss_agent_act = [ y / SS_total for y in (SS_agent, SS_act, SS_agent_act) ]

.. code:: ipython3

    #
    # the amount of variation
    #
    print('intra-individual: %.4f' % (ss_act) )
    print('inter-individual: %.4f' % (ss_agent) )
    print('combo: %.4f' % (ss_agent_act) )


.. parsed-literal::

    intra-individual: 0.0000
    inter-individual: 0.9025
    combo: 0.0975
    

.. code:: ipython3

    print(s_params.toString())


.. parsed-literal::

    start mean min: 5.000, start mean max: 10.917, start std max: 2.000
    end mean min: 5.083, end mean max: 11.917, end std max: 1.000
    dt mean min: 0.083, dt mean max: 1.000, dt std max: 2.000
    
    

