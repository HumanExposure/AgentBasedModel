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
This file contains information to run the Agent-Based Model of Human Activity Patterns (ABMHAP) in \
in different simulation scenarios in which the agent has a user-defined parametrization.

The following classes are in this module

#. :class:`scenario.Scenario`
#. :class:`scenario.Solo`
#. :class:`scenario.Duo`

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===========================================
# import
# ===========================================
import sys, time
sys.path.append('..\\source')

# general math functionality
import numpy as np

# agent-based model modules
import activity, diary, location, params, singleton, state, universe

# ===========================================
# constants
# ===========================================

# codes for different scenarios / simulations
NO_SIMULATION   = -1

# a scenario with 1 person in the simulation
SOLO            = 1

# a scenario with 2 people in the simulation
DUO             = 10

# ===============================================
# class Scenario
# ===============================================
class Scenario(object):

    """
    This class governs what a simulation scenario consists of.

    :param params.Params hhld_params: the parameters for the household that contain relevant information \
    for the simulation

    :var int id: the scenario identifier number
    :var universe.Universe u: the universe object for the simulation
    :var params.Params 'params': the parameters needed that control the simulation
    """

    def __init__(self, hhld_params):

        # the scenario identifier
        self.id     = NO_SIMULATION

        # kew word arguments
        # probably will need to access various features of kwarg in the future when the model
        # becomes more complex
        self.params = hhld_params

        # create the universe object
        self.u      = universe.Universe(self.params.num_steps, self.params.dt, t_start=self.params.t_start, \
                                        num_people=self.params.num_people, \
                                        do_minute_by_minute=self.params.do_minute_by_minute)

        # set the clock to the desired time
        self.u.clock.t_univ = self.params.t_start
        self.u.clock.set_time()

        return

    def activity_diary(self):

        """
        This function returns the activity diary for each person

        Each person will attain the following tuple

        #. grouping of the index for each activity
        #. the day, (start-time, end-time), activity code, and location for each activity-event, in a numeric format
        #. the same as above in a string format

        :return:
        """

        # the time of each step in the simulation [universal time, minutes]
        t = self.u.hist_time

        # the (index, numerical diary, string diary) for each
        x = [ diary.Diary(t, p.hist_activity, p.hist_local) for p in self.u.people]

        return x

    def default_location(self):

        """
        Sets the default location for all Person's to be be at the home. This location may \
        be overridden later in the initialization of persons.

        :return: None
        """

        for p in self.u.people:
            # set the location to be at home
            p.location.local = location.HOME

        return None

    def initialize(self):

        """
        This function initializes the scenario before the simulation scenario is run

        More specifically, the function does the following:

        #. Sets the state and location for each person
        #. Sets the home
        #. Initialize the initial need-association states for the Person(s) and Home

        :return: None
        """

        # set the default location of Persons(to be overridden)
        self.default_location()

        # set the state and location
        self.set_state()

        # set the home
        self.set_home()

        # initialize the needs
        self.u.initialize_needs()

        # initialize the home assets
        self.u.home.initialize(self.u.people)

        return

    def run(self):

        """
        This function initializes the scenario and then runs the ABMHAP simulation.

        :return: None
        """

        # initialize the Agents in the scenario
        self.initialize()

        # run the simulation
        self.u.run()

        return

    def set_home(self):

        """
        This function sets aspects of the home in order to run the simulation scenario.

        More specifically, the function does the following

        #. set the home revenue
        #. set the home population

        :return: None
        """

        # set the home revenue
        self.u.home.set_revenue(self.u.people)

        # set the home population
        self.u.home.set_population(self.u.people)

        return

    def set_state(self):

        """
        This function initializes the scenario in order to run the simulation. More \
        specifically, this function does the following:

        #. For each Person, the following is set:

            #. identification number
            #. the state

        :return: None
        """

        #
        # set the state and location of each Person
        #

        # a personal identification number
        pin = 0
        for p in self.u.people:

            # put the people in the initialization phase for
            # the first step of the simulation
            p.state.is_init = True

            # set the Person to be idle
            p.state.stats   = state.IDLE

            # Set the Person's state
            p.state.t_start = self.u.clock.t_univ
            p.state.t_end   = p.state.t_start

            # set the Person ID
            p.id    = pin

            # update the ID number for the next Person
            pin     += 1

        return

# ===============================================
# class Solo
# ===============================================

class Solo(Scenario):

    """
    This class parametrizes / runs a simulation scenario for the Singleton (:class:`singleton.Singleton`) person.

    :param params.Params hhld_params: the parameters for the household that contain relevant information \
    for the simulation

    """

    def __init__(self, hhld_params):

        # Scenario constructor
        Scenario.__init__(self, hhld_params)

        # scenario identifier
        self.id = SOLO

        # create a single person
        sam = singleton.Singleton(self.u.home, self.u.clock, self.u.schedule)
        sam.set(self.params, idx=0)

        # add Single Sam to the universe
        self.u.people.append(sam)

        return

# ===============================================
# class Duo
# ===============================================

class Duo(Scenario):

    """
    This class parametrizes / runs a simulation scenario for the cases where two Singleton \
    (:class:`singleton.Singleton`) persons live in the same residence.

    .. note::
        This scenario is used in order to check for activity conflicts among 2 agents living in \
        the same household. Currently it is used primarily as a debugging tool.

    :param params.Params hhld_params: the parameters for the household that contain relevant information \
    for the simulation

    """

    def __init__(self, hhld_params):

        Scenario.__init__(self, hhld_params)

        # scenario identifier
        self.id = DUO

        # create Single Sam(s) and add them to the universe
        for i in np.arange(self.params.num_people):
            sam = singleton.Singleton(self.u.home, self.u.clock, self.u.num_sample_points)
            sam.set(self.params, idx=i)
            self.u.people.append(sam)

        # testing: changing the max occupancy of the bed
        # this should cause an activity conflict when it comes to sleeping
        self.u.home.assets['bed'].max_users = 1

        return