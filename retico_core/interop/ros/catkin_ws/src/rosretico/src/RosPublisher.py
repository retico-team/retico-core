#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from retico.core import abstract
import rospy
import datetime
import json

class RosPublisher(abstract.AbstractModule):
    """A ROS Publishing Node

    Attributes:
    topic (str): topic/scope that this publishes to
        
    """
    @staticmethod
    def name():
        return "ROS publisher node"

    @staticmethod
    def description():
        return "A Node providing publishing to a Ros topic"

    @staticmethod
    def output_iu():
        return abstract.IncrementalUnit

    @staticmethod
    def input_ius():
        return [abstract.IncrementalUnit] 

    def __init__(self, topic, debug = False, message_type = String,**kwargs):
        """Initializes the Ros publisher.

        Args: topic(str): the topic/scope where the information will be published to.
            
        """
        super().__init__(**kwargs)
        self.debug = debug

        self.publisher = rospy.Publisher(str(topic), message_type, queue_size=10)

        if(self.debug):
            rospy.loginfo('Created publisher on topic ' + str(topic))

    def process_iu(self, input_iu):
        self.publisher.publish(str(input_iu.payload))
        if(self.debug):
            rospy.loginfo('publishing data: ' + str(input_iu.payload))

    def setup(self):
        pass