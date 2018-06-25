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
This module contains information about the activities associated with eating. This class is an \
Activity (:class:`activity.Activity`) that gives a Person (:class:`person.Person`) the ability \
to eat and satisfy the need Hunger (:class:`hunger.Hunger`).

This module contains the following classes:

#. :class:`eat.Eat` (general eating capabilities)
#. :class:`eat.Eat_Breakfast` (eating breakfast)
#. :class:`eat.Eat_Lunch` (eating lunch)
#. :class:`eat.Eat_Dinner` (eating dinner)

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# general math capability
import numpy as np

# agent-based model modules
import activity, location, meal, need, occupation, state, temporal

# ===============================================
# class
# ===============================================


class Eat(activity.Activity):

    """
    This class has general capabilities that allow the person to eat in order to satisfy :class:`hunger.Hunger`. \
    This class acts as a parent class and is expected to inherited.
    """

    #
    # constructor
    #
    def __init__(self):

        activity.Activity.__init__(self)
        
        return

    def advertise(self, p):

        """
        This function handles advertising the score to an agent. This function returns 0.
        
        .. note::
            This function should be overloaded when inherited.
        
        :param person.Person p:  the person of interest
        :return: the score (0)
        :rtype: float        
        """

        score = 0.0

        return score


    def advertise_help(self, p, dt):

        """
        This function does some of the logistics needed for :func:`advertise`. 
        
        This function does the following:
        
        #. sets the suggested recharge rate for hunger
        #. calculates the score        
        
        
        :param person.Person p: the person who is being advertised to 
        :param float dt: the duration of the activity
         
        :return: the score
        :rtype: float
        """

        # this is needed in order to do hunger.perceive()
        p.hunger.set_suggested_recharge_rate(dt)

        # get the score
        score   = super(Eat, self).advertise(p.hunger, dt)

        return score

    def advertise_interruption(self, p):

        """
        This function calculates the score of an activity advertisement when a person is going to interrupt an \
        ongoing activity in order to do an eating activity.    

        This function does the following:
        
        #. temporarily sets the satiation of hunger  :math:`n_{hunger}(t) = \\eta_{interruption}`
        #. calculate the score advertised for the potential eating activity that will interrupt a current activity
        #. restores the the satiation for hunger to the original value
        
        :param person.Person p: the person of interest
        :return score: the value of the advertisement
        :rtype: float
        """

        # store the old magnitude
        mag_temp = p.hunger.magnitude
        
        # set the hunger magnitude temporarily to a low number
        p.hunger.magnitude = need.MAG_INTERRUPTION
        
        # store the score
        score = self.advertise(p)
        
        # restore the proper hunger magnitude
        p.hunger.magnitude = mag_temp            
 
        return score        

    def end(self, p):

        """
        This function ends the eat activity.

        :param person.Person p: the person whose activity is ending
        :return: None
        """

        # end the eating activity
        self.end_meal(p)

        # do logistics for ending an activity
        super(Eat, self).end(p)

        return

    def end_meal(self, p):

        """
        This function ends the eat activity by doing the following:
        
        #. frees the person's use of the asset
        #. sets the state to idle (:const:`state.IDLE`)
        #. sets the satiation of hunger 
        #. set the current meal for the next day
        #. set any skipped meals to be on the next day
        #. find the the next meal
        #. sets the decay rate of hunger
        #. update the scheduler so that hunger will trigger the schedule to stop at the next meal
        #. set the next meal to the current meal

        :param person.Person p: The person whose meal is ending.
        :return: None
        """

        # frees up the asset
        p.state.asset.free()

        # change the status of the person
        p.state.status = state.IDLE

        # the amount of time spent eating
        dt = p.state.t_end - p.state.t_start

        # the gain in need magnitude
        delta = p.hunger.recharge_rate * (dt+1)

        # update the person's Hunger Need
        p.hunger.magnitude = min( p.hunger.magnitude + delta, 1.0 )

        # set the current meal for the next day
        p.socio.current_meal.update(p.clock.day + 1)

        #
        # this handles skipped meals, all durations to the meal are positive
        # set any skipped meals to start on the next day
        #
        for m in p.socio.meals:
            i = 1
            while (m.t_start_univ <= p.clock.t_univ):
                m.update(p.clock.day + i)
                i = i + 1

        #
        # need to find the next meal so that the following is avoided
        # an early lunch ends before a late breakfast
        #

        dt, the_meal = p.socio.duration_to_next_meal(p.clock.t_univ)

        # set the hunger decay rate
        p.hunger.set_decay_rate_new(dt)

        # update the schedule
        p.schedule.update(p.id, need.HUNGER, dt)

        # set the new current meal
        p.socio.current_meal = the_meal

        return

    def set_end_time(self, p):

        """
        This function returns the end time of eating (universal time).

        :param person.Person p: the person of interest.

        :return t_end: the end time of eating [minutes, universal time]
        :rtype: int
        """

        # this is the meal being used. This is useful when the current meal begins in 1 meal space and
        # ends in another meal space. Do not use p.socio.get_current_meal(p.clock.time_of_day)
        the_meal    = p.socio.current_meal

        # set hunger suggested recharge rate
        p.hunger.set_suggested_recharge_rate(the_meal.dt)

        # the amount of time it takes to eat a meal until fully satisfied
        # (make sure it is an integer)
        #if (p.state.is_init):
        if (p.clock.initial_step):
            dt = (1 - p.hunger.magnitude) / p.hunger.recharge_rate
        else:
            dt = (1 - p.hunger.magnitude) / p.hunger.suggested_recharge_rate

        # round the time to the nearest minute
        dt = np.round(dt).astype(int)

        # the time to end the meal
        t_end = p.state.t_start + dt


        return t_end

    def start(self, p):

        """
        This function starts the eating activity.

        :param person.Person p: The person whose activity is starting.

        :return: None
        """

        # start the meal
        self.start_meal(p)
        
        # store a list of the arguments for the end() procedure
        p.state.arg_end.append(p)
        
        return

    def start_meal(self,p):

        """
        This function starts the eat activity by doing the following:

        #. sets the person's state to busy (:const:`state.BUSY`)
        #. set the decay rate of hunger to 0
        #. store the start time to the state
        #. sets the end time
        #. sets the hunger recharge rate
        #. updates the asset's state and number of users        
        #. update the schedule for the hunger need to trigger when the eat activity is scheduled to end         

        :param person.Person p: the person who is starting the meal
        :return: None
        """

        # set the state of of the person to 
        p.state.status = state.BUSY        
        
        # hunger does not decay while eating
        p.hunger.decay_rate = 0.0

        # set the start time of the current state
        p.state.t_start = p.clock.t_univ

        # calculate the end time of sleep
        p.state.t_end = self.set_end_time(p)

        # calculate the duration
        dt = p.state.t_end - p.state.t_start

        if dt < 0:
            uu = 1
        # set the recharge rate for the hunger need association
        p.hunger.set_recharge_rate(dt+1)

        # update the asset
        p.state.asset.update()

        # update the scheduler
        p.schedule.update(p.id, need.HUNGER, dt)

        return

    def test_func(self, p):

        """
        .. note::
            This function is for debugging and has no practical purpose. This function will be \
            removed in the future.

        :param person.Person p: person of interest
        :return: None
        """

        print([(m.t_start_univ - p.clock.t_univ) for m in p.socio.meals])
        print('current meal: %s' % meal.INT_2_STR[p.socio.current_meal.id])

        return

# ===============================================
# class Eat_Breakfast
# ===============================================

class Eat_Breakfast(Eat):

    """
    This class is used to handle the logistics for eating breakfast.
    """

    def __init__(self):

        Eat.__init__(self)

        self.id = activity.EAT_BREAKFAST

        return

    def advertise(self, p):

        """
        This function calculates the score of the activity's advertisement to a person. The activity \
        advertise to the agent if the following conditions are met:
        
        #. the current meal is breakfast
        #. the agent's location is at home (:const:`location.HOME`)
        #. calculate the score :math:`S`
                                        
        .. math::     
            S = \\begin{cases}
            0  & n_{hunger}(t) > \\lambda \\\\
            W( n_{hunger}(t) ) - W( n_{hunger}(t + \\Delta{t} )) & n_{hunger}(t) \\le \\lambda
            \\end{cases}

        where
            * :math:`t` is the current time
            * :math:`\\Delta{t}` is the duration of eating breakfast [minutes]
            * :math:`n_{hunger}(t)` is the satiation for Hunger at time :math:`t`
            * :math:`\\lambda` is the threshold value of Hunger
            * :math:`W(n)` is the weight function for Hunger

        :param person.Person p: the person of interest
        :return score: the advertised score of doing the eat breakfast activity
        :rtype: float
        """

        score = 0.0

        # get the next meal
        the_meal = p.socio.get_current_meal(p.clock.time_of_day)

        # only eat breakfast at home
        if (the_meal is not None) and (the_meal.id == meal.BREAKFAST) and (p.location.local == location.HOME):

            score = self.advertise_help(p, the_meal.dt)

        return score

    def end_meal(self, p):

        """
        This function handles the logistics for ending the eat breakfast activity by doing the following:
         
         #. call :func:`eat.end_meal`
         #. if planning to skip lunch, update the lunch event to be the next day
        
        :param person.Person p: the person who's meal is ending 
        :return: 
        """

        # call the constructor of the parent class
        super(Eat_Breakfast, self).end_meal(p)

        # if planning to skip lunch
        # say, it's day 1 and breakfast ends and for whatever reason dinner is the nearest meal
        # Then, lunch must be planned to be eaten on day 2
        if p.socio.current_meal.id == meal.DINNER:
            p.socio.meals[meal.LUNCH].update(p.clock.day + 1)

        return

    def start_meal(self, p):

        """
        This function handles the logistics for starting the eat activity by doing the following:
        
        #. set the current meal to breakfast
        #. call :func:`eat.start_meal`
        
        :param person.Person p: the person who is starting the eat activity 
        :return: 
        """
        p.socio.meals[meal.BREAKFAST].day   = p.clock.day
        p.socio.current_meal                = p.socio.get_meal(meal.BREAKFAST)

        super(Eat_Breakfast, self).start_meal(p)

        return

# ===============================================
# class Eat Lunch
# ===============================================

class Eat_Lunch(Eat):

    """
    This class is used to handle the logistics for eating lunch.
    """

    def __init__(self):

        Eat.__init__(self)

        self.id = activity.EAT_LUNCH

        return

    def advertise(self, p):

        """        
        This function calculates the score of an activities advertisement to a person. The activity \
        advertise to the agent if the following conditions are met:
        
        #. the current meal is lunch
        #. the agent's location is at home (:const:`location.HOME`) or the agent's location is at the \
        workplace (:const:`location.OFF_SITE`)
        #. calculate the score :math:`S`
                                        
        .. math::     
            S = \\begin{cases}
            0  & n_{hunger}(t) > \\lambda \\\\
            W( n_{hunger}(t) ) - W( n_{hunger}(t + \\Delta{t} )) & n_{hunger}(t) \\le \\lambda
            \\end{cases}

        where
            * :math:`t` is the current time
            * :math:`\\Delta{t}` is the duration of eating lunch [minutes]
            * :math:`n_{hunger}(t)` is the satiation for Hunger at time :math:`t`
            * :math:`\\lambda` is the threshold value of Hunger
            * :math:`W(n)` is the weight function for Hunger

        If the threshold is not met, score is 0. The advertisements assume that the duration \
        of the activity is the mean duration.

        :param person.Person p: the person of interest

        :return score: the advertised score of doing the eat lunch activity
        :rtype: float
        """

        # adjust the range of start times
        score   = 0.0

        # find the meal that is advertised.
        the_meal = p.socio.get_current_meal(p.clock.time_of_day)

        # need to add something for limiting advertisements at work during non-lunch time

        # if  breakfast is skipped, need to make sure lunch is advertised at the correct time. If a meal is advertised,
        # n < lambda.
        if (the_meal is not None) and (the_meal.id == meal.LUNCH):

            # set flags for if it's time to work
            is_work_time    = occupation.is_work_time(p.clock, p.socio.job)

            # set flag to see if the time is before lunch starts
            is_before_lunch = p.clock.time_of_day < the_meal.t_start

            # if agent is at work and before lunch time, do NOT eat lunch
            if (is_work_time and is_before_lunch):
                score = 0.0
            else:
                score = self.advertise_help(p, the_meal.dt)

        return score

    def end_meal(self, p):

        """
        This function ends the eat lunch activity by doing the following:

        #. calls :func:`eat.end_meal`
        #. if dinner is to be skipped, update the dinner event by doing the following:

            * if the lunch is an interrupting activity
                * set the time until the next lunch activity
                * update the schedule for the interruption to the next lunch activity
                * set the interruption state to False        

        :param person.Person p: The person whose meal is ending.
        :return: None
        """

        # update interruption at end of work NOT end of meal
        # also set hunger decay rate
        super(Eat_Lunch, self).end_meal(p)

        # if planning to skip dinner
        # say it's day 1 and we plan to skip dinner
        # must update dinner to be on day 2
        if p.socio.current_meal.id == meal.BREAKFAST:
            p.socio.meals[meal.DINNER].update(p.clock.day + 1)

        # update the scheduler if lunch was started due to an interruption
        # Note: I added the if clause later
        if p.state.do_interruption:
            dt  = p.interruption.get_time_to_next_work_lunch(p)
            p.schedule.update(p.id, need.INTERRUPTION, dt)
            p.state.do_interruption = False

        return

    def start_meal(self,p):

        """
        This function handles the logistics for starting the eat activity by doing the following:
        
        #. sets the current meal to lunch
        #. call :func:`eat.start_meal`
        
        :param person.Person p: the person starting the eat lunch event 
        :return: None
        """

        p.socio.meals[meal.LUNCH].day   = p.clock.day
        p.socio.current_meal            = p.socio.get_meal(meal.LUNCH)

        super(Eat_Lunch, self).start_meal(p)

        return

# ===============================================
# class Eat_Dinner
# ===============================================

class Eat_Dinner(Eat):

    """
    This class is used to handle the logistics for eating dinner.
    """

    def __init__(self):


        Eat.__init__(self)

        self.id = activity.EAT_DINNER

        return

    def advertise(self, p):

        """
        This function calculates the score of an activities advertisement to a Person. This activity \
        advertises to the agent if the following conditions are met
        
        #. the current meal is lunch
        #. the agent's location is at home (:const:`location.HOME`)
        #. calculate the score :math:`S`
                                        
        .. math::     
            S = \\begin{cases}
            0  & n_{hunger}(t) > \\lambda \\\\
            W( n_{hunger}(t) ) - W( n_{hunger}(t + \\Delta{t} )) & n_{hunger}(t) \\le \\lambda
            \\end{cases}

        where
            * :math:`t` is the current time
            * :math:`\\Delta{t}` is the duration of eating dinner [minutes]
            * :math:`n_{hunger}(t)` is the satiation for Hunger at time :math:`t`
            * :math:`\\lambda` is the threshold value of Hunger
            * :math:`W(n)` is the weight function for Hunger

        If the threshold is not met, score is 0. The advertisements assume that the duration \
        of the activity is the mean duration.

        :param person.Person p: the person of interest

        :return score: the advertised score of doing the eat dinner activity
        :rtype: float
        """

        score = 0.0

        # find the meal that is advertised. The meal that is to be eaten next. Depends on the time
        the_meal = p.socio.get_current_meal(p.clock.time_of_day)

        if (the_meal is not None) and (the_meal.id == meal.DINNER) and (p.location.local == location.HOME):
           score = self.advertise_help(p, the_meal.dt)

        return score

    def end_meal(self, p):

        """
        This function goes through the logistics of ending the dinner meal by doing the following:
        
        #. calls :func:`end.end_meal`
        #. if breakfast will be skipped, update the lunch event to be 2 days from the current day
        
        :param person.Person p: the person who is finishing the eating dinner event 
        :return:  None
        """
        super(Eat_Dinner, self).end_meal(p)

        # if a NEW meal will be skipped
        # say it's day 1 and the agent has finished dinner
        # the agent plans on skipping breakfast (on day 2) for whatever reason and eating lunch instead (day 2)
        # That means the next breakfast event needs to be on day 3
        if p.socio.current_meal.id == meal.LUNCH:
            p.socio.meals[meal.BREAKFAST].update(p.clock.day + 2)

        return

    def start_meal(self, p):

        """
        This function goes through the logistics of starting the dinner meal by doing the following:
        
        #. set the current meal to dinner
        #. call :func:`eat.start_meal`
        
        :param person.Person p: the person who is starting the eat dinner event
        :return: None
        """

        p.socio.meals[meal.DINNER].day  = p.clock.day
        p.socio.current_meal            = p.socio.get_meal(meal.DINNER)

        super(Eat_Dinner, self).start_meal(p)

        return