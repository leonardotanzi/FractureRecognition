import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
import collections
from PIL import Image
import kivy
from kivy.app import App
from kivy.uix.label import Label


#KIVY


class MyPaintApp(App):
    def build(self):
        return Label(text = 'Hello world')

MyPaintApp().run()


def find_coeffs(x1, y1, x2, y2):

    # Just to avoid division by zero error
    if x2 - x1 == 0:
        den = 0.1
    else:
        den = x2 - x1

    a = float(y2 - y1) / (den)
    b = y1 - a * x1
    return a, b


def find_maximums(points, thresh):
    over = False
    local_points = {}
    local_max = 0  # our values can't go lower than 0
    cur_idx = 0

    for (k, v) in points.items():
        if over:
            if v > local_max:
                local_max = v
                cur_idx = k
            elif v <= thresh:
                local_points[cur_idx] = local_max
                over = False
                local_max = 0
        else:
            if v > thresh:
                local_max = v
                cur_idx = k
                over = True
    return local_points



if __name__ == '__main__':



    #PARAMETER SETTING
    clean_img = False
    usingAvg = True
    maxLines = 4
    interval = 5
    gaussianWindow = 5
    cannyWindow = 24
    

    broken = '/Users/leonardotanzi/Desktop/Fratture Computer Vision/Jpeg Notevoli/Broken/ok9.jpg'
    clean = '/Users/leonardotanzi/Desktop/Fratture Computer Vision/Jpeg Notevoli/Unbroken/ok5.jpg'
    out = '/Users/leonardotanzi/Desktop/houghlines2.jpg'

    # We need to open the img twice, this is to retrieve the img dimensions
    if clean_img:
        img_h = Image.open(clean)
    else:
        img_h = Image.open(broken)

    width, height = img_h.size
    diagonal = math.sqrt(width ** 2 + height ** 2)

    if clean_img:
        img = cv2.imread(clean)
    else:
        img = cv2.imread(broken)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Blur to remove noise
    blur = cv2.GaussianBlur(gray, (gaussianWindow, gaussianWindow), 0)

    # Find edges first is for clean image, second for unbroken, maxLines parameter must be adapted
    edges = cv2.Canny(blur, cannyWindow, cannyWindow * 3, apertureSize = 3)

    # Erode and dilate with kernel window
    kernel_erode = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    boneEdges = cv2.erode(edges, kernel_erode, iterations = 2)
    boneEdges = cv2.dilate(boneEdges, kernel_dilate, iterations = 2)

    # Plot the result
    plt.imshow(boneEdges)
    plt.show()

    # Find lines with houghlines:
    # second arg is rho accuracy (that is 10 pixels in this case) and third is theta accuracy, fourth is the threshold
    # which means minimum vote it should get for it to be considered as a line.
    lines = cv2.HoughLines(boneEdges, 10, np.pi / 45, 1000)

    '''
    if __debug__:
        print(lines.shape)        # (337, 1, 2)
        print(lines[0].shape)     # (1, 2)
        print(lines[0][0].shape)  # (2,)

        print(lines)        # [[  modulo, angolo in rad ]]
        print(lines[0])     # [[  3.30000000e+02   2.09439516e-01]]
        print(lines[0][0])  # [  3.30000000e+02   2.09439516e-01]
    '''


    # Find the average between the first maxLines angles
    peak = 0
    count = 0
    totangle = 0


    for i in range(maxLines):
        for rho, theta in lines[i]:
            angle = (theta * 180) / math.pi
            if angle > 90: #if angle is for example 175, convert it to -5 in order to compute the correct avg
                angle -= 180
            totangle += angle
            count += 1

    peak = totangle / count

    rightInterval = peak + interval
    leftInterval = peak - interval

    print("Peak is = %f\n" % peak)
    print("Interval is from %f to %f\n" % (leftInterval, rightInterval))

    # Above threshold there are all the lines that must be taken into account
    # first maxLines have a weight in order to distinguish them
    th_occ = {}
    threshold = 10
    weight = 10
    i = 0

    for line in lines:
        for rho, theta in line:
            theta_degs = int(theta * 180 / math.pi)
            if theta_degs in th_occ:
                if i < maxLines:
                    th_occ[theta_degs] += weight
                else:
                    th_occ[theta_degs] += 1
            else:
                if i < maxLines:
                    th_occ[theta_degs] = weight
                else:
                    th_occ[theta_degs] = 1
        i += 1


    ordered_occ = collections.OrderedDict(sorted(th_occ.items())) #order the tuples from 0° to 180°

    maximums = find_maximums(ordered_occ, threshold)  #find local maximum

    '''
    ITEMS(): 
    
    dict = {'Name': 'Zara', 'Age': 7}
    print "Value : %s" % dict.items()
    When we run above program it produces following result:
    Value: [('Age', 7), ('Name', 'Zara')]
    
    ORDEREDDICT():
    
    Ordered dictionaries are just like regular dictionaries but they remember the order that items were inserted.
    When iterating over an ordered dictionary, the items are returned in the order their keys were first added.
    '''

    # Here we define the limit of the interval in the range 0° - 180°, just to draw them correctly

    if rightInterval > 180:
        rightInterval -= 180
    if rightInterval < 0:
        rightInterval += 180

    if leftInterval > 180:
        leftInterval -= 180
    if leftInterval < 0:
        leftInterval += 180

    if peak < 0:
        peak += 180
    if peak > 180:
        peak -= 180

    plt.scatter(maximums.keys(), maximums.values(), marker='x', color='r')
    plt.plot(ordered_occ.keys(), ordered_occ.values())
    plt.plot((0, 180), (threshold, threshold), linestyle = '--')
    plt.axvline(x = peak, color = 'b')
    plt.axvline(x = rightInterval, color = 'r', linestyle = ':')
    plt.axvline(x = leftInterval, color = 'r', linestyle = ':')
    plt.xlabel("Theta")
    plt.ylabel("Weight")
    plt.show()

    broken = False
    end = False

    if usingAvg == False:
        for rho, theta in lines[0]:
            peak = (theta * 180) / math.pi

    # Back to the negative value
    if peak > 90:
        peak -= 180

    # Draw the first maxLines
    for i in range(maxLines):
        for rho, theta in lines[i]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho

            # height id the lines len
            x1 = int(x0 + height * (-b))
            y1 = int(y0 + height * a)
            x2 = int(x0 - height * (-b))
            y2 = int(y0 - height * a)

            # convert in degree
            angle = (theta * 180) / math.pi

            # ex: set 175° to -5°
            if angle > 90:
                angle -= 180

            print("Lines %d: Theta %f and Rho %f\n" % (i + 1, angle, rho))

            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)

            a, b = find_coeffs(x1, y1, x2, y2)
            cv2.circle(img, (int(-b / a), 0), 20, (0, 255, 255), thickness = -1)  # -1 thickness is for
            cv2.circle(img, (int((height - b)/a), int(height)), 20, (0, 255, 0), thickness = -1)

            if abs(angle - peak) > interval:
                broken = True
                break
        if end:
            break

    if broken:
        print("Broken!\n")
    else:
        print("Unbroken!\n")

    cv2.imwrite(out, img)