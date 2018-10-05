#!/usr/bin/env python

import cv2, numpy as np
import sys
from time import sleep
import time

import annotate_tools_for_connectomics as annotate_tools
import pandas as pd
import colorsys

from Tkinter import *
# import Image, ImageTk
from skimage import color
import ttk
import os
import glob
from ConfigParser import SafeConfigParser


# config
PLAYER_WNAME = 'connectomics_annotation'


def flick(x):
    pass

def show_image_sequencees(cube_as_array, labels_all_images_as_array, output_folder):

    # get some parameters
    image_w = labels_all_images_as_array.shape[2]
    image_h = labels_all_images_as_array.shape[1]
    # assert labels_all_images_as_array == images_as_array
    z_depth = labels_all_images_as_array.shape[0]
    z_index = 0
    label_transparency = 0.4

    # initiation
    cv2.destroyAllWindows()
    cv2.moveWindow(PLAYER_WNAME, 400, 150)
    cv2.namedWindow(PLAYER_WNAME, 16) # WINDOW_GUI_NORMAL
    # for debug - to test whether select the same sells
    # cv2.namedWindow("mask", 16) 
    # cv2.namedWindow('boundary', 16) 
    annotate_tools.init(annotate_tools.annots, PLAYER_WNAME, labels_all_images_as_array, image_w, image_h)
    cv2.setMouseCallback(PLAYER_WNAME, annotate_tools.dragcircle, annotate_tools.annots)
    # controls = np.zeros((50, int(playerwidth*3)), np.uint8)
    # cv2.putText(controls, "W/w: Play, S/s: Stay, A/a: Prev, D/d: Next, E/e: Fast, Q/q: Slow, Esc: Exit, g: good, b: bad, n: no annot.", (40, 20),
                # cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)

    cv2.createTrackbar('z_index', PLAYER_WNAME, 0, z_depth - 1, flick)
    cv2.setTrackbarPos('z_index', PLAYER_WNAME, z_index)

    while True:
        # update
        z_index = cv2.getTrackbarPos('z_index', PLAYER_WNAME)
        # prepare image to show
        crt_cube_image = cube_as_array[z_index, :, :]   
        crt_to_show_cube_image = np.dstack((crt_cube_image, crt_cube_image, crt_cube_image))
        # still the last frame, show the one that stored in the annotate_tools.annots
        # because it's the one that add highlight of selected cells
        if z_index == annotate_tools.annots.frame_n:
            crt_to_show_image = annotate_tools.annots.crt_shown_image
        # update the crt_to_show_image and crt_shown_image in annotate_tools.annots
        # could be z_index changed
        # could be image need to be updates (after mergin labels)
        else:
            crt_label_image = labels_all_images_as_array[z_index, :, :]
            # convert labels uint16 data to rgb
            # crt_label_image = color.label2rgb(crt_label_image) # the before image's color doesn't correspond to the next image's color
            r = ((crt_label_image >> 8) & 0xff).astype('uint8')           # first 8 byte
            g = (((crt_label_image<<4)>>8) & 0xff).astype('uint8')        # middle 8 byte
            b = (((crt_label_image)) & 0xff).astype('uint8')              # last 8 byte
            # b = np.ones((image_w, image_h), 'uint8')
            crt_to_show_label_img = np.dstack((r,g,b))
            # make sure label img on the top because the response region is [(0,0), (image_w, image_h)]
            # crt_to_show_stacked_image = np.vstack((crt_to_show_label_img, crt_to_show_cube_image))
            crt_to_show_stacked_image = cv2.addWeighted(crt_to_show_cube_image, 1-label_transparency, crt_to_show_label_img, label_transparency, 0)
            
            annotate_tools.annots.crt_shown_image = crt_to_show_stacked_image
        if z_index == annotate_tools.annots.frame_n:
            pass
        else:
            annotate_tools.reset_annot(annotate_tools.annots)
            annotate_tools.annots.frame_n = z_index

        # show image
        cv2.imshow(PLAYER_WNAME, crt_to_show_stacked_image)
        
        # check the update of annotator to update the label
        if annotate_tools.annots.state == "selected":
            cell_masks = annotate_tools.annots.selected_cell_masks
            # update the second cell with the first cell's label in the whole cube
            first_cell_label = labels_all_images_as_array[z_index, cell_masks[0]][0]
            second_cell_label = labels_all_images_as_array[z_index, cell_masks[1]][0]
            labels_all_images_as_array[labels_all_images_as_array == second_cell_label] = first_cell_label
            # reset all things
            annotate_tools.reset_annot(annotate_tools.annots)

        c = cv2.waitKey(50) 
        # s: save annotation
        if c == 1048691:
            print 's pressed'
            os.chdir(output_folder)
            np.save('annotated_segs_'+time.strftime("%Y%m%d_%H%M%S")+'.npy', labels_all_images_as_array)
        

    cv2.destroyWindow(PLAYER_WNAME)
    
    
#
## /usr/bin/python annotate_gui_connectomics.py '/home/shuqi/Desktop/shuqi/annotate_opencv-master/data/predicted_segs_second_try.npy' '/home/shuqi/Desktop/shuqi/annotate_opencv-master/data/cube_sem_data_second_try.npy' '/home/shuqi/Desktop/shuqi/annotate_opencv-master/annotation_history/'
#if len(sys.argv) < 4:
#    print("Usage: python annotate_gui_connectomics.py <path_to_predicted_segs_npy_file> <path_to_cube_data_npy_file> <path_to_folder_where_you_want_to_store_your_annotation>")
#    sys.exit(1)
#
## '/home/shuqi/Desktop/shuqi/annotate_opencv-master/data/cube_sem_data_second_try.npy'
#cube_raw_data_file = str(sys.argv[2])
## '/home/shuqi/Desktop/shuqi/annotate_opencv-master/data/predicted_segs_second_try.npy'
#seg_raw_data_file = str(sys.argv[1])
## '/home/shuqi/Desktop/shuqi/annotate_opencv-master/annotation_history/'
#output_folder = str(sys.argv[3])


def main(sem, seg, output_folder):    
    """Run file."""
    # root = Tk()
    # root.title("connectomics annotation")
    
    
    # readin file
    print('Reading SEM')
    cube_raw_data = np.load(sem)
    print(')
    seg_raw_data = np.load(seg)
    
    show_image_sequencees(
        cube_raw_data.reshape((768,384,384)),
        seg_raw_data.reshape((768,384,384)).astype('uint16'),
        output_folder=output_folder)
    # show_image_sequencees(cube_raw_data, False)
