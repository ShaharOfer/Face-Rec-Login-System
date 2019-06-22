from __future__ import division
from PIL import Image
import cv2
import math
import base64
import sys

FACE_CASCADE = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
EYE_CASCADE = cv2.CascadeClassifier("haarcascade_eye.xml")

CURRENT = "checking.jpg"
CROPPED = "cropped.jpg"
EYE = "eye.jpg"
SIZE = (128, 128)


class Recognizer(object):
    def string_to_defult(self, image_string):
        """
        Receiving image string and converting it to an image
        :param image_string: string("'" -> "[", "/" -> "]")
        :return: None, Save the image in checking.jpg
        """
        copy = image_string
        with open(CURRENT, 'wb') as file:
            copy = copy.replace("[", "'")
            copy = copy.replace("]", "/")
            file.write(base64.b64decode(copy.encode()))

    def validity_check(self, image_string):
        """
        Checking if image has only ONE face and TWO eyes
        :param image_string: string("'" -> "[", "/" -> "]")
        :return: boolean value
        """
        self.string_to_defult(image_string)
        img = cv2.imread(CURRENT)
        # r = 500.0 / img.shape[1]
        # dim = (500, int(img.shape[0] * r))
        # resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)
        if len(faces) != 1:
            return False
        for (x, y, w, h) in faces:
            # cv2.rectangle(resized, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            eyes = EYE_CASCADE.detectMultiScale(roi_gray)

            if len(eyes) != 2:
                return False
        return True

    def get_data(self, image_string):
        """
        The main function of the class to get data from an image
        :param image_string: string("'" -> "[", "/" -> "]")
        :return: two parameters: 1. the distance between the eyes. 2. The average color of the face
        """
        self.string_to_defult(image_string)
        eyes_distance = self.get_eyes_distance()
        average_color = self.get_average_color()
        return eyes_distance, average_color

    """"""
    """Calculating Distance Area"""
    """"""

    def calculate_distance(self, point1, point2):
        """
        Calculating the distance of two points
        :param point1: list -> [x, y]
        :param point2: list -> [x, y]
        :return: float, the distance between the points
        """
        return math.sqrt(pow(point1[0] - point2[0], 2) + pow(point1[1] - point2[1], 2))

    def calculate_middle(self, eyes, roi):
        """Calculating the center of the eyes"""
        eye1 = eyes[0]
        middle_x_eye1 = (2 * eye1[0] + eye1[2]) / 2
        middle_y_eye1 = (2 * eye1[1] + eye1[3]) / 2
        eye2 = eyes[1]
        middle_x_eye2 = (2 * eye2[0] + eye2[2]) / 2
        middle_y_eye2 = (2 * eye2[1] + eye2[3]) / 2
        """
        #Drawing dots on eyes and creating a line between them
        cv2.circle(roi, (int(middle_x_eye1), int(middle_y_eye1)), 5, (0, 0, 255), -1)
        cv2.circle(roi, (int(middle_x_eye2), int(middle_y_eye2)), 5, (0, 0, 255), -1)
        cv2.line(roi, (int(middle_x_eye1), int(middle_y_eye1)), (int(middle_x_eye2), int(middle_y_eye2)), (0, 0, 0), 2)
        """
        return self.calculate_distance((middle_x_eye1, middle_y_eye1), (middle_x_eye2, middle_y_eye2)) / ((eye1[2] *
                                                                                                           eye1[3] +
                                                                                                           eye2[2] *
                                                                                                           eye2[3]) / 2)

    def get_eyes_distance(self):
        """
        The main function of the eyes distance calculation.
        Recognizing the eyes and calculating the distance between them
        :return: float, the eyes distance.
        """
        img = cv2.imread(CURRENT)
        # r = 500.0 / img.shape[1]
        # dim = (500, int(img.shape[0] * r))
        # resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            # cv2.rectangle(resized, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]
            cv2.imwrite(CROPPED, roi_color)
            eyes = EYE_CASCADE.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
            return self.calculate_middle(eyes, roi_color)

    """"""
    """Calculating Average Color Area"""
    """"""

    def get_average_color(self):
        """
        The main function of the face's average color calculation.
        Finding the average color of the face
        :return: float, the average color in the face.
        """
        self.resize()
        im = Image.open(CROPPED)
        gray_im = self.rgb2gray(im)
        normal_rgb_avg = self.get_avg(self.get_rgb_list(im))
        gray_rgb_avg = self.get_avg(self.get_rgb_list(gray_im))
        divided = float(normal_rgb_avg / gray_rgb_avg)
        return divided

    def get_rgb_list(self, im):
        """
        Converting image into a RGB list
        :param im: An Image image.
        :return: List, (int, int, int). The RGB values in the image
        """
        pixels = list(im.getdata())
        return [pixels[i * im.size[0]:(i + 1) * im.size[0]] for i in range(im.size[1])][0]

    def get_avg(self, list_pixels):
        """
        Finding the average color in the list.
        :param list_pixels: List of RGB values -> (int, int, int)
        :return: The average color -> float
        """
        counter = 0
        sum = 0
        for rgb in list_pixels:
            sum += (rgb[0] + rgb[1] + rgb[2]) / 3
            counter += 1
        return sum / counter

    def rgb2gray(self, im):
        """
        Converting a colored image to gray image.
        :param im: Colored Image image
        :return: Grayed image.
        """
        matrix = (0.2, 0.5, 0.3, 0.0, 0.2, 0.5, 0.3, 0.0, 0.2, 0.5, 0.3, 0.0)
        return im.convert('RGB', matrix)

    def resize(self):
        """
        Resizing the image to even size
        :return: None, Saving the cropped image to cropped.jpg
        """
        im = Image.open(CROPPED)
        im.thumbnail((SIZE[0], SIZE[1]), Image.ANTIALIAS)
        im.save(CROPPED, "JPEG")
