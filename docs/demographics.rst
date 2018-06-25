demographics notebook
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

This file does the following

1. Goes through the Consolidated Human Activity Database (CHAD) data and
   seprates CHAD into datasets of different demographic groups

2. Or loads saved datasets representing different demographic groups for
   CHAD

3. Saves data for each demographic group:

   -  Saves the demographic data into the 'data\_large' directory
   -  Saves the demographic in a compressed form in the 'data' directory
      as zip files

4. For a given demographic group and a given collection of activities

   -  prints the amount of individuals found doing each activity given
      by a unique CHAD code
   -  plots the histogram and/or CDF of distributions of start time, end
      time, and duration for each specific activity given by a CHAD code
   -  Saves the plots

import

.. code:: ipython3

    #
    # import
    #
    import sys
    sys.path.append('..\\source')
    sys.path.append('..\\run_chad')
    import os
    
    # plotting capabilities
    import matplotlib.pylab as plt
    
    # math capability
    import numpy as np
    
    # ABMHAP modules
    import my_globals as mg
    import demography as dmg
    
    import chad, chad_code

functions

.. code:: ipython3

    def plot_cdfs(df, codes, N=1000, linewidth=1, do_save=False, fpath=''):
    
        """
        This function plots the distribution of activity distrbution of \
        start time, end time, and duration as cumulative distribution \
        functions (CDFs) from the CHAD data of the given activity.
        
        :param pandas.core.frame.DataFrame df:
        :param codes: the CHAD activity codes
        :type codes: list of list of int
        :param int N: the number of points sampled within the empirical CDF
        :param int linewidth: the width of the plotted lines
        :param bool do_save: a flag indicating whether (if True) to save the \
        figures or not(if False)
        :param str fpath: the file directory to save the files in
        
        :return:
        """
        
        # codes: chad_codes for each activity
    
        figs, fnames = [], []
    
        # for each activity category within the CHAD codes
        for act in codes:
            
            # get the data w
            temp = df[df.act == act]
            gb = temp.groupby('PID')
    
            # get the mean duration data
            y_dt = np.array( [ gb.get_group(p).dt.mean() for p in temp.PID.unique() ] )
            
            # get the mean start time data
            y_start = np.array( [ gb.get_group(p).start.mean() for p in temp.PID.unique() ] )
            
            # get the mean end time data
            y_end = np.array( [ gb.get_group(p).end.mean() for p in temp.PID.unique() ] )
    
            if len(y_dt) != 0:
                
                # create subplots
                fig, axes = plt.subplots(2,2)
    
                # create title
                fig.suptitle(chad_code.INT_2_STR[act])
    
                # plot the start time
                ax = axes[0, 0]
                x, y = mg.get_ecdf(y_start, N)
                ax.plot(x, y, color='blue', label='start', lw=linewidth)
    
                # plot the end time
                ax = axes[0, 1]
                x, y = mg.get_ecdf(y_end, N)
                ax.plot(x, y, color='purple', label='end', lw=linewidth)
    
                # plot the duration
                ax = axes[1, 0]
                x, y = mg.get_ecdf(y_dt, N)
                ax.plot(x, y, color='red', label='duration', lw=linewidth)
    
                # plot axis label and legend
                for ax in axes.flatten():
                    ax.set_xlabel('Hours')
                    ax.legend(loc='best') 
                    
                #
                # save
                #
                if do_save:
                    # figure name
                    fname = fpath + chad_code.INT_2_SAVE_FIG_FNAME[act]
                    
                    # split the file name into 2 parts from the back
                    x = fname.rsplit('\\', maxsplit=1)
                    
                    # create the filename
                    fname = x[0] + '\\cdf\\' + x[1]                          
                    
                    print(fname)
                    
                    # add list of figures and finle names
                    figs.append(fig)                            
                    fnames.append(fname)
                    
        # save the figures
        if do_save:
            for fig, fname in zip(figs, fnames):            
                os.makedirs(os.path.dirname(fname), exist_ok=True)
                fig.savefig(fname, dpi=800)            
                plt.close(fig)
                    
    
        return
    
    def plot_histograms(df, codes, num_bins=12, fpath='', do_save=False):
        
        """
        This function plots the distribution of activity distrbution of \
        start time, end time, and duration as histograms from the CHAD \
        data of the given activity.
        
        :param pandas.core.frame.DataFrame df:
        :param codes: the CHAD activity codes
        :type codes: list of list of int
        :param int num_bins: the number of bins within the histogram    
        :param bool do_save: a flag indicating whether (if True) to save the \
        figures or not(if False)
        :param str fpath: the file directory to save the files in
        
        :return:
        """
            
        figs, fnames = [], []
        
        # for each activitiy within the CHAD activity codes
        for act in codes:
        
            # get the data w
            temp = df[df.act == act]
            gb = temp.groupby('PID')
    
    
            # get the mean duration data
            y_dt = np.array( [ gb.get_group(p).dt.mean() for p in temp.PID.unique() ] )
            
            # get the mean start time data
            y_start = np.array( [ gb.get_group(p).start.mean() for p in temp.PID.unique() ] )
            
            # get the mean end time data
            y_end = np.array( [ gb.get_group(p).end.mean() for p in temp.PID.unique() ] )
    
            if len(y_dt) != 0:
                # create subplots
                fig, axes = plt.subplots(2,2)
    
                # create title
                fig.suptitle(chad_code.INT_2_STR[act])
    
                # plot the start time
                ax = axes[0, 0]    
                ax.hist(y_start, bins=num_bins, color='blue', label='start')
    
                # plot the end time
                ax = axes[0, 1]
                ax.hist(y_end, bins=num_bins, color='purple', label='end')
    
                # plot the duration
                ax = axes[1, 0]
                ax.hist(y_dt, bins=num_bins, color='red', label='duration')
    
                # plot axis label and legend
                for ax in axes.flatten():
                    ax.set_xlabel('Hours')
                    ax.legend(loc='best')        
    
                #
                # save
                #
                if do_save:
                 
                    # figure name
                    fname = fpath + chad_code.INT_2_SAVE_FIG_FNAME[act]
                    
                    # split the file name into 2 parts from the back
                    x = fname.rsplit('\\', maxsplit=1)
                    
                    fname = x[0] + '\\histo\\' + x[1]
                    
                    print(fname)
                    # add list of figures and finle names
                    figs.append(fig)                            
                    fnames.append(fname)
                    
        # save the figures
        if do_save:
            for fig, fname in zip(figs, fnames):            
                
                os.makedirs(os.path.dirname(fname), exist_ok=True)
                fig.savefig(fname, dpi=800)
                plt.close(fig)
        return
    
    def save(x, fname):
        
        """
        This function saves the data for a given demographic.
        
        :param chad.CHAD_RAW x: the data to be pickled
        :param str fname: the name of the file 
        """
        
        # first, close the zip file. This is necessary to avoid an pickling error
        x.z.close()
        
        # pickle the data
        mg.save(x, fname)
        
        return

Load data

.. code:: ipython3

    # set flags
    
    # flag to load pre-saved CHAD data(if True) or (if False) to process the CHAD data, \
    # which takes substantially more time
    do_load = True
    
    # flag to show messages
    do_print = True

.. code:: ipython3

    #
    # load all of the data
    #
    if do_load:
        all_data  = mg.load(dmg.FNAME_ALL)
    else:
        all_data = dmg.get_all()

.. code:: ipython3

    #
    # get all of the data for working age adults
    #
    if do_load:
        adult = mg.load(dmg.FNAME_ADULT)
    else:
        adult = dmg.get_adult()

.. code:: ipython3

    #
    # get data for working adults
    #
    if do_load:
        adult_work = mg.load(dmg.FNAME_ADULT_WORK)
    else:
        adult_work = dmg.get_adult_work(adult)

.. code:: ipython3

    #
    # get data for non-working adults
    #
    if do_load:
        adult_non_work = mg.load(dmg.FNAME_ADULT_NON_WORK)
    else:
        adult_non_work = dmg.get_adult_non_work(adult)

.. code:: ipython3

    #
    # children school
    #
    if do_load:    
        child_school = mg.load(dmg.FNAME_CHILD_SCHOOL)
    else:
        child_school = dmg.get_child_school()

.. code:: ipython3

    #
    # pre-school children
    #
    if do_load:
        child_young = mg.load(dmg.FNAME_CHILD_YOUNG)
    else:
        child_young = dmg.get_child_young()

save data

save all the information for the demographics in data\_large directory

.. code:: ipython3

    # save all of the information for the following demographics
    
    do_save = False
    
    if do_save:
        x = [all_data, adult, adult_non_work, adult_work, child_school, child_young]    
        fnames = [ dmg.FNAME_ALL, dmg.FNAME_ADULT, dmg.FNAME_ADULT_NON_WORK, dmg.FNAME_ADULT_WORK, \
                   dmg.FNAME_CHILD_SCHOOL, dmg.FNAME_CHILD_YOUNG ]
        
        # save all of the data
        for y, fname in zip(x, fnames):
            save(y, fname)

Compress the demographics direcotory information

.. code:: ipython3

    #
    # The demographic
    #
    demos = [dmg.ADULT_WORK, dmg.ADULT_NON_WORK, dmg.CHILD_SCHOOL, dmg.CHILD_YOUNG]
    

.. code:: ipython3

    #
    # compress the directory in the non-large data directory
    #
    do_compression = False
    
    chooser_temp = {dmg.ADULT: (chad.FNAME_ADULT[:-4], chad.FDIR_ADULT_LARGE),
               dmg.ADULT_WORK: (chad.FNAME_ADULT_WORK[:-4], chad.FDIR_ADULT_WORK_LARGE),
               dmg.ADULT_NON_WORK: (chad.FNAME_ADULT_NON_WORK[:-4], chad.FDIR_ADULT_NON_WORK_LARGE),
               dmg.CHILD_SCHOOL: (chad.FNAME_CHILD_SCHOOL[:-4], chad.FDIR_CHILD_SCHOOL_LARGE),
               dmg.CHILD_YOUNG: (chad.FNAME_CHILD_YOUNG[:-4], chad.FDIR_CHILD_YOUNG_LARGE),
              }
    
    if do_compression:
        for d in demos:
            fname_out, fdir_src = chooser_temp[d]
            mg.save_zip(out_file=fname_out, source_dir=fdir_src)

printing information about the data

.. code:: ipython3

    #
    # get the data
    #
    code_groups = [ chad_code.SLEEP, chad_code.EAT, chad_code.EDUCATION, chad_code.WORK, chad_code.COMMUTE, \
                   chad_code.COMMUTE_EDU ]
    
    # code_groups = [chad_code.SLEEP]
    
    df_list = [ data.activity_times(data.events, codes) for codes in code_groups ]

.. code:: ipython3

    #
    # for each CHAD code, print information about the amount of data that is in the respective demographic group
    #
    for df, codes in zip(df_list, code_groups):
        
        if do_print:
            print('data shape')
            print(df.shape)
    
    
            print('number of individuals: %d' % len( df.PID.unique() ) )
    
            for act in codes:
                temp = df[df.act == act]
                print('%s:\tIndividuals:\t%d\tCount:\t%d' % (chad_code.INT_2_STR[act], len(temp.PID.unique()), \
                                                             len(temp) ) )           
    
            print('\n')    

plotting

.. code:: ipython3

    chooser_fpath ={dmg.ALL: mg.FDIR_SAVE_FIG_ALL,
                    dmg.ADULT: mg.FDIR_SAVE_FIG_ADULT,
                    dmg.ADULT_WORK: mg.FDIR_SAVE_FIG_ADULT_WORK,
                    dmg.ADULT_NON_WORK: mg.FDIR_SAVE_FIG_ADULT_NON_WORK,
                    dmg.CHILD_SCHOOL: mg.FDIR_SAVE_FIG_CHILD_SCHOOL,
                    dmg.CHILD_YOUNG: mg.FDIR_SAVE_FIG_CHILD_YOUNG,
                   }
    
    chooser_data = {dmg.ALL: all_data,
                    dmg.ADULT: adult,
                    dmg.ADULT_WORK: adult_work,
                    dmg.ADULT_NON_WORK: adult_non_work,
                    dmg.CHILD_SCHOOL: child_school,
                    dmg.CHILD_YOUNG: child_young,
                   }

.. code:: ipython3

    # 
    # get data and fpath for saving
    #
    data = chooser_data[demo]
    fpath = chooser_fpath[demo] + '\\chad'
    
    print(fpath)


.. parsed-literal::

    ..\my_data\fig\demographic\adult_work\chad
    

.. code:: ipython3

    # flags for figures
    
    # plot the figures
    do_plot = False
    
    # save the figure plots
    do_save_fig= False

.. code:: ipython3

    #
    # plot the histograms
    #
    
    if do_plot:
        
        for df, codes in zip(df_list, code_groups):
            
            plot_histograms(df, codes, num_bins=24, do_save=do_save_fig, fpath=fpath)
    
        plt.show()

.. code:: ipython3

    #
    # plot the CDFs
    #
    if do_plot:
        
        for df, codes in zip(df_list, code_groups):
            
            plot_cdfs(df, codes, linewidth=2, do_save=do_save_fig, fpath=fpath)
    
        plt.show()
