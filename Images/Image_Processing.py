from matplotlib.image import imread, imsave
import numpy as np
import os
import csv
import sys

def ProcessData(path, output = "./Images/DataSet.csv"):
    """Processes all photos of a directory and saves the result to a csv"""
    
    images = []
    for filename in os.listdir(path): # gets path to all images in directory
        if filename.endswith(".jpg"):
            images.append(path + filename)

    dataset = [["Mean Value", "Mean Saturation", "Mean Value"]]

    length = len(images)
    for i, image in enumerate(images):
        sys.stdout.write('\r')
        sys.stdout.write('Processing: %s/%s (%s)' % (i+1, length, image))
        sys.stdout.flush()

        dataset.append(ProcessImage(OpenHSV(image)))
    sys.stdout.write('\n')
    sys.stdout.flush()
    print("Done processing")

    with open(output, "w") as file:
        writer = csv.writer(file)
        for row in dataset:
            writer.writerow(row)
    print("CSV created")

def OpenHSV(image_path):
    """Opens image and converts to HSV"""

    image = imread(image_path)  # opens image

    # converts image to HSV
    image_HSV = RGBtoHSV(image)

    return image_HSV

def ProcessImage(image_HSV):
    """Returns mean hue, value and saturation and RMS Contrast"""
    
    properties = [0, 0, 0]
    pixel_count = 0

    for i in range(0, image_HSV.shape[0]):
        for j in range(0, image_HSV.shape[1]):
            pixel_count += 1
            for k in range(0,3):
                properties[k] += image_HSV[i][j][k]

    properties[0] /= pixel_count #calculates mean hue
    properties[1] /= pixel_count #calculates mean saturation
    properties[2] /= pixel_count #calculates mean value

    # properties.append(CalculateRMSContrast(image_HSV, properties[2], pixel_count)) # calculate RMS Contrast

    return properties

def RGBtoHSV(image):
    """Converts RGB image to HSV"""

    HSV_image = np.zeros(image.shape)
    for i in range(0, image.shape[0]):
        for j in range(0, image.shape[1]):

            Red = image[i][j][0]/255
            Green = image[i][j][1]/255
            Blue = image[i][j][2]/255

            Cmax = max([Red, Green, Blue])
            Cmin = min([Red, Green, Blue])
            Delta = Cmax - Cmin

            # calculates hue
            if Delta == 0:
                HSV_image[i][j][0] = 0
            elif Cmax == Red and Green >= Blue:
                HSV_image[i][j][0] = 60 * ((Green - Blue)/Delta)
            elif Cmax == Red and Green < Blue:
                HSV_image[i][j][0] = 60 * ((Green - Blue)/Delta + 6)
            elif Cmax == Green:
                HSV_image[i][j][0] = 60 * ((Blue - Red)/Delta + 2)
            elif Cmax == Blue:
                HSV_image[i][j][0] = 60 * ((Red - Green)/Delta + 4)

            # calculates saturation
            if Cmax == 0:
                HSV_image[i][j][1] = 0
            else:
                HSV_image[i][j][1] = Delta/Cmax

            # calculates value
            HSV_image[i][j][2] = Cmax
    
    return HSV_image

def HSVtoRGB(image):
    """Converts HSV image to RGB"""

    RGB_image = np.zeros(image.shape)
    for i in range(0, image.shape[0]):
        for j in range(0, image.shape[1]):
            C = image[i][j][1] * image[i][j][2]
            X = C * (1 - abs((image[i][j][0] / 60) % 2 - 1))
            m = image[i][j][2] - C

            if image[i][j][0] < 60:
                R = C
                G = X
                B = 0
            elif image[i][j][0] < 120:
                R = X
                G = C
                B = 0 
            elif image[i][j][0] < 180:
                R = 0
                G = C
                B = X
            elif image[i][j][0] < 240:
                R = 0
                G = X
                B = C
            elif image[i][j][0] < 300:
                R = X
                G = 0
                B = C 
            elif image[i][j][0] < 360:
                R = C
                G = 0
                B = X  

            RGB_image[i][j][0] = (R + m)# * 255
            RGB_image[i][j][1] = (G + m)# * 255
            RGB_image[i][j][2] = (B + m)# * 255
    
    return RGB_image

def CalculateRMSContrast(image_HSV, mean_value, pixel_count):
    """Returns RMS contrast"""

    RMS_Contrast = 0
    for i in range(0, image_HSV.shape[0]):
        for j in range(0, image_HSV.shape[1]): #sums the square error for each pixel
            RMS_Contrast += (image_HSV[i][j][2]-mean_value)**2
    
    RMS_Contrast = (RMS_Contrast/pixel_count)**(1/2) #does the root and mean part
    return RMS_Contrast

def EditImage(image_path, dataset_path = "./Images/DataSet.csv"):
    """Edits image so it's ready to publish"""

    dataset = [[],[],[]]
    with open(dataset_path, "r") as dataset_file:
        dataset_reader = csv.reader(dataset_file)
        line_count = 0
        for row in dataset_reader:
            if len(row) > 1:
                if line_count != 0:
                    for i in range(0,len(dataset)):
                        dataset[i].append(float(row[i]))
                line_count += 1
        print(f'Processed {line_count} lines.')

    #calculates average of all properties
    mean_Hue = sum(dataset[0])/len(dataset[0])
    mean_Saturation = sum(dataset[1])/len(dataset[1])
    mean_Value = sum(dataset[2])/len(dataset[2])
    
    image = imread(image_path)  # opens image

    # converts image to HSV
    image_HSV = RGBtoHSV(image)
    
    for i in range(0,1):
        Properties = ProcessImage(image_HSV)

        # Calculates loss
        loss_Hue = Properties[0] - mean_Hue
        loss_Saturation = Properties[1] - mean_Saturation
        loss_Value = Properties[2] - mean_Value

        print(mean_Hue,mean_Saturation,mean_Value)
        print(loss_Hue,loss_Saturation,loss_Value)

        Variation = np.zeros(image_HSV.shape)

        for i in range(0, image_HSV.shape[0]):
            for j in range(0, image_HSV.shape[1]):
                Variation[i][j][0] = loss_Hue
                Variation[i][j][1] = loss_Saturation
                Variation[i][j][2] = loss_Value

        image_HSV += Variation

        print(image_HSV)

    
    # Makes sure everything stays within bounds
    for i in range(0, image_HSV.shape[0]):
        for j in range(0, image_HSV.shape[1]):
            while image_HSV[i][j][0] >= 360: image_HSV[i][j][0] -= 360
            while image_HSV[i][j][0] < 0: image_HSV[i][j][0] += 360
            
            if image_HSV[i][j][1] > 1: image_HSV[i][j][1] = 1
            elif image_HSV[i][j][1] < 0: image_HSV[i][j][1] = 0
            
            if image_HSV[i][j][2] > 1: image_HSV[i][j][2] = 1
            elif image_HSV[i][j][2] < 0: image_HSV[i][j][2] = 0

    print(image_HSV)

    image_RGB = HSVtoRGB(image_HSV)

    imsave("editado.jpg",image_RGB)

if __name__ == "__main__":
    # ProcessData("./certafonso/")

    EditImage("./Images/IMG_9037.JPG")

    # imsave("editado.jpg",HSVtoRGB(RGBtoHSV(imread("./Images/IMG_9037.JPG"))))