"""
This module redefines the abstract classes to fit the needs of visual processing.
"""

from retico_core import abstract
import numpy as np
from PIL import Image

class ImageIU(abstract.IncrementalUnit):
    """An image incremental unit that receives raw image data from a source.

    Attributes:
        creator (AbstractModule): The module that created this IU
        previous_iu (IncrementalUnit): A link to the IU created before the
            current one.
        grounded_in (IncrementalUnit): A link to the IU this IU is based on.
        created_at (float): The UNIX timestamp of the moment the IU is created.
        image (bytes[]): The image of this IU
        rate (int): The frame rate of this IU
        nframes (int): The number of frames of this IU
    """

    @staticmethod
    def type():
        return "Image IU"

    def __init__(self, creator=None, iuid=0, previous_iu=None, grounded_in=None,
                 rate=None, nframes=None, image=None,
                 **kwargs):
        super().__init__(creator=creator, iuid=iuid, previous_iu=previous_iu,
                         grounded_in=grounded_in, payload=image)
        self.image = image
        self.rate = rate
        self.nframes = nframes

    def set_image(self, image, nframes, rate):
        """Sets the audio content of the IU."""
        self.image = image
        self.payload = image
        self.nframes = int(nframes)
        self.rate = int(rate)

    def get_json(self):
        payload = {}
        payload['image'] = np.array(self.payload).tolist()
        payload['nframes'] = self.nframes
        payload['rate'] = self.rate
        return payload

    def create_from_json(self, json_dict):
        self.image =  Image.fromarray(np.array(json_dict['image'], dtype='uint8'))
        self.payload = self.image
        self.nframes = json_dict['nframes']
        self.rate = json_dict['rate']

class PosePositionsIU(abstract.IncrementalUnit):
    """An image incremental unit that maintains a list of pose_landmarks (points on body) and segmentation_mask (pixel values where 1 represents human pixel and 0 represents background pixel)).

    Attributes:
        creator (AbstractModule): The module that created this IU
        previous_iu (IncrementalUnit): A link to the IU created before the
            current one.
        grounded_in (IncrementalUnit): A link to the IU this IU is based on.
        created_at (float): The UNIX timestamp of the moment the IU is created.
    """
    @staticmethod
    def type():
        return "Pose Positions IU"

    def __init__(self, creator=None, iuid=0, previous_iu=None, grounded_in=None,
                    rate=None, nframes=None, sample_width=None, raw_audio=None,
                    **kwargs):
        super().__init__(creator=creator, iuid=iuid, previous_iu=previous_iu,
                            grounded_in=grounded_in, payload=None)
        self.pose_landmarks = None
        self.segmentation_mask = None
        self.image = None

    def set_landmarks(self, image, pose_landmarks, segmentation_mask):
        "Sets landmark content of the IU"
        self.image = image
        self.payload = pose_landmarks
        self.segmentation_mask = segmentation_mask

    def get_json(self):
        payload = {}
        payload['image'] = np.array(self.payload).tolist()
        payload['pose_landmarks'] = self.pose_landmarks
        payload['segmentation_mask'] = self.segmentation_mask
        return payload

    def create_from_json(self, json_dict):
        self.image =  Image.fromarray(np.array(json_dict['image'], dtype='uint8'))
        self.pose_landmarks = json_dict['pose_landmarks']
        self.payload = self.pose_landmarks
        self.segmentation_mask = json_dict['segmentation_mask']


class DetectedObjectsIU(abstract.IncrementalUnit):
    """An image incremental unit that maintains a list of detected objects and their bounding boxes.

    Attributes:
        creator (AbstractModule): The module that created this IU
        previous_iu (IncrementalUnit): A link to the IU created before the
            current one.
        grounded_in (IncrementalUnit): A link to the IU this IU is based on.
        created_at (float): The UNIX timestamp of the moment the IU is created.
    """

    @staticmethod
    def type():
        return "Detected Objects IU"

    def __init__(self, creator=None, iuid=0, previous_iu=None, grounded_in=None,
                 rate=None, nframes=None, sample_width=None, raw_audio=None,
                 **kwargs):
        super().__init__(creator=creator, iuid=iuid, previous_iu=previous_iu,
                         grounded_in=grounded_in, payload=None)
        self.detected_objects = None
        self.num_objects = 0
        self.image = None

    def set_detected_objects(self, image, detected_objects):
        """Sets the audio content of the IU."""
        self.image = image
        self.payload = detected_objects
        self.detected_objects = detected_objects
        self.num_objects = detected_objects['num_objs']

    def get_json(self):
        payload = {}
        payload['image'] = np.array(self.payload).tolist()
        payload['detected_objects'] = self.detected_objects
        payload['num_objects'] = self.num_objects
        return payload

    def create_from_json(self, json_dict):
        self.image =  Image.fromarray(np.array(json_dict['image'], dtype='uint8'))
        self.detected_objects = json_dict['detected_objects']
        self.payload = self.detected_objects
        self.num_objects = json_dict['num_objects']

class ObjectFeaturesIU(abstract.IncrementalUnit):
    """An image incremental unit that maintains a list of feature vectors for detected objects in a scene.

    Attributes:
        creator (AbstractModule): The module that created this IU
        previous_iu (IncrementalUnit): A link to the IU created before the
            current one.
        grounded_in (IncrementalUnit): A link to the IU this IU is based on.
        created_at (float): The UNIX timestamp of the moment the IU is created.
    """

    @staticmethod
    def type():
        return "Object Features IU"

    def __init__(self, creator=None, iuid=0, previous_iu=None, grounded_in=None,
                 rate=None, nframes=None, sample_width=None, raw_audio=None,
                 **kwargs):
        super().__init__(creator=creator, iuid=iuid, previous_iu=previous_iu,
                         grounded_in=grounded_in, payload=None)
        self.object_features = None
        self.num_objects = 0
        self.image = None

    def set_object_features(self, image, object_features):
        """Sets the audio content of the IU."""
        self.image = image
        self.payload = object_features
        self.object_features = object_features
        self.num_objects = len(object_features)

    def get_json(self):
        payload = {}
        payload['image'] = np.array(self.payload).tolist()
        payload['object_features'] = self.object_features
        payload['num_objects'] = self.num_objects
        return payload

    def create_from_json(self, json_dict):
        self.image =  Image.fromarray(np.array(json_dict['image'], dtype='uint8'))
        self.object_features = json_dict['object_features']
        self.payload = self.detected_objects
        self.num_objects = json_dict['num_objects']


class HandPositionsIU(ObjectFeaturesIU):
    """An image incremental unit that maintains a list of multi_hand_landmarks (points on hand) and multi_handedness (whether each hand is left or gith).

    Attributes:
        creator (AbstractModule): The module that created this IU
        previous_iu (IncrementalUnit): A link to the IU created before the
            current one.
        grounded_in (IncrementalUnit): A link to the IU this IU is based on.
        created_at (float): The UNIX timestamp of the moment the IU is created.
    """
    @staticmethod
    def type():
        return "Hand Positions IU"
    
    def __init__(self, creator=None, iuid=0, previous_iu=None, grounded_in=None,
                 rate=None, nframes=None, sample_width=None, raw_audio=None,
                 **kwargs):
        super().__init__(creator=creator, iuid=iuid, previous_iu=previous_iu,
                         grounded_in=grounded_in, payload=None)
        self.multi_hand_landmarks = None
        self.multi_handedness = None
        self.image = None

    def set_landmarks(self, image, multi_hand_landmarks, multi_handedness):
        "Sets landmark content of the IU"
        self.image = image
        self.payload = multi_hand_landmarks
        self.multi_handedness = multi_handedness

    def payload_to_vector(self, count):
        if self.payload is None: return
        tempPayload = self.payload
        self.payload = {}
        # print(self.payload[0])
        for hand_index, hand_landmarks in enumerate(tempPayload):
            # Iterate over the detected landmarks of the hand.
            vector = []
            for landmark in hand_landmarks.landmark:
                vector.append(landmark.x)
                vector.append(landmark.y)
                vector.append(landmark.z)
            if hand_index == 0:
                self.payload['hand' + str(hand_index)] = np.array(vector)
            # print(len(vector))

            # print("vector: ", self.payload)
        # vector = []
        # if self.payload is None: return
        # print("size ", len(self.payload))
        # for landmark in self.payload[0]:
        #     print(type(landmark))
        #     print(landmark)
        #     vector.append(landmark.x)
        #     vector.append(landmark.y)
        #     vector.append(landmark.z)
        #     print(self.payload)
        # self.payload = np.array(self.payload)


    def get_json(self):
        payload = {}
        payload['image'] = np.array(self.payload).tolist()
        payload['multi_hand_landmarks'] = self.multi_hand_landmarks
        payload['multi_handedness'] = self.multi_handedness
        return payload

    def create_from_json(self, json_dict):
        self.image =  Image.fromarray(np.array(json_dict['image'], dtype='uint8'))
        self.multi_hand_landmarks = json_dict['multi_hand_landmarks']
        self.payload = self.multi_hand_landmarks
        self.multi_handedness = json_dict['multi_handedness']

class ImageCropperModule(abstract.AbstractModule):
    """A module that crops images"""

    @staticmethod
    def name():
        return "Image Cropper Module"

    @staticmethod
    def description():
        return "A module that crops images"


    @staticmethod
    def input_ius():
        return [ImageIU]

    @staticmethod
    def output_iu():
        return ImageIU

    def __init__(self, top=-1, bottom=-1, left=-1, right=-1, **kwargs):
        """
        Initialize the Webcam Module.
        Args:
            width (int): Width of the image captured by the webcam; will use camera default if unset
            height (int): Height of the image captured by the webcam; will use camera default if unset
            rate (int): The frame rate of the recording; will use camera default if unset
        """
        super().__init__(**kwargs)
        self.top =  top
        self.bottom = bottom
        self.left = left
        self.right = right

    def process_iu(self, input_iu):
        image = input_iu.image
        width, height = image.size
        left = self.left if self.left != -1 else 0
        top = self.top if self.top != -1 else 0
        right = self.right if self.right != -1 else width
        bottom = self.bottom if self.bottom != -1 else height
        image = image.crop((left, top, right, bottom)) 
        output_iu = self.create_iu(input_iu)
        output_iu.set_image(image, input_iu.nframes, input_iu.rate)
        return output_iu