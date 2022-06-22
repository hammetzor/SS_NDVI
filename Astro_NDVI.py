# -*- coding: utf-8 -*-
import cv2
import numpy as np
from fastiecm import fastiecm

original = cv2.imread(r'C:\Users\hamme\.spyder-py3\image197a.jpg')  #file path here


def display(image, image_name):
    image = np.array(image, dtype=float)/float(255)
    #shape = image.shape       #these lines are comented because we only used them to resize certain images
    #height = int(shape[0]/4)
    #width = int(shape[1]/4)
    #image = cv2.resize(image, (width, height))
    cv2.namedWindow(image_name)
    cv2.imshow(image_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def contrast_stretch(im):
    in_min = np.percentile(im, 1)       #we changed the min and max values of pixels' brightness to find the best ones for the NDVI calculation, considering the differences of the light intensity in each image.
    in_max = np.percentile(im, 99)      #we used the values 1 - 99 on the Cape Verde islands image, because the differences of light intensity were lower, so we needed a bigger range of pixels' contrast.
                                        #we used the values 8 - 80 on the USA image, because the differences of the light intensity were higher, so we needed a smaller range of pixels' contrast.
    
    out_min = 0.0
    out_max = 255.0

    out = im - in_min
    out *= ((out_min - out_max) / (in_min - in_max))
    out += in_min

    return out

def calc_ndvi(image):
    b, g, r = cv2.split(image)
    bottom = (r.astype(float) + b.astype(float))
    bottom[bottom==0] = 0.01
    ndvi = (b.astype(float) - r) / bottom
    return ndvi

display(original, 'Original')
contrasted = contrast_stretch(original)
display(contrasted, 'Contrasted original')
cv2.imwrite('contrasted.png', contrasted)
ndvi = calc_ndvi(contrasted)
display(ndvi, 'NDVI')
cv2.imwrite('ndvi.png', ndvi)
ndvi_contrasted = contrast_stretch(ndvi)
display(ndvi_contrasted, 'NDVI Contrasted')
cv2.imwrite('ndvi_contrasted.png', ndvi_contrasted)
color_mapped_prep = ndvi_contrasted.astype(np.uint8)
color_mapped_image = cv2.applyColorMap(color_mapped_prep, fastiecm)
display(color_mapped_image, 'Color mapped')
cv2.imwrite('color_mapped_image.png', color_mapped_image)
