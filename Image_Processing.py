from matplotlib.image import imread
import numpy as np

def ProcessImage(image_path):
    image = imread(image_path)  # opens image

    # converts image to HSV
    image_HSV = RGBtoHSV(image)
    
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

    properties.append(CalculateRMSContrast(image_HSV, properties[2], pixel_count)) # calculate RMS Contrast

    return properties

def RGBtoHSV(image):
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

def CalculateRMSContrast(image_HSV, mean_value, pixel_count):
    RMS_Contrast = 0
    for i in range(0, image_HSV.shape[0]):
        for j in range(0, image_HSV.shape[1]): #sums the square error for each pixel
            RMS_Contrast += (image_HSV[i][j][2]-mean_value)**2
    
    RMS_Contrast = (RMS_Contrast/pixel_count)**(1/2) #does the root and mean part
    return RMS_Contrast

if __name__ == "__main__":
    print(ProcessImage("./test-image.jpg"))