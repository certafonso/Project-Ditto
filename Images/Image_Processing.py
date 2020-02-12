from matplotlib.image import imread, imsave
import numpy as np
import os
import sys
import json

def GetImages(path):
    """gets path to all images in directory"""

    images = []
    for filename in os.listdir(path):
        if filename.endswith(".jpg"):
            images.append(path + filename)

    return images

def ProcessData(images):
    """Processes photos and returns a json"""

    dataset = []

    length = len(images)
    for i, image in enumerate(images):
        sys.stdout.write('\r')
        sys.stdout.write('Processing: %s/%s (%s)' % (i+1, length, image))
        sys.stdout.flush()

        mean_Hue, mean_Saturation, mean_Value = ProcessImage(OpenHSV(image))

        dataset.append({"Filename": image,
                        "mean_Hue": mean_Hue,
                        "mean_Saturation": mean_Saturation,
                        "mean_Value": mean_Value})

    sys.stdout.write('\n')
    sys.stdout.flush()
    print("Done processing")

    return dataset

def ProcessNewData(path, dataset_dir = "./Images/DataSet.json"):
    """Processes new images at a directory and saves them to a json file"""
    
    images = GetImages(path)
    dataset = Import_JSON(dataset_dir)

    for i in range(len(images)-1, -1, -1):
        if images[i] == dataset["images"][-1]["Filename"]: # detects first image in dataset
            try:
                dataset["images"] += ProcessData(images[i+1:len(images)])

                Save_JSON(CalculateMean(dataset), dataset_dir)

                break
            except:
                print("except")
                break

def CreateDataSet(path, dataset_dir = "./Images/DataSet.json"):
    """Creates a new dataset from a path"""

    images = GetImages(path)

    dataset = {"Hue": {"mean": 0, "std": 0},
               "Saturation": {"mean": 0, "std": 0},
               "Value": {"mean": 0, "std": 0},
               "images": ProcessData(images)}

    dataset = CalculateMean(dataset)
    
    Save_JSON(dataset, dataset_dir)

def CalculateMean(dataset):
    """Calculates mean and standart deviation of all attributes"""

    # puts all attributes in lists
    Hues = [d["mean_Hue"] for d in dataset["images"]]
    Saturations = [d["mean_Saturation"] for d in dataset["images"]]
    Values = [d["mean_Value"] for d in dataset["images"]]

    # calculates means
    dataset["Hue"]["mean"] = sum(Hues) / len(Hues)
    dataset["Saturation"]["mean"] = sum(Saturations) / len(Saturations)
    dataset["Value"]["mean"] = sum(Values) / len(Values)

    # calculates standart deviations
    dataset["Hue"]["std"] = np.std(Hues)
    dataset["Saturation"]["std"] = np.std(Saturations)
    dataset["Value"]["std"] = np.std(Values)

    return dataset

def Import_JSON(path):
    """Imports JSON file"""

    with open(path, "r") as json_file:
        item = json.load(json_file)

    return item

def Save_JSON(content, path):
    """Saves to a JSON file"""

    with open(path, "w") as f:
        json.dump(content, f)

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

    return properties[0], properties[1], properties[2]

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

def EditImage(image_path, dataset_path = "./Images/DataSet.json"):
    """Edits image so it's ready to publish"""

    dataset = Import_JSON(dataset_path)
    
    image = imread(image_path)  # opens image

    # converts image to HSV
    image_HSV = RGBtoHSV(image)
    Properties = ProcessImage(image_HSV)

    # Calculates loss
    # loss_Hue = Properties[0] - np.random.normal(loc=dataset["Hue"]["mean"],scale=dataset["Hue"]["std"]/10)
    loss_Saturation = Properties[1] - np.random.normal(loc=dataset["Saturation"]["mean"],scale=dataset["Saturation"]["std"]/10)
    loss_Value = Properties[2] - np.random.normal(loc=dataset["Value"]["mean"],scale=dataset["Value"]["std"]/10)

    Variation = np.zeros(image_HSV.shape)

    for i in range(0, image_HSV.shape[0]):
        for j in range(0, image_HSV.shape[1]):
            # Variation[i][j][0] = loss_Hue
            Variation[i][j][1] = loss_Saturation
            Variation[i][j][2] = loss_Value

    image_HSV += Variation

    
    # Makes sure everything stays within bounds
    for i in range(0, image_HSV.shape[0]):
        for j in range(0, image_HSV.shape[1]):
            while image_HSV[i][j][0] >= 360: image_HSV[i][j][0] -= 360
            while image_HSV[i][j][0] < 0: image_HSV[i][j][0] += 360
            
            if image_HSV[i][j][1] > 1: image_HSV[i][j][1] = 1
            elif image_HSV[i][j][1] < 0: image_HSV[i][j][1] = 0
            
            if image_HSV[i][j][2] > 1: image_HSV[i][j][2] = 1
            elif image_HSV[i][j][2] < 0: image_HSV[i][j][2] = 0

    image_RGB = HSVtoRGB(image_HSV)

    imsave(image_path + "_edited.jpg",image_RGB)
