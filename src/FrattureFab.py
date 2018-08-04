import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
from PIL import Image

if __name__ == '__main__':
    leo_broken = '/Users/leonardotanzi/Desktop/Fratture Computer Vision/Jpeg Notevoli/Broken/bone3cut.jpg'
    leo_clean = '/Users/leonardotanzi/Desktop/Fratture Computer Vision/Jpeg Notevoli/Unbroken/sana2.jpg'
    leo_out = '/Users/leonardotanzi/Desktop/houghlines2.jpg'

    fab_broken = r"C:\Users\cassa\Desktop\Fabien\Fabien\Jpeg Notevoli\Broken\bone3cut.jpg"
    fab_clean = r"C:\Users\cassa\Desktop\Fabien\Fabien\Jpeg Notevoli\Unbroken\sana2.jpg"
    fab_out = r"C:\Users\cassa\Desktop\Fabien\out.jpg"
    # open image with open to compute sizes
    img_h = Image.open(fab_broken)
    # img_h = Image.open(fab_clean)

    # compute width, height and diagonal
    width, height = img_h.size
    diagonal = math.sqrt(width ** 2 + height ** 2)

    # open image with imread
    img = cv2.imread(fab_broken)
    # img = cv2.imread(fab_clean)

    # convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # blur to remove noise
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # find edges first is for broken image, second for unbroken
    edges = cv2.Canny(blur, 25, 75, apertureSize=3)  # 25 is minvalue, 75 maxvalue, 3 the size of windows to convolute

    # edges = cv2.Canny(blur, 15, 45, apertureSize = 3) #25 is minvalue, 75 maxvalue, 3 the size of windows to convolute

    # erode and dilate with kernel window
    kernel = np.ones((7, 7), np.uint8)
    boneEdges = cv2.erode(edges, kernel, iterations=2)
    boneEdges = cv2.dilate(edges, kernel, iterations=2)

    # plot the result
    plt.imshow(boneEdges)
    plt.show()

    # find lines with houghlines:
    # second arg is rho accuracy (that is 10 pixels in this case) and third is theta accuracy, fourth is the threshold
    lines = cv2.HoughLines(boneEdges, 10, np.pi/45, 50)

    # print(lines.shape)
    # print(lines[0].shape)
    # print(lines[0][0].shape)

    # stampa
    # (337, 1, 2)
    # (1, 2)
    # (2,)

    # print(lines)
    # print(lines[0])   #[[  3.30000000e+02   2.09439516e-01]]
    # print(lines[0][0]) #[  3.30000000e+02   2.09439516e-01]

    # gli ultimi due stampano la stessa cosa, in pratica e un formato nested quindi e una lista di un solo elemento

    # vuol dire che ci sono 337 linee

    # lines e nel formato
    # [[  3.30000000e+02   2.09439516e-01]]
    # [[  2.90000000e+02   1.39626339e-01]]
    # [[  modulo, angolo in rad ]]

    # set the max n of lines
    maxLines = 3

    # creo due liste una con gli angoli e una con il num di angoli associati,
    # ma e sbagliato perche questa cosa e gia stata fatta dalla hough transform
    list_weighted = [0] * 180
    list_thetas = [i for i in range(180)]

    for i in range(maxLines):
        for r, theta in lines[i]:
            theta_degs = int(theta * 180 / math.pi)
            list_weighted[theta_degs] = list_weighted[theta_degs] + 1

    plt.scatter(list_thetas, list_weighted)
    plt.plot(list_thetas, list_weighted)

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
    for i in range(maxLines):
        for rho, theta in lines[i]:
            angle = (theta * 180) / math.pi
            totangle = totangle + angle
            count = count + 1

    peaks = totangle / count

    print("peaks is = %f\n" % peaks)

    # draw the first maxLines
    for i in range(maxLines):
        for rho, theta in lines[i]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho

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

            print("Line %d\n" % i)
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

    cv2.imwrite(fab_out, img)
