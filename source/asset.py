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
This module contains code that governs objects that enable access to activities \
(:class:`activity.Activity`) that an agent may use in order to address a need.

This module contains the following class: :class:`asset.Asset`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# agent-based model modules
import location, state

# ===============================================
# constants
# ===============================================

# asset identifiers
TRANSPORT       = 0
BED             = 1
WORKPLACE       = 2
FOOD            = 3
INTERRUPTION    = 4

# This dictionary takes the INTEGER representation of an Asset category and
# returns a STRING representation
INT_2_STR = {
    TRANSPORT: 'Transport',
    BED: 'Bed',
    WORKPLACE: 'Workplace',
    FOOD: 'Food',
    INTERRUPTION: 'Interruption',
    }

# This dictionary takes the STRING representation of an Asset category and
# returns an INTEGER representation
STR_2_INT = { v: k for k, v in INT_2_STR.items() }

# ===============================================
# class Asset
# ===============================================

class Asset(object):

    """
    An asset is an object that allows the agent to perform an activity. Each asset \
    contains a list of activities that an agent can use to perform actions.

    :ivar dict activities: a dictionary of all the activities associated with this asset
    :ivar int category: a code that indicates the category type of asset
    :ivar int id: an identifier number for the asset
    :ivar location.Location 'location': the location of the asset
    :ivar int max_users: the maximum number of users that can simultaneously access the asset
    :ivar int num_users: the current number of users for the asset
    :ivar int status: the state of the asset

    """
    #
    # constructor
    #
    def __init__(self):

        # the identifier of the asset
        self.id         = -1

        # the category type of the asset
        self.category   = -1

        # the status of the asset
        self.status     = state.IDLE

        # the number of users currently using the asset
        self.num_users  = 0

        # the maximum amount of users for the asset
        self.max_users  = 1

        # a dictionary of activities that asset contains
        self.activities = dict()

        # the location of the asset
        self.location = location.Location()

        return

    def free(self):

        """
        This function changes the state of an asset once it is freed by a Person by doing the following:
        
        #. decreases the number of users of the asset by 1
        #. if the number of users is zero, the status of the asset is set to idle (:const:`state.IDLE`)

        :return: None
        """

        # decrease the users of that state
        self.num_users = self.num_users - 1

        # change the state of the asset
        if (self.num_users == 0):
            self.status = state.IDLE

        return

    def initialize(self, people):

        """
        This function initializes the asset at the beginning of the simulation.

        .. note:: 
            This function is meant to be overridden 
            
        :param people: the Person objects who could be using the asset.
        :type people: list[ person.Person ]
        
        :return:  None

        """

        return

    def print_category(self):
        """
         This function represents the category as a string.

        :return: the string representation of the category
        :rtype: str
        """

        # error message
        msg = 'ERROR! %d is an Invalid choice of asset.Asset.category!\n' % self.category

        # If the category is a valid option, return the category as a string
        # Else, return the error message
        return INT_2_STR.get(self.category, msg)

    def reset(self):

        """
        This function does the following:
        
        #. sets the number of users to zero
        #. sets the asset's status to idle
        
        :return: None 
        """

        self.num_users  = 0
        self.status     = state.IDLE

        return

    def toString(self):

        """
         This function represents the asset as a string.

        :return msg: The string representation of the asset object.
        :rtype: str
        """

        msg = ''

        # write the category type
        msg = msg + 'Asset Type: ' + self.print_category() + '\n'

        # write the number of users
        msg = msg + 'number of users:\t%d out of %f\n' % (self.num_users, self.max_users)

        # write the activities
        msg = msg + 'Activity list\n'
        for a in self.activities.values():
            msg = msg + a.toString()

        # location
        msg = msg + 'Location\n'
        msg = msg + self.location.toString()

        return msg

    def update(self):

        """
        This function changes the state of the asset once it is used by a person. The update does \
        the following:
        
        #. increases the number of people by 1
        #. if the number of users is at the maximum number, set the asset's status to busy
        #. if the number of users is less than the maximum number, set the asset's status to busy but \
        able to be used by another agent

        :return: None
        """

        # increase the number of users for this asset
        self.num_users = self.num_users + 1

        # update the state of the asset, since it is in use
        if (self.num_users == self.max_users):
            self.status = state.BUSY
        else:
            self.status = state.BUSY_MULTI

        return

