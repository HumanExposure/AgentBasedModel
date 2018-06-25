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
# March 22, 2018

"""
This module handles the logistics of data dealing with demographics from the \
raw data from the Consolidated Human Activity Database (CHAD) data in order to \
be used in Agent-Based Model of Human Activity Patterns (ABMHAP).
"""

# ===========================================
# import
# ===========================================
import copy, sys
sys.path.append('..\\source')

# ABMHAP modules
import my_globals as mg
import chad, social

# ===========================================
# constants
# ===========================================

# the file names for the various demographic groups

ALL             = 1
ADULT           = 2
ADULT_NON_WORK  = 3
ADULT_WORK      = 4
CHILD_SCHOOL    = 5
CHILD_YOUNG     = 6

# the file names for the various demographic groups
FNAME_ALL               = chad.FDIR_ALL_LARGE + '\\data.pkl'
FNAME_ADULT             = chad.FDIR_ADULT_LARGE + '\\data.pkl'
FNAME_ADULT_NON_WORK    = chad.FDIR_ADULT_NON_WORK_LARGE + '\\data.pkl'
FNAME_ADULT_WORK        = chad.FDIR_ADULT_WORK_LARGE + '\\data.pkl'
FNAME_CHILD_SCHOOL      = chad.FDIR_CHILD_SCHOOL_LARGE + '\\data.pkl'
FNAME_CHILD_YOUNG       = chad.FDIR_CHILD_YOUNG_LARGE + '\\data.pkl'

# dictionary to choose input file and output file
INT_2_FIN_FOUT = {ADULT: (FNAME_ADULT, chad.FNAME_ADULT),
                  ADULT_NON_WORK: (FNAME_ADULT_NON_WORK, chad.FNAME_ADULT_NON_WORK),
                  ADULT_WORK: (FNAME_ADULT_WORK, chad.FNAME_ADULT_WORK),
                  CHILD_SCHOOL: (FNAME_CHILD_SCHOOL, chad.FNAME_CHILD_SCHOOL),
                  CHILD_YOUNG: (FNAME_CHILD_YOUNG, chad.FNAME_CHILD_YOUNG),
                  ALL: (FNAME_ALL, chad.FNAME_ALL)
                  }

INT_2_FIN_FOUT_LARGE = { ADULT: (FNAME_ADULT, chad.FDIR_ADULT_LARGE),
                         ADULT_NON_WORK: (FNAME_ADULT_NON_WORK, chad.FDIR_ADULT_NON_WORK_LARGE),
                         ADULT_WORK: (FNAME_ADULT_WORK, chad.FDIR_ADULT_WORK_LARGE),
                         CHILD_SCHOOL: (FNAME_CHILD_SCHOOL, chad.FDIR_CHILD_SCHOOL_LARGE),
                         CHILD_YOUNG: (FNAME_CHILD_YOUNG, chad.FDIR_CHILD_YOUNG_LARGE),
                         ALL: (FNAME_ALL, chad.FDIR_ALL_LARGE)
                        }

# dictionary to choose the file name of the compressed data based on demography
FNAME_DEMOGRAPHY = {ALL: chad.FNAME_ALL,
                    ADULT: chad.FNAME_ADULT,
                    ADULT_NON_WORK: chad.FNAME_ADULT_NON_WORK,
                    ADULT_WORK: chad.FNAME_ADULT_WORK,
                    CHILD_SCHOOL: chad.FNAME_CHILD_SCHOOL,
                    CHILD_YOUNG: chad.FNAME_CHILD_YOUNG,
                    }

# a dictionary to choose the file name to save the figure data for a given demographic
INT_2_FDIR_SAVE_FIG_DEFAULT = { ALL: mg.FDIR_SAVE_FIG_ALL,
                                ADULT: mg.FDIR_SAVE_FIG_ADULT,
                                ADULT_NON_WORK: mg.FDIR_SAVE_FIG_ADULT_NON_WORK,
                                ADULT_WORK: mg.FDIR_SAVE_FIG_ADULT_WORK,
                                CHILD_SCHOOL: mg.FDIR_SAVE_FIG_CHILD_SCHOOL,
                                CHILD_YOUNG: mg.FDIR_SAVE_FIG_CHILD_YOUNG,
                                }
# ===========================================
# functions
# ===========================================

def filter_adult(x, do_work):

    """
    This function goes through the adult CHAD data and filters the results if \
    the data is supposed to be for working adult or non-working adults.

    :param chad.CHAD_RAW x: CHAD data for adults
    :param bool do_work: a flag indicating whether to get data from working \
    adults (if True) or non-working adults (if False)

    :return:
    """

    q = x.quest
    e = x.events

    if do_work:
        idx = (q.employed == 'Y') & (q.fulltime == 'Y')

        # the unique set of appropriate PIDs
        pid = q.PID[idx].unique()
    else:
        gb  = q.groupby('PID')
        pid = []

        # the unique set of PIDs for unemployed people
        for p in q.PID.unique():
            df = gb.get_group(p)
            if (df.employed == 'N').all():
                pid.append(p)

    # function that checks to see if a PID(p) is in the unique set of desired PIDs (pid)
    f   = lambda p: p in pid

    # limit the questionnaire and events data
    q   = q[q.PID.apply(f)]
    e   = e[e.PID.apply(f)]

    x.quest     = q
    x.events    = e

    return

def get_adult():

    """
    This function gets the CHAD data for adults.

    :return: the raw CHAD data from individuals that correspond to adult age
    :rtype: chad.CHAD_RAW
    """

    # get all of the data for working age adults
    x = chad.CHAD_RAW(min_age=social.ADULT_AGE, max_age=social.MAX_AGE)

    return x

def get_adult_non_work(adult):

    """
    This function gets raw CHAD data from non-working adults.

    :param chad.CHAD_RAW adult: the raw adult data from CHAD

    :return: raw CHAD data from non-working adults
    :rtype: chad.CHAD_RAW
    """

    x = copy.copy(adult)

    # get about non working adults
    filter_adult(x, do_work=False)

    return x

def get_adult_work(adult):

    """
    This function gets raw CHAD data from working adults.

    :param chad.CHAD_RAW adult: the raw adult data from CHAD

    :return: raw CHAD data from working adults
    :rtype: chad.CHAD_RAW
    """

    x = copy.copy(adult)

    # get data about fulltime working adults
    filter_adult(x, do_work=True)

    return x

def get_all():

    """
    This function gets all of the raw CHAD data.

    :return: all of the raw CHAD data
    :rtype: chad.CHAD_RAW
    """

    # load all of the data
    x = chad.CHAD_RAW(min_age=0, max_age=social.MAX_AGE)

    return x

def get_child_school():

    """
    This function gets the CHAD data for school-age children.

    :return: the raw CHAD data from individuals that correspond to school-age children
    :rtype: chad.CHAD_RAW
    """

    # school aged children
    x = chad.CHAD_RAW(min_age=social.SCHOOL_AGE, max_age=social.ADULT_AGE - 1)

    return x

def get_child_young():

    """
    This function gets the CHAD data for preschool children.

    :return: the raw CHAD data from individuals that correspond to preschool children
    :rtype: chad.CHAD_RAW
    """

    # pre-school children
    x = chad.CHAD_RAW(min_age=social.MIN_AGE, max_age=social.SCHOOL_AGE - 1)

    return x

def load(fname):

    """
    This function loads data given by the file name

    :param str fname: the file name of the data to load

    :return: the data
    """

    # load the data
    return mg.load(fname)

def save(x, fname):

    """
    This function saves the raw CHAD data for the given demographic as a .pkl file.

    :param chad.CHAD_RAW x: the raw CHAD data to save for a given demographic
    :param str fname: the file name to save raw CHAD data for a given demographic

    :return:
    """

    # first, close the zip file. This is necessary to avoid an pickling error
    x.z.close()

    # pickle the data
    mg.save(x, fname)

    return

# ===========================================
# run
# ===========================================

if __name__ == '__main__':

    # flag to indicate whether or not to load the data
    do_load = False

    # flag to indicate whether or not the files will be saved
    do_save = False

    # load the data
    if do_load:

        # load all of the data
        print('loading all of the data...\n')
        all = get_all()

        print('loading all of the adult data...\n')
        adult = get_adult()

        print('loading the non-working adult data...\n')
        adult_non_work = get_adult_non_work(adult)

        print('loading the working adult data...\n')
        adult_work = get_adult_work(adult)

        print('loading child data...\n')
        child_school, child_young = get_child_school(), get_child_young()

        print('finished loading data...\n')

        # save the data
        if do_save:

            print('saving the data...\n')

            x       = [all, adult, adult_non_work, adult_work, child_school, child_young]
            fnames  = [FNAME_ALL, FNAME_ADULT, FNAME_ADULT_NON_WORK, FNAME_ADULT_WORK,FNAME_CHILD_SCHOOL, \
                       FNAME_CHILD_YOUNG]

            # save all of the data
            for y, fname in zip(x, fnames):
                save(y, fname)

            print('finished saving')