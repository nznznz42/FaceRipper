import logging
import os
import numpy as np
import cv2
import mediapipe as mp
import dlib
from PIL import Image

logger = logging.getLogger(__name__)


class FaceExtractor:
    def __init__(self, image_path: str | None, output_dir: str) -> None:
        """
        :parameter: image_path: Absolute path to an image
        :parameter: output_dir: Absolute path to an output directory
        :exception: InvalidImageError: cv2 exception when image is unable to be read
        """
        self.output_dir = output_dir
        self.image_path = image_path
        try:
            self.image = cv2.imread(image_path)
        except Exception as InvalidImageError:
            logger.error(f"Error reading image: {InvalidImageError}")
            raise InvalidImageError
        if image_path is not None:
            self.image_name = os.path.basename(image_path)
        else:
            pass
        self.segmented_image = None
        self.detected_faces = None

    def extract_humans(self) -> None:
        if self.segmented_image is not None:
            return
        mp_selfie_segmentation = mp.solutions.selfie_segmentation
        try:
            BG_COLOR = (192, 192, 192)  # gray
            MASK_COLOR = (255, 255, 255)  # white
            with mp_selfie_segmentation.SelfieSegmentation(model_selection=0) as selfie_segmentation:
                image_height, image_width, _ = self.image.shape
                results = selfie_segmentation.process(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
                condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
                fg_image = np.zeros(self.image.shape, dtype=np.uint8)
                fg_image[:] = MASK_COLOR
                bg_image = np.zeros(self.image.shape, dtype=np.uint8)
                bg_image[:] = BG_COLOR
                self.segmented_image = np.where(condition, fg_image, bg_image)
                blurred_image = cv2.GaussianBlur(self.image, (55, 55), 0)
                condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
                self.segmented_image = np.where(condition, self.image, blurred_image)
        except Exception as e:
            logger.error(f"Error extracting humans: {e}")
            raise e

    def extract_faces(self) -> None:
        """
        Extracts all faces from the segmented image.
        If no faces are found, the detected_faces property is set to None.
        """
        if self.detected_faces is not None:
            return
        face_detector = dlib.get_frontal_face_detector()
        try:
            detected_faces = face_detector(self.segmented_image, 1)
            face_frames = [(x.left(), x.top(),
                            x.right(), x.bottom()) for x in detected_faces]
            for n, face_rect in enumerate(face_frames):
                faces = Image.fromarray(self.segmented_image).crop(face_rect)
                self.detected_faces = np.array(faces)
        except Exception as e:
            logger.error(f"Error extracting faces: {e}")
            raise e


    def save_face(self) -> None:
        if self.detected_faces is None:
            self.extract_faces()
            output_path = os.path.join(self.output_dir, os.path.splitext(self.image_name)[0] + "_face.png")
            try:
                cv2.imwrite(output_path, self.detected_faces)
            except Exception as e:
                logger.error(f"Error saving the face: {e}")
                raise e
