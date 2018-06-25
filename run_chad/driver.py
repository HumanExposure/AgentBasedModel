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

"""
This code runs the simulation for the Agent-Based Model of Human Activity Patterns \
(ABMHAP) module of the Life Cycle Human Exposure Model (LC-HEM) project. This code is \
the driver for seeing how well ABMHAP parameterized with empirical human behavior data from the \
Consolidated Human Activity Database (CHAD) compares to results seen in CHAD.

.. note::
    This code may be run in batches in order to run many households while conserving memory. That is, \
    instead of running 32 households at once (and keeping 32 households in memory), the program can \
    run 2 batches of 16 households (for a total of 32 household). This halves the amount of memory \
    used in the simulation compared to running the simulation of 1 batch of 32 households. We  \
    will shown how to run the code using "batches" below.

The driver can also be run in **parallel**. We will show how to do so below.

To run the code, do the following.

#. Set the simulation-centric parameters in driver_params.py
#. Run the code as
    \> :literal:`python driver.py num_process num_hhld num_batch`
    where
        * :literal:`num_process` is the total number of cores (i.e, processing units) used in the simulation
        * :literal:`num_hhld` is the number of simulations to run per batch
        * :literal:`num_batch` is the number of batches used per core

The following are examples on how to run the code:

To run in **serial** with with 64 households per batch, 1 batch (implied)

\> :literal:`python driver.py 1 64 1`

\> :literal:`python driver.py 1 64`

To run in serial using 2 batches with 1 thread with 32 households per batch, 2 batches

\> :literal:`python driver.py 1 32 2`

To run in **parallel** using 4 cores with 64 households total (16 household per core per batch), 1 batch (implied)

\> :literal:`python driver.py 4 64 1`

\> :literal:`python driver.py 4 64`

To run in parallel using 4 cores with 32 households per batch, 2 batches(8 households per core per batch)

\> :literal:`python driver.py 4 32 2`

"""

# ===========================================
# import
# ===========================================

import sys
sys.path.append('..\\source')
sys.path.append('..\\run')
sys.path.append('..\\processing')

# for plotting
import matplotlib.pylab as plt

# for parallelism
import multiprocessing as mp

# timing capability
import datetime, os, time

# mathematical capabilities
import numpy as np

# ABMHAP modules
import demography as dmg
import my_globals as mg
import driver_params as dp

import chad_params, commute_from_work_trial, commute_to_work_trial, driver_result, \
    eat_breakfast_trial, eat_dinner_trial, eat_lunch_trial, omni_trial, params, \
    sleep_trial, trial, work_trial

import chad_demography_adult_non_work as cdanw
import chad_demography_adult_work as cdaw
import chad_demography_child_school as cdcs
import chad_demography_child_young as cdcy

# ===========================================
# constants
# ===========================================
# this chooses the correct trial to run
TRIAL_2_CONSTRUCTOR = { trial.COMMUTE_FROM_WORK: commute_from_work_trial.Commute_From_Work_Trial,
                        trial.COMMUTE_TO_WORK: commute_to_work_trial.Commute_To_Work_Trial,
                        trial.EAT_BREAKFAST: eat_breakfast_trial.Eat_Breakfast_Trial,
                        trial.EAT_DINNER: eat_dinner_trial.Eat_Dinner_Trial,
                        trial.EAT_LUNCH: eat_lunch_trial.Eat_Lunch_Trial,
                        trial.SLEEP: sleep_trial.Sleep_Trial,
                        trial.WORK: work_trial.Work_Trial,
                        trial.OMNI: omni_trial.Omni_Trial,
                        }

# given a trial, this obtains the respective CHAD parameters
TRIAL_2_CHAD_PARAMS = { trial.COMMUTE_FROM_WORK: chad_params.COMMUTE_FROM_WORK,
                        trial.COMMUTE_TO_WORK: chad_params.COMMUTE_TO_WORK,
                        trial.EAT_BREAKFAST: chad_params.EAT_BREAKFAST,
                        trial.EAT_DINNER: chad_params.EAT_DINNER,
                        trial.EAT_LUNCH: chad_params.EAT_LUNCH,
                        trial.SLEEP: chad_params.SLEEP,
                        trial.WORK: chad_params.WORK,
                        trial.OMNI: chad_params.OMNI,
                        }

# ===========================================
# functions
# ===========================================

def create_trials(num_hhld, num_days, num_hours, num_min, trial_code, chad_activity_params, \
                  demographic, num_people, do_minute_by_minute, do_print=False):

    """
    This function creates the input data for each household in the simulation.

    :param int num_hhld: the number of households simulated
    :param int num_days: the number of days in the simulation
    :param int num_hours: the number of additional hours
    :param int num_min: the number of additional minutes
    :param int trial_code: the trial identifier
    :param chad_params.CHAD_params chad_activity_params: the activity parameters \
    used to sample "good" CHAD data

    :param int demographic: the demographic identifier
    :param int num_people: the number of people per household
    :param bool do_minute_by_minute: a flag for how the time steps progress in the scheduler
    :param bool do_print: flag whether to print messages to the console

    :returns: input data where each entry corresponds to the input \
    for the respective household in the simulation
    :rtype: list of :class:`trial.Trial`
    """

    # load the parameters necessary for the runs comparing the ABMHAP to CHAD
    # run the simulation using default parameters
    param_list = [params.Params(num_days=num_days, num_hours=num_hours, num_min=num_min, \
                                num_people=num_people, do_minute_by_minute=do_minute_by_minute) \
                  for _ in range(num_hhld)]

    # print message
    if do_print:
        print('initializing trials...')

    #
    # create the conditions for each trial
    #

    # start timing
    start = time.time()

    # initialize the simulation inputs
    trials = initialize_trials(param_list, trial_code, chad_activity_params, demographic)

    # end timing
    end = time.time()

    # calculate the elapsed time
    dt_elapsed = end - start

    # print message
    if do_print:
        print('elapsed time to initialize %d trials:\t%.3f [s]\n' % (num_hhld, dt_elapsed))

    return trials

def delete_batch_files(fname_base, num_batch):

    """
    This function deletes the batch files.

    :param str fname_base: the file name for the files without the ".pkl", that are the basis of the batch files \
    that will be deleted
    :param int num_batch: the number of batches used in the code run

    :returns:
    """

    # delete all batch files marked by fname_base
    for i in range(num_batch):

        # add the respective ending to fname_base for appropriate batch number
        f_ending    = mg.F_BATCH_ENDING % i
        fname       = fname_base + f_ending

        # if the path exists (which it should), delete the file
        if os.path.exists(fname):
            os.remove(fname)

    return

def get_batch_filenames(fpath, fname):

    """
    This file gets the file names for the batch saves.

    :param str fpath: the name of the directory that the batch file names are stored
    :param str fname: the name of the file to save (.pkl)

    :returns: the batched file names
    :rtype: list
    """

    # list all of the file names in the directory that end with '.pkl'
    fname_list = [x  for x in os.listdir(fpath)
                  if mg.check_filename_extension(x, mg.EXTENSION_PKL) ]

    # get the file names for the data that corresponds to batch files
    fname_list = [ x for x in fname_list if is_batch_file(x, mg.EXTENSION_PKL) ]

    # take away the leading '\\'
    fname_temp = fname.lstrip('\\')

    # get the index of where the .pkl, .pickle is
    idx = fname_temp.find('.')

    # get the file name before the '.'
    fname_temp = fname_temp[:idx]

    # get the file names that are part of the batch
    x = [('%s\\%s' % (fpath, f)) for f in fname_list if fname_temp in f]

    return x

def get_chad_demo(demographic):

    """
    Given the demographic, this function returns the respective CHAD_demography object.

    :param int demographic: the demography identifier

    :returns: the respective CHAD_demography object
    """

    chooser = {dmg.ADULT_WORK: cdaw.CHAD_demography_adult_work(),
               dmg.ADULT_NON_WORK: cdanw.CHAD_demography_adult_non_work(),
               dmg.CHILD_SCHOOL: cdcs.CHAD_demography_child_school(),
               dmg.CHILD_YOUNG: cdcy.CHAD_demography_child_young(),
               }

    return chooser[demographic]

def get_cmd_line_params():

    """
    This function gets the parameters from the command line.

    The order of arguments to be read on the command line in order:

    #. the number of processors (threads)
    #. the number of households per batch
    #. the number of batches

    :returns: the number of processors, the, the total number of households to simulate, the number of batches
    :rtype: int, int, int
    """

    #indices
    IDX_NUM_PROCESS = 1
    IDX_NUM_HHLD    = 2
    IDX_NUM_BATCH   = 3

    # the number of command line arguments + 1
    N_MAX   = 4

    # the number of arguments on the command line
    N = len(sys.argv)

    # the error message if the something is wrong on the command line
    msg_error = '\n\nERROR. Did not specify the number of processors, number of households! Quitting...'

    # check to see if the the number of arguments is the full amount. If batch size is not entered, then it is \
    # assumed to be the value 1
    condition = (N >= N_MAX - 1) and (N <= N_MAX)

    # check to make sure the command line argument count is acceptable
    assert condition, msg_error

    # check to see if the the number of arguments is the full amount. If batch size is not entered, then it is \
    # assumed to be the value 1

    num_process = sys.argv[IDX_NUM_PROCESS]
    num_hhld    = sys.argv[IDX_NUM_HHLD]

    # all of the entries were entered on the command line
    if N == N_MAX:
        num_batch = sys.argv[IDX_NUM_BATCH]
    else:
        # default batch size
        num_batch = 1

    # convert the entries into integers
    num_process = int(num_process)
    num_hhld    = int(num_hhld)
    num_batch   = int(num_batch)

    return num_process, num_hhld, num_batch

def get_current_batch_size(num_hhld, idx, max_batch_size):

    """
    This function returns the number of households for the current batch if the total
    number of households is a multiple of the number of batches. Each batch
    contains max_batch_size amount of households.
    However, if not, the last batch will be smaller than the number of the max_batch_size.

    :param int num_hhld: the total amount of households in the simulation
    :param int idx: the index of the current batch number
    :param int max_batch_size: the maximum number of households per batch

    :returns: the current batch size
    :rtype: int
    """

    # the total number of households remaining to simulate
    hhld_remaining = num_hhld - idx * max_batch_size

    # calculate the batch size to be the minimum of the number of households left to simulate OR the
    # max_batch_size
    batch_size = min(hhld_remaining, max_batch_size)

    return batch_size

def get_fnames(fpath, demographic, num_days, N, do_print=False):

    """
    Given a directory, this function creates the file names that will be used
    to save the ABMHAP trials (input) and the ABMHAP data (output) according
    to the respective demographic.

    :param str fpath: the directory in which to save the files
    :param int demographic: the demography identifier
    :param int num_days: the number of days in the simulation
    :param int N: the total number of households
    :param bool do_print: a flag to indicate whether (if True) or not \
    (if False) to print a message to the screen

    :returns: the file name to save the trials data (".pkl" extension); \
    the file name to save the data (".pkl" extension"), \
    the file name to save the the basis (no ".pkl" extension) of the file \
    name to save the trials data, \
    the basis (no ".pkl" extension) of the file name to save the ABMHAP output data
    :rtype: str, str, str, str
    """

    # the path to save the the data
    fpath_save      = set_save_path(fpath, N, num_days)

    # choose the file names for the given demographic
    chooser_fname   = { dmg.ADULT_WORK: (fpath_save + '\\trials_adult_work.pkl', \
                                         fpath_save + '\\data_adult_work.pkl'),
                        dmg.ADULT_NON_WORK: (fpath_save + '\\trials_adult_non_work.pkl', \
                                             fpath_save + '\\data_adult_non_work.pkl'),
                        dmg.CHILD_SCHOOL: (fpath_save + '\\trials_child_school.pkl', \
                                           fpath_save + '\\data_child_school.pkl'),
                        dmg.CHILD_YOUNG: (fpath_save + '\\trials_child_young.pkl', \
                                          fpath_save + '\\data_child_young.pkl'),
                        }

    # get the file name of the trials and data, respectively
    fname_trials, fname_data = chooser_fname[demographic]

    #
    # Strip the ".pkl" at the end of the file name ino order to do batch saving
    #
    fname_trials_base   = fname_trials[:-4]
    fname_data_base     = fname_data[:-4]

    # print the name of fname_trials_base and fname_data_base
    if do_print:
        print('trials base:\t%s\ndata base:\t%s' % (fname_trials_base, fname_data_base))

    return fname_trials, fname_data, fname_trials_base, fname_data_base

def get_loaded_trials_for_batch(loaded_trials, i, batch_size):

    """
    This function extracts the household input information from the pre-loaded
    input data for the respective batch.

    :param loaded_trials: input data needed for the simulation
    :type loaded_trials: list of :class:`trial.Trial`
    :param int i: the current batch number
    :param int batch_size: the number of households in the batch

    :returns: the input data that corresponds to the batch number
    :rtype: list of :class:`trial.Trial`
    """

    # the start index of the trials for the current batch
    start = i * batch_size

    # the ending index of the trials for the current batch
    end = min(start + batch_size, len(loaded_trials))

    # get the trials that correspond to the current batch
    trials = loaded_trials[start:end]

    return trials

def get_max_batch_size(num_hhld, num_batch):

    """
    This function returns the maximum number of households
    simulated per batch.

    :param int num_hhld: the total number of households to simulate
    :param int num_batch: the number of batches

    :returns: the number of households to simulate per batch
    :rtype: int
    """

    # the batch size
    batch_size = np.ceil(num_hhld / num_batch).astype(int)

    return batch_size

def get_results(diaries, trials):

    """
    This function takes the output and input from the simulation and converts
    the data into the appropriate output and input types.

    :param diaries: each activity diary (output) in the Monte-Carlo simulation
    :type diaries: list of :class:`diary.Diary`
    :param trials: the input data for each household simulation.
    :type trials: list of :class:`trial.Trial`

    :returns: the output, the input
    :rtype: :class:`driver_result.Driver_Result`, list of :class:`params.Params`
    """

    # get the demographic
    demographic = trials[0].demographic

    # store the CHAD parameters
    chad_param_list = [t.sampling_params for t in trials]

    # store the results of the simulations in an object
    results = driver_result.Driver_Result(diaries=diaries, chad_param_list=chad_param_list, demographic=demographic)

    # adding this for testing
    param_list = [t.params for t in trials]

    return results, param_list

def initialize_trials(param_list, trial_code, chad_activity_params, demographic):

    """
    This function initializes the trials (input parameters) for the simulation.

    :param param_list: contains information on how to initialize the \
    simulation for each household.
    :type pram_list: list of :class:`params.Params`

    :param int trial_code: the code of what trial to run
    :param chad_params.CHAD_params chad_activity_params: the activity parameters used to sample "good" CHAD data
    :param int demographic: this is the code for what demographic to run

    :returns: the initialized simulation scenarios
    :rtype: list of :class:`trial.Trial`
    """

    trials = list()

    # create and initialize each trial
    for x in param_list:

        # choose the correct trial constructor
        f = TRIAL_2_CONSTRUCTOR[trial_code]

        # create the trial object using the constructor f()
        t = f(x, chad_activity_params, demographic)

        t.initialize()

        # add the initialized trial to the list of trials to do
        trials.append(t)

    return trials

def is_batch_file(fname, extensions):

    """
    This function indicates whether or not the filename is a batch file. For example,
    given a file name called filename_b0000.pkl will return True. On the other hand,
    filename.pkl will return False.

    :param str fname: the file name
    :param extensions: the file extensions for the file name
    :type extensions: str, list of str

    :returns: flag indicating whether the file name is a batch file
    :rtype: bool
    """

    # remove the pickle file name extension
    x = [ fname[:-len(x)] for x in extensions if x in fname ][0]

    # split the string about the '_'
    x = x.split('_')

    # the last item corresponds to the ending of the string
    x = x[-1]

    # if the sting starts with a 'b' and the rest can be an integer,
    # the file was a batch file in the format ('filename_b0000.pkl')
    # Thus, return True
    ok =  (x[0] == 'b') and ( type( int(x[1:]) ) is int)

    return ok

def load_trials_for_batches(fname_load_trials_base, num_batch, do_print):

    """
     This function loads pre-existing trials data.

     :param str fname_load_trials: the filename (.pkl) of the trials data to load
     :param int num_batch: the number of batches
     :param bool do_print: a flag to indicate whether or not to print a message to \
     screen about the logistics of loading the data

     :returns: the input data that has been loaded, \
     the file name for the input data, \
     the batch size
     :rtype: list of :class:`trial.Trial`, str, int
     """

    # the name of the file names for the pre-existing trial data
    fname_load_trials = fname_load_trials_base + '.pkl'

    # start timing
    start = time.time()

    # load the trials
    trials = mg.load(fname_load_trials)

    # end timing
    end = time.time()

    # the elapsed time
    dt_elapsed = end - start

    # the number of households
    num_hhld    = len(trials)

    # the maximum number of households per batch
    batch_size  = get_max_batch_size(num_hhld, num_batch)

    if do_print:
        print('\nloaded trials from\t%s' % fname_load_trials)
        print('elapsed time to load %d trials:\t%.3f [s]\n' % (num_hhld, dt_elapsed))

    return trials, fname_load_trials, batch_size

def print_end(elapsed_time):

    """
    Print the elapsed time for the simulation message.

    :param float elapsed_time: the elapsed time for the simulation [seconds]
    :returns:
    """

    print('--------------------------------------')
    print('------------ Finished ----------------')
    print('--------------------------------------')

    print('elapsed time: %.2f[s]' % elapsed_time)

    return

def print_start():

    """
    Print the message about starting the simulation.

    :return:
    """

    print('--------------------------------------')
    print('------------ Starting ----------------')
    print('--------------------------------------')

    return

def print_starting_info(num_hhld, batch_size, num_batch, num_days, num_process, total_cpus):

    """
    Print information before the beginning of the simulation.

    :param int num_hhld: the total number of households
    :param int batch_size: the maximum number of households to simulate per batch
    :param int num_hhld_per_batch: the number of households per batch
    :param num_days: the number of days in the simulation
    :param num_process: the number of processors used
    :param total_cpus: the total amount of potential CPUs available.

    :returns:
    """

    print('number of households: %d\t\tnumber of days per simulation: %d' % (num_hhld, num_days) )
    print('number of batches: %d\t\t\tmaximum number of households per batch: %d' % (num_batch, batch_size) )
    print('using %d out of %d CPU processors' % (num_process, total_cpus) )

    return

def run(num_process, trials, do_print=False):

    """
    This function runs each simulation (in serial or parallel).

    :param int num_process: the number of processors to use
    :param trials: the input for each simulation
    :type trials: list of :class:`trial.Trial`
    :param bool do_print: a flag indicating whether to print (if True) or not (if False)

    :returns: the results of the simulations, the input parameters
    :rtype: diary_result.Diary_result, list of :class:`params.Params`
    """

    # close all plots
    plt.close('all')

    # start timing
    start = time.time()

    if do_print:
        print('starting...')

    #
    # run in serial
    #

    if num_process == 1:
        # this test prints the parameters for each agent in the trial
        diaries = run_serial(trials, do_print=True)

    #
    # run in parallel
    #
    else:
        diaries = run_parallel(num_process, trials)

    # record the elapsed simulation time
    end = time.time()
    total_simulation_time = end - start

    # print the elapsed simulation time
    if do_print:
        print('elapsed time for driver.run():\t%.3f [s]' % total_simulation_time)

    # get the results
    results, param_list = get_results(diaries, trials)

    return results, param_list

def run_batch(num_batch, num_hhld, num_process, num_days, num_hours, num_min, trial_code, chad_activity_params, \
              demographic, num_people, do_minute_by_minute, do_print, do_save, \
              fpath, do_load_trials=False, fname_load_trials_base=None):

    """
    Run the simulation in batches.

    :param int num_batch: the number of batches
    :param int num_hhld: the total number of households to simulate
    :param int num_process: the number of processors used
    :param int num_days: the number of days in the simulation
    :param int num_hours: the number of additional hours in the simulation
    :param int num_min: the number of additional minutes in the simulation
    :param int trial_code: the identifier for the trial being run
    :param chad_params.CHAD_params chad_activity_params: the activity parameters used to sample "good" CHAD data
    :param int demographic: the demographic identifier
    :param bool do_print: a flag indicating whether to print (if True) or not (if False)

    :param bool do_save: flag to save the output
    :param str fname_trials_base: the file name for the trials without the .pkl, which will be used for saving the \
    trial information (.pkl)
    :param str fname_data_base: the file name for the ABMHAP without the .pkl, which will be used for saving the \
    trial information (.pkl)
    :param bool do_load_trials: indicating whether (if True) or not (if False) to load trials from a saved \
    file instead of creating a new set of trials
    :param str fname_load_trials_base: the file name for the ABMHAP trials without the .pkl, which will be used for \
    saving the trial information (.pkl)

    :returns: the file name of the input data, \
    the file name of the output data, \
    the file name of the input data (no ".pkl"), \
    the file name of the output data (no ".pkl")

    :rtype: str, str, str, str
    """

    #
    # load all the trials if loading trials (input)
    #
    if do_load_trials:

        loaded_trials, fname_load_trials, max_batch_size \
            = load_trials_for_batches(fname_load_trials_base, num_batch, do_print)

        #
        # start testing
        #
        for x in loaded_trials:
            x.params.num_days = 7
            x.params.set_num_steps()
            x.params.set_no_variation()
        #
        # end testing
        #
        num_days    = loaded_trials[0].params.num_days
        num_hhld    = len(loaded_trials)
    else:
        max_batch_size = get_max_batch_size(num_hhld, num_batch)

    #  print starting information
    print_starting_info(num_hhld, max_batch_size, num_batch, num_days, num_process, mp.cpu_count())

    # create the file names for saving files
    fname_trials, fname_data, fname_trials_base, fname_data_base = \
        get_fnames(fpath, demographic, num_days, num_hhld, do_print)

    #
    # loop through batches
    #
    for i in range(num_batch):

        # the number of households to simulate for the current batch
        batch_size = get_current_batch_size(num_hhld, i, max_batch_size)

        #
        # set the trials (input)
        #

        # load the trials data
        if do_load_trials:

            # load the trials data for this batch
            trials = get_loaded_trials_for_batch(loaded_trials, i, batch_size)

        else:

            # if not loading pre-existing trials data, create trials data for this batch
            trials = create_trials(batch_size, num_days, num_hours, num_min, trial_code, \
                                   chad_activity_params, demographic, num_people, \
                                   do_minute_by_minute, do_print)

        #
        # set the file names for saving data for this batch
        #

        # set the file names for the save files for the current batch
        fname_save_trials, fname_save_data \
            = set_save_files_for_batch(fname_trials_base, fname_data_base, i, do_print)

        #
        # run the simulation
        #

        result, param_list = run(num_process, trials, do_print)

        #
        # save the data from the batch as a .pkl file
        #

        if do_save:
            save_for_batch(trials, fname_save_trials, do_print)
            save_for_batch(result, fname_save_data, do_print)

    return fname_trials, fname_data, fname_trials_base, fname_data_base

def run_parallel(num_process, trials):

    """
    This function runs the simulation in parallel.

    :param int num_process: the number of processors used
    :param trials: the input data
    :type trials: list of :class:`trial.Trial`

    :returns: the output of the simulations
    :rtype: list of :class:`diary.Diary`
    """

    # pool the threads
    p = mp.Pool(processes=num_process)

    # the simulation data for each simulation
    diaries = p.map(run_trials_parallel, trials)

    return diaries

def run_serial(trials, do_print=False):

    """
    This function runs the simulation in serial.

    :param trials: the input data
    :type trials: list of :class:`trial.Trial`
    :param bool do_print: a flag whether or not to print the trial number

    :returns: the output of the simulations
    :rtype: list of :class:`diary.Diary`
    """

    diaries = []

    # loop through each simulation
    for i, t in enumerate(trials):

        if do_print:
            print('trial: %d' % i)

        diaries.append(t.run())

    return diaries

def run_trials_parallel(t):

    """
    This function is called in order to run the trials in parallel.

    :param trial.Trial t: the trial to run

    :return: the results of the simulation
    :rtype: diary.Diary
    """

    # run the simulation
    diary_hhld = t.run()

    return diary_hhld

def save(fname_data, fname_trials, fname_data_base, fname_trials_base, num_batch, do_print=False):

    """
    This function saves the input and output from the simulation. It merges \
    the data from the batch save files into one file for not only the \
    trials data (input) but also the ABMHAP simulation data (output). Afterwards, \
    the individual batch files are deleted.

    :param str fname_data: the file name in which to save the ABMHAP data (output)
    :param str fname_trials: the file name in which to save the ABMHAP trials (input)
    :param str fname_data_base: the base (no ".pkl" extension) of the file name in \
    which to save the ABMHAP data (output)
    :param str fname_trials_base: the base (no ".pkl" extension) of file name in \
    which to save the ABMHAP trials (input)
    :param bool do_print: print flag


    :returns:
    """

    # save the batch files as 1 unit
    save_batch_data_as_one_file(fname_data, do_print)
    save_batch_trials_as_one_file(fname_trials, do_print)

    # clean up the batch files
    delete_batch_files(fname_data_base, num_batch)
    delete_batch_files(fname_trials_base, num_batch)

    # save the data as a .csv
    save_diary_to_csv(fname_data)

    return

def save_batch_data_as_one_file(fname, do_print=False):

    """
    The function combines the ABMHAP data from the individual batch saves and saves them in one file.

    :param str fname: the file name of the ABMHAP data (.pkl)

    :returns:
    """

    # the file path
    fpath       = os.path.dirname(fname)

    # take the file name without the path
    f_name      = fname.split(fpath)[1]

    # get the batch file names
    fname_list  = get_batch_filenames(fpath, f_name)

    # get the data
    data_list   = [ mg.load(x) for x in fname_list]

    # save the results
    result      = driver_result.Batch_Result(data_list)

    # saving message
    if do_print:
        msg         = 'saving all batch data....\nFile name: \t%s' % fname
        print(msg)

    # save the data
    mg.save(result, fname)

    return

def save_batch_trials_as_one_file(fname, do_print=False):

    """
    This function combines the trial (input) data from the individual \
    batch saves and saves them in one file.

    :param str fname: the file name of the trials data (.pkl)
    :param bool do_print: print flag

    :returns:
    """

    # the file path
    fpath       = os.path.dirname(fname)

    f_name      = fname.split(fpath)[1]

    # get the batch filen ames
    fname_list  = get_batch_filenames(fpath, f_name)

    # get the data
    trials_list   = [ mg.load(x) for x in fname_list]

    # save the results
    trials = [ subitem for item in trials_list for subitem in item ]

    # saving message
    if do_print:
        msg         = 'saving all batch trials....\nFile name: \t%s' % fname
        print(msg)

    # save the data
    mg.save(trials, fname)

    return

def save_diary_to_csv(fname):

    """
    This function loads an activity diary from a compressed file format \
    and saves it as a .csv file.

    :param str fname: the pickle file that holds the activity diary file.

    :returns:
    """

    # load the data as driver_rest.Driver_Result object
    data = mg.load(fname)

    # acceptable extensions for pickle files
    extensions = mg.EXTENSION_PKL

    # set the file name to .csv
    fname_csv = [ fname.replace(x, '.csv') for x in extensions if x in fname ][0]

    # save the diary as a .csv file
    mg.save_diary_to_csv( data.get_combined_diary(), fname_csv)

    return

def save_for_batch(result, fname, do_print=False):

    """
    Save the data for the current batch.

    :param driver_result.Driver_Result result: the result of the simulation for the current batch
    :param str fname: the file name to save the data for the current batch
    :param bool do_print: print flag

    :returns:
    """

    # save the data from the batch as a .pkl file
    if do_print:
        msg = 'saving data....\nFile name: \t%s' % fname
        print(msg)

    # save the data in compressed form
    mg.save(result, fname)

    return

def set_save_files_for_batch(fname_trials_base, fname_data_base,  i, do_print=False):

    """
    This function sets the save files (inputs and output files) for the current batch.

    :param str fname_trials_base: the file name for the ABMHAP data without the .pkl, \
    which will be used for saving the input data (.pkl)
    :param str fname_data_base: the file name for the ABMHAP data without the .pkl, \
    which will be used for saving the output data (.pkl)
    :param int i: the current batch index
    :param bool do_print: flag indicating whether or not to print relevant \
    information to the console

    :returns: the save file name for the input data, \
    the save file name for the output data
    :rtype: str, str
    """
    # the file ending used for batch saves
    file_ending = mg.F_BATCH_ENDING % i

    # the file name of the trials for the current batch
    fname_save_trials = fname_trials_base + file_ending

    # the file name of the results data for the current batch
    fname_save_data = fname_data_base + file_ending

    # print the batch number and the file name for both the trials and the data from the ABM
    if do_print:
        msg = '\nBatch number: %d\n' % i
        msg = msg + '%s\n%s\n' % (fname_save_trials, fname_save_data)
        print(msg)

    return fname_save_trials, fname_save_data

def set_save_path(fpath, N, num_days):

    """
    This function sets the save path for the data. Given a save path, the function appends it by adding an \
    extension of the current year, month, day, number of households, and number of days in the format.

    For example, if this code is being run to simulate 64 households for 100 days on July 4, 2017 and the \
    file path is "output_path", the file path is set to the following: //output_path//2017_07_04//n0064_d100.

    :param str fpath: the file path in which to save the data
    :param int N: the number of households
    :param int num_days: the number of days in the simulation


    :returns: the file directory in the format '//output_file_path//YYYY_MM_DD//nXXXX_dXXX'
    :rtype: str
    """

    # get today's date
    x = datetime.date.today()

    # set file path with the appropriate ending
    fpath_data = fpath + ( '\\%04d_%02d_%02d\\n%04d_d%03d' % (x.year, x.month, x.day, N, num_days) )

    return fpath_data

def run_everything(num_process, num_hhld, num_batch):

    """
    This code runs the Monte-Carlo simulations. More specifically, it

    #. creates / loads the input data
    #. runs the simulations
    #. saves both the input and output data

    :param int num_process: the number of processes
    :param int num_hhld: the number of households per core per batch
    :param int num_batch: the number of batches

    :return: the file name for the input data, the file name for the output data
    :rtype: str, str
    """

    #
    # Run the code
    #

    # chad demographic
    chad_demo = get_chad_demo(dp.demographic)

    # print starting message
    print_start()

    # start timing the simulation
    tic = time.time()

    fname_trials, fname_data, fname_trials_base, fname_data_base \
        = run_batch(num_batch, num_hhld, num_process, dp.num_days, dp.num_hours, \
                    dp.num_min, dp.trial_code, chad_demo.int_2_param, dp.demographic, \
                    dp.num_people, dp.do_minute_by_minute, \
                    dp.do_print, dp.do_save, dp.fpath, dp.do_load_trials, dp.fname_load_trials_base)

    # end timing the simulation
    toc = time.time()
    elapsed_time = toc - tic

    #
    # print ending statement
    #
    print_end(elapsed_time)

    #
    # Batch Save
    #
    if dp.do_save:

        # save the data
        save(fname_data, fname_trials, fname_data_base, fname_trials_base, num_batch)


    return fname_trials, fname_data

# ===========================================
# run
# ===========================================

if __name__ == '__main__':

    #
    # command line parameters
    #

    # get monte-carlo parameters from command line
    num_process, num_hhld, num_batch = get_cmd_line_params()

    # run the simulations
    run_everything(num_process, num_hhld, num_batch)
