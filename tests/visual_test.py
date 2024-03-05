import unittest
from retico_core.core import visual
from retico_core.core import UpdateType
from mock_classes import MockImageIU
from mock import patch
from PIL import Image



'''
test format:
def test_X(self):
    #Arrange

        #Act

        #Assert
'''

# Test cases
class TestVisualModule(unittest.TestCase):

    def test_image_iu_type(self):
        #Arrange
        expected_result = "Image IU"

        #Act
        result = visual.ImageIU.type()

        #Assert
        self.assertEqual(result, expected_result)

    def test_image_iu_init(self):
        #Arrange
        mock_image = "test_image"
        mock_rate = 10
        mock_nframes = 5


        #Act
        result = visual.ImageIU(image=mock_image,
                                rate=mock_rate,
                                nframes=mock_nframes
                                )

        #Assert
        self.assertEqual(result.image, mock_image)
        self.assertEqual(result.rate, mock_rate)
        self.assertEqual(result.nframes, mock_nframes)

    def test_image_iu_set_image(self):
        #Arrange
        mock_image_IU = MockImageIU()
        expected_payload_image = "new_image"
        expected_nframes = "8"
        expected_rate = "99"

        #Act
        visual.ImageIU.set_image(mock_image_IU,
                                           image=expected_payload_image,
                                           nframes=expected_nframes,
                                           rate=expected_rate
                                          )

        #Assert
        self.assertEqual(mock_image_IU.image, expected_payload_image)
        self.assertEqual(mock_image_IU.payload, expected_payload_image)
        self.assertEqual(mock_image_IU.nframes, int(expected_nframes))
        self.assertEqual(mock_image_IU.rate, int(expected_rate))

    def test_image_iu_get_json(self):
        #Arrange
        mock_image_IU = MockImageIU()
        expected_result = {'image': mock_image_IU.payload, 'nframes': mock_image_IU.nframes, 'rate': mock_image_IU.rate}
        #Act
        result = visual.ImageIU.get_json(mock_image_IU)

        #Assert
        self.assertEqual(result, expected_result)

    def test_image_iu_create_from_json(self):
        #Arrange
        mock_image_IU = MockImageIU()
        mock_json = {'image': [51, 45, 233], 'nframes': 5, 'rate': 10}
        #Act
        visual.ImageIU.create_from_json(mock_image_IU, mock_json)

        #Assert
        self.assertEqual(type(mock_image_IU.image), Image.Image)
        self.assertEqual(mock_image_IU.image, mock_image_IU.payload)
        self.assertEqual(mock_image_IU.nframes, mock_json['nframes'])
        self.assertEqual(mock_image_IU.rate, mock_json['rate'])

    def test_pose_positions_iu_type(self):
        #Arrange
        expected_result = "Pose Positions IU"

        #Act
        result = visual.PosePositionsIU.type()

        #Assert
        self.assertEqual(result, expected_result)

    def test_pose_positions_iu_init(self):
        #Arrange
        expected_result = None


        #Act
        result = visual.PosePositionsIU()

        #Assert
        self.assertEqual(result.image, expected_result)
        self.assertEqual(result.pose_landmarks, expected_result)
        self.assertEqual(result.segmentation_mask, expected_result)

    def test_pose_positions_iu_set_landmarks(self):
        #Arrange
        mock_pose_IU = MockImageIU()
        mock_image = "test_image"
        mock_pose_landmarks = "test_landmarks"
        mock_segmentation_mask = "test_segment"

        #Act
        visual.PosePositionsIU.set_landmarks(mock_pose_IU,
                                                      image=mock_image,
                                                      pose_landmarks=mock_pose_landmarks,
                                                      segmentation_mask=mock_segmentation_mask)

        #Assert
        self.assertEqual(mock_pose_IU.image, mock_image)
        self.assertEqual(mock_pose_IU.payload, mock_pose_landmarks)
        self.assertEqual(mock_pose_IU.segmentation_mask, mock_segmentation_mask)

    def test_pose_positions_iu_get_json(self):
        #Arrange
        mock_image_IU = MockImageIU()
        mock_image_IU.pose_landmarks = "test_landmark"
        mock_image_IU.segmentation_mask = "test_segmant"
        expected_result = {'image': mock_image_IU.payload,
                            'pose_landmarks': mock_image_IU.pose_landmarks,
                            'segmentation_mask': mock_image_IU.segmentation_mask}
        #Act
        result = visual.PosePositionsIU.get_json(mock_image_IU)

        #Assert
        self.assertEqual(result, expected_result)

    def test_pose_positions_iu_create_from_json(self):
        #Arrange
        mock_image_IU = MockImageIU()
        mock_image_IU.pose_landmarks = "test_landmark"
        mock_image_IU.segmentation_mask = "test_segmant"
        mock_json = {'image': mock_image_IU.payload,
                            'pose_landmarks': mock_image_IU.pose_landmarks,
                            'segmentation_mask': mock_image_IU.segmentation_mask}
        #Act
        visual.PosePositionsIU.create_from_json(mock_image_IU, mock_json)

        #Assert
        self.assertEqual(type(mock_image_IU.image), Image.Image)
        self.assertEqual(mock_image_IU.payload, mock_image_IU.pose_landmarks)
        self.assertEqual(mock_image_IU.pose_landmarks, mock_json['pose_landmarks'])
        self.assertEqual(mock_image_IU.segmentation_mask, mock_json['segmentation_mask'])

    def test_detected_objects_iu_type(self):
        #Arrange
        expected_result = "Detected Objects IU"

        #Act
        result = visual.DetectedObjectsIU.type()

        #Assert
        self.assertEqual(result, expected_result)

    def test_detected_objects_iu_init(self):
        #Arrange
        expected_result = None
        expected_objects = 0


        #Act
        result = visual.DetectedObjectsIU()

        #Assert
        self.assertEqual(result.detected_objects, expected_result)
        self.assertEqual(result.num_objects, expected_objects)
        self.assertEqual(result.image, expected_result)

    def test_detected_objects_iu_set_detected_objects(self):
        #Arrange
        mock_image_IU = MockImageIU()
        mock_image = "test_image"
        mock_objects = {'num_objs': 2, 'types': 'fake'}

        #Act
        visual.DetectedObjectsIU.set_detected_objects(mock_image_IU,
                                                      image=mock_image,
                                                      detected_objects=mock_objects)

        #Assert
        self.assertEqual(mock_image_IU.image, mock_image)
        self.assertEqual(mock_image_IU.payload, mock_objects)
        self.assertEqual(mock_image_IU.detected_objects, mock_image_IU.payload)
        self.assertEqual(mock_image_IU.num_objects, mock_objects['num_objs'])


    def test_detected_objects_iu_get_json(self):
        #Arrange
        mock_image_IU = MockImageIU()
        mock_image_IU.detected_objects = "test_objects"
        mock_image_IU.num_objects = 5
        expected_result = {'image': mock_image_IU.payload,
                            'detected_objects': mock_image_IU.detected_objects,
                            'num_objects': mock_image_IU.num_objects}
        #Act
        result = visual.DetectedObjectsIU.get_json(mock_image_IU)

        #Assert
        self.assertEqual(result, expected_result)

    def test_detected_objects_iu_create_from_json(self):
        #Arrange
        mock_image_IU = MockImageIU()
        mock_image_IU.detected_objects = "test_objects"
        mock_image_IU.num_objects = 5
        mock_json = {'image': mock_image_IU.payload,
                            'detected_objects': mock_image_IU.detected_objects,
                            'num_objects': mock_image_IU.num_objects}
        #Act
        visual.DetectedObjectsIU.create_from_json(mock_image_IU, mock_json)

        #Assert
        self.assertEqual(type(mock_image_IU.image), Image.Image)
        self.assertEqual(mock_image_IU.payload, mock_image_IU.detected_objects)
        self.assertEqual(mock_image_IU.detected_objects, mock_json['detected_objects'])
        self.assertEqual(mock_image_IU.num_objects, mock_json['num_objects'])

    def test_detected_objects_iu_type(self):
        #Arrange
        expected_result = "Object Features IU"

        #Act
        result = visual.ObjectFeaturesIU.type()

        #Assert
        self.assertEqual(result, expected_result)

    def test_object_features_iu_init(self):
        #Arrange
        expected_result = None
        expected_objects = 0


        #Act
        result = visual.ObjectFeaturesIU()

        #Assert
        self.assertEqual(result.object_features, expected_result)
        self.assertEqual(result.num_objects, expected_objects)
        self.assertEqual(result.image, expected_result)

    def test_object_features_iu_set_object_features(self):
        #Arrange
        mock_image_IU = MockImageIU()
        mock_image = "test_image"
        mock_objects = [1,2,43]

        #Act
        visual.ObjectFeaturesIU.set_object_features(mock_image_IU,
                                                      image=mock_image,
                                                      object_features=mock_objects)

        #Assert
        self.assertEqual(mock_image_IU.image, mock_image)
        self.assertEqual(mock_image_IU.payload, mock_objects)
        self.assertEqual(mock_image_IU.object_features, mock_image_IU.payload)
        self.assertEqual(mock_image_IU.num_objects, len(mock_objects))


    def test_object_features_iu_get_json(self):
        #Arrange
        mock_image_IU = MockImageIU()
        mock_image_IU.object_features = "test_objects"
        mock_image_IU.num_objects = 5
        expected_result = {'image': mock_image_IU.payload,
                            'object_features': mock_image_IU.object_features,
                            'num_objects': mock_image_IU.num_objects}
        #Act
        result = visual.ObjectFeaturesIU.get_json(mock_image_IU)

        #Assert
        self.assertEqual(result, expected_result)

    def test_object_features_iu_create_from_json(self):
        #Arrange
        mock_image_IU = MockImageIU()
        mock_image_IU.detected_objects = "test_objects"
        mock_image_IU.num_objects = 5
        mock_json = {'image': mock_image_IU.payload,
                            'object_features': mock_image_IU.detected_objects,
                            'num_objects': mock_image_IU.num_objects}
        #Act
        visual.ObjectFeaturesIU.create_from_json(mock_image_IU, mock_json)

        #Assert
        self.assertEqual(type(mock_image_IU.image), Image.Image)
        self.assertEqual(mock_image_IU.payload, mock_image_IU.detected_objects)
        self.assertEqual(mock_image_IU.object_features, mock_json['object_features'])
        self.assertEqual(mock_image_IU.num_objects, mock_json['num_objects'])

    def test_hand_positions_iu_type(self):
        #Arrange
        expected_result ="Hand Positions IU"

        #Act
        result = visual.HandPositionsIU.type()

        #Assert
        self.assertEqual(result, expected_result)

    def test_hand_positions_iu_init(self):
        #Arrange
        expected_result = None


        #Act
        result = visual.HandPositionsIU()

        #Assert
        self.assertEqual(result.multi_hand_landmarks, expected_result)
        self.assertEqual(result.multi_handedness, expected_result)
        self.assertEqual(result.image, expected_result)

    def test_hand_positions_iu_set_landmarks(self):
        #Arrange
        mock_image_IU = MockImageIU()
        mock_image = "test_image"
        mock_multi_hand_landmarks = "test_landmarks"
        mock_multi_handedness = True

        #Act
        visual.HandPositionsIU.set_landmarks(mock_image_IU,
                                                      image=mock_image,
                                                      multi_hand_landmarks=mock_multi_hand_landmarks,
                                                      multi_handedness=mock_multi_handedness)

        #Assert
        self.assertEqual(mock_image_IU.image, mock_image)
        self.assertEqual(mock_image_IU.payload, mock_multi_hand_landmarks)
        self.assertEqual(mock_image_IU.multi_handedness, mock_multi_handedness)


    def test_hand_positions_iu_get_json(self):
        #Arrange
        mock_image_IU = MockImageIU()
        mock_image_IU.multi_hand_landmarks = "test_hands"
        mock_image_IU.multi_handedness = False
        expected_result = {'image': mock_image_IU.payload,
                            'multi_hand_landmarks': mock_image_IU.multi_hand_landmarks,
                            'multi_handedness': mock_image_IU.multi_handedness}
        #Act
        result = visual.HandPositionsIU.get_json(mock_image_IU)

        #Assert
        self.assertEqual(result, expected_result)

    def test_hand_positions_iu_create_from_json(self):
        #Arrange
        mock_image_IU = MockImageIU()
        mock_image_IU.multi_hand_landmarks = "test_hands"
        mock_image_IU.multi_handedness = False
        mock_json = {'image': mock_image_IU.payload,
                            'multi_hand_landmarks': mock_image_IU.multi_hand_landmarks,
                            'multi_handedness': mock_image_IU.multi_handedness}
        #Act
        visual.HandPositionsIU.create_from_json(mock_image_IU, mock_json)

        #Assert
        self.assertEqual(type(mock_image_IU.image), Image.Image)
        self.assertEqual(mock_image_IU.payload, mock_image_IU.multi_hand_landmarks)
        self.assertEqual(mock_image_IU.multi_hand_landmarks, mock_json['multi_hand_landmarks'])
        self.assertEqual(mock_image_IU.multi_handedness, mock_json['multi_handedness'])

    def test_image_cropper_module_iu_name(self):
        #Arrange
        expected_result ="Image Cropper Module"

        #Act
        result = visual.ImageCropperModule.name()

        #Assert
        self.assertEqual(result, expected_result)

    def test_image_cropper_module_iu_description(self):
        #Arrange
        expected_result ="A module that crops images"

        #Act
        result = visual.ImageCropperModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_image_cropper_module_iu_input_ius(self):
        #Arrange
        expected_result = [visual.ImageIU]

        #Act
        result = visual.ImageCropperModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_image_cropper_module_output_iu(self):
        #Arrange
        expected_result = visual.ImageIU

        #Act
        result = visual.ImageCropperModule.output_iu()

        #Assert
        self.assertEqual(result, expected_result)

    def test_image_cropper_module_output_init(self):
        #Arrange
        mock_top = 4
        mock_bottom = 10
        mock_left = -6
        mock_right = 395

        #Act
        result = visual.ImageCropperModule(top=mock_top,
                                            bottom=mock_bottom,
                                            left=mock_left,
                                            right=mock_right)

        #Assert
        self.assertEqual(result.top, mock_top)
        self.assertEqual(result.bottom, mock_bottom)
        self.assertEqual(result.left, mock_left)
        self.assertEqual(result.right, mock_right)

if __name__ == '__main__':
    unittest.main()