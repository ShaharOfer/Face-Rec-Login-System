from __future__ import division
from PIL import Image
import cv2
import math

FACE_CASCADE = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
EYE_CASCADE = cv2.CascadeClassifier("haarcascade_eye.xml")

CURRENT = "checking.jpg"
CROPPED = "cropped.jpg"
EYE = "eye.jpg"
SIZE = (128, 128)


class Recognizer(object):
    def string_to_defult(self, image_string):
        """Putting string data into default image"""
        with open(CURRENT, 'w') as file:
            file.write(image_string)

    def validity_check(self, image_string):
        """Checking if image has 1 face and 2 eyes"""
        self.string_to_defult(image_string)
        img = cv2.imread(CURRENT)
        r = 500.0 / img.shape[1]
        dim = (500, int(img.shape[0] * r))
        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)
        if len(faces) != 1:
            return False
        for (x, y, w, h) in faces:
            # cv2.rectangle(resized, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            eyes = EYE_CASCADE.detectMultiScale(roi_gray)

            if len(eyes) != 2:
                return False

    def get_data(self, image_string):
        """Calculating and returning the data"""
        self.string_to_defult(image_string)
        eyes_distance = self.get_eyes_distance()
        average_color = self.get_average_color()
        return eyes_distance, average_color

    """"""
    """Calculating Distance Area"""
    """"""

    def calculate_distance(self, point1, point2):
        """Calculating distance between two points"""
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
        """Recognizing the eyes and calculating the distance between them"""
        img = cv2.imread(CURRENT)
        r = 500.0 / img.shape[1]
        dim = (500, int(img.shape[0] * r))
        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            # cv2.rectangle(resized, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = resized[y:y + h, x:x + w]
            cv2.imwrite(CROPPED, roi_color)
            eyes = EYE_CASCADE.detectMultiScale(roi_gray)
            # for (ex, ey, ew, eh) in eyes:
            # cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
            return self.calculate_middle(eyes, roi_color)

    """"""
    """Calculating Average Color Area"""
    """"""

    def get_average_color(self):
        """Finding the average color of the face (Another authentication)"""
        self.resize()
        im = Image.open(CROPPED)
        gray_im = self.rgb2gray(im)
        normal_rgb_avg = self.get_avg(self.get_rgb_list(im))
        gray_rgb_avg = self.get_avg(self.get_rgb_list(gray_im))
        divided = float(normal_rgb_avg / gray_rgb_avg)
        return divided

    def get_rgb_list(self, im):
        """Getting Image image and returning list of RGB"""
        pixels = list(im.getdata())
        return [pixels[i * im.size[0]:(i + 1) * im.size[0]] for i in range(im.size[1])][0]

    def get_avg(self, list_pixels):
        """Finding the average color in the list"""
        counter = 0
        sum = 0
        for rgb in list_pixels:
            sum += (rgb[0] + rgb[1] + rgb[2]) / 3
            counter += 1
        return sum / counter

    def rgb2gray(self, im):
        """Getting Image image and returning it gray"""
        matrix = (0.2, 0.5, 0.3, 0.0, 0.2, 0.5, 0.3, 0.0, 0.2, 0.5, 0.3, 0.0)
        return im.convert('RGB', matrix)

    def resize(self):
        """Resizing the cropped.jpg image"""
        im = Image.open(CROPPED)
        im.thumbnail((SIZE[0], SIZE[1]), Image.ANTIALIAS)
        im.save(CROPPED, "JPEG")
