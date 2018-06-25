figure_loader notebook
======================

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

This notebook loads the individual data about the cumuluative
distribution functions (CDFs) comaparing the Agent-Based Model of Human
Activity Patterns (ABMHAP) results to the Consolidated Human Activity
Database (CHAD) data. The plots compare the distribution
activity-parameter data from ABMHAP to CHAD. More specifically, the
ABMAHP simulation data parameterized with CHAD longitduinal data are
comared to the single-day data from CHAD. The following is plotted: 1.
CDFs of ABMHAP vs. CHAD longitudianl data for activity-parameters 2.
CDFs of ABMHAP vs CHAD single-day data for activity-parameters 3.
Inverse CDFs of ABMHAP vs CHAD single-day data for ctivity-parameters 4.
Residual of the Inverse CDF of ABMHAP vs CHAD single-day data for
activity-parameters 5. Scaled Residual of the Quantile Functions of
ABMHAP vs CHAD single-day data for activity-parameters

Import

.. code:: ipython3

    import sys
    sys.path.append('..\\source')
    sys.path.append('..\\processing')
    sys.path.append('..\\plotting')
    
    # plotting capabilities
    import matplotlib.pylab as plt
    import matplotlib.ticker as ticker
    
    # math capability
    import numpy as np
    
    # data frame capability
    import pandas as pd
    
    # python pickle capability
    import pickle
    
    # ABMHAP capability 
    import my_globals as mg
    import chad_demography_adult_work as cdaw
    import chad_demography_adult_non_work as cdanw
    import chad_demography_child_school as cdcs
    import chad_demography_child_young as cdcy
    import demography as dmg
    
    import activity, analyzer, plotter, temporal

.. code:: ipython3

    %matplotlib auto


.. parsed-literal::

    Using matplotlib backend: Qt5Agg
    

define functions

.. code:: ipython3

    def plot_subplots(data_list, do_cdf, main_title, legend, xlabels, ylabels, xunits, yunits, colors, \
                      do_save=False, fname=None, linewidth=1):
        
        # the dimensions of a maximized figure. Base x Height [pixels]
        b_pixels, h_pixels = 2400, 1255
        my_dpi = 800
        
        b_in = b_pixels/my_dpi
        h_in = h_pixels/my_dpi
        
        
        # set the figure size for saving to custom if savinig
        if do_save:
            figsize, dpi = (b_in, h_in), my_dpi        
        else:
            figsize, dpi = None, None
            
        # data_list is     
        nrows, ncols = 3, len(data_list[0])
    
        if do_cdf:
            f, axes = plt.subplots(nrows, ncols, sharey=True, figsize=figsize, dpi=dpi)
        else:
            f, axes = plt.subplots(nrows, ncols, sharex=True, figsize=figsize, dpi=dpi)
    
       
        #
        # plot
        #
        for i , ax in enumerate(f.axes):
    
            # indices
            irow = i // ncols
            jcol = i % ncols
    
            # plot data
            temp = data_list[irow][jcol]
            
            for t, color in zip(temp, colors):
                
                x_data, y_data = t            
                if do_cdf and irow == 2:
                    idx = x_data >= 0
                    ax.plot(x_data[idx], y_data[idx], color=color, linewidth=linewidth)                                
                else:
                    ax.plot(x_data, y_data, color=color, linewidth=linewidth)                                
                
                #
                # set the tick labels
                #
                ticksize=14
                ax.tick_params(axis='both', labelsize=ticksize)
                
                if irow == 2:
                    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
                            
                if do_cdf and irow in [0, 1]:
                    # limit the xaxis to integernumbers
                    x_all = [x.get_xdata() for x in ax.lines]
                    x_all = np.hstack(x_all).flatten()
                    x_min, x_max = np.floor( np.min(x_all) ), np.ceil( np.max(x_all))
                    dx = abs(x_min - x_max) + 1
                    nbins = np.ceil(dx/2)
                    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins))
                    
                    ax.set_xlim(x_min, x_max)
                    
                    # set the xticks
                    # testing
                    x_min = np.round(x_min).astype(int)
                    x_max = np.round(x_max).astype(int)
                    dx = (x_max - x_min) / (5 - 1)                
                    dx = np.floor(dx).astype(int)
                    xticks = np.arange(x_min, x_max, dx)
                    ax.set_xticks(xticks)
                    
                
        # main title
        fontsize_title = 18
        f.suptitle(main_title, fontsize=fontsize_title)
    
        # legend    
        f.legend( f.axes[0].lines, legend, 'best')
    
        #
        # set the x-axis labels
        #    
    
        fontsize_label = 18
        for ax, xlabel in zip( axes[nrows-1,:], xlabels) :
            ax.set_xlabel(xlabel, fontsize=fontsize_label)                
            
            if not do_cdf:
                x_min, x_max = 0, 1    
                ax.set_xlim(x_min, x_max)
                xticks = np.linspace(x_min, x_max, 3)
                ax.set_xticks(xticks)
                ##ax.set_xticks(xticks, fontsize=20)
                #ax.set_xticklabels(labels=[], fontsize=20)        
            
        # set x titles
        for ax, key in zip(axes[0,:], keys):
            #ax.set_title( activity.INT_2_STR[key], fontsize=fontsize_title )
            ax.set_title( activity.INT_2_STR[key], fontsize=14 )
            
        #
        # set the y-axis labels
        #
        for ax, ylabel in zip(axes[:, ncols-1], ylabels):    
            ax.yaxis.set_label_position('right')
            ax.set_ylabel(ylabel, fontsize=fontsize_label, rotation=270, labelpad=20)
            
        for i, ax in enumerate(axes[:,0]):        
            ax.yaxis.set_label_position('left')
            ax.set_ylabel(yunits[i], fontsize=fontsize_label)
            
            if do_cdf:
                y_min, y_max = 0, 1
                ax.set_ylim(y_min, y_max)
                
        if do_save and (fname is not None):
            f.savefig(fname, dpi=my_dpi)    
        
        return

set up the parameters

.. code:: ipython3

    #
    # choose the deomography
    #
    demo = dmg.ADULT_NON_WORK
    
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
    linewidth = 0.5

.. code:: ipython3

    # use a custom figure directory
    fpath = mg.FDIR_SAVE_FIG + '\\01_16_2018_no_variation\\n8192_d007'
    
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
    
    # non-eating activities
    keys_not_eat = [ k for k in keys_all if k not in keys_eat ]


.. parsed-literal::

    the figure save path:	..\my_data\fig\01_16_2018_no_variation\n8192_d007\adult_non_work
    

Plotting

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

Plot CDFs vs Longitudinal data

plot verification

.. code:: ipython3

    fpaths = analyzer.get_verify_fpath(fpath_figure_save, keys)

.. code:: ipython3

    #
    # plot the verification cdf
    #
    
    # load the data
    fname = '\\cdf_' + fname_keys + '.png'
    data_list_all, fname_subplot = plotter.get_figure_data(fpaths, fpath_figure_save, fname)
    
    #
    # plotting parameters
    #
    do_cdf = True
    
    colors = ['blue', 'red']
    legend = ['Predicted', 'Means (CHAD)']
    
    xunits = 'Hours'
    yunits = ['Quantile'] * 3
    
    main_title = 'CDFs of Activity-parameters'
    
    xlabels = [xunits] * len(keys)
    
    # 
    # plot
    #
    
    plot_subplots(data_list=data_list_all, do_cdf=do_cdf, main_title=main_title, legend=legend, \
                      xlabels=xlabels, ylabels=ylabels, xunits=xunits, yunits=yunits, colors=colors, \
                      do_save=do_save_fig, fname=fname_subplot, linewidth=linewidth)
    
    if do_show:
        plt.show()
    else:
        plt.close()


.. parsed-literal::

    C:\Users\nbrandon\AppData\Local\Continuum\Anaconda3\lib\site-packages\matplotlib\legend.py:338: UserWarning: Automatic legend placement (loc="best") not implemented for figure legend. Falling back on "upper right".
      warnings.warn('Automatic legend placement (loc="best") not '
    

Plot CDFs vs random days

.. code:: ipython3

    # choose the activities to plot
    # get the figure directories
    fpaths = [ (fpath_figure_save + mg.KEY_2_FDIR_SAVE_FIG[k] + mg.FDIR_SAVE_FIG_RANDOM_DAY) for k in keys]

plot the cdf

.. code:: ipython3

    #
    # plot the CDF
    #
    
    fname = '\\cdf_' + fname_keys + '.png'
    fnames_load = ('\\cdf_start.pkl', '\\cdf_end.pkl', '\\cdf_dt.pkl')
    
    # load the data
    data_list_all, fname_subplot = plotter.get_figure_data(fpaths, fpath_figure_save, fname, fnames_load=fnames_load)
    
    #
    # plotting parameters
    #
    do_cdf = True
    
    colors = ['blue', 'red']
    legend = ['Predicted', 'Observed']
    
    xunits = 'Hours'
    yunits = ['Quantile'] * 3
    
    main_title = 'CDFs of Activity-parameters'
    
    xlabels = [xunits] * len(keys)
    
    # 
    # plot
    #
    
    plot_subplots(data_list=data_list_all, do_cdf=do_cdf, main_title=main_title, legend=legend, \
                      xlabels=xlabels, ylabels=ylabels, xunits=xunits, yunits=yunits, colors=colors, \
                      do_save=do_save_fig, fname=fname_subplot, linewidth=linewidth)
    
    if do_show:
        plt.show()
    else:
        plt.close()


.. parsed-literal::

    C:\Users\nbrandon\AppData\Local\Continuum\Anaconda3\lib\site-packages\matplotlib\legend.py:338: UserWarning: Automatic legend placement (loc="best") not implemented for figure legend. Falling back on "upper right".
      warnings.warn('Automatic legend placement (loc="best") not '
    

Plot the Inverse CDF

.. code:: ipython3

    #
    # plot the Inverse CDF
    #
    
    fname = '\\cdf_inv_' + fname_keys + '.png'
    fnames_load = ('\\cdf_inv_start.pkl', '\\cdf_inv_end.pkl', '\\cdf_inv_dt.pkl')
    
    # load the data 
    data_list_all, fname_subplot = plotter.get_figure_data(fpaths, fpath_figure_save, fname, fnames_load=fnames_load)
    
    #
    # plotting parameters
    #
    do_cdf = True
    
    colors = ['blue', 'red']
    legend = ['Predicted', 'Observed']
    
    xunits = 'Hours'
    yunits = ['Quantile'] * 3
    
    main_title = 'Inverse CDFs of Activity-parameters'
    
    xlabels = [xunits] * len(keys)
    
    # 
    # plot
    #
    
    plot_subplots(data_list=data_list_all, do_cdf=do_cdf, main_title=main_title, legend=legend, \
                      xlabels=xlabels, ylabels=ylabels, xunits=xunits, yunits=yunits, colors=colors, \
                      do_save=do_save_fig, fname=fname_subplot, linewidth=linewidth)
    
    if do_show:
        plt.show()
    else:
        plt.close()


.. parsed-literal::

    C:\Users\nbrandon\AppData\Local\Continuum\Anaconda3\lib\site-packages\ipykernel_launcher.py:73: RuntimeWarning: divide by zero encountered in long_scalars
    

::


    ---------------------------------------------------------------------------

    ValueError                                Traceback (most recent call last)

    <ipython-input-39-2c25156c1693> in <module>()
         28 #
         29 
    ---> 30 plot_subplots(data_list=data_list_all, do_cdf=do_cdf, main_title=main_title, legend=legend,                   xlabels=xlabels, ylabels=ylabels, xunits=xunits, yunits=yunits, colors=colors,                   do_save=do_save_fig, fname=fname_subplot, linewidth=linewidth)
         31 
         32 if do_show:
    

    <ipython-input-3-8a15175d88ba> in plot_subplots(data_list, do_cdf, main_title, legend, xlabels, ylabels, xunits, yunits, colors, do_save, fname, linewidth)
         71                 dx = (x_max - x_min) / (5 - 1)
         72                 dx = np.floor(dx).astype(int)
    ---> 73                 xticks = np.arange(x_min, x_max, dx)
         74                 ax.set_xticks(xticks)
         75 
    

    ValueError: Maximum allowed size exceeded


plot residuals

.. code:: ipython3

    #
    # plot the residuals ICDF
    #
    
    
    # recall that the residuals should be multiplied by -1
    fname = '\\res_inv_' + fname_keys + '.png'
    fnames_load = ('\\res_inv_start.pkl', '\\res_inv_end.pkl', '\\res_inv_dt.pkl')
    
    data_list_all, fname_subplot = plotter.get_figure_data(fpaths, fpath_figure_save, fname, fnames_load=fnames_load)
    #
    # plotting parameters
    #
    
    # residual plot (inverse CDF)
    do_cdf = False
    legend = ['Residual']
    colors = ['Red']
    
    xunits = 'Quantile'
    yunits = ['Hours', 'Hours', 'Minutes']
    
    main_title = 'Residual of the Inverse CDF'
    
    xlabels = [xunits] * len(keys)
    
    #
    # plot the data
    #
    plot_subplots(data_list=data_list_all, do_cdf=do_cdf, main_title=main_title, legend=legend, \
                      xlabels=xlabels, ylabels=ylabels, xunits=xunits, yunits=yunits, colors=colors, \
                      do_save=do_save_fig, fname=fname_subplot, linewidth=linewidth)
    
    if do_show:
        plt.show()
    else:
        plt.close()


.. parsed-literal::

    C:\Users\nbrandon\AppData\Local\Continuum\Anaconda3\lib\site-packages\matplotlib\legend.py:338: UserWarning: Automatic legend placement (loc="best") not implemented for figure legend. Falling back on "upper right".
      warnings.warn('Automatic legend placement (loc="best") not '
    

plot the scaled residuals

.. code:: ipython3

    #
    # plot the residuals ICDF scaled
    #
    
    # recall that the residuals should be multiplied by -1
    fnames = '\\res_inv_scaled' + fname_keys + '.png'
    
    fnames_load = ('\\res_inv_scaled_start.pkl', '\\res_inv_scaled_end.pkl', \
                   '\\res_inv_scaled_dt.pkl')
    
    data_list_all, fname_subplot = plotter.get_figure_data(fpaths, fpath_figure_save, fname, fnames_load=fnames_load)
    
    #
    # plotting parameters
    #Q
    do_cdf = False
    
    legend = ['Residual']
    colors = ['Red']
    xunits = 'Quantitle'
    yunits = ['Standard Deviations'] * 3
    
    main_title = 'Scaled Residual of the Quantile Functions'
    
    xlabels = [xunits] * len(keys)
    
    #
    # plot the data
    #
    
    plot_subplots(data_list=data_list_all, do_cdf=do_cdf, main_title=main_title, legend=legend, \
                      xlabels=xlabels, ylabels=ylabels, xunits=xunits, yunits=yunits, colors=colors, \
                      do_save=do_save_fig, fname=fname_subplot, linewidth=linewidth)
    
    if do_show:
        plt.show()
    else:
        plt.close()


.. parsed-literal::

    C:\Users\nbrandon\AppData\Local\Continuum\Anaconda3\lib\site-packages\matplotlib\legend.py:338: UserWarning: Automatic legend placement (loc="best") not implemented for figure legend. Falling back on "upper right".
      warnings.warn('Automatic legend placement (loc="best") not '
    

