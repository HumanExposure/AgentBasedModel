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
This module contains information about the :class:`asset.Asset` that allows a :class:`person.Person` to do \
the following:

#. :class:`commute.Commute_To_Work`
#. :class:`commute.Commute_From_Work`

activities. This module contains code for :class:`transport.Transport`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ----------------------------------------------------------
# import
# ----------------------------------------------------------

# agent-based model modules
import asset, commute, location, occupation

# ===============================================
# class
# ===============================================

class Transport(asset.Asset):

    """
    This class is an asset that allows for commuting.

    Activities in this asset:

    #. :class:`commute.Commute_To_Work`
    #. :class:`commute.Commute_From_Work`

    """

    #
    # constructor
    #
    def __init__(self):
        
        asset.Asset.__init__(self)
        
        self.category   = asset.TRANSPORT
        self.max_users  = 1

        # add the activities to the activity list
        self.activities = {'commute to work': commute.Commute_To_Work(),
                           'commute from work': commute.Commute_From_Work() }
        return

    def initialize(self, people):

        """
        This function sets the transport location according to whether or not the Person is commuting to or \
        from work.

        .. note::
            This function just sets the transport object to be at the home

        :param list people: a list of people in the simulation

        :return: None
        """

        self.location.local = location.HOME

        # find out if it's work time for each person
        # is_work_time = [occupation.is_work_time(p.clock, p.socio.job) for p in people ]

        # find out if it's commute time for each person
        # is_commute_time = [occupation.is_work_time(p.clock, p.socio.job, is_commute_to_work=True) for p in people ]

        # if a person is commuting / working, set the location to that Person's location
        # if (True in is_work_time):
        #    self.location.local = people[is_work_time.index(True)].socio.job.location.local
        # elif (True in is_commute_time):
        #    self.location.local = people[is_commute_time.index(True)].socio.job.location.local

        return