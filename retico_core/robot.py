"""
This module redefines the abstract classes to fit the needs of internal robot state processing.
"""

import retico_core


class RobotStateIU(retico_core.abstract.IncrementalUnit):
    """An image incremental unit that receives raw image data from a source.

    Attributes:
        creator (AbstractModule): The module that created this IU
        previous_iu (IncrementalUnit): A link to the IU created before the
            current one.
        grounded_in (IncrementalUnit): A link to the IU this IU is based on.
        created_at (float): The UNIX timestamp of the moment the IU is created.
        state (dict): The state of the robot
    """

    @staticmethod
    def type():
        return "Robot State IU"

    def __init__(
        self,
        creator=None,
        iuid=0,
        previous_iu=None,
        grounded_in=None,
        state=None,
        **kwargs
    ):
        super().__init__(
            creator=creator,
            iuid=iuid,
            previous_iu=previous_iu,
            grounded_in=grounded_in,
            payload=state,
        )
        self.state = state

    def set_state(self, state):
        """Sets the state of the robot"""
        self.state = state
        self.payload = state
