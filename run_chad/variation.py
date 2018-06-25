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
.. warning::
    This file as antiquated and needs to be **REMOVED**.
"""

# ===========================================
# import
# ===========================================
import sys, time
sys.path.append('..\\source')
sys.path.append('..\\processing')

# plotting capability
import matplotlib.pylab as plt

# multiprocessing capability
import multiprocessing as mp

# mathematical capability
import numpy as np

from scipy import integrate
from scipy import optimize

# ABMHAP modules
import my_globals as mg
import demography as dmg
import analysis, driver, driver_result, evaluation, params, trial

# ===========================================
# function
# ===========================================

def run_universe_parallel(u):

    u.run()

    return u

def run_trial_parallel(t):

    t.run()

    return

def run_uni_parallel(t):

    u = t.run_uni()

    return u

def sweep_parallel(x):

    v, chad_param_list, u_list = x
    I = sweep(v, chad_param_list, u_list)

    return I

def run_simulation(t_0, u_list, chad_param_list, num_cpu=1, pool=None, do_print=True):

    # empty trial
    t = trial.Trial(None, None, None)

    # reset / initialize the runs
    for u in u_list:
        u.reset(t_0)

    # start recording the time
    start = time.time()

    # this test prints the parameters for each agent in the trial
    # need to restart the clock to t_start, need to reiniitalize all parameters to the default state
    # before restarting the simulations
    if num_cpu == 1:
        for u in u_list:
            u.run()
    else:
        u_list = pool.map(run_universe_parallel, u_list)

    # record the time
    end = time.time()

    # time to run the simulation
    dt = end - start

    if do_print:
        print('elapsed time for variation.run_simulation():\t%.3f [s]' % dt)

    # this is the list of activity diaries per household
    diaries = [ t.get_diary(u) for u in u_list]

    # store the results of the simulations in an object
    result = driver_result.Driver_Result(diaries=diaries, chad_param_list=chad_param_list)

    return result


def run_initial(trials, chad_param_list, do_print=True, num_cpu=1, pool=None):

    # start recording the time
    start = time.time()

    # this test prints the parameters for each agent in the trial
    if num_cpu == 1:
        u_list = [ t.run_uni() for t in trials]
    else:
        u_list = pool.map( run_uni_parallel, trials)

    # record the time
    end = time.time()

    # simulation time
    dt = end - start

    if do_print:
        print('elapsed time for variation.run_initial():\t%.3f [s]' % dt)

    # this is the list of activity diaries per household
    t = trials[0]
    diaries = [ t.get_diary(u) for u in u_list]

    # store the results of the simulations in an object
    result = driver_result.Driver_Result(diaries=diaries, chad_param_list=chad_param_list)

    return result, u_list


def integrate_residual(result, df_obs, act_code, do_periodic, do_weekday, do_duration, N=int(1e4) + 1):

    weekend_list = [d[0].get_weekend_data() for d in result.diaries]
    weekday_list = [d[0].get_weekday_data() for d in result.diaries]

    chooser_weekday = {True: weekday_list, False: weekend_list}

    df_list = chooser_weekday[do_weekday]

    df_abm = evaluation.sample_activity_abm(df_list, act_code)

    # get the duration data
    x_dt, cdf_dt, inv_cdf_dt = evaluation.residual_analysis(pred=df_abm.dt.values, obs=df_obs.dt.values, N=N)

    # get the start time data
    x_start, cdf_start, inv_cdf_start = evaluation.residual_analysis(pred=df_abm.start.values, \
                                                                     obs=df_obs.start.values, N=N, \
                                                                     do_periodic=do_periodic)
    q = np.linspace(0, 1, N)

    if do_duration:
        df = inv_cdf_dt
    else:
        df = inv_cdf_start

    # integrate the residual [the expected value of the absolute value of the residual]
    I = integrate.simps(y=df.res_scale.abs(), x=q)

    return I

def sweep(x, chad_param_list, u_list):

    std = x

    for u in u_list:
        for p in u.people:
            p.bio.sleep_wd_dt_std = std
            p.bio.sleep_we_dt_std = std

    u       = u_list[0]
    t_0     = u.t_start
    result  = run_simulation(t_0=t_0, chad_param_list=chad_param_list, u_list=u_list, do_print=False)

    return result

# the function to minimize
# this assumes that u_list was already created, that is to say that run_initial was already run
def f(x):
    """

    :param numpy.ndarray x: the standard deviation a
    :return:
    """

    # values must be in minutes (fractional minutes are ok)

    std = x

    for u in u_list:
        for p in u.people:
            p.bio.sleep_wd_dt_std = std
            p.bio.sleep_we_dt_std = std

    result = run_simulation(t_0=t_0, chad_param_list=chad_param_list, u_list=u_list, num_cpu=num_cpu, pool=pool,
                            do_print=False)

    # integrate the residual curve
    I = integrate_residual(result=result, df_obs=df_obs, act_code=act, do_periodic=do_periodic, \
                           do_weekday=do_weekday, do_duration=do_duration)

    #print(I)
    return I

# ===========================================
# run
# ===========================================

if __name__ == '__main__':

    # get monte-carlo parameters from command line
    num_cpu, num_hhld = driver.get_cmd_line_params()

    # set the parameters for the simulation
    num_days = 1
    num_hours = 2
    num_min = 0

    # set the parameters for the simulation
    trial_code = trial.OMNI
    demographic = dmg.ADULT
    chad_activity_params = driver.TRIAL_2_CHAD_PARAMS[trial_code]

    # run the simulation using default parameters
    param_list = [params.Params(num_days=num_days, num_hours=num_hours, num_min=num_min) for _ in range(num_hhld)]

    #
    # create the conditions for each trial
    #
    trials = driver.initialize_trials(param_list, trial_code, chad_activity_params, demographic)

    # this is the original start time for the simulation
    t_0 = param_list[0].t_start

    chad_param_list = [t.sampling_params for t in trials]

    # run the initial simulations

    results = []

    #
    # do the initial run
    #
    print('doing the initial run...')
    if num_cpu > 1:
        pool = mp.Pool(processes=num_cpu)
    else:
        pool = None

    result, u_list = run_initial(trials, chad_param_list)

    # store the results
    results.append(result)

    # grab the observed data

    act = mg.KEY_SLEEP
    do_periodic = False
    do_weekday = True
    do_duration = True

    # get the observed data (df_obs)
    stats_dt, stats_start, df_obs = analysis.get_verification_info(demo=demographic, key_activity=act,
                                                                 sampling_params=chad_param_list, do_weekday=do_weekday)

    #
    # variation
    #


    print('doing a sweep of variation...')
    start = time.time()

    std_max = 90
    x = np.arange(std_max + 1)
    results = []

    if num_cpu == 1:
        for i, v in enumerate(x):
            print('i: %d' % i)
            results.append( sweep(v, chad_param_list, u_list) )
    else:
        d = [ (v, chad_param_list, u_list) for v in x]
        results = pool.map( sweep_parallel, d)

    end = time.time()
    print('elapsed time: %.2f\n' % (end - start))

    f = lambda r: integrate_residual(result=r, df_obs=df_obs, act_code=act, do_periodic=do_periodic, \
                                     do_weekday=do_weekday, do_duration=do_duration)

    y = [ f(result) for result in results]
    y = np.array(y)

    end = time.time()
    print('elapsed time: %.2f\n' % (end - start) )

    # poly fit
    z2 = np.polyfit(x, y, deg=2)
    z3 = np.polyfit(x, y, deg=3)

    fit2 = np.poly1d(z2)
    fit3 = np.poly1d(z3)

    plt.plot(x, y, label='data')
    plt.plot(x, fit2(x), label='deg 2')
    plt.plot(x, fit3(x), label='deg 3')
    plt.legend(loc='best')
    plt.show()

    #
    # plot some stuff
    #
    do_plot = False
    if do_plot:
        x = np.arange(start=0, stop=100, step=1)
        y = np.zeros( x.shape)
        for i, u in enumerate(x):
            uu = u * np.ones( (1, 1) )
            y[i] = f(uu)


        plt.plot(x, y )
        plt.show()

    #
    # minimize
    #

    # initial guess of variation [minutes]
    x0 = 22 * np.ones(1)


    print('\n--------------------------')
    print('starting the minimization...')
    print('--------------------------')

    xtol = 1e0
    ftol = 1e-3
    do_display = True

    do_optimize = False
    if do_optimize:
        method = 'nelder-mead'
        chooser_opt = {'powell':{'xtol':xtol, 'disp': do_display, 'ftol': ftol},
                       'nelder-mead': {'xtol': xtol, 'disp': do_display, 'ftol': ftol},
                       'bfgs': {'disp': do_display}, }

        options = chooser_opt[method]
        #res = optimize.minimize(f, x0=x0, method=method, options=options)

        minimizer_kwargs = {'method': 'powell'}
        res = optimize.basinhopping(f, x0=x0, minimizer_kwargs=minimizer_kwargs, niter=1, disp=True, stepsize=0.5, interval=4)

        print('print the results')
        print(res)