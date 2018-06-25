
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

import

.. code:: ipython3

    import os, sys
    sys.path.append('..\\source')
    sys.path.append('..\\processing')
    
    # data frame capability
    import pandas as pd
    
    # ABMHAP modules
    import my_globals as mg
    import demography as dmg
    

function

.. code:: ipython3

    def add_id(df_list):
        
        """
        Add the agent identifier to the activity diaries.
        
        :param df_list: the activity diaries
        :type df_list: list of pandas.core.frame.DataFrame
        """
        
        for i, df in enumerate(df_list):
            df['id'] = i+1
            
        return df_list
    
    def save(df, fname):
        
        # copy the data
        x = df.copy()
        
        # add +1 to day for ICF
        x.day = x.day + 1
        
        # create the directory for the save file if it does not exist
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        
        # save the data frame
        x.to_csv(fname, index=False)
        
        return
    

run

.. code:: ipython3

    # get the file name
    fpath_load_data = mg.FDIR_MY_DATA + '\\with_without_variation\\n8192_d364_with_variation'
    fname_load_data = fpath_load_data + '\\data_adult_work.pkl'

.. code:: ipython3

    # load the driver_result object
    x = mg.load(fname_load_data)

.. code:: ipython3

    # list of each data frame
    df_list = x.get_all_data()
    
    # add unique identifiers for ICF
    df_list = add_id(df_list)
    
    # get the name of the columns to include the id as the first column instead of the last
    colnames = df_list[0].columns.values.tolist()
    colnames = [ colnames[-1] ] + colnames[:-1]
    
    # set the reorder the columns for each dataframe
    df_list = [df[colnames] for df in df_list]
    
    # combine the data into one dataframe
    df_all = pd.concat(df_list)

.. code:: ipython3

    #
    # save parameters
    #
    
    # file directory to save the data in 
    fpath = mg.FDIR_MY_DATA  + '\\icf'
    
    # the file name of the file to save
    chooser = {dmg.ADULT_WORK: '\\adult_work.csv',
               dmg.ADULT_NON_WORK: '\\adult_non_work.csv',
               dmg.CHILD_SCHOOL: '\\child_school.csv',
               dmg.CHILD_YOUNG: '\\child_young.csv',
              }
    
    # the full file name
    fname_save = fpath + chooser[x.demographic]
    
    # print the full file name
    print(fname_save)


.. parsed-literal::

    ..\my_data\icf\adult_work.csv
    

.. code:: ipython3

    #
    # save the data
    #
    
    do_save = False
    
    if do_save:
        save(df_all, fname_save)

