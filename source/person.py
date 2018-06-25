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
This module has code that governs information about the agent.

This module contains information about class :class:`person.Person`.


.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# general math capability
import numpy as np

# agent-based model modules
import my_globals as mg
import location as loc
import activity, diary, bio, home, hunger, income, interruption, need, rest, social, state, temporal, travel

# ===============================================
# class Person
# ===============================================

class Person (object):

    """
    This class contains all of the information relevant for a Person.

    A person is parametrized by the following

    * a place of residence
    * a biology
    * social behavior
    * a location
    * a history of activities and states

    * Needs

        #. Hunger
        #. Rest
        #. Income
        #. Travel
        #. Interruption

    :param home.Home house: the Home object the person resides in. (will need to remove this)
    :param temporal.Temporal clock: the time
    :param scheduler.Scheduler schedule: the schedule
    
    :var bio.Bio 'bio': the biological characteristics
    :var temporal.Temporal clock: keeps track of the current time. It is linked to the Universe clock
    :var numpy.ndarray hist_state: the state history [int] for each time step
    :var numpy.ndarray hist_activity: the activity history [int] for each time step
    :var home.Home 'home': this contains the place where the person resides
    :var int id: unique person identifier
    :var income.Income 'income': the need that concerns itself with working/school
    :var interruption.Interruption 'interruption': the need that concerns itself with interrupting an ongoing activity
    :var location.Location 'location': the location data of a person
    :var dict needs: a dictionary of all of the  needs
    :var rest.Rest 'rest': the need that concerns itself with sleeping
    :var social.Social socio: the social characteristics of a Person
    :var state.State 'state': information about a Person's state
    :var travel.Travel 'travel': the need that concerns itself with moving from one area to another
    
    :var numpy.ndarray hist_state: the state of the person at each time step
    :var numpy.ndarray hist_activity: the activity code of the person at each time step
    :var numpy.ndarray hist_local: the location code of the person at each time step
    :var numpy.ndarray H: the satiation level for each need at each time step
    :var numpy.ndarray need_vector: the satiation level for each need at a given time step

    """

    def __init__(self, house, clock, schedule):

        # this allows the Person to be aware of the time
        self.clock = clock

        # a unique identification number for the Person
        self.id = -1

        # the home
        self.home = house

        # the biology characteristics
        self.bio = bio.Bio()

        # the Age of the person
        self.bio.age = 30

        # The gender of a person
        self.bio.gender = bio.FEMALE

        # set the social characteristics
        self.socio = social.Social(self.bio.age)

        # set the location of the Person to a copy of the Home's location
        self.location = loc.Location( house.location.geo, house.location.local )

        # the number of steps
        num_sample_points = len(self.clock.hist_time)

        # create major need-associations (income, rest, hunger)
        self.income = income.Income(clock, num_sample_points)
        self.rest   = rest.Rest(clock, num_sample_points)
        self.hunger = hunger.Hunger(clock, num_sample_points)
        
        # create minor need-associations (travel, interruption)
        self.travel         = travel.Travel(clock, num_sample_points)
        self.interruption   = interruption.Interruption(clock, num_sample_points)
                
        # a dictionary (key, value)-pairs of need-associations
        self.needs = {need.INCOME: self.income, need.REST: self.rest,
                need.HUNGER: self.hunger, need.TRAVEL: self.travel,
                need.INTERRUPTION: self.interruption,}

        # the state of a person
        self.state = state.State(state.IDLE)

        # history of the Person's state, activities, and location
        self.hist_state     = state.IDLE * np.ones( (num_sample_points,1) )
        self.hist_activity  = activity.NO_ACTIVITY * np.ones( self.hist_state.shape)
        self.hist_local     = loc.HOME * np.ones( self.hist_state.shape )

        # history of magnitude of each need. There must to be one per person
        self.H              = -1 * np.ones((num_sample_points, need.N))
        self.need_vector    = -1 * np.ones( (need.N, 1) )
        self.schedule       = schedule

        return

    def get_diary(self):

        """
        This function output the result of the simulation in terms of an activity diary.

        :return: the activity diary describing the behavior of the agent
        :rtype: diary.Diary
        """

        # the indices of simulation data
        idx = self.clock.hist_time != -1
        idx = idx.flatten()

        # the time
        t = self.clock.hist_time[idx].flatten()

        # the array of the activities
        hist_act = self.hist_activity[idx]

        # the array of the locations
        hist_loc = self.hist_local[idx]

        # make the time continuous
        t_all = mg.fill_out_time(t)

        # fill out the time in between events to get data that corresponds to contiguous time
        act_all = mg.fill_out_data(t, hist_act)

        # fill out the location data in between events that corresponds to contiguous time
        loc_all = mg.fill_out_data(t, hist_loc)

        # create the activity diary
        d = diary.Diary(t=t_all, act=act_all, local=loc_all)

        return d

    def print_basic_info(self):

        """
        This function expresses basic information about the Person object as a string by \
        printing the following:
        
        * person identifier
        * home identifier
        * age
        * gender

        :return: basic information about the Person
        :rtype: str
        """

        msg = ''

        # the Person ID
        msg = msg + 'ID: %d' % self.id + '\n'

        # the Home ID
        msg = msg + 'Home ID: %d' % self.home.id + '\n'

        # the Age of a person [years]
        msg = msg + 'Age: %d' % self.bio.age + '\n'

        # the gender of a person
        msg = msg + 'Gender: ' + self.bio.print_gender() + '\n'

        return msg

    def reset(self):

        """
        This function rests the person at the beginning of a simulation by doing the following:
        
        #. reset the history
        #. reset the state
        #. reset the location
        #. reset the needs
        
        .. note::
            the clock needs to be set to the beginning of simulation
        
        :return: None 
        """

        # reset the history
        self.reset_history()

        # reset the state
        self.state.reset(self.clock.t_univ)

        # reset the location
        self.location.reset()

        # reset the needs
        self.reset_needs()

        return

    def reset_history(self):

        """
        This function resets the variables:
        
        #. history of the state
        #. history of the activity
        #. history of the location
        
        :return: None 
        """

        self.hist_state[:]     = state.IDLE
        self.hist_activity[:]  = activity.NO_ACTIVITY
        self.hist_local[:]     = loc.HOME

        return

    def reset_needs(self):

        """
        This function resets the needs.
        
        :return: None 
        """

        for x in self.needs.values():
            x.reset()

        return

    def toString(self):

        """
        This function represents the Person object as a string.

        :return: information about the Person
        :rtype: str
        """

        msg = ''

        # write basic information as a string
        msg = msg + self.print_basic_info()

        # express the location as a string
        msg = msg + '\t\tLocation\n' + self.location.toString()

        # the social state
        msg = msg + '\t\tSocial\n' + self.socio.toString()

        # write the state as a string
        msg = msg + '\t\tState\n' + self.state.toString()

        # write the need-associations as a string
        msg = msg + 'need mangitudes\n\n'
        for n in self.needs.values():
            msg = msg + n.toString()

        return msg

    def update_history(self):

        """
        This function updates the history of the following values with their current values:
        
        * state history
        * location history
        * activity history
        * need (satiation) history
        
        :return: 
        """

        i = self.clock.step

        # store the history of the state
        self.hist_state[i] = self.state.status

        # store the history of the location
        self.hist_local[i] = self.location.local

        # store the history of the activity
        self.update_history_activity()

        # store the history of the needs
        self.update_history_needs()

        return

    def update_history_activity(self):

        """
        This function updates the activity history with the current values.
        
        :return: None
        """

        # store the history of the activity
        if (self.state.status == state.IDLE):
            act = activity.NO_ACTIVITY
        else:
            act = self.state.activity.id

        self.hist_activity[self.clock.step] = act

        return

    def update_history_needs(self):

        """
        This function updates the needs (satiation) history with the current values.
         
        :return: None
        """

        # loop through all of the needs and store the satiation
        for k in self.needs.keys():
            self.H[self.clock.step, k] = self.needs[k].magnitude

        return
