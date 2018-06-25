figure_residuals notebook
=========================

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

This file calculates the residuals in the cumaltive distribution
functions (CDFs) for the activities in each demographic.

The file calculates the residuals = \|cdf\_predicted - cdf\_observed\|
as a function of percentile from 0 to 1. Then the mean value for the
residual plot is calculated which represents the expected deviation from
the data for each percentile

Import

.. code:: ipython3

    import sys
    sys.path.append('..\\source')
    sys.path.append('..\\processing')
    sys.path.append('..\\plotting')
    
    # plotting capability analysis
    import matplotlib.pylab as plt
    
    # math capability
    import numpy as np
    
    # python data compression
    import pickle
    
    # ABMHAP modules
    import my_globals as mg
    import chad_demography_adult_work as cdaw
    import chad_demography_adult_non_work as cdanw
    import chad_demography_child_school as cdcs
    import chad_demography_child_young as cdcy
    import demography as dmg
    
    import activity, plotter

.. code:: ipython3

    %matplotlib auto


.. parsed-literal::

    Using matplotlib backend: Qt5Agg
    

define functions

.. code:: ipython3

    def f(data, alpha=0):
        
        # create the residuals between the prediction (ABMHAP) and observation (CHAD)
        # data. Plot the quantiles of the data [alpha, 1 - alpha] percentiles of the data.
        
        # predicted data and observed data
        pred, obs = data
        
        # the x and y values for the predicted data and observed data
        x_pred, y_pred = pred
        x_obs, y_obs = obs
    
        # residual
        r = np.abs(y_pred - y_obs)
        
        # the number of data points
        m = len(r)
        
        # the bottom and top percentile
        bot, top = alpha/2, 1 - alpha/2
        
        # get the percentiles within range
        x = x_pred
        idx = (x >= bot) & (x <= top)
            
        return x[idx], r[idx]
    
    # get the moments
    def get_moments(x):
        
        # the mean data
        mu = x.mean()
        
        # the standard deviation data
        std = x.std()
        
        return mu, std
    

set up the parameters

.. code:: ipython3

    #
    # choose the deomography
    #
    demo = dmg.CHILD_YOUNG
    
    chooser = {dmg.ADULT_WORK: cdaw.CHAD_demography_adult_work(),
               dmg.ADULT_NON_WORK: cdanw.CHAD_demography_adult_non_work(),
               dmg.CHILD_SCHOOL: cdcs.CHAD_demography_child_school(),
               dmg.CHILD_YOUNG: cdcy.CHAD_demography_child_young(),
               }
    
    # the CHAD demogramphy object
    chad_demo = chooser[demo]
    
    # the CHAD sampling parameters
    s_params = chad_demo.int_2_param

.. code:: ipython3

    # save the figures
    do_save_fig = False
    
    # whether or not to show the plots
    do_show = True
    
    # the linewidth
    linewidth = 1.5

.. code:: ipython3

    # choose the appropriate figure directory
    fpath = mg.FDIR_SAVE_FIG + '\\12_07_2017\\n8192_d364'
    
    chooser_fin = {dmg.ADULT_WORK: fpath + '\\adult_work',
           dmg.ADULT_NON_WORK: fpath + '\\adult_non_work',
           dmg.CHILD_SCHOOL: fpath + '\\child_school',
           dmg.CHILD_YOUNG: fpath + '\\child_young',
          }
    
    fpath_figure_save = chooser_fin[demo]
    
    # print the save figure directory
    print('the figure save path:\t%s' % fpath_figure_save)
    
    # different sets of activitiy data to plot
    keys_all = chad_demo.keys
    
    # eating activities
    keys_eat = [mg.KEY_EAT_BREAKFAST, mg.KEY_EAT_LUNCH, mg.KEY_EAT_DINNER]
    
    # non eating activities
    keys_not_eat = [ k for k in keys_all if k not in keys_eat ]


.. parsed-literal::

    the figure save path:	..\my_data\fig\12_07_2017\n8192_d364\child_young
    

Load plotting data

.. code:: ipython3

    DO_ALL = 1
    DO_MEALS = 2
    DO_NOT_MEALS = 3
    
    # (the activites to plot, part of the file name that matches the keys)
    chooser_keys = { DO_ALL: (keys_all, 'all'), \
                    DO_MEALS: (keys_eat, 'meals'),\
                    DO_NOT_MEALS: (keys_not_eat, 'not_meals'),
                   }

.. code:: ipython3

    #
    # set the activities to plot
    #
    plot_keys = DO_ALL
    
    keys, fname_keys = chooser_keys[plot_keys]
    name_keys = [ activity.INT_2_STR[k] for k in keys]
    
    
    # labels on the right hand side of the plot
    ylabels = ['Start Time', 'End Time', 'Duration']

Load all data

.. code:: ipython3

    # choose the activities to plot
    
    # get the figure directories
    fpaths = [ (fpath_figure_save + mg.KEY_2_FDIR_SAVE_FIG[k] + mg.FDIR_SAVE_FIG_RANDOM_DAY) for k in keys]
    
    # the file name (no file path) of the data to save
    fname = fpath_figure_save + '\\cdf_inv_' + fname_keys + '.png'
    
    # file name to load
    fnames_load = ('\\cdf_inv_start.pkl', '\\cdf_inv_end.pkl', '\\cdf_inv_dt.pkl')
    
    # load the data
    data_list_all, fname_subplot = plotter.get_figure_data(fpaths, fpath_figure_save, fname, fnames_load=fnames_load)

Load the data for a specific activity-data

.. code:: ipython3

    idx = -1
    start = data_list_start[idx]
    end = data_list_end[idx]
    dt = data_list_dt[idx]
    
    f_end = fnames_end[idx]
    f_start = fnames_start[idx]
    f_dt = fnames_dt[idx]
    
    print(f_start)
    print(f_end)
    print(f_dt)


.. parsed-literal::

    ..\my_data\fig\12_07_2017\n8192_d364\child_young\sleep\random_day\cdf_inv_start.pkl
    ..\my_data\fig\12_07_2017\n8192_d364\child_young\sleep\random_day\cdf_inv_end.pkl
    ..\my_data\fig\12_07_2017\n8192_d364\child_young\sleep\random_day\cdf_inv_dt.pkl
    

plot the residuals

.. code:: ipython3

    #
    # plot the residuals
    #
    
    alpha = 0.05
    plt.close('all')
    
    for idx, k in enumerate(keys):
        
        print( activity.INT_2_STR[k] )
        
        # load the start time, end time, and duration data
        start = data_list_start[idx]
        end = data_list_end[idx]
        dt = data_list_dt[idx]
    
        # quantile, and residual data
        x_start, r_start = f(start, alpha=alpha)
        x_end, r_end = f(end, alpha=alpha)
        x_dt, r_dt = f(dt, alpha=alpha)
    
        # covert the residuals into minutes
        r_start = r_start * 60
        r_end = r_end * 60
        r_dt = r_dt
    
        # get the moments on the residuals for start time, end time, and duration
        mu_start, std_start = get_moments(r_start)
        mu_end, std_end = get_moments(r_end)
        mu_dt, std_dt = get_moments(r_dt)
    
        print('mu start: %.2f\t\tstd start: %.2f' % (mu_start, std_start))
        print('mu end: %.2f\t\tstd end: %.2f' % (mu_end, std_end))
        print('mu dt: %.2f\t\tstd dt: %.2f\n' % (mu_dt, std_dt))
        
        # create subplots
        fig, axes = plt.subplots(3)
        
        # create title
        fig.suptitle( activity.INT_2_STR[k] )
    
        # plot data about start time
        ax = axes[0]
        ax.plot(x_start, r_start, label='start')
        ax.axhline(mu_start, ls='--')
        ax.legend(loc='best')
    
        # plot data about end time
        ax = axes[1]
        ax.plot(x_end, r_end, label='end')
        ax.axhline(mu_end, ls='--')
        ax.legend(loc='best')
    
        # plot data about duration
        ax = axes[2]
        ax.plot(x_dt, r_dt, label='dt')
        ax.axhline(mu_dt, ls='--')
        ax.legend(loc='best')
    
    plt.show()


.. parsed-literal::

    Eat Breakfast
    mu start: 11.83		std start: 8.87
    mu end: 8.20		std end: 9.31
    mu dt: 3.79		std dt: 4.17
    
    Eat Lunch
    mu start: 12.39		std start: 8.78
    mu end: 14.46		std end: 7.60
    mu dt: 2.10		std dt: 1.56
    
    Eat Dinner
    mu start: 7.21		std start: 5.18
    mu end: 8.86		std end: 4.73
    mu dt: 3.24		std dt: 2.95
    
    Sleep
    mu start: 5.94		std start: 4.78
    mu end: 5.88		std end: 5.57
    mu dt: 13.44		std dt: 10.27
    
    


