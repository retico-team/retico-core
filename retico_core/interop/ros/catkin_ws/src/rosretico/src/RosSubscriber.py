#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from retico.core import abstract
import rospy
import datetime
import json

class RosSubscriber(abstract.AbstractProducingModule):
    """A ROS subscriber Node

    Attributes:
    topic (str): topic/scope that this writes to
        
    """
    @staticmethod
    def name():
        return "ROS Subscriber node"

    @staticmethod
    def description():
        return "A Node providing reading from a Ros topic"

    @staticmethod
    def output_iu():
        return abstract.IncrementalUnit

    @staticmethod
    def input_ius():
        return [] 

    def __init__(self, topic, debug = False,**kwargs):
        """Initializes the Ros subscriber.

        Args: topic(str): the topic/scope where the information will be read from.
            
        """
        super().__init__(**kwargs)
        self.debug = debug
        self.subscriber = rospy.Subscriber(str(topic), String, self.callback)
        if(self.debug):
            rospy.loginfo('subscribing to topic: ' + str(topic))

    def process_iu(self, input_iu):
        pass

    def callback(self, data):
        if(self.debug):
            rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)

        output_iu = self.create_iu()
        self.payload = data.data
        return output_iu

    def setup(self):
        pass