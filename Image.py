from matplotlib.image import imread
import numpy as np

def ProcessImage(image_path):
    image = imread(image_path)  #opens image

    # calculates contrast
    luminance = CalculateRelativeLuminance(image)
    contrast = CalculateRMSContrast(luminance)

    return contrast

def CalculateRelativeLuminance(image, normalized = True):
    shape = image.shape
    luminance = np.empty(shape[0:1])
    
    for i in range(0, shape[0]):
        for j in range(0, shape[1]): #calculates relative luminance for each pixel with the formula: Y = 0.21226 * R + 0.7152 * G + 0.0722 * B
            luminance_calc = 0.21226 * image[i][j][0] + 0.7152 * image[i][j][1] + 0.0722 * image[i][j][2]
            if normalized:
                luminance_calc /= 255 # normalizes to a 0-1 scale
            luminance[i][j] = luminance_calc

    return luminance

def CalculateRMSContrast(luminance):
    shape = luminance.shape
    Mean_Luminance = luminance.mean() #calculates mean luminance
    RMS_Contrast = 0
    for i in range(0, shape[0]):
        for j in range(0, shape[1]): #multiplies by the square error for each pixel
            RMS_Contrast *= (luminance[i][j]-Mean_Luminance)**2
    
    RMS_Contrast = (RMS_Contrast/2)**(1/2) #does the root and mean part
    return RMS_Contrast



if __name__ == "__main__":
    print(ProcessImage("./IMG_0854.jpg"))