plot_diary notebook
===================

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

This file contains the functions necessary to visualize the activity
diaries.

Import

.. code:: ipython3

    import sys
    sys.path.append('..\\source')
    
    # plotting functions
    import matplotlib.pylab as plt
    
    # mathematical capability
    import numpy as np
    
    # dataframe capability
    import pandas as pd
    
    # agent-based model modules
    import my_globals as mg
    import activity, temporal
    

.. code:: ipython3

    # plotting scheme
    %matplotlib auto


.. parsed-literal::

    Using matplotlib backend: Qt5Agg
    

Functions

.. code:: ipython3

    def plot_activity_diary(df, show_legend=False, fontsize=8, dpi=300):
        
        """
        This function plots the activity diary for a given agent. The information is represented 
        in terms of horizontal barcharts in which the agent is performing an activity and where 
        the x-axis is the time of day (in hours).
        
        :param pandas.core.frame.DataFrame df: the activity diary of a given agent
        :param bool show_legend: a flag indicating whether (if True) or not (if False) to show \
        the legend in the plot
        :param int fontsize: the font size of the text within the plot
        :param int dpi: the resolution of the plot in dots per inch
        
        :return: a tuple of a list of the lines that were plotted AND a list of the labels. This \ 
        information is used in plotting the legend seperately
        """    
        
        # set the font size for ticks, labels, titles, and legend
        fontsize_ticks = fontsize
        fontsize_title = fontsize
        fontsize_label = fontsize
        fontsize_title = fontsize   
        fontsize_legend = fontsize
        
        # set font axis parameters
        font_axis = {'family': 'serif',
            'color':  'black',
            'weight': 'normal',
            'size': fontsize_ticks,}
        
        #
        # plot horizontal bars using matplotlib
        #
        
        # create the plot
        f, ax = plt.subplots(dpi=dpi)
    
        # a list of the lines plotted
        lines = list()
        align = 'center'
        
        # the labels in chornological order
        labels = [ activity.INT_2_STR[x] for x in df.act.unique() ]
        
        # set the label for "no actviity" to "Idle"
        for i, x in enumerate(labels):
            if x == activity.INT_2_STR[activity.NO_ACTIVITY]:
                labels[i] = 'Idle'
        
        # the flag to indicate whether the figure lines will be used for the legend
        do_legend = [ (x, True) for x in df.act.unique()]
        do_legend = dict(do_legend)
        
        # plot the diaries 
        for i in range( len(df) ):
            
            # get the activity entry
            x = df.iloc[i]    
            
            # get the corresponding color and label
            color = activity.INT_2_COLOR[x.act]
            label = activity.INT_2_STR[x.act]
            
            # for the first entry
            if i == 0:           
                # plot the entry in the beginning of the bar chart
                p = ax.barh(x.day, x.start, color=color, label=label, left=x.start, align=align)        
            
            else:
                # if the activity starts on one day and ends on the next,            
                if x.start > x.end:
                    # plot the activity entry until midnight on the first days bar chart and 
                    # and starting at midnight on the next day's bar chart
                    p = ax.barh(x.day, x.start, left=df.iloc[i-1].end, color=color, label=label, align=align)
                    ax.barh(x.day+1, x.end, left=0, color=color, label=label, align=align)
    
                else:
                    # add the activity entry to the current day's bar chart
                    p = ax.barh(x.day, x.start, left=df.iloc[i-1].end, color=color, label=label, align=align)
    
            # if it's the first time an activity is plotted, add it to the legend.
            if do_legend[x.act]:
                lines.append(p)
                do_legend[x.act] = False            
    
        #
        # handle the text related to plotting
        #
    
        # set the title
        f.suptitle('Daily Activity Diary', fontsize=fontsize_title)
    
        # create the legend    
        if show_legend:
            f.legend(lines, labels, 'best', fontsize=fontsize_legend)
    
        # set the x limits
        ax.set_xlim( [0, 24])
    
        # set the x tick-marks
        xticks = np.linspace(0, 24, 9)
        ax.set_xticks(xticks)
    
        # set the font size of the x ticks
        ax.tick_params(axis='both', labelsize=fontsize_ticks)
    
        # label axes
        ax.set_xlabel('Time [h]', fontdict=font_axis)
        ax.set_ylabel('Day', fontdict=font_axis)
    
        # invert yaxis
        ax.invert_yaxis()
        
        return lines, labels
    
    def plot_longitude(data, titles, linewidth=1):
        
        """
        This function plots a chart showing the amount of time spent during each activity. The x-axis is the 
        time in hours and the y-axis is the duration (in minutes) represented in a log10 scale.
        
        :param list data: a list of dataframes where each dataframe represents an activity diary of an agent.
        :param list titles: a list of titles for each plot
        :param int linewidth: the linewidth of the lines within the plot
        """
            
        # the number of rows and columns (the dimensions) for the subplots
        nrows, ncols = 1, 1
        
        #
        # create axes
        #
        f, ax = plt.subplots(nrows, ncols, sharex=True, sharey=True)
        
        
        # plot the graphs
        K = [ plot_longitude_help(ax, data[i], linewidth) for i, ax in enumerate(f.axes)] 
       
        # the number of unique activities, including idle time
        K0 = data[0].act.unique()
        
        # a list of each activity expressed as a string
        keys = [ activity.INT_2_STR[k] for k in K0]
        print(keys)
        
        # show the legend
        f.legend( f.axes[0].lines, keys, 'best' )
    
        # the subplot title size
        fontsize_title=18
        
        # the tick size
        ticksize=14
        
        # for each plot, set the font size and the tick size
        for i, ax in enumerate(f.axes):
            ax.set_title(titles[i], fontsize=fontsize_title)         
            ax.tick_params(axis='both', labelsize=ticksize)
    
        # set the main title
        f.suptitle('Daily Activity Duration', fontsize=fontsize_title)
    
        # write axes for x and y 
        df = data[0]
        xlabel, ylabel = 'Day', 'Duration [minutes]'
        x_min, x_max = df.day.values[0], df.day.values[-1]
    
        #
        # set the x and y axes
        #
        
        # the y-label size
        fontsize_label = 18 
        
        # set the ylabel
        ax.set_ylabel(ylabel, fontsize=fontsize_label)
        
        return
    
    def plot_longitude_help(ax, df, linewidth=1):
        
        """
        This function actually handles plotting the longitude plot. This is to be used in 
        plot_longitude(). For each activity, the function plots the respectivie activity-duration 
        on a long10 scale on each day.
        
        :param matplotlib.axes._subplots.AxesSubplot ax: for plotting object
        :param pandas.core.frame.DataFrame df: the activity diary of a given agent
        :param int linewidth: the linewidth of the lines within the plot
        
        :return: a list of the unique activity codes in the activity diary
        """
        
        colors = activity.INT_2_COLOR
        
        # the days in the simulation
        days = df.day.unique()
        
        # the activities that were done by the person in the simulation
        keys = df.act.unique()
                
        # group activities by day
        gb = df.groupby('day')
    
        # for each activity, plot the duration 
        for k in keys:
            
            # the duration data
            y = np.zeros(days.shape)
    
            # for each day
            for i, d in enumerate(days):
    
                # get the activity data for the given day
                temp = gb.get_group(d)
                temp = temp[temp.act == k]
                            
                # if there the respectivie activity does not happen that day, return NaN
                # this allows python to avoid plotting the activity on that specific day
                if temp.size == 0:
                    dt = np.nan                
                else:
                    dt = temp.dt.values.sum()
    
                # convert the duration from hours to minutes
                y[i] = temporal.HOUR_2_MIN * dt
    
            # plot the data for the kth activity on a log10 scale     
            ax.plot(days, np.log10(y), '-*', label=activity.INT_2_STR[k], color=colors[k], linewidth=linewidth)            
            
        return keys
    
    

Run

Load Activity Diary

.. code:: ipython3

    # the file name of the activity diary
    fname = mg.FDIR_MY_DATA + '\\main_result.csv'
    
    # load the activity diary as a dataframe
    df = pd.read_csv(fname)

Plot the activity diary

.. code:: ipython3

    # figure resolution [ dots per inch (dpi) ]
    # dpi needs to be at least 300 for submission to some journals
    dpi=300
    
    # font size of text within the figure
    fontsize = 8
    
    # plot the activity diary
    lines, labels = plot_activity_diary(df, dpi=dpi, fontsize=8)
    
    # show the plot
    plt.show()
    

Isolate the legend

.. code:: ipython3

    # create the plot
    fig, ax = plt.subplots(dpi=dpi)
    
    # plot the legend
    fig.legend(lines, labels, 'best', fontsize=fontsize)
    
    # do not plot anything else
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    # show the plot
    plt.show()


.. parsed-literal::

    C:\Users\nbrandon\AppData\Local\Continuum\Anaconda3\lib\site-packages\matplotlib\legend.py:338: UserWarning: Automatic legend placement (loc="best") not implemented for figure legend. Falling back on "upper right".
      warnings.warn('Automatic legend placement (loc="best") not '
    

Longitudinal Activity-Duration Plots

.. code:: ipython3

    #
    # plot longitudinal plots of the daily activities
    #
    
    # the title
    titles = ('Working Adult',)
    
    # the activity data
    data = (df,)
    
    # the width of the lines in the plots
    linewidth = 1
    
    # plot the activity durations
    plot_longitude(data=data, titles=titles, linewidth=linewidth)
    
    # show the plot
    plt.show()


.. parsed-literal::

    ['No Activity', 'Eat Dinner', 'Sleep', 'Commute to Work', 'Work', 'Eat Lunch', 'Commute from Work', 'Eat Breakfast']
    

.. parsed-literal::

    C:\Users\nbrandon\AppData\Local\Continuum\Anaconda3\lib\site-packages\matplotlib\legend.py:338: UserWarning: Automatic legend placement (loc="best") not implemented for figure legend. Falling back on "upper right".
      warnings.warn('Automatic legend placement (loc="best") not '
    

