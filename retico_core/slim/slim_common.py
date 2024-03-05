from retico_core.core import abstract

class GroundedFrameIU(abstract.IncrementalUnit):
    """An image incremental unit that receives raw image data from a source.

    Attributes:
        creator (AbstractModule): The module that created this IU
        previous_iu (IncrementalUnit): A link to the IU created before the
            current one.
        grounded_in (IncrementalUnit): A link to the IU this IU is based on.
        created_at (float): The UNIX timestamp of the moment the IU is created.
        frames (dict): key/value pairs of the frame
    """

    @staticmethod
    def type():
        return "Grounded Frame IU"

    def __init__(self, creator=None, iuid=0, previous_iu=None, grounded_in=None,
                 frame=None, **kwargs):
        super().__init__(creator=creator, iuid=iuid, previous_iu=previous_iu,
                         grounded_in=grounded_in, payload=frame)

    def set_frame(self, frame):
        """Sets the frame content of the IU."""
        self.payload = frame