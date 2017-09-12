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
This module contains code for the :class:`asset.Asset` that allows a Person to go to work / school.

This file contains :class:`workplace.Workplace`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ----------------------------------------------------------
# import
# ----------------------------------------------------------
# general math capabilities
import numpy as np

# ABM modules
import asset, location, work

# ===============================================
# class
# ===============================================


class Workplace(asset.Asset):

    """
    This class allows a Person to go to work / school.

    Activities in this asset: :class:`work.Work`
    """

    #
    # constructor
    #
    def __init__(self):
        
        asset.Asset.__init__(self)
        
        self.category   = asset.WORKPLACE
        self.max_users  = np.inf
        
        # set the location
        self.location.local = location.OFF_SITE
        
        # the work activity
        self.activities = {'work': work.Work(), }
        
        return
     
   
