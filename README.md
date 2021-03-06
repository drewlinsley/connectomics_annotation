# Connectomics Annotation Prototype

An interaction prototype to help correct the cell labels predicted by state-of-the-art image segmentation algorithm.

- [x] On the top of the prototype is a track bar where you can control z_index. You can either drag it, or (continuously) press left/right to see the different slices of the connectomics cube. 
- [x] Resize the window
- [x] The color image of predicted segmentation is overlayed on the origin cube data. Different colors encode different labels.
- [x] ** Merge Cells ** (merged labels will propogate to the whole cube)(details can be seen below)
- [x] Cancel first selection: You can either click on the just selected one or switch to a previous or next slice (it works as a saver when the selected part are too small to select again)
- [x] ** save the current annotation **: just need to press 's' on the keyboard (timestamp is used to distinguish between different versions.)
- [ ] ** undo **
- [ ]  manually label the cells from the origin cube image/split the wrongly segmented cells

### Merging Cells

1. Select one part of the over-segmented cells that you want to merge. After selection, pixels of the same label will be highlighted.
2. Choose the other part of the over segmented cells that you want to merge with the previous part. And after you click that part, they will be merged and labels will be updated (and the visulization will also be updated (as you can see, now they are of the same color.)).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

* python2.7
* opencv2 (opencv2+ would be prefered, if you use opencv3, there are some problem with namespace, e.g. in opencv2.x, constants are of the form cv2.cv.CV_CAP_X, while in opencv3.x, they are cv2.CAP_X)
* numpy


### Running

*python annotate_gui_connectomics.py 'path_to_predicted_segs_npy_file 'path_to_cube_data_npy_file' 'path_to_folder_where_you_want_to_store_your_annotation'*


## Authors

* Shuqi Wang - *Initial work* 

