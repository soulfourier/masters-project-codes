import numpy as np
import cv2
import matplotlib.pyplot as plt

img_dark = cv2.imread("E:\Suvam\codes\Exp_4_avg_dark_FLIR.jpg",0)
img_sat = cv2.imread("E:\Suvam\codes\Exp_4_avg_sat_FLIR.jpg",0)

rows = len(img_dark[:,0])
columns = len(img_dark[0,:])

#Row wise 
def Horizontal_SNU(img):
        dft_r = []
        for m in range(rows):                              
                current_row = img[m,:]
                dft = cv2.dft(np.float32(current_row),flags=cv2.DFT_COMPLEX_OUTPUT)
                dft_r.append(dft)
        dft_r = np.array(dft_r)
        power_spec = np.zeros(columns)

        for v in range(columns):
                p = 0
                for m in range(rows):
                        p += np.multiply(dft_r[m][v],dft_r[m][v].conj())
                p = p/rows
                power_spec[v] = np.log(np.sqrt(p[0][0]) + 1)

        v = np.arange(power_spec.size)/columns
        plt.title("Horizontal PRNU")
        plt.plot(v[0:(int(columns/2))],power_spec[0:(int(columns/2))])
        plt.ylabel("standard deviation and \n relative presence of each cycle (%)")
        plt.xlabel("Cycles [periods/pixel]")
        plt.show()

def Vertical_SNU(img):
        dft_r = []
        for n in range(columns):                              
                current_column = img[:,n]
                dft = cv2.dft(np.float32(current_column),flags=cv2.DFT_COMPLEX_OUTPUT)
                dft_r.append(dft)
        dft_r = np.array(dft_r)
        power_spec = np.zeros(rows)

        for v in range(rows):
                p = 0
                for n in range(columns):
                        p += np.multiply(dft_r[n][v],dft_r[n][v].conj())
                p = p/columns
                power_spec[v] = np.log(np.sqrt(p[0][0]) + 1)

        v = np.arange(power_spec.size)/rows
        plt.title("Vertical PRNU")
        plt.plot(v[0:(int(rows/2))],power_spec[0:(int(rows/2))])
        plt.ylabel("standard deviation and \n relative presence of each cycle (%))")
        plt.xlabel("Cycles [periods/pixel]")
        plt.show()

Horizontal_SNU(img_dark)
Vertical_SNU(img_dark)
Horizontal_SNU(img_sat)
Vertical_SNU(img_sat)