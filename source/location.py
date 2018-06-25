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
This module is responsible for containing information about the \
concept of location.

This module contains class :class:`location.Location`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# constants
# ===============================================

# geographical location constants
NORTH   = 1
SOUTH   = 2
EAST    = 3
WEST    = 4

# local location constants
HOME        = 0
TRANSIT     = 1
OFF_SITE    = 3


# This dictionary takes the INTEGER representation of a geographical location code
# and returns a STRING representation
INT_2_STR_GEO = {
    NORTH: 'North',
    SOUTH: 'South',
    EAST: 'East',
    WEST: 'West',
}

# This dictionary takes the INTEGER representation of a local location code
# and returns a STRING representation
INT_2_STR_LOCAL = {
    HOME: 'Home',
    TRANSIT: 'Transit',
    OFF_SITE: 'Off-Site',
}

# ===============================================
# class Location
# ===============================================

class Location(object):

    """
    This class holds information relevant to the location of persons and assets.

    :param int geography: the geographical location code
    :param int local: the local location code

    :ivar int geo: the geographical location code within the United States (e.g. north, south, eats, or west)
    :ivar int local: the local location code (e.g. home, off site, etc)
    """

    #
    # Constructor
    #

    def __init__( self, geography=NORTH, local=HOME ):

        # the geographical location (referring to area of the United States)
        self.geo = geography
        
        # the local location
        self.local = local
        
        return

    def print_geo(self):

        """
        Returns the geographical location in a string format

        :return: the string representation of the geographical location
        :rtype: str
        """

        # message to be printed if there is an error
        msg = 'ERROR! %d is an invalid geographical location!\n' % self.geo
            
        return INT_2_STR_GEO.get(self.geo, msg)

    def print_local(self):

        """
        Returns the local location in a string format

        :return: the string representation of the local location
        :rtype: str
        """

        # message to be printed if there is an error
        msg = 'ERROR! %d is an invalid location.local!\n' % self.local

        return INT_2_STR_LOCAL.get(self.local, msg)

    def reset(self):

        """
        This function resets the location to the default value, (:const:`location.HOME`).
        
        :return: None
        """

        self.local = HOME

        return

    def toString( self ):

        """
        This function represents the Location object as a string.

        :return msg: the string representation of the Location object
        :rtype: str
        """

        msg = ''
        msg = msg + 'Geographical location: ' + self.print_geo() + '\n'
        msg = msg + 'Local location: ' + self.print_local() + '\n'
        
        return msg
