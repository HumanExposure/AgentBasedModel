figure_loader_with_without_variation notebook
=============================================

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
activity-parameter data from ABMHAP to CHAD. More specifically, the we
compare the ABMHAP with intra-individual variation, ABMHAP without
intra-individual variation, and CHAD single-day data.

This module loads and plots a figure with the following:

1. CDFs of ABMHAP with intra-individual variation vs. ABMHAP without
   intra-individual variation vs. CHAD longitudinal data for
   activity-parameters

Import

.. code:: ipython3

    import sys
    sys.path.append('..\\source')
    sys.path.append('..\\processing')
    sys.path.append('..\\plotting')
    
    # plotting capability
    import matplotlib.pylab as plt
    import matplotlib.ticker as ticker
    
    # math capability
    import numpy as np
    
    # data frame capability
    import pandas as pd
    
    # pickling capability
    import pickle
    
    # ABMHAP modules
    import my_globals as mg
    import demography as dmg
    import activity, analyzer, plotter, temporal
    
    import chad_demography_adult_work as cdaw
    import chad_demography_adult_non_work as cdanw
    import chad_demography_child_school as cdcs
    import chad_demography_child_young as cdcy

.. code:: ipython3

    %matplotlib auto


.. parsed-literal::

    Using matplotlib backend: Qt5Agg
    

define functions

.. code:: ipython3

    # plot subplots
    
    def plot_subplots(data_list1, data_list2, data_list3, do_cdf, main_title, legend, xlabels, ylabels, \
                           xunits, yunits, colors, do_save=False, fname=None, linewidth=1):
        
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
        nrows, ncols = 3, len(data_list1[0])
    
        if do_cdf:
            f, axes = plt.subplots(nrows, ncols, sharey=True, figsize=figsize, dpi=dpi)
        else:
            f, axes = plt.subplots(nrows, ncols, sharex=True, figsize=figsize, dpi=dpi)
    
       
        #
        # plot
        #
        alpha = 0.7
        for i , ax in enumerate(f.axes):
    
            # indices
            irow = i // ncols
            jcol = i % ncols
    
            # plot data
            temp1 = data_list1[irow][jcol]
            temp2 = data_list2[irow][jcol]
            temp3 = data_list3[irow][jcol]
            
            counter = 0
            
            # ii for testing if 
            ii = 0
            
            for t1, t2, color in zip(temp1, temp2, colors):
                
                if ii == 0:
                    x_data1, y_data1 = t1
                    x_data2, y_data2 = t2
    
                    if counter == 0:
                        c1 = 'blue'
                        c2 = 'k'
                        #c2 = 'green'
                    else:
                        c1 = 'red'
                        c2 = 'red'
    
                    if do_cdf and irow == 2:
                        idx = x_data1 >= 0                                
    
                        ax.plot(x_data1[idx], y_data1[idx], color=c1, linewidth=linewidth, alpha=alpha) 
                        ax.plot(x_data2[idx], y_data2[idx], color=c2, ls='--', linewidth=linewidth, alpha=alpha)
                    else:
                        ax.plot(x_data1, y_data1, color=c1, linewidth=linewidth, alpha=alpha) 
                        ax.plot(x_data2, y_data2, color=c2, ls='--', linewidth=linewidth, alpha=alpha) 
    
                    # access the CHAD data
                    x_data3, y_data3 = temp3[1]
                    
                    if (irow in [0, 1]) and jcol in [1, 4]:
                        x_data3 = mg.from_periodic(x_data3, do_hours=True)
    
                    ax.plot(x_data3, y_data3, color='r', linewidth=linewidth, alpha=alpha)
    
                    counter = counter + 1
                    ii = ii + 1
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
    linewidth = 1

.. code:: ipython3

    
    #fpath1 = mg.FDIR_SAVE_FIG + '\\11_21_2017\\n8192_d364' # with variation
    #fpath2 = mg.FDIR_SAVE_FIG + '\\01_11_2018\\n8192_d007_no_variation' # no variation
    
    fpath1 = mg.FDIR_SAVE_FIG + '\\12_07_2017\\n8192_d364' # with variation
    fpath2 = mg.FDIR_SAVE_FIG + '\\01_16_2018_no_variation\\n8192_d007' # no variation
    
    #fpath_temp = mg.FDIR_SAVE_FIG + '\\with_without_variation'
    #fpath1 = fpath_temp + '\\n8192_d007_with_variation'
    #fpath2 = fpath_temp + '\\n8192_d364_no_variation'
    
    fpath_figure_save1 = fpath1 + '\\child_young'
    fpath_figure_save2 = fpath2 + '\\child_young'
    
    # print the save figure directory
    print('the figure save path 1:\t%s' % fpath_figure_save1)
    print('the figure save path 2:\t%s' % fpath_figure_save2)
    
    # different sets of activitiy data to plot
    keys_all = chad_demo.keys
    
    keys_eat = [mg.KEY_EAT_BREAKFAST, mg.KEY_EAT_LUNCH, mg.KEY_EAT_DINNER]
    
    keys_not_eat = [ k for k in keys_all if k not in keys_eat ]


.. parsed-literal::

    the figure save path 1:	..\my_data\fig\12_07_2017\n8192_d364\child_young
    the figure save path 2:	..\my_data\fig\01_16_2018_no_variation\n8192_d007\child_young
    

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

    # get the figure directory of ABMHAP runs with intra-individual variation
    fpaths1 = analyzer.get_verify_fpath(fpath_figure_save1, keys)
    
    # get the figure directory of ABMHAP runs with no intra-individual variation
    fpaths2 = analyzer.get_verify_fpath(fpath_figure_save2, keys)

.. code:: ipython3

    # load figure data with longitudinal data
    
    # file names
    fname = '\\cdf_' + fname_keys + '.png'
    
    # load figure data
    data_list_all1, fname_subplot1 = plotter.get_figure_data(fpaths1, fpath_figure_save1, fname)
    data_list_all2, fname_subplot2 = plotter.get_figure_data(fpaths2, fpath_figure_save2, fname)

Get the data for a random single day

.. code:: ipython3

    # load figure data of sinlge-day data
    
    # file names
    fname = '\\cdf_' + fname_keys + '.png'
    
    fnames_load = ('\\cdf_start.pkl', '\\cdf_end.pkl', '\\cdf_dt.pkl')
    
    # load figure data from ABMHAP figures with intra-individual variation
    data_list_all_single_day1, fname_subplot1 = \
    plotter.get_figure_data(fpaths1, fpath_figure_save1, fname, fnames_load=fnames_load, do_single_day=True)
    
    # load figure data from ABMHAP figures with no intra-individual variation
    data_list_all_single_day2, fname_subplot2 = \
    plotter.get_figure_data(fpaths2, fpath_figure_save2, fname, fnames_load=fnames_load, do_single_day=True)
    

.. code:: ipython3

    fpath_figure_save2




.. parsed-literal::

    '..\\my_data\\fig\\01_16_2018_no_variation\\n8192_d007\\child_young'



plot the cdf

.. code:: ipython3

    #
    # plot the verification cdf
    #
    
    #
    # plotting parameters
    #
    do_cdf = True
    
    colors = ['blue', 'red']
    legend = ['With Intra','No Intra', 'CHAD single day', 'CHAD means']
    
    xunits = 'Hours'
    yunits = ['Quantile'] * 3
    
    main_title = 'CDFs of Activity-parameters'
    
    xlabels = [xunits] * len(keys)
    
    # 
    # plot
    #
    
    # set the data
    data_list1 = data_list_all_single_day1 # with variaiton
    data_list2 = data_list_all_single_day2 # no variation
    data_list3 = data_list_all_single_day1 # acesses the CHAD random day data which is encapsulated within
                                            # data_list[irow][icol][1]
    
    # plot the data
    plot_subplots(data_list1=data_list1, data_list2=data_list2, data_list3=data_list3, \
                       do_cdf=do_cdf, main_title=main_title, \
                       legend=legend, xlabels=xlabels, ylabels=ylabels, xunits=xunits, yunits=yunits, colors=colors, \
                       do_save=do_save_fig, fname=fname_subplot1, linewidth=0.5)
    
    if do_show:
        plt.show()
    else:
        plt.close()


.. parsed-literal::

    C:\Users\nbrandon\AppData\Local\Continuum\Anaconda3\lib\site-packages\matplotlib\legend.py:338: UserWarning: Automatic legend placement (loc="best") not implemented for figure legend. Falling back on "upper right".
      warnings.warn('Automatic legend placement (loc="best") not '
    

