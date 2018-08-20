import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
import collections
from PIL import Image


def find_maximums(points, thresh):
    over = False
    local_points = {}
    local_max = 0  # our values can't go lower than 0
    cur_idx = 0

    for (k, v) in points.iteritems():
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
    leo = False
    clean_img = False

    if leo:
        broken = '/Users/leonardotanzi/Desktop/Fratture Computer Vision/Jpeg Notevoli/Broken/bone3cut.jpg'
        clean = '/Users/leonardotanzi/Desktop/Fratture Computer Vision/Jpeg Notevoli/Unbroken/sana2.jpg'
        out = '/Users/leonardotanzi/Desktop/houghlines2.jpg'
    else:
        broken = r"C:\Users\cassa\Desktop\Fabien\Fabien\Jpeg Notevoli\Broken\bone3cut.jpg"
        clean = r"C:\Users\cassa\Desktop\Fabien\Fabien\Jpeg Notevoli\Unbroken\sana2.jpg"
        out = r"C:\Users\cassa\Desktop\Fabien\out.jpg"

    # we need to open the img twice, this is to retrieve the img dimensions
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

    # convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # blur to remove noise
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # find edges first is for broken image, second for unbroken
    if clean_img:
        edges = cv2.Canny(blur, 15, 45, apertureSize=3)
    else:
        edges = cv2.Canny(blur, 25, 75, apertureSize=3)

    # erode and dilate with kernel window
    kernel_erode = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    boneEdges = cv2.erode(edges, kernel_erode, iterations=2)
    boneEdges = cv2.dilate(boneEdges, kernel_dilate, iterations=2)

    # plot the result
    plt.imshow(boneEdges)
    plt.show()

    # find lines with houghlines:
    # second arg is rho accuracy (that is 10 pixels in this case) and third is theta accuracy, fourth is the threshold
    lines = cv2.HoughLines(boneEdges, 10, np.pi / 45, 50)

    if __debug__:
        print(lines.shape)        # (337, 1, 2)
        print(lines[0].shape)     # (1, 2)
        print(lines[0][0].shape)  # (2,)

        print(lines)        # [[  modulo, angolo in rad ]]
        print(lines[0])     # [[  3.30000000e+02   2.09439516e-01]]
        print(lines[0][0])  # [  3.30000000e+02   2.09439516e-01]

    # set the max n of lines ????
    maxLines = 3

    # creo due liste una con gli angoli e una con il num di angoli associati,
    # ma e sbagliato perche questa cosa e gia stata fatta dalla hough transform
    th_occ = {}
    threshold = 34

    for line in lines:
        for r, theta in line:
            theta_degs = int(theta * 180 / math.pi)
            if theta_degs in th_occ:
                th_occ[theta_degs] += 1
            else:
                th_occ[theta_degs] = 1

    ordered_occ = collections.OrderedDict(sorted(th_occ.items()))
    maximums = find_maximums(ordered_occ, threshold)

    plt.scatter(maximums.keys(), maximums.values(), marker='x', color='r')
    plt.plot(ordered_occ.keys(), ordered_occ.values())
    plt.plot((0, 180), (threshold, threshold), linestyle='--')
    plt.xlabel("Theta")
    plt.ylabel("Weight")
    plt.show()

    # peak array
    peaks = 0
    broken = False
    end = False

    # save the two lines with different angles in format lines[x1, y1][x2, y2]
    w = 2
    line_first = [[0 for x in range(w)] for y in range(w)]
    line_second = [[0 for x in range(w)] for y in range(w)]

    # faccio una media tra le linee iniziali
    count = 0
    totangle = 0
    for line in lines:
        for rho, theta in line:
            angle = (theta * 180) / math.pi
            totangle += angle
            count += 1

    peaks = totangle / count

    print("peaks is = %f\n" % peaks)

    # draw the first maxLines
    for line in lines:
        for rho, theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho

            # height e la lunghezza della linea
            x1 = int(x0 + height * (-b))
            y1 = int(y0 + height * a)
            x2 = int(x0 - height * (-b))
            y2 = int(y0 - height * a)

            # converto in gradi
            angle = (theta * 180) / math.pi

            # 0 e 179 hanno una differenze di 1 grado, ma viene letta come 179 se non faccio questa operazione
            if angle > 90:
                angle = angle - 180

            # print("Line %s\n" % line)
            print("Theta: %f\n" % angle)
            print("Rho: %f\n" % rho)
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)

            # uso il primo angolo come riferimento, qua forse andrebbe meglio prendere una media tra i vari theta
            # if i == 0:
            #   peaks = angle
            #   line_first[0][0] = x1
            #   line_first[0][1] = y1
            #   line_first[1][0] = x2
            #   line_first[1][1] = y2

            # else:
            # for j in range(i):
            if abs(angle - peaks) > 5:
                # qua ci farebbe fare un confronto proporzionato con maxlines, piu linee analizzate piu ampia la soglia
                # line_second[0][0] = x1
                # line_second[0][1] = y1
                # line_second[1][0] = x2
                # line_second[1][1] = y2

                broken = True
                # end = True
                break
        if end:
            break

    if broken:
        print("Broken!\n")
    else:
        print("Unbroken!\n")

    cv2.imwrite(out, img)
