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
This module contains activity codes found in the Consolidated Human Activity Database (CHAD).

The following general :class:`chad_code` constants consist of groupings of CHAD activity codes

#. sleep
#. eat
#. work 
    * work and income producing activities; work, general; work, income-related only; work, secondary \
    (income-related); work breaks     
#. education
    * general education and professional training, attending full-time school, attend day-care; attend school \
    kindergarten - 12th grade    
#. commute to/ from work
    * travel to/ from work general; travel to/ from work by bus; travel to/ from work by foot; travel to/ from via \
    motor vehicle; travel to/ from work via motor vehicle, by driving; travel to/from work via motor vehicle by \
    driving via motor vehicle, by riding; travel to/ from work waiting
#. commute to/ from school
    * travel for education general; travel for education by bus; travel for education by foot; travel to/ from \
      school via motor vehicle; travel for education via motor vehicle, by driving; travel for education via motor \
      vehicle, by riding; travel for education, waiting
#. All
    * sleep + eat + work + education + commute to/ from work + commute to/ from school

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# constants
# ===============================================


# CHAD codes

#
# sleep
#

SLEEP0      = 14500     # sleep or nap
SLEEP       = [SLEEP0]

#
# eat
#
EAT0        = 14400
EAT         = [EAT0]

#
# work
#
WORK0       = 10000     # work and other income producing activities, general
WORK_GEN    = 10100     # work, general
WORK_INC    = 10120     # work, income-related only
WORK_INC2   = 10130     # work, secondary (income-related)
WORK_BREAK  = 10300     # work breaks
WORK        = [WORK0, WORK_GEN, WORK_INC, WORK_INC2, WORK_BREAK]

#
# school / education
#
EDU_GEN             = 15000         # general education and professional training
EDU_FULLTIME        = 15100         # attending full-time school
EDU_DAYCARE         = 15110         # attend-day care
EDU_K_12            = 15120         # attend school K-12
EDU_COLLEGE         = 15130         # attending college or trade school
EDU_ADULT           = 15140         # attend adult education and special training
EDU_OTHER_CLASSES   = 15200         # attend other classes
EDU_HW              = 15300         # do homework
EDU_LIBRARY         = 15400         # use the library
EDU_OTHER           = 15500         # other education
EDUCATION           = [EDU_GEN, EDU_FULLTIME, EDU_DAYCARE, EDU_K_12] # these had the best results for school aged children

#
# commuting to and from work
#
COMM_GEN        = 18200     # travel to/from work, general
COMM_BUS        = 18210     # travel to/from work by bus
COMM_FOOT       = 18220     # travel to/from work by foot
COMM_MV         = 18230     # travel to/from work via motor vehicle
COMM_MV_DRIVE   = 18231     # travel to/from work via motor vehicle, while driving
COMM_MV_RIDE    = 18232     # travel to/from work via motor vehicle, while riding
COMM_WAIT       = 18240     # travel to/from work, wait
COMMUTE         = [COMM_GEN, COMM_BUS, COMM_FOOT, COMM_MV, COMM_MV_DRIVE, COMM_MV_RIDE, COMM_WAIT]

#
# commuting to and from school
#
COMM_EDU_GEN        = 18300 # travel for education, general
COMM_EDU_BUS        = 18310 # travel for education by bus
COMM_EDU_FOOT       = 18320 # travel for education by foot
COMM_EDU_MV         = 18330 # travel for education by motor vehicle
COMM_EDU_MV_DRIVE   = 18331 # travel for education, drive a motor vehicle
COMM_EDU_MV_RIDE    = 18332 # travel for education, ride in a motor vehicle
COMM_EDU_WAIT       = 18340 # travel for education, wait
COMMUTE_EDU         = [COMM_EDU_GEN, COMM_EDU_BUS, COMM_EDU_FOOT, COMM_EDU_MV, COMM_EDU_MV_DRIVE, COMM_EDU_MV_RIDE, \
                       COMM_EDU_WAIT]

#
# a list of all of the CHAD codes, thus far
#
ALL = SLEEP + EAT + WORK + EDUCATION + COMMUTE + COMMUTE_EDU

#
# convert the CHAD code to a string
#

INT_2_STR = {
    COMM_GEN: 'Travel to/from work, general',
    COMM_BUS: 'Travel to/from work by bus',
    COMM_FOOT: 'Travel to/from work by foot',
    COMM_MV: 'Travel to/from work via motor vehicle',
    COMM_MV_DRIVE: 'Travel to/from work via motor vehicle, while driving',
    COMM_MV_RIDE: 'Travel to/from work via motor vehicle, while riding',
    COMM_WAIT: 'Travel to/from work, wait',

    COMM_EDU_GEN: 'Travel for education, general',
    COMM_EDU_BUS: 'Travel for education by bus',
    COMM_EDU_FOOT: 'Travel for education by foot',
    COMM_EDU_MV: 'Travel for education by motor vehicle',
    COMM_EDU_MV_DRIVE: 'Travel for education, drive a motor vehicle',
    COMM_EDU_MV_RIDE: 'Travel for education, ride in a motor vehicle',
    COMM_EDU_WAIT: 'Travel for education, wait',

    EAT0: 'Eat',

    EDU_GEN: 'General education and professional training',
    EDU_FULLTIME: 'Attend full-time school',
    EDU_DAYCARE: 'Attend full-time school: daycare',
    EDU_K_12: 'Attend full-time school: K-12',
    EDU_COLLEGE: 'Attend full-time school: college or trade school',
    EDU_ADULT: 'Attend full-time school: adult education and special training',
    EDU_OTHER_CLASSES: 'Attend other classes',
    EDU_HW: 'Do homework',
    EDU_LIBRARY: 'Use library',
    EDU_OTHER: 'Other education',

    SLEEP0: 'Sleep',

    WORK0: 'Work and other income producing activities, general',
    WORK_GEN: 'Work, general',
    WORK_INC: 'Work, income-related only',
    WORK_INC2: 'Work, secondary (income-related)',
    WORK_BREAK: 'Work breaks',
}

# convert code into a file name to save a figure
INT_2_SAVE_FIG_FNAME = {
    COMM_GEN: '\\commute_work\\commute_general.png',
    COMM_BUS: '\\commute_work\\commute_bus.png',
    COMM_FOOT: '\\commute_work\\commute_foot.png',
    COMM_MV: '\\commute_work\\commute_mv.png',
    COMM_MV_DRIVE: '\\commute_work\\commute_mv_drive.png',
    COMM_MV_RIDE: '\\commute_work\\commute_mv_ride.png',
    COMM_WAIT: '\\commute_work\\commute_wait.png',

    COMM_EDU_GEN: '\\commute_edu\\commute_general.png',
    COMM_EDU_BUS: '\\commute_edu\\commute_bus.png',
    COMM_EDU_FOOT: '\\commute_edu\\commute_foot.png',
    COMM_EDU_MV: '\\commute_edu\\commute_mv.png',
    COMM_EDU_MV_DRIVE: '\\commute_edu\\commute_mv_drive.png',
    COMM_EDU_MV_RIDE: '\\commute_edu\\commute_mv_ride.png',
    COMM_EDU_WAIT: '\\commute_edu\\commute_wait.png',

    EAT0: '\\eat\\eat.png',

    EDU_GEN: '\\education\\edu_general.png',
    EDU_FULLTIME: '\\education\\edu_fulltime.png',
    EDU_DAYCARE: '\\education\\edu_daycare.png',
    EDU_K_12: '\\education\\edu_K_12.png',
    EDU_COLLEGE: '\\education\\edu_college.png',
    EDU_ADULT: '\\education\\edu_adult.png',
    EDU_OTHER_CLASSES: '\\education\\edu_other_classes.png',
    EDU_HW: '\\education\\edu_homework.png',
    EDU_LIBRARY: '\\education\\edu_library.png',
    EDU_OTHER: '\\education\\edu_other.png',

    SLEEP0: '\\sleep\\sleep.png',

    WORK0: '\\work\\work_income_general.png',
    WORK_GEN: '\\work\\work_general.png',
    WORK_INC: '\\work\\work_primary.png',
    WORK_INC2: '\\work\\work_secondary.png',
    WORK_BREAK: '\\work\\work_break.png',
}