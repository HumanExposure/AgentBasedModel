count_records notebook
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
    # March 22, 2018

This function reports the amount of records from the Consolidated Human
Activity Database (CHAD) records for each activity for each demographic
that are suitable for use within the Agent-Based Model of Human Activity
Patterns (ABMHAP) code.

import

.. code:: ipython3

    #
    # import
    #
    import sys
    sys.path.append('..\\source')
    sys.path.append('..\\run_chad')
    
    # math capability
    import numpy as np
    
    # data frame capability
    import pandas as pd
    
    # zipfile capability
    import zipfile
    
    # ABMHAP modules
    import my_globals as mg
    import chad_demography_adult_work as cdaw
    import chad_demography_adult_non_work as cdanw
    import chad_demography_child_school as cdcs
    import chad_demography_child_young as cdcy
    
    import chad

define functions

.. code:: ipython3

    def counter(demos, names, key):
        
        """
        This create a dataframe that contains the amount of CHAD records for the single-entry \
        and longitdinal data.
        
        :param demos: the demographics to compare the results to
        :type demoos: list of demography.Demography
        :param names: the names of the demographcs, respectively
        :type names: list of str
        :param int key: the ABMHAP activity code
        
        :return: a table the shows how many individuals have single-entry and longitudinal data \
        within each demographic
        :retype: pandas.core.frame.DataFrame
        """
        
        do_periodic = False
        
        if key == mg.KEY_SLEEP:
            do_periodic = True
            
        solo_count = np.zeros( (len(demos), ) )
        long_count = np.zeros( solo_count.shape)
    
        for i, demo in enumerate(demos):
            solo, long = f(demo.fname_zip, demo.fname_stats[key][chad.RECORD], demo.int_2_param[key], 
                           do_periodic)
    
            solo_count[i] = sum( solo == 1 )
            long_count[i] = sum( long >= 2)
    
        df = pd.DataFrame( np.vstack( (solo_count, long_count) ).T )
        df.columns = ('single', 'long')
        df.index = names
        
        return df
    
    def f(fname_zip, fname_record, s_param, do_periodic):
        
        """
        This function opens the demographic data and counts the number of both the single-entry \
        (solo) records and the longitudinal (multiple-entry) records that can be used within \
        ABMHAP according to the sepcific activity's requirements for filtering CHAD data
        
        :param str fname_zip: the file name of the .zip file of the CHAD data for a specific \
        demographic
        :param str fname_record: the file name of the CHAD record data for a given activity \
        within the specific demographic
        :param chad_params.CHAD_params: the CHAD sampling parameters for the specific activity
        :param bool do_periodic: a flag to inicate whether (if True) or not (if False) \
        to express time of day in hours [-12, 12)
        
        :return: for each person within the deographic in the CHAD data, the number of activity \
        instances from the single-entry record data, multiple-entry record data
        :rtype: numpy.ndarray, numpy.ndarray
        """
        
        # the zipfile of the data for the given demographic
        z = zipfile.ZipFile(fname_zip)
        
        # count the number of activity instances per PID for the multiple-entry records
        long = f_temp(z, fname_record, s_param, do_periodic)
        
        # count the number of activity instances per PID for the single-entry records
        solo = f_temp(z, fname_record.replace('longitude', 'solo'), s_param, do_periodic)
                
        return solo, long
    
    def f_temp(z, fname_record, s_param, do_periodic):
        
        """
        This function reads the record file and counts the number of entries of a person in \
        CHAD for a given activity with single-entry or multiple-entry data.
        
        :param zipfile.Zipfile:
        :param str fname_record: the file name of the CHAD record data for a given activity \
        within the specific demographic
        :param chad_params.CHAD_params: the CHAD sampling parameters for the specific activity
        :param bool do_periodic: a flag to inicate whether (if True) or not (if False) \
        to express time of day in hours [-12, 12)
        
        :return: the number of activity instances per PID
        :rtype: numpy.ndarray
        """
        
        # read the record file
        df      = pd.read_csv( z.open(fname_record, mode='r') )
        
        # filter the dataframe for valid values for the reocrds
        df      = s_param.get_record(df, do_periodic)
        
        # group the records by PID
        gb      = df.groupby('PID')
        
        # count the number of records per PID
        counts  = np.array( [ len(gb.get_group(u)) for u in df.PID.unique() ] )
        
        return counts
    
    
    def print_count(demo, key, do_periodic=False):    
      
        """
        This function prints the counts of single-entry data and longitudinal data.
        
        :param demography.Demography: the demographic of interest
        :int key: activity code
        :param bool do_periodic: a flag to inicate whether (if True) or not (if False) \
        to express time of day in hours [-12, 12)
        
        :return:
        """
        
        # count the number of activity instances per PID for the given activity within 
        # both the single-entry data and longitudinal data
        solo, long = f(demo.fname_zip, demo.fname_stats[key][chad.RECORD], demo.int_2_param[key], \
                      do_periodic)
        
        # print the results
        print( 'solo: %d\tlong: %d' % (sum(solo == 1), sum(long >= 2) ) )
        
        return
    
    

load the demographics information

.. code:: ipython3

    #
    # load demographics
    #
    adult_work = cdaw.CHAD_demography_adult_work()
    adult_non_work = cdanw.CHAD_demography_adult_non_work()
    child_school = cdcs.CHAD_demography_child_school()
    child_young = cdcy.CHAD_demography_child_young()

.. code:: ipython3

    # set the demographics and names for the data frame rows
    demos = [adult_work, adult_non_work, child_school, child_young]
    names = ['adult_work', 'adult_non_work', 'child_school', 'child_young']
    
    demos_work = [adult_work, child_school]
    names_work = ['adult_work', 'child_school']

meals and sleep

.. code:: ipython3

    # breakfast
    bf = counter(demos, names, mg.KEY_EAT_BREAKFAST)
    
    # lunch
    lunch = counter(demos, names, mg.KEY_EAT_LUNCH)
    
    # dinner
    dinner = counter(demos, names, mg.KEY_EAT_DINNER)
    
    # sleep
    sleep = counter(demos, names, mg.KEY_SLEEP)

commuting, working

.. code:: ipython3

    work = counter(demos_work, names_work, mg.KEY_WORK)
    commute_to_work = counter(demos_work, names_work, mg.KEY_COMMUTE_TO_WORK)
    commute_from_work = counter(demos_work, names_work, mg.KEY_COMMUTE_FROM_WORK)

View

.. code:: ipython3

    sleep




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>single</th>
          <th>long</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>adult_work</th>
          <td>662.0</td>
          <td>501.0</td>
        </tr>
        <tr>
          <th>adult_non_work</th>
          <td>620.0</td>
          <td>0.0</td>
        </tr>
        <tr>
          <th>child_school</th>
          <td>903.0</td>
          <td>139.0</td>
        </tr>
        <tr>
          <th>child_young</th>
          <td>115.0</td>
          <td>0.0</td>
        </tr>
      </tbody>
    </table>
    </div>



