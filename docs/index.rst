.. ABMHAP documentation master file, created by
   sphinx-quickstart on Fri Sep  8 13:20:54 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the documentation for the Agent-Based Model of Human Activity Patterns (ABMHAP)!
===========================================================================================
The Agent-Based Model of Human Activity Patterns (ABMHAP, pronounced "ab-map") is one of the
modules for the Life Cycle Human Exposure Model (LC-HEM) project as described in the United States Environmental
Protection Agency (U.S. EPA) research plan, which may be found
`here <https://19january2017snapshot.epa.gov/sites/production/files/2016-11/documents/css_fy16-19_strap.pdf>`_.
ABMHAP is a model capable of creating agents that simulate longitudinal human behavior. The current version of
ABMHAP is able to simulate daily routines for the following behaviors:

#. Sleeping
#. Eating Breakfast
#. Eating Lunch
#. Eating Dinner
#. Working
#. Commuting to Work
#. Commuting from Work
#. Being idle (i.e., time spent not doing the above activities)

The current version of ABMHAP requires the user to input parameters that describe the longitudinal variation in \
behavior of a single individual.

.. The following line is for the application paper.
   ABMHAP can be used to simulate the behaviors of people that represent different demographic groups within the
   general United States population.
   The current version of ABMHAP uses the Consolidated Human Activity Database
   (CHAD) to parametrize the above behavior of agents. More information about CHAD may be found
   `here <https://www.epa.gov/healthresearch/consolidated-human-activity-database-chad-use-human-exposure-and-health-studies-and>`_.


.. This is for the ABMHAP application paper.
   The current version of ABMHAP is written in Python version 3.5.3 and can be run in parallel. The Python libraries \
   that must be installed in order for ABMHAP to run are listed below.

The current version of ABMHAP is written in Python version 3.5.3. More information on the Python programming
language may be found `here <https://www.python.org/>`_. The Python libraries that must be installed in
order for ABMHAP to run are listed below.

* matplotlib
* multiprocessing
* numpy
* pandas
* scipy
* sphinx
* statsmodels

ABMHAP is written by Dr. Namdi Brandon (ORCID: 0000-0001-7050-1538).

|

Disclaimer
   The United States Environmental Protection Agency through its Office of Research and Development has
   developed this software. The code is made publicly available to better communicate the research. All
   input data used for a given application should be reviewed by the researcher so that the model results
   are based on appropriate data for any given application. This model is under continued development. The
   model and data included herein do not represent and should not be construed to represent any Agency
   determination or policy.

How to Run the Code
#################################
The following describes how to run an ABMHAP simulation of one agent. In order to do so, the user must
do the following:

#. set the input parameters of the simulation in the file :literal:`\\run\\main_params.py`
#. run the executable using :literal:`\\run\\main.py`


Setting the input parameters
----------------------------

In order to run ABMHAP, the user must set the following types of input parameters in
:literal:`\\run\\main_params.py`:

#. input parameters that govern the general logistics of the simulation
#. input parameters that govern the the length of simulation duration
#. input parameters that define the behavior of the agent

For illustrative purposes, what follows is a demonstration of how to parametrize a run for ABMHAP.

The below code does the following:

* informs the algorithm to not print the output to the screen
* informs the algorithm to not plot the output
* informs the algorithm to not save the output to a file
* should the output file be saved, sets the output file to :literal:`\\some_directory\\outputfile.csv`

The user must set the input parameters that govern the general logistics of the simulation::

   # whether (if True) or not (if False) the output of the simulation should
   # print a message to screen
   do_print    = False

   # whether (if True) or not (if False) the output of the simulation should
   # be plotted a message to screen
   do_plot     = False

   # whether (if True) or not (if False) the output of the simulation should
   # be saved in a file
   do_save     = False

   # the name of the output file should the output be saved. The filename
   # should have a ".csv" extension
   fname       = 'some_directory\\outputfile.csv'

The following code shows how to set ABMHAP to run starting on Sunday, Day 0 starting from 16:00
and ending on Monday, Day 7 at 0:00. It's recommended that the user start running the code on a Sunday or Saturday
at 16:00 in order to minimize potential activity conflicts at initiation.

The user must set the input parameters dealing with the duration of the simulation::

   # the number of days for the simulation
   num_days    = 7

   # the number of additional hours
   num_hours   = 8

   # the number of additional minutes
   num_min     = 0

The user must set the input parameters dealing with when in the simulation year the simulation should start::

   # start the simulation on Sunday, Day 0 at 16:00
   t_start     = WINTER * SEASON_2_MIN + 0 * WEEK_2_MIN \
               + SUNDAY * DAY_2_MIN + 16 * HOUR_2_MIN

where the following constants are useful in assigning input parameters that define
the start time of the simulation::

   # an agent-based model module with capabilities concerning time
   import temporal

   # the value of Sunday
   SUNDAY         = temporal.SUNDAY

   # convert one day into minutes
   DAY_2_MIN      = temporal.DAY_2_MIN

   # convert one hour into minutes
   HOUR_2_MIN     = temporal.HOUR_2_MIN

   # the number of minutes in one season (13 weeks)
   SEASON_2_MIN   = temporal.SEASON_2_MIN

   # the number of minutes in one week
   WEEK_2_MIN     = WEEK_2_MIN

   # the winter season (has the value 0)
   WINTER         = temporal.WINTER

The user must set the input parameters that govern the behavior of the agent. The input parameters will govern
the agent's behavior for the following activities.

#. sleeping
#. eating breakfast
#. eating lunch
#. eating dinner
#. working
#. commuting to work
#. commuting from work

In order to set the sleeping behavior, the user must set the the mean and standard deviation for the start time
and end time for the sleep activity. The agent's behavior for sleeping is set as follows::

   # set the mean start time to be 22:00
   sleep_start_mean     = np.array( [22 * HOUR_2_MIN] )

   # set the standard deviation of the start time to be 30 minutes
   sleep_start_std      = np.array( [30] )

   # set the mean end time to be 8:00
   sleep_end_mean       = np.array( [8 * HOUR_2_MIN] )

   # set the standard deviation of the end time to be 15 minutes
   sleep_end_std        = np.array( [15] )


In order to set the eat breakfast behavior, the user must set the mean and standard deviation for the start time
and duration for the eat breakfast activity. The agent's behavior for eating breakfast is set as follows::

   # set the mean start time to be 8:00
   bf_start_mean       = np.array( [8 * HOUR_2_MIN] )

   # set the standard deviation of the start time to be 10 minutes
   bf_start_std        = np.array( [10] )

   # set the mean duration to be 15 minutes
   bf_dt_mean          = np.array( [15] )

   # set the standard deviation of the duration to be 10 minutes
   bf_dt_std           = np.array( [10] )

In order to set the eat lunch behavior, the user must set the mean and standard deviation for the start time
and duration for the eat lunch activity. The agent's behavior for eating lunch is set as follows::

   # set the mean start time to be 12:000
   lunch_start_mean       = np.array( [12 * HOUR_2_MIN] )

   # set the standard deviation of start time to be 15 minutes
   lunch_start_std        = np.array( [15] )

   # set the mean duration to be 30 minutes
   lunch_dt_mean          = np.array( [30] )

   # set the standard deviation of duration to be 10 minutes
   lunch_dt_std           = np.array( [10] )

In order to set the eat dinner behavior, the user must set the mean and standard deviation for the start time
and duration for the eat dinner activity. The agent's behavior for eating dinner is set as follows::

   # set the mean start time to be 19:00
   dinner_start_mean       = np.array( [19 * HOUR_2_MIN] )

   # set the standard deviation of start time to be 10 minutes
   dinner_start_std        = np.array( [10] )

   # set the mean of duration to be 45 minutes
   dinner_dt_mean          = np.array( [45] )

   # set the standard deviation of duration to be 5 minutes
   dinner_dt_std           = np.array( [5] )

In order to set the work behavior, the user must set the mean and standard deviation for the start time and
end time for the work activity. The agent's behavior for working is set as follows::

   # set the mean start time to be 9:00
   work_start_mean     = np.array( [9 * HOUR_2_MIN] )

   # set the standard deviation of start time to be 15 minutes
   work_start_std      = np.array( [15] )

   # set the mean end time to be 17:00
   work_end_mean       = np.array( [17 * HOUR_2_MIN] )

   # set the standard deviation of end time to be 5 minutes
   work_end_std        = np.array( [5] )

The user must set the agent's employment status. The agent's employment status is set as follows::

   # an agent-based model module for functionality dealing with occupation
   import occupation

   # set the job identifier (job id) as standard job if the agent
   # is supposed to work
   job_id   = occupation.STANDARD_JOB

   # OR set the job identifier (job id) as not having a job if the agent
   # is NOT supposed to work
   job_id   = occupation.NO_JOB

In order to set the commute to work behavior, the user must set the mean and standard deviation for the duration
of the commute to work activity. The agent's behavior for commuting to work is set as follows::

   # set the mean duration to be 30 minutes
   commute_to_work_dt_mean     = np.array( [30] )

   # set the standard deviation to be 10 minutes
   commute_to_work_dt_std      = np.array( [10] )

In order to set the commute from work behavior, the user must set the mean and standard deviation for the duration
of the commute from work activity. The agent's behavior for commuting from work is set as follows::

   # set the mean duration to be 30 minutes
   commute_from_work_dt_mean     = np.array( [30] )

   # set the standard deviation to be 10 minutes
   commute_from_work_dt_std      = np.array( [10] )


Running the simulation
----------------------

After defining all of the parameters in the file :literal:`\\run\\main_params.py`, the code is run by doing
the following:

#. go to the :literal:`\\run` directory.
#. enter :literal:`python main.py` into the terminal (or command line)
#. press enter (or return)

Interpreting the output
-----------------------

ABMHAP outputs the record of the activities that the agent did during the simulation. This record is called an
**activity diary**. An activity diary is a chronological record contains the following information about each
activity: day, start time, end time, duration, and location.

Below is an example of the output of ABMHAP. Recall that ABMHAP saves the activity diary in terms of a .csv file

+-----+--------+--------+--------+-----+-----+
| day | start  | end    | dt     | act | loc |
+=====+========+========+========+=====+=====+
| 0   | 16     | 19     | 3      | -1  | 0   |
+-----+--------+--------+--------+-----+-----+
| 0   | 19     | 19.75  | 0.75   | 4   | 0   |
+-----+--------+--------+--------+-----+-----+
| 0   | 19.75  | 22     | 2.25   | -1  | 0   |
+-----+--------+--------+--------+-----+-----+
| 0   | 22     | 8      | 10     | 6   | 0   |
+-----+--------+--------+--------+-----+-----+
| 1   | 8      | 8.25   | 0.25   | 3   | 0   |
+-----+--------+--------+--------+-----+-----+
| 1   | 8.25   | 8.5    | 0.25   | -1  | 0   |
+-----+--------+--------+--------+-----+-----+
| 1   | 8.5    | 9      | 0.5    | 2   | 1   |
+-----+--------+--------+--------+-----+-----+
| 1   | 9      | 12     | 3      | 7   | 3   |
+-----+--------+--------+--------+-----+-----+
| 1   | 12     | 12.5   | 0.5    | 5   | 3   |
+-----+--------+--------+--------+-----+-----+
| 1   | 12.5   | 17     | 4.5    | 7   | 3   |
+-----+--------+--------+--------+-----+-----+
| 1   | 17     | 17.5   | 0.5    | 1   | 1   |
+-----+--------+--------+--------+-----+-----+
| 1   | 17.5   | 19     | 1.5    | -1  | 0   |
+-----+--------+--------+--------+-----+-----+
| 1   | 19     | 19.75  | 0.75   | 4   | 0   |
+-----+--------+--------+--------+-----+-----+
| 1   | 19.75  | 22     | 2.25   | -1  | 0   |
+-----+--------+--------+--------+-----+-----+
| 1   | 22     | 8      | 10     | 6   | 0   |
+-----+--------+--------+--------+-----+-----+

where day, start, end, dt, act, and loc represent the day the activity starts, the start time of the
activity (in hours), the end time of the activity (in hours), the duration of the activity (in hours), the
activity identifier, and the location identifier, respectively. In the results, the time of day 16:30 is
represented as 16.5.

The following table is an interpretation of the example output shown above. In the table, the duration is
expressed in minutes.

+-----+--------+--------+-----------+--------------------+--------------------+
| Day | Start  | End    | Duration  | Activity Code      | Location Code      |
+=====+========+========+===========+====================+====================+
| 0   | 16:00  | 19:00  | 180       | Idle               | Home               |
+-----+--------+--------+-----------+--------------------+--------------------+
| 0   | 19:00  | 19:45  | 45        | Eat dinner         | Home               |
+-----+--------+--------+-----------+--------------------+--------------------+
| 0   | 19:45  | 22:00  | 135       | Idle               | Home               |
+-----+--------+--------+-----------+--------------------+--------------------+
| 0   | 22:00  | 8:00   | 600       | Sleep              | Home               |
+-----+--------+--------+-----------+--------------------+--------------------+
| 1   | 8:00   | 8:15   | 15        | Eat breakfast      | Home               |
+-----+--------+--------+-----------+--------------------+--------------------+
| 1   | 8:15   | 8:30   | 15        | Idle               | Home               |
+-----+--------+--------+-----------+--------------------+--------------------+
| 1   | 8:30   | 9:00   | 30        | Commute to work    | Out of doors       |
+-----+--------+--------+-----------+--------------------+--------------------+
| 1   | 9:00   | 12:00  | 180       | Work               | Workplace          |
+-----+--------+--------+-----------+--------------------+--------------------+
| 1   | 12:00  | 12:30  | 30        | Eat lunch          | Workplace          |
+-----+--------+--------+-----------+--------------------+--------------------+
| 1   | 12:30  | 17:00  | 270       | Work               | Workplace          |
+-----+--------+--------+-----------+--------------------+--------------------+
| 1   | 17:00  | 17:30  | 30        | Commute from work  | Out of doors       |
+-----+--------+--------+-----------+--------------------+--------------------+
| 1   | 17:30  | 19:00  | 90        | Idle               | Home               |
+-----+--------+--------+-----------+--------------------+--------------------+
| 1   | 19:00  | 19:45  | 45        | Eat dinner         | Home               |
+-----+--------+--------+-----------+--------------------+--------------------+
| 1   | 19.45  | 22:00  | 135       | Idle               | Home               |
+-----+--------+--------+-----------+--------------------+--------------------+
| 1   | 22:00  | 8:00   | 600       | Sleep              | Home               |
+-----+--------+--------+-----------+--------------------+--------------------+

The activity codes map as the following:

+--------------------+-----------------+
| Activity           | Activity Code   |
+====================+=================+
| Idle               | -1              |
+--------------------+-----------------+
| Commute from work  | 1               |
+--------------------+-----------------+
| Commute to work    | 2               |
+--------------------+-----------------+
| Eat breakfast      | 3               |
+--------------------+-----------------+
| Eat dinner         | 4               |
+--------------------+-----------------+
| Eat lunch          | 5               |
+--------------------+-----------------+
| Sleep              | 6               |
+--------------------+-----------------+
| Work               | 7               |
+--------------------+-----------------+

The location codes map as the following:

+--------------------+-----------------+
| Location           | Location Code   |
+====================+=================+
| Home               | 0               |
+--------------------+-----------------+
| Out of doors       | 1               |
+--------------------+-----------------+
| Workplace          | 3               |
+--------------------+-----------------+

Source Directory
##############################
These files are the key modules that are used to create the ABMHAP algorithm.

Contents:

.. toctree::
   :maxdepth: 4

   activity
   asset
   bed
   bio
   commute
   diary
   eat
   food
   home
   hunger
   income
   interrupt
   interruption
   location
   meal
   my_globals
   need
   occupation
   params
   person
   rest
   scheduler
   sleep
   social
   state
   temporal
   transport
   travel
   universe
   work
   workplace

Run Directory
##############################
These are the files needed to run an instance of ABMHAP with one agent parametrized by user-defined parameters.

The driver for these type of runs is main.py.

Contents:

.. toctree::
   :maxdepth: 4

   main
   main_params
   scenario
   singleton

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
