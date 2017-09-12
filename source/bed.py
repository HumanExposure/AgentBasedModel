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
This module contains code that enables the agent to use a bed. This class allows access to the \
sleep (:class:`sleep.Sleep`) activity.

This module contains the following class: :class:`bed.Bed`.

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# general math package
import numpy as np

# agent-based model modules
import asset, sleep

# ===============================================
# class Bed
# ===============================================

class Bed(asset.Asset):

    """
    This asset models a bed. It allows the agent to address the Rest (:class:`rest.Rest`) need by doing the \
    sleep (:class:`sleep.Sleep`) action .

    """

    # constructor
    def __init__(self):

        # call the Asset constructor
        asset.Asset.__init__(self)

        # set the category
        self.category = asset.BED

        # set the maximum amount of users
        self.max_users = np.inf

        # set the activities
        self.activities = {'sleep': sleep.Sleep(), }

        return
     
