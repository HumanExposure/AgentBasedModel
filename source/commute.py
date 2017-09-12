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
This module contains about activities associated with commuting to and from work. This class is an \
:class:`activity.Activity` that gives a :class:`person.Person` the ability to commute to/ from work/ \
school and satisfy the need Travel :class:`travel.Travel`.

This module contains the following classes:

#. :class:`commute.Commute` (general commuting capability)
#. :class:`commute.Commute_To_Work` (commute to work/ school)
#. :class:`commute.Commute_From_Work` (commute from work/ school)

.. moduleauthor:: Dr. Namdi Brandon
"""

# ===============================================
# import
# ===============================================

# agent-based model modules
import activity, income, location, need, state, temporal

# ===============================================
# class commute
# ===============================================


class Commute(activity.Activity):

    """
    This class allows for commuting. This class is to be derived from.
    """

    #
    # constructor
    #
    def __init__(self):

        activity.Activity.__init__(self)

        self.id = None
        
        return

    def end(self,p, local):

        """
        This function handles the end of an Activity.

        :param person.Person p: the person of interest
        :param int local: the local location (work or home)

        :return: None
        """

        # end the commute activity
        self.end_commute(p)

        # do some logistics
        super(Commute, self).end(p)

        return    

    def end_commute(self, p):

        """
        This function ends the commuting activity.
        
        .. note::
            This function is to be overridden

        :param person.Person p: the person of interest 
        :return: None
        """

        return

    def start(self, p):

        """
        This handles the start of the commute activity.

        * If the current location of person is at home, the person is going to work, so set the \
        location to :const:`location.OFF_SITE`

        * If the current location of the person is off site, the person is going back home, so \
        set the location to :const:`location.HOME`

        :param person.Person p: the person of interest

        :return: None
        """

        # store the end location of the commute
        if (p.location.local == location.HOME):
            end_loc = location.OFF_SITE
            
        elif (p.location.local == location.OFF_SITE):
            end_loc = location.HOME
            
        # start the commute, itself
        self.start_commute(p)
        
        # store a list of the arguments for the end() procedure
        p.state.arg_end.append(p)
        p.state.arg_end.append(end_loc)
                
        return

    def start_commute(self, p):

        """
        This function sets the variables pertaining to starting the commute activity.


        #. set the status of the person to :const:`location.TRANSIT`
        #. set the location of the asset to :const:`location.TRANSIT`
        #. set the person's state start time of the commute         
        #. set the person's state end time for the commute
        #. update the asset
        #. update the scheduler for the travel need for the end of the commute
        
        :param person.Person p: the person of interest
        :return: None
        """

        local = p.location.local

        # no updates in start functions()
        if (local == location.HOME):
            #p.socio.job.update_commute_to_work_dt()
            dt = p.socio.job.commute_to_work_dt

        elif (local == location.OFF_SITE):
            #p.socio.job.update_commute_from_work_dt()
            dt = p.socio.job.commute_from_work_dt

        # update the state of the Person 
        p.state.status = state.TRANSIT
        
        # set the location of the Person to be in transit
        p.location.local = location.TRANSIT

        # set the start time of the current state
        p.state.t_start = p.clock.t_univ

        # calculate the end time of commuting
        p.state.t_end = p.state.t_start + dt

        # update the asset
        p.state.asset.update()

        # update scheduler
        p.schedule.update(p.id, need.TRAVEL, dt)

        return

# ===============================================
# class Commute_From_Work
# ===============================================

class Commute_From_Work(Commute):

    """
    This class allows for the activity: commuting from work.
    """

    #
    # constructor
    #
    def __init__(self):

        Commute.__init__(self)

        self.id = activity.COMMUTE_FROM_WORK

        return

    def advertise(self, p):

        """
        This function calculates the score of an activities advertisement \
        advertise the score to commute.

        #. calculate advertisement only if the person is located at work (off-site)
        #. calculate the score
        
            .. math::     
                S = \\begin{cases}
                0  & n_{travel}(t) > \\lambda \\\\
                W( n_{travel}(t) ) - W( n_{travel}(t + \\Delta{t} )) & n_{travel}(t) \\le \\lambda
                \\end{cases}
            
        :param person.Person p: the person of interest

        :return: the advertised score
        :rtype: float
        """

        # this is the lowest score
        score = 0.0

        # seek a non zero advertisement if the person's location is off site (at work)
        if (p.location.local == location.OFF_SITE):

            # the end of the commute to work sequence is:
            # the current time + the time to commute to work + the time at work
            t_day           = p.clock.day * temporal.DAY_2_MIN

            # the duration of the commute
            dt_commute      = p.socio.job.commute_from_work_dt

            # store the time in universal time
            t_univ_later    = t_day + p.socio.job.t_end + dt_commute

            # create a clock for the Need perception due the Activity when it's finished
            future_clock = temporal.Temporal(t_univ_later)

            # the current need level and the resulting need level if an Activity is done
            n_now = p.travel.magnitude

            # if the Travel need association is under a threshold, do something
            if (p.travel.under_threshold(n_now)):
                # calculate the magnitude of the need association assuming the commute activity has finished
                n_later = p.travel.perceive(future_clock, p.socio.job)

                # update the value of the advertisement
                score = score + (p.travel.weight(n_now) - p.travel.weight(n_later))

        return score

    def calc_end_time(self, p):

        """
        #. calculate the end time (minutes, universal time) of the commute
        #. set the the end time in the person's state

        :param person.Person p: the person of interest

        :return: None
        """

        # the start of the day (universal time)
        dt              = p.socio.job.commute_from_work_dt
        p.state.t_end   = p.clock.t_univ + dt

        return

    def end(self, p):

        """
        This function handles the end of an Activity.

        :param person.Person p: the person of interest
        :return: None
        """

        # end the commute activity
        self.end_commute(p)

        # do some logistics
        super(Commute, self).end(p)

        return

    def end_commute(self, p):

        """
        This function sets the variables pertaining to ending the commute activity.

        #. Sets the person's state to idle(:const:`state.IDLE`)
        #. Updates the asset's state and number of users
        #. Sets the travel magnitude
        #. Sets the work magnitude to :const:`need.MAG_WORK`, to allow for work \
        to be the next activity, even if commute ends begin the work-start time
        #. Sets the person's state's end time

        :param person.Person p: person of interest
        :param int destination: a local location where the commute ends (home or workplace)

        :return: None
        """

        # free the asset
        p.state.asset.free()

        # update the travel need
        p.travel.magnitude = 1.0

        # update the person's status
        p.state.status = state.IDLE

        # change the location of the Person and the asset
        p.location.local                = location.HOME
        p.state.asset.location.local    = p.location.local

        # change the status of the person
        # if the commute ends at home

        # update the commute from work duration
        p.socio.job.update_commute_from_work_dt()

        # the time until the next commute event
        dt = p.socio.duration_to_work_event(p.clock) - p.socio.job.commute_to_work_dt

        # update the schedule
        p.schedule.update(p.id, need.TRAVEL, dt)

        return

    def start(self, p):

        """
        This handles the start of the commute activity.

        If the current location of person is at home, the person is going to work, so set the \
        location to :const:`location.OFF_SITE`

        If the current location of the person is off site, the person is going back home, so \
        set the location to :const:`location.HOME`

        :param person.Person p: the person of interest

        :return: None
        """

        # start the commute, itself
        self.start_commute(p)

        # store a list of the arguments for the end() procedure
        p.state.arg_end.append(p)

        return

# ===============================================
# class Commute_To_Work
# ===============================================

class Commute_To_Work(Commute):

    """
     This class allows for the activity: commute to work
    """

    #
    # constructor
    #
    def __init__(self):

        Commute.__init__(self)

        self.id = activity.COMMUTE_TO_WORK

        return

    def advertise(self, p):
        """
        This function calculates the score of an activities advertisement \
        advertise the score to commute.

        #. calculate advertisement only if the person is located at work (off-site)
        #. calculate the score
        
            .. math::     
                S = \\begin{cases}
                0  & n_{travel}(t) > \\lambda \\\\
                W( n_{travel}(t) ) - W( n_{travel}(t + \\Delta{t} )) & n_{travel}(t) \\le \\lambda
                \\end{cases}
                
        :param person.Person p: the person of interest

        :return score: the advertisement score
        :rtype: float
        """

        DAY_2_MIN = temporal.DAY_2_MIN

        # this is the lowest score
        score = 0.0

        if (p.location.local == location.HOME):

            # the end of the commute to work sequence is:
            # the time that the travel need should increase to 1 if ignored
            # the current time + the time to commute to work + the time at work
            t_univ_later    = p.clock.t_univ + (p.socio.job.t_end - p.clock.time_of_day) % DAY_2_MIN

            # create a clock for the Need perception due the Activity when it's finished
            future_clock    = temporal.Temporal(t_univ_later)

            # the current need level and the resulting need level if an Activity is done
            n_now = p.travel.magnitude

            # if the Travel need association is under a threshold, do something
            if (p.travel.under_threshold(n_now)):
                # calculate the magnitude of the need association assuming the commute activity has finished
                n_later = p.travel.perceive(future_clock, p.socio.job)

                # update the value of the advertisement
                score = score + (p.travel.weight(n_now) - p.travel.weight(n_later))

        return score

    def calc_end_time(self, p):

        """
        Given the commute duration, store the end time.
        
        #. calculate the end time [universal time] of the commute.
        #. store the end time in the person.state 


        :param person.Person p: the person of interest
        :return: None
        """

        dt              = p.socio.job.commute_to_work_dt
        p.state.t_end   = p.clock.t_univ + dt

        return

    def end_commute(self, p):

        """
        This function handles the logistics concerning ending the commute.
        
        #. the asset is freed up from use
        #. the magnitude of the travel need is set :math:`n_{travel}=1`
        #. the person's state is set to idle (:const:`state.IDLE`)
        #. the person's location is set to the location of the job
        #. the asset's location is set to the location of the job
        #. the person's income need is set to :math:`n_{income}=\\eta_{work}`
        #. update the commute to work duration
        #. calculate the time until the next leave work event
        #. update the schedule for the travel need
        
        :param person.Person p: the person of interest 
        :return: 
        """

        DAY_2_MIN = temporal.DAY_2_MIN

        # free the asset
        p.state.asset.free()

        # update the travel need
        p.travel.magnitude = 1.0

        # update the person's status
        p.state.status = state.IDLE

        # change the location of the Person and the asset
        p.location.local                = p.socio.job.location.local
        p.state.asset.location.local    = p.location.local

        # update income
        p.income.magnitude = need.MAG_WORK

        # update the commute to work duration
        p.socio.job.update_commute_to_work_dt()

        # update travel
        # time until the next leave work event
        dt = (p.socio.job.t_end - p.clock.time_of_day + DAY_2_MIN) % DAY_2_MIN

        # update the schedule
        p.schedule.update(p.id, need.TRAVEL, dt)

        return

    def end(self, p):

        """
        This function handles the logistics of ending the commute to work activity.

        :param person.Person p: the person of interest
        :return: None
        """

        # end the commute activity
        self.end_commute(p)

        # do some logistics
        super(Commute, self).end(p)

        return

    def start(self, p):

        """
        This function handles the start of the commute to work activity. If the current location of person is \
        at home, the person is going to work, so set the location to workplace location (:const:`location.OFF_SITE`)

        
        :param person.Person p: the person of interest
        :return: None
        """

        # start the commute, itself
        self.start_commute(p)

        # store a list of the arguments for the end() procedure
        p.state.arg_end.append(p)

        return

    def start_commute(self, p):

        """
        This function sets the variables pertaining to starting the commute to work activity.
        
        #. set the person's status to :const:`state.TRANSIT`
        #. set the asset's location to :const:`location.TRANSIT`
        #. set the person's state start time to the current time
        #. calculate the end time of commute to work
        #. update the asset's update
        #. update the scheduler for the travel need to take into account the end of the commute
        #. update the scheduler for the income need to take into account the end of the commute

        :param person.Person p: the person of interest

        :return: None
        """

        # the commute to work duration is used by other activities
        dt = p.socio.job.commute_to_work_dt

        # update the state of the Person
        p.state.status = state.TRANSIT

        # set the location of the Person to be in transit
        p.location.local = location.TRANSIT

        # set the start time of the current state
        p.state.t_start = p.clock.t_univ

        # calculate the end time of commuting
        p.state.t_end = p.state.t_start + dt

        # update the asset
        p.state.asset.update()

        # update scheduler for travel AND income
        p.schedule.update(p.id, need.TRAVEL, dt)
        p.schedule.update(p.id, need.INCOME, dt)

        return