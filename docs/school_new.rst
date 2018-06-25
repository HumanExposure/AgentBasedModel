school_new notebook
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
    # March 22, 2018

This file goes through the data from the Consoldiated Human Activity
Database (CHAD) and gets information relevent to \*\* school\*\* and
processes the data for use in the Agent-Based Model of Human Activity
Patterns (ABMHAP) for the school-age children demographic. More
specficially, this file does the following:

For school-age children demographic,

1. This function goes through the CHAD data and finds the school
   activity data

2. The CHAD activity data are seperated into start time, end time,
   duration, and CHAD record data

3. The CHAD activity data is saved into longitudinal data and
   single-activity data

import

.. code:: ipython3

    import sys
    sys.path.append('..\\source')
    
    # ABMHAP modules
    import demography as dmg
    import datum

load data

.. code:: ipython3

    #
    # demographic
    # 
    key = dmg.CHILD_SCHOOL
    
    fname_input, fpath_output = dmg.INT_2_FIN_FOUT_LARGE[key]
    
    # load the data
    data = dmg.load(fname_input)

process the data

.. code:: ipython3

    # dictionaries about the moments
    d = datum.analyze_education(data)

save the data

.. code:: ipython3

    # choose to save longitudinal data or single-day data
    chooser = {True: (2, fpath_output + '\\longitude'), 
               False: (1, fpath_output + '\\solo'), } 
    
    # whether to save the longitudinal data (if True) or the single-day data (if False)
    do_long = True

.. code:: ipython3

    #
    # save the data 
    #
    do_save = False
    
    if do_save:
    
        N, fpath = chooser[do_long]
        
        # the directory the data should be saved in
        fpath = fpath + '\\education'
            
        # save the data
        stats_dt, stats_start, stats_end, record = d['stats_dt'], d['stats_start'], d['stats_end'], d['data']
                        
        if do_long:
            dt, start, end, rec = datum.get_longitude(stats_dt, stats_start, stats_end, record, N=N)
        else:
            dt, start, end, rec = datum.get_solo(stats_dt, stats_start, stats_end, record)
            
        datum.save(fpath, record=rec, stats_dt=dt, stats_start=start, stats_end=end)
            
