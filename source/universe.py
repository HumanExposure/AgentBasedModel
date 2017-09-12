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
# August 14, 2017

"""
This module contains code that is responsible for running the simulation. This file contains \
:class:`universe.Universe`. The Universe contains all agents and objects. The Universe is responsible for \
running the simulation itself.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ----------------------------------------------------------
# import
# ----------------------------------------------------------

# general mathematical capabilities
import numpy as np

# agent-based module modules
import activity, home, need, scheduler, state, temporal

# ===============================================
# class
# ===============================================

class Universe(object):

    """
    The Universe is the governing engine of the simulation.

    :param int num_steps: the number of time steps in the simulation
    :param int dt:  the step size in the simulation [minutes]
    :param int t_start: the start time for the simulation [minutes, universal time]
    :param int num_people: the number of people in the household

    :var temporal.Temporal clock: does the timekeeping in the simulation
    :var home.Home "home": the home the Persons live in
    :var list people: a list of all Person objects created in the Universe object
    :var int t_start: the start time for the simulation [minutes, universal time]
    :var int t_end: the last time for the simulation [minutes, universal time]
    :var scheduler.Scheduler schedule: the schedule governing each agent's needs
    """

    #
    # Constructor
    # 
    #
    def __init__(self, num_steps, dt, t_start, num_people):

        # create a clock.
        self.clock          = temporal.Temporal()
        self.clock.dt       = dt
        self.clock.t_univ   = t_start
        self.clock.set_time()

        # store the initial time [minutes] in universal time
        self.t_start = t_start

        # the final time of the simulation in universal time
        self.t_end = self.t_start + num_steps * dt

        # create a home
        self.home = home.Home(self.clock)

        # list of persons
        self.people = []

        # the schedule
        self.schedule = scheduler.Scheduler(clock=self.clock, num_people=num_people)

        return


    # ------------------------------------------------------
    # functions
    # ------------------------------------------------------

    def address_needs(self, do_interruption=False):

        """
        This function checks the needs of the agents

        The function uses a recursion loop to choose activities.

        The Recursion:

        #. Gather all of the advertisements (object-person pairings)
        #. Assigns 1 activity to the Person with the highest score.
        #. That Person starts the activity, thereby updating the state of available activities in the home.
        #. The recursion starts again, where the Home advertises to all remaining Person(s).

        :Note: If no activity will be done this time step to a Person, a Person is set to \
            the temporary status :const:`state.IDLE_TEMP`, so that the Home knows not to advertise to that Person.

        :param bool do_interruption: this flag indicates whether or not advertisements should be made \
            for activities that will interrupt the current activity (if True). If False, the advertisements \
            are made for non-interrupting activities.

        :return: None
        """

        # this is the list of adds per Person AND the Person object
        # this will be Empty if NO ONE is able to do something.
        # Recall, a Person needs to be IDLE
        #
        ads = self.advertise(do_interruption = do_interruption)

        # select the activity for each person by recursion
        # after each recursion, a Person does an activity; thereby,
        # updating the rest of potential activities in the Home
        # BEGIN the recursion

        # flatten the ads to figure out the TOTAL amount of advertisements in the Home
        total_ads = lambda z: len( [item for sublist in z for item in sublist] )

        # total amount of ads (not including empty lists)
        N = total_ads(ads)

        counter = 0

        do_stop = False

        while( N > 0) and (not do_stop):

            # given all of the possible activities, select the activity for the
            # person with the highest score
            ad = self.select_activity(ads)

            (score, do_asset, do_activity, p) = ( ad['score'], ad['asset'], ad['activity'], ad['person'] )

            # if the activity is useful (score > 0), do the activity
            if ( score > 0.0 ):

                # if necessary, interrupt the current activity before starting
                # the newly selected activity

                # make sure that the interruption activity can be DONE, depending on the availability of
                # of the required asset!
                if ( do_activity.id == p.interruption.activity_start ):

                    p.state.halt_activity(p)

                else:
                    p.interruption.reset()

                # Store required activity data
                p.state.asset       = do_asset
                p.state.activity    = do_activity
                p.state.arg_start   = [p]

                # the interruption should be the need with the highest score
                # start the activity
                p.state.start_activity()

            else:
                # do not do an activity
                # BUT, remember to not re-look for advertisements (state.IDLE_TEMP)
                p.state.status = state.IDLE_TEMP

            # update the new choices, given the fact that a  is already chosen
            ads = self.advertise(do_interruption = do_interruption)

            # update the total amount of ads
            N = total_ads(ads)

            if counter >= 1:
                uu = 1

            counter = counter + 1

        # OUTSIDE of recursion:
        # reset the state.IDLE_TEMP to state.IDLE
        for p in self.people:
            if (p.state.status == state.IDLE_TEMP):
                p.state.status = state.IDLE

        return

    def advertise(self, do_interruption = False):

        """
        This function obtains a list of all of the possible activities each person could potentially start in \
        this time step.


        :param bool do_interruption: this flag indicates whether to make advertisements due to an \
        interrupting activity (if True) or not (if False).

        :return ads: ads is a list of dictionaries for advertisements:

                    Dictionary  (score, asset, activity, person) containing the various data for
                    each advertisement: (score, asset, activity, person) coupling
        :rtype: list
        """

        # handle the interruptions
        do_test = True

        # optimized way to get all of the advertisements
        # there is a list of ads for each person

        if (do_interruption):

            # advertise if the Interruption satiation is under the threshold value **and** the agent has not already \
            # been advertised to, indicated by p.state.status != state.IDLE_TEMP
            # state.IDLE_TEMP indicates that there was no activity for the agent to undergo at the current moment
            ads = [ self.home.advertise(p, do_interruption = do_interruption) for p in self.people
                    if p.interruption.under_threshold(p.interruption.magnitude) and (p.state.status != state.IDLE_TEMP) ]

            # the total amount of ads advertised across all people
            N = lambda z: len( [item for sublist in z for item in sublist] )

            if do_test:
                x = np.array( [ item['score'] <= 0 for sublist in ads for item in sublist ] )
                if x.all():
                    sam                             = self.people[0]
                    #sam.interruption.magnitude      = 1.0
                    sam.interruption.activity_start = None
                    sam.interruption.activity_stop  = None
                    ads = []
            else:
                # if there are no advertisements from assets that address interruptions,
                # set the interruption state to 0
                # this can occur if there are no assets that address the respective interruption
                if ( N(ads) == 0 ):
                    # original: worked in python 2.7
                    # p.interruption.reset()

                    for p in self.people:
                        p.interruption.reset_minor()

        else:
            # advertise if the agent is idle
            ads = [ self.home.advertise(p, do_interruption = do_interruption) for p in self.people
                    if (p.state.status == state.IDLE) ]

        return ads

    def check_expired_activities(self):

        """
        This function checks for expired activities. If found, end the activities.

        :return: None
        """

        # naturally expiring activity routine
        for p in self.people:

            # check to see if an activity has ended
            # An activity ends if a Person is idle AND the current time is at least the
            # value of the suggested end time of the activity
            if (p.state.status != state.IDLE) and (self.clock.t_univ >= p.state.t_end):

                # an action has expired
                # this allows for the initialization of sleep to do nothing
                # when the activity ends
                p.state.end_activity()

        return

    def decay_needs(self, dt=None):

        """
        This function decays the needs according to the default behavior. That is, assume the needs are not \
        addressed earlier.

        :param int dt: the number of minutes to decay the needs by. The default behavior is to use the scheduler's \
        time. If a number is specified, then it should be the number of minutes until the end of the simulation.

        :return: None
        """

        #
        # decay the needs for each person
        #

        if dt is None:
            dt = self.schedule.dt

        for p in self.people:

            # decay the major needs first
            p.rest.decay_new(p.state.status, dt)
            p.hunger.decay_new(dt)
            p.income.decay(p)

            # decay the minor needs last( because they may depend on the major needs)
            p.travel.decay(p)

            # MUST decay interruption need LAST
            #p.interruption.decay(p)

            # for debugging
            uu = 1
        #
        # update the home
        #

        return

    def initial_step(self):

        """
        This function is supposed to run the first time step of the run() loop

        #. store the current time
        #. address the needs assuming interruption
        #. address the needs assuming NO interruption
        #. update the history
        #. update the clock
        #. decay the needs

        .. note::
            this function is **NOT** called on in the current implementation yet

        :return: None
        """

        # store the current time
        self.clock.hist_time[0] = self.clock.t_univ

        # address needs due to interruptions
        #self.address_needs(do_interruption=True)

        # address the needs NOT due to interruptions
        self.address_needs(do_interruption=False)

        self.address_needs(do_interruption=True)

        # record the state/ activity history
        self.update_history(0)

        # update the clock for the next time step
        self.clock.update_time()

        # decay needs according to the default behavior
        self.decay_needs()

        #self.clcok.initial_step = False

        return

    def initialize_needs(self):

        """
        This function initializes the need state of each Person at the beginning of simulation based on \
        the current time.

        The needs are initialized in this order (the order matters)

        #. Rest
        #. Hunger
        #. Income
        #. Travel
        #. Interruption


        :return: None
        """

        # for testing work
        do_test = True

        YEAR_2_MIN  = temporal.YEAR_2_MIN

        #
        # initialize the needs of each person
        #
        for p in self.people:

            # initialize the major needs (the order matters)
            p.rest.initialize(p)
            p.hunger.initialize(p)
            p.income.initialize(p)

            # initialize the minor needs (may/ may not depend on the major needs)
            p.travel.initialize(p)

            # initialize interruption...
            p.interruption.initialize(p)

            if do_test:
                keys    = self.home.assets.keys()
                dt      = 100 * YEAR_2_MIN

                if 'workplace' not in keys:
                    p.schedule.update(p.id, need.INCOME, dt)
                    p.schedule.update(p.id, need.INTERRUPTION, dt)

                if 'transport' not in keys:
                    p.schedule.update(p.id, need.TRAVEL, dt)

                if 'bed' not in keys:
                    p.schedule.update(p.id, need.REST, dt)

                if ('food' not in keys) and ('cafeteria' not in keys):
                    p.schedule.update(p.id, need.HUNGER, dt)

                if 'cafeteria' not in keys:
                    p.schedule.update(p.id, need.INTERRUPTION, dt)

        return


    def print_activity_info(self, p):

        """
        This function stores activity info used for testing / developing/ debugging as a string.

        :param person.Person p: the person of interest

        :return: None
        """

        msg = ''
        msg = msg + '\nPerson %d:\tTime has expired!\n' % p.id
        msg = msg + 'Day: ' + temporal.DAY_2_STR[self.clock.day_of_week]
        msg = msg + '\t\ttime:\t' + self.clock.print_time_of_day_to_military() + '\n'
        msg = msg + p.state.activity.toString()

        print(msg)

        return

    def reset(self, t_univ):

        """
        This code resets the simulation by initializing the agents, home, and clock to the beginning status \
        of the simulation.

        This code does the following:

        #. reset the clock
        #. reset the home
        #. reset each person
        #. initialize each person
        #. initialize the home

        :param params.Params p: the parameters
        :param int t_univ: the time of the beginning of the simulation [seconds]
        :return:
        """

        #
        # reset
        #

        # reset the time
        self.clock.reset(t_univ)

        # parameters

        # reset the home and assets
        self.home.reset()

        # reset the people
        for x in self.people:
            x.reset()

        #
        # initialize
        #

        for p in self.people:
            p.state.is_init = True

        # initialize the needs
        self.initialize_needs()

        # initialize the home assets
        self.home.initialize(self.people)

        # set the home economics
        self.home.set_revenue(self.people)
        self.home.set_population(self.people)

        return

    def run(self):

        """
        This function is responsible for running the simulation. Instead of running the simulation minute-by-minute, \
        in an effort to reduce run-time, the simulation skips time steps and addresses the agent at times that \
        actions should occur. These times are dictated by the scheduler.

        The function proceeds as following:

        While the current time is less than the final time

        #. check for expired activities for all agents. If activities should have expired, tell the agent to end them
        #. start new activities by addressing the needs for all agents (assuming no interruption)
        #. decay the satiation for Interruption for all agents
        #. start new activities by addressing the needs for all agents (assuming interruptions only)
        #. update the history of the status of each agent
        #. find the next time to jump to in the simulation according to the scheduler
        #. update the clock to the new time
        #. decay the needs for all agents
        #. Repeat

        For the last time step

        #. update the clock
        #. decay the needs for each agent
        #. update the history of the status of each agent

        .. note::
            I must change N_MAX to N_MAX = DAY_2_MIN * 365

        :return:
        """

        # set the next scheduled time to stop the clock as the current time as the
        t_next = self.clock.t_univ

        # store a history of the time
        self.clock.hist_time[self.clock.step] = self.clock.t_univ

        # the iterating variables: the current iteration and the maximum iterations in the loop, respectively
        i, N_MAX = 0, 1e4 # 1e6

        # print test function
        do_test = False

        # while the current time is before the final time AND the iteration counter is under the maximum iteration
        # allowed
        while (t_next <= self.t_end) and (i < N_MAX):

            # if the current time is under the next scheduled time (in the scheduler) to stop the clock
            if self.clock.t_univ >= t_next:

                # check for expired activities
                # if they are found, end the activity
                # set the Person to state: IDLE
                self.check_expired_activities()

                # address needs due to interruptions
                #self.address_needs(do_interruption=True)

                # address the needs NOT due to interruptions
                self.address_needs(do_interruption=False)

                # decay the interruption
                for p in self.people:
                    p.interruption.decay(p)

                self.address_needs(do_interruption=True)

                if do_test:
                    self.test_func()

                # update the history
                self.update_history_new()

                # get the next time
                # need to add something about an interrupting event
                # in the case that work and lunch start simultaneously
                t_next = self.schedule.get_next_event_time()

                # update the clock and decay the needs for the next time
                if (t_next <= self.t_end):

                    # update the clock for the next time step
                    self.update_clock(t_next)

                    # decay
                    #dt = self.clock.t_univ - self.schedule.t_old + 1
                    #self.decay_needs(dt)
                    self.decay_needs()

                    uu = 1

            # after the first time step, there are no initializing procedures
            self.clock.initial_step = False

            # update loop iteration counter
            i = i + 1

        # THE FINAL STEP this will occur because t_next will be > clock.t_end
        if (t_next > self.t_end):

            # update the clock for the next time step
            self.update_clock(self.t_end)

            dt = self.t_end - self.schedule.t_old
            self.decay_needs(dt)

            # update the history
            self.update_history_new()

        return

    #
    # this runs the simulation
    #

    # Each time step the simulation does the following for each person
    # decay the needs
    # check for expired activities
    # set an alarm, for the respective people
    # address needs by assigning activities
    # update the history of events
    # advance the clock

    # Given a list of activity advertisements,
    # this function selects the Person with the largest activity score and
    # outputs the score, asset, activity, and person.
    #
    # input:
    #     ads:          a list of advertisements: (score, asset, activity, person)
    #                   tuples for a each person
    # output:
    #    chosen:        dictionary. The chosen advertisement
    #                   keys: ("score", "asset", "activity", "person")
    #
    def select_activity(self, ads):

        """
        Given a list of activity advertisements, this function selects the Person
        with the largest activity score and outputs the score, asset, activity, and person.

        :param list ads: a list of advertisements for this time step

        :return chosen: the selected activity advertisement (score, asset, activity, person)
        :rtype: dict
        """

        do_print = False

        # to check for an empty list
        # nn = len( [item for sublist in ads for item in sublist] )

        # go through the ads / person
        # this function goes through the list and finds the score
        g = lambda x: x['score']

        # for each person, sort the add in terms of decreasing score
        ads = [ sorted(a, key=g, reverse=True) for a in ads]

        # for each person with (non-empty) advertisements, get the highest score
        score = np.array( [ a[0]['score'] for a in ads if a] ).astype(float)

        #
        # check for activity conflicts!!
        #

        # see if the max score is unique
        max_score = score[score == max(score)]

        # a flag indicating if the maximum socre is unique
        is_unique = ( len(max_score) == 1)

        # an array of indices of Person(s) with the max score
        p_idx = np.where( score == max(score) )[0]

        # if NO Person(s) have a max-score conflict, the Person with the
        # highest score wins
        if (is_unique):
            chosen = ads[p_idx[0]][0] # recall, the ads per Person are sorted
        else:
            # 2 or more people have a max-score conflict, choose 1 randomly (uniform)
            # by randomly assigning numbers, the winner has the highest value
            rando = np.random.rand( len(p_idx) )
            winner_idx = p_idx[rando == max(rando)][0]

            chosen = ads[winner_idx][0] # recall, the ads per Person are sorted

        return chosen

    # this sets the alarm for those Person(s) who use an alarm
    def set_alarm(self):

        """
        This function sets the alarm for those Person(s) who use an alarm

        .. note::
            This function is **NOT** used. There is currently no alarm capability.

        :return: None
        """

        # set the alarm at the turn of the day
        for p in self.people:
            if (p.socio.uses_alarm) and (self.clock.day_of_week in p.socio.job.work_days):
                p.socio.is_alarm_set = True
            else:
                p.socio.is_alarm_set = False

        return

    def test_func(self):

        """
        .. note::
            This function is just for debugging.

        :return:
        """

        DAY_2_MIN = temporal.DAY_2_MIN
        p = self.people[0]

        msg = ''
        # msg = '---------------------------------\n'

        f = temporal.print_military_time
        # msg = msg + '%s\t\t %d\n' % (f(self.clock.time_of_day), self.clock.time_of_day)


        msg = msg + state.INT_2_STR[p.state.status] + '\n'

        for k, v in p.needs.items():
            msg = msg + ('%s: %.2f\n' % (need.INT_2_STR[k], v.magnitude))

        y = [f(x % DAY_2_MIN) for x in p.schedule.A[0]]

        msg = msg + '%s: ' % y
        print(msg)
        print(p.schedule.A[0])

        return

    def toString(self):

        """
        Represent the Universe object as a string.

        This function outputs the representation of:

        #. the clock
        #. the home
        #. agent person residing in the home

        :return msg: a representation of the Universe object
        :rtype: str
        """
        msg = ''
        msg = msg + '-------Clock ------\n'
        msg = msg + self.clock.toString()
        msg = msg + '--------- Home ------\n'
        msg = msg + self.home.toString()

        msg = msg + '---------- People ------\n'
        for p in self.people:
            msg = msg + p.toString() + '\n'

        return msg

    def update_clock(self, t):

        """
        This function updates the clock by

        #. setting the clock to the given time
        #. updating the step of the simulation
        #. storing the history of the time nodes used in the simulation

        :param int t: the time the clock should be set to
        :return:
        """

        self.clock.t_univ = t
        self.clock.set_time()
        self.clock.step = self.clock.step + 1

        # store the temporal history
        self.clock.hist_time[self.clock.step] = self.clock.t_univ

        return

    def update_history(self, step):

        """
        Update the histories for each Person by storing the following:

        #. the current state's status
        #. the current activity
        #. the current satiation value for each needs
        #. the current location

        :param int step: the time step

        :return: None
        """

        # update history of Persons
        for p in self.people:

            # store state
            p.hist_state[step] = p.state.status

            # store activity
            if (p.state.status != state.IDLE):
                p.hist_activity[step] = p.state.activity.id
            else:
                p.hist_activity[step] = activity.NO_ACTIVITY

            # store needs
            for k in p.needs.keys():
                p.needs[k].history[step] = p.needs[k].magnitude

            # store location
            p.hist_local[step] = p.location.local

        return

    def update_history_new(self):

        """
        Update the histories of each person.

        :return: None
        """

        # update history of Persons
        for p in self.people:
            p.update_history()

        return

