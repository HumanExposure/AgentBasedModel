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
This module contains information about the asset that allows for the eating activity. 

This module contains the following class: :class:`food.Food`.

.. moduleauthor:: Dr. Namdi Brandon.
"""


# ===============================================
# import
# ===============================================

# general math capability
import numpy as np

# agent-based model modules
import asset, eat, location

# ===============================================
# class Food
# ===============================================

class Food(asset.Asset):

    """
    This class represents an asset that allows the agent to eat breakfast, eat lunch, and eat dinner.

    Activities in this asset:

    #. :class:`eat.Eat_Breakfast`
    #. :class:`eat.Eat_Lunch`
    #. :class:`eat.Eat_Dinner`

    """
    #
    # constructor
    #
    def __init__(self):

        # call the Asset constructor
        asset.Asset.__init__(self)

        # assign the asset category
        self.category = asset.FOOD

        # set the maximum number of users
        self.max_users = np.inf
        
        # set the location
        self.location.local = location.HOME
        
        # add the activity to the activity list
        self.activities = {'eat breakfast': eat.Eat_Breakfast(),
                           'eat lunch': eat.Eat_Lunch(),
                           'eat dinner': eat.Eat_Dinner(),
                           }

        return
