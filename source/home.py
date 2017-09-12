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
This module governs the control of assets used in the simulation. Mainly, the home contains all of \
the assets used in the simulation for the current version of the code.

This module contains the following class: :class:`home.Home`

.. moduleauthor:: Dr. Namdi Brandon.
"""

# ----------------------------------------------------------
# imports
# ----------------------------------------------------------

# agent-based model modules
import location as loc
import bed, food, state, transport, workplace

# ----------------------------------------------------------
# Constants
# ----------------------------------------------------------

# home categories
# these are not used in the current version of ABMHAP
APARTMENT   = 1
HOUSE       = 2
TRAILER     = 3

# home properties
# these are not used in the current version of ABMHAP
POOL     = 0
OUTDOORS = 1
PETS     = 2

# this takes an INTEGER representation of a home category and represents it
# as a STRING
INT_2_STR_CAT = {
    APARTMENT: 'Apartment',
    HOUSE: 'House',
    TRAILER: 'Trailer',
}

# this takes an STRING representation of a home category and represents it
# as an INTEGER
# this is not used in the current version of ABMHAP
STR_2_INT_CAT = { v: k for k, v in INT_2_STR_CAT.items() }

# this takes an INTEGER representation of a home properties and represents it
# as a STRING
# this is not used in the current version of ABMHAP
INT_2_STR_PROP = {
    POOL: 'Pool',
    OUTDOORS: 'Outdoors',
    PETS: 'Pets',
    }

# this takes an STRING representation of a home properties and represents it
# as an INTEGER
# this is not used in the current version of ABMHAP
STR_2_INT_PROP = { v: k for k, v in INT_2_STR_PROP.items() }

# the number of properties
# these are not used in the current version of ABMHAP
N_PROPERTIES = len(INT_2_STR_PROP) 
N_CATEGORIES = len(INT_2_STR_CAT)

class Home(object):

    """
    Contains all of the physical characteristics of a home/ residence. Currently, the home \
    contains all of the assets within the simulation.

    :param temporal.Temporal clock: the time

    :ivar dict assets: contains a list of all of the assets available in the home.
    :ivar int category: the type of home
    :ivar temporal.Temporal clock: the time
    :ivar int id: a unique home identification number
    :ivar location.Location location: the location of the home
    :ivar int population: the number of people who reside in a home
    :ivar float revenue: the household revenue
    """

    #
    # Constructor
    #

    def __init__(self, clock):

        self.id = -1
        self.category = APARTMENT

        self.population = 0
        self.clock = clock
        self.location = loc.Location( loc.NORTH, loc.HOME)
        
        # list of assets all Homes have
        # recall need to set the location of the work asset
        wp1 = workplace.Workplace()
        
        # allows sleeping
        bed1 = bed.Bed()
        
        # allows commuting
        the_transport = transport.Transport()
        the_transport.max_users = 1
           
        # food1 allows eating at home
        food1 = food.Food()
        
        # cafeteria allows eating at work
        cafeteria = food.Food()
        cafeteria.location.local = loc.OFF_SITE
        
        # store all of the assets
        self.assets = {
            'workplace': wp1,
            'bed': bed1,
            'transport': the_transport,
            'food': food1,
            'cafeteria': cafeteria
        }

        # the revenue of the house
        self.revenue = 0.0

        return
    
    #-----------------------------------------------------
    # functions
    #-----------------------------------------------------

    def advertise(self, p, do_interruption=False, locale=None):

        """
        This function handles all of the Activities' advertisements to a Person. This occurs by looping \
        through each asset in the home and collecting a list of advertisements for each activity in each asset.

        #. loop through each asset
        #. if the asset is busy *and* is in the same location of the person
            * for each activity in the given asset
                #. advertise for interrupting activities
                #. advertise for non interrupting activities
                #. collect the advertisements
                
        :param person.Person p: a person to whom the assets are advertising
        :param bool do_interruption: a flag that indicates whether or not we should advertise for interruptions

        :param int locale: a local location identifier

        :return: the advertisements (score, asset, activity, person) containing the various data for \
                        each advertisement: ("score", "asset", "activity", "person") coupling
        :rtype: dict        
        """

        ads = [] #(score, Asset, Activity)

        # find the free Assets
        for a in self.assets.values():

            # can only use free assets
            # and when assets and people are in the same location
            if ( (a.status != state.BUSY) and (a.location.local == p.location.local) ):

                score = None

                # calculate the score for each activity for the Asset
                for act in a.activities.values():

                    if (do_interruption and act.id == p.interruption.activity_start):
                        score = act.advertise_interruption(p)

                    elif (not do_interruption):
                        score = act.advertise(p)

                    if (score is not None):
                        # add the score for each activity
                        x = {'score': score, 'asset': a, 'activity': act, 'person': p}
                        ads.append(x)

        return ads

    def initialize(self, people):

        """
        Initialize the assets in the home.        

        :param list people: a list of people who reside in the home

        :return: None
        """

        # initialize all of the assets
        for a in self.assets.values():
            a.initialize(people)

        return

    def print_category(self):

        """
        This function expresses the category variable as a string.


        :return: string representation of the category
        :rtype: str
        """

        msg = 'ERROR! %d is an invalid choice for home.category!\n'


        return INT_2_STR_CAT.get(self.category, msg)

    def reset(self):

        """
        This function resets the each asset in the home.
        
        :return: None 
        """
        # reset the assets
        for x in self.assets.values():
            x.reset()

        return

    def set_population(self, people):

        """
        Set the population of the house.

        :param list people: the list of people living in the home

        :return: None
        """
        # people is a list of Person objects that share the same Home
        self.population = len(people)

        return

    def set_revenue(self, people):

        """
        Sets the revenue of the home by adding the revenue of each person in the home.

        :param list people: the list of people living in the home
        :return: None
        """

        # people is a list of Person objects that share the same Home
        self.revenue = sum( [p.socio.job.wage for p in people] )

        return

    def toString(self):

        """
        This function expresses the Home object as a string

        :return msg: the string representation of the home object
        :rtype: str
        """

        msg = ''
        # the identification number of the home
        msg = msg + 'Home ID:\t%d\n' % self.id

        # the home type
        msg = msg + 'Home Type:\t' + self.print_category() + '\n'

        # the revenue of the household
        msg = msg + 'Household Revenue:\t$ %d\n' % self.revenue

        # population of the home
        msg = msg + 'Population:\t%d\n' % self.population

        # the location info about the home
        msg = msg + self.location.toString()

        # assets in the home
        msg = msg + 'Assets\n'
        for a in self.assets.values():
            msg = msg + a.toString()

        return msg

