############## IMPORT MODULES HERE #################
import cv2 as cv
import numpy as np
import os
import shutil
import glob
import random

####################################################

############### GLOBAL VARIABLES ###################
img_lst = []


img = cv.imread('photo.jpg')
#resizing
scale_percent = 50
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dsize = (width, height)
output = cv.resize(img, dsize)
# cv.imshow('resize',output)

#blackandwhite
gray = cv.cvtColor(output,cv.COLOR_BGR2GRAY)
# cv.imshow('gray',gray)

#rgbeffect
rgb = cv.cvtColor(output,cv.COLOR_BGR2RGB)
# cv.imshow('rgb',rgb)
'''
#hsv
hsv = cv.cvtColor(output, cv.COLOR_BGR2HSV)
cv.imshow('HSV', hsv)

#lab
lab = cv.cvtColor(output, cv.COLOR_BGR2LAB)
cv.imshow('LAB', lab)'''

#blur
blur = cv.GaussianBlur(output, (7,7), cv.BORDER_DEFAULT)
# cv.imshow('Blur', blur)

#dilating
dilated = cv.dilate(output, (7,7), iterations=2)
# cv.imshow('Dilated', dilated)

#canny
canny = cv.Canny(output, 125, 175)
# cv.imshow('Canny Edges', canny)

#thresholding
threshold, thresh = cv.threshold(output, 100, 150, cv.THRESH_BINARY )
# cv.imshow('Simple Thresholded', thresh)

#watercolor

gray_1 = cv.medianBlur(gray, 5)
edges = cv.adaptiveThreshold(gray_1, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 9, 5)

bilateral = cv.bilateralFilter(output, d=9, sigmaColor=200,sigmaSpace=200)
#cv.imshow('bil_blur',bilateral)

cartoon = cv.bitwise_and(bilateral, bilateral, mask=edges)
# cv.imshow('cartoon',cartoon)

#pencilsketch

invert = cv.bitwise_not(gray)
#cv.imshow('invert',invert)

smoothing = cv.GaussianBlur(invert, (21, 21),sigmaX=0, sigmaY=0)
##cv.imshow('smoothing',smoothing)

def dodgeV2(x, y):
    return cv.divide(x, 255 - y, scale=256)
pencilsketch = dodgeV2(gray, smoothing)
# cv.imshow('pencilsketch',pencilsketch)

os.mkdir("temp")
cv.imwrite("temp/output.jpg", output)
cv.imwrite("temp/blur.jpg", blur)
cv.imwrite("temp/rgb.jpg", rgb)
cv.imwrite("temp/canny.jpg", canny)
cv.imwrite("temp/thresh.jpg", thresh)
cv.imwrite("temp/gray.jpg", gray)
cv.imwrite("temp/dilated.jpg", dilated)
cv.imwrite("temp/cartoon.jpg", cartoon)
cv.imwrite("temp/pencilsketch.jpg", pencilsketch)

class Image:
    def __init__(self, filename, time=600, size=500):
        self.size = size
        self.time = time
        self.shifted = 0.0
        self.img = cv.imread(filename)
        self.height, self.width, _ = self.img.shape
        if self.width < self.height:
            self.height = int(self.height*size/self.width)
            self.width = size
            self.img = cv.resize(self.img, (self.width, self.height))
            self.shift = self.height - size
            self.shift_height = True
        else:
            self.width = int(self.width*size/self.height)
            self.height = size
            self.shift = self.width - size
            self.img = cv.resize(self.img, (self.width, self.height))
            self.shift_height = False
        self.delta_shift = self.shift/self.time

    def reset(self):
        if random.randint(0, 1) == 0:
            self.shifted = 0.0
            self.delta_shift = abs(self.delta_shift)
        else:
            self.shifted = self.shift
            self.delta_shift = -abs(self.delta_shift)

    def get_frame(self):
        if self.shift_height:
            roi = self.img[int(self.shifted):int(self.shifted) + self.size, :, :]
        else:
            roi = self.img[:, int(self.shifted):int(self.shifted) + self.size, :]
        self.shifted += self.delta_shift
        if self.shifted > self.shift:
            self.shifted = self.shift
        if self.shifted < 0:
            self.shifted = 0
        return roi


def process():
    path = "temp"
    filenames = glob.glob(os.path.join(path, "*"))

    cnt = 0
    images = []
    for filename in filenames:
        print(filename)

        img = Image(filename)

        images.append(img)
        if cnt > 300:
            break
        cnt += 1

    prev_image = images[random.randrange(0, len(images))]
    prev_image.reset()

    while True:
        while True:
            img = images[random.randrange(0, len(images))]
            if img != prev_image:
                break
        img.reset()

        for i in range(100):
            alpha = i/100
            beta = 1.0 - alpha
            dst = cv.addWeighted(img.get_frame(), alpha, prev_image.get_frame(), beta, 0.0)

            cv.imshow("Slide", dst)
            img_lst.append(dst)
            if cv.waitKey(1) == ord('q'):
                return

        prev_image = img
        for _ in range(300):
            cv.imshow("Slide", img.get_frame())
            img_lst.append(img.get_frame())
            if cv.waitKey(2) == ord('q'):
                return



process()
shutil.rmtree("temp", ignore_errors=False, onerror=None)
