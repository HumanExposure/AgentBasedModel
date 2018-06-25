longitude_plot notebook
=======================

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

This module plots the daily activity-duration for each activity over
time done by an agent in an Agent-Based Module of Human Activity
Patterns (ABMHAP) simulation. An agent representing each demographic are
shown in a combined subplot:

1. An agent representing a respective demographic has its activity
   behavior is plotted in a log10 scale over time
2. This function plots a histogram showing the amount of times each
   activity was done in an ABMHAP simulation.

import

.. code:: ipython3

    import os, sys
    sys.path.append('..\\source')
    sys.path.append('..\\processing')
    sys.path.append('..\\plotting')
    
    # plotting capability
    import matplotlib.pylab as plt
    
    # math capabilitiy
    import numpy as np
    
    # dataframe capability
    import pandas as pd
    
    # ABMHAP capability
    import my_globals as mg
    import chad_demography_adult_non_work as cdanw
    import chad_demography_adult_work as cdaw
    import chad_demography_child_school as cdcs
    import chad_demography_child_young as cdcy
    import demography as dmg
    
    import activity, plotter, temporal

.. code:: ipython3

    %matplotlib auto


.. parsed-literal::

    Using matplotlib backend: Qt5Agg
    

run

.. code:: ipython3

    #
    # get the file name
    #
    
    # variation
    fpath = mg.FDIR_MY_DATA 
    
    # file paths for each demographic
    fpath_adult_work = fpath + '\\11_21_2017\\n8192_d364'
    fpath_adult_non_work = fpath + '\\11_27_2017\\n8192_d364'
    fpath_child_school = fpath + '\\11_29_2017\\n8192_d364'
    fpath_child_young = fpath + '\\12_07_2017\\n8192_d364'
    
    # full file names for each demographic
    fname_adult_work = fpath_adult_work + '\\data_adult_work.pkl'
    fname_adult_non_work = fpath_adult_non_work + '\\data_adult_non_work.pkl'
    fname_child_school = fpath_child_school + '\\data_child_school.pkl'
    fname_child_young  = fpath_child_young + '\\data_child_young.pkl' 
    
    # demographic chooser
    chooser = {dmg.ADULT_WORK: cdaw.CHAD_demography_adult_work(),
               dmg.ADULT_NON_WORK: cdanw.CHAD_demography_adult_non_work(),
               dmg.CHILD_SCHOOL: cdcs.CHAD_demography_child_school(),
               dmg.CHILD_YOUNG: cdcy.CHAD_demography_child_young(),
              }

.. code:: ipython3

    #
    # load demographic information
    #
    adult_work     = mg.load(fname_adult_work)
    adult_non_work = mg.load(fname_adult_non_work)
    child_school   = mg.load(fname_child_school)
    child_young    = mg.load(fname_child_young)

.. code:: ipython3

    # set the data
    data_all = (adult_work, adult_non_work, child_school, child_young)
    
    # set the titles of the data
    titles   = ('Working Adults', 'Non-working Adults', 'School-age Children', 'Pre-school Children')

.. code:: ipython3

    # th index of the agent whose chosen for each demgoraphic, respectively
    idx = 2
    
    # full simulation data
    diary_demo_full = [ xx.diaries[idx][0].df for xx in data_all]
    
    # simulation data set to 14 days
    diary_demo_week = []
    for xx in data_all:
        df = xx.diaries[idx][0].df
        diary_demo_week.append( df[df.day <= 14])

plot

.. code:: ipython3

    #
    # plot longitudinal plots of the daily activities
    #
    linewidth = 0.5
    data = diary_demo_week
    plotter.plot_longitude(data=data, titles=titles, linewidth=linewidth)
    linewidth = None
    
    plt.show()

.. code:: ipython3

    #
    # plot the distribution of how many times each activity was done
    #
    
    for data, title in zip(data_all, titles):    
        plotter.plot_count(data, chooser[data.demographic].keys, do_abs=True, title=title)
        plotter.plot_count(data, chooser[data.demographic].keys, do_abs=False, title=title)
        
    plt.show()
