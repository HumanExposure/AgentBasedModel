
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

**This file is NOT used** in order to load the appropriate data.

See **commute\_work.ipynb** notebook instead

import

.. code:: ipython3

    # plotting capability
    import matplotlib.pylab as plt
    
    # import 
    import os
    
    # ABMHAP modules
    from datum import *
    
    import my_globals as mg

run

.. code:: ipython3

    # the file where the raw data will be pickled
    fpath = os.path.dirname( os.getcwd() ) + '\\my_data'
    fname = fpath + '\\data_raw.pkl'

.. code:: ipython3

    # save and load data as a pkl file
    do_save = False
    do_load = False

.. code:: ipython3

    if do_load:
        data = mg.load(fname)
    else:
        data = chad.CHAD_RAW(min_age=social.ADULT_AGE, max_age=social.MAX_AGE)


.. parsed-literal::

    M:\Net MyDocuments\research\code\HEM\abm\source\chad.py:246: DtypeWarning: Columns (1) have mixed types. Specify dtype option on import or set low_memory=False.
      self.quest  = self.get_quest()
    C:\Users\nbrandon\AppData\Local\Continuum\Anaconda3\lib\site-packages\ipykernel\__main__.py:4: DtypeWarning: Columns (4,5) have mixed types. Specify dtype option on import or set low_memory=False.
    

save

.. code:: ipython3

    if do_save:    
        mg.save(data, fname)

The order for getting work data

1. Get the CHADIDs that are for employed, fulltime workers

2. Get the work events data from employed, fulltime workers

3. Calculate the longitudinal data in order to sum ajacent periods and
   merge events from before midnight to after midnight

4. Make 1 work event starting from the first event and ending on the
   last event

.. code:: ipython3

    d_raw, d_long, d_full = analyze_work(data)


.. parsed-literal::

    loading work data...
    calculating longitudinal data...
    calculating fulltime data...
    analyzing moments...
    

.. code:: ipython3

    # the activity data
    d = d_full

.. code:: ipython3

    x = d['stats_end']
    y = d['stats_start']

plot

.. code:: ipython3

    plt.figure(1)
    histogram( x.mu.values, color='green' )
    
    plt.figure(2)
    histogram( y.mu.values, color='blue' )
    
    plt.show()
