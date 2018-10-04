import cv2
import numpy as np

class Rect:
    x = None
    y = None
    w = None
    h = None

    def printit(self):
        print str(self.x) + ',' + str(self.y) + ',' + str(self.w) + ',' + str(self.h)
 

class annots:
    # Limits on the canvas
    keepWithin = Rect()

    '''
    If you want to build up your matrix one at a time, 
    might be best off to keep it in a list until it is finished, 
    and only then convert it into an array.
    '''
    selected_cell_masks = []
    selected_cell_masks_boundary = [] # just to highlight the selected cell

    # Window Name
    wname = ""

    # when frame_n is -1, it means 
    # crt_label_image needs to be updated from gui
    # it could happen 1. in initialization
    # 2. when finish selecting two cells and merging them. it's time to update the new label image and remove the previous highlight
    frame_n = -1
    
    labels_all_images = None
    crt_shown_image = None

    # idle - nothing happens
    # selecting - selecting cells
    state = "idle"

# def update_state(annot_obj, new_state):
#     print annot_obj.state, new_state, ord('a')
#     # 1310819 is the input if your press "a"
#     if annot_obj.state == "idle" and new_state == 1310819:
#         annot_obj.state = "selecting"
#     elif annot_obj.state == "selecting" and new_state == -1:
#         annot_obj.state = "selected"
#     elif annot_obj.state == "selcted" and new_state == -1:
#         annot_obj.state = "idle"

def reset_annot(annot_obj):
    annot_obj.selected_cell_masks = []
    annot_obj.selected_cell_masks_boundary = []
    annot_obj.frame_n = -1
    annot_obj.state = "idle"




def init(annot_obj, windowName, labels_all_images, windowWidth, windowHeight):
    # Image
    # annot_obj.image = Img

    # Window name
    annot_obj.wname = windowName
    # Limit the selection box to the canvas
    annot_obj.keepWithin.x = 0
    annot_obj.keepWithin.y = 0
    annot_obj.keepWithin.w = windowWidth
    annot_obj.keepWithin.h = windowHeight
    # store the labels data
    annot_obj.labels_all_images = labels_all_images

# enddef

def dragcircle(event, x, y, flags, dragObj):
    print event, x, y, flags, dragObj

    if x < dragObj.keepWithin.x:
        return
    #     x = dragObj.keepWithin.x
    if y < dragObj.keepWithin.y:
        return
    #     y = dragObj.keepWithin.y
    if x > (dragObj.keepWithin.x + dragObj.keepWithin.w - 1):
        return
    #     x = dragObj.keepWithin.x + dragObj.keepWithin.w - 1
    if y > (dragObj.keepWithin.y + dragObj.keepWithin.h - 1):
        return
    #     y = dragObj.keepWithin.y + dragObj.keepWithin.h - 1


    if event == cv2.EVENT_LBUTTONDOWN:
        mouseDown(x, y, dragObj)
    if event == cv2.EVENT_LBUTTONUP:
        mouseUp(x, y, dragObj)
    # if event == cv2.EVENT_MOUSEMOVE:
        # mouseMove(x, y, dragObj)
    # if event == cv2.EVENT_LBUTTONDBLCLK:
    #     mouseDoubleClick(x, y, dragObj)

# enddef

# def pointInRect(pX, pY, rX, rY, rW, rH):
def pointInCircle(pX, pY, rX, rY, rR):
    if ((pX - rX)**2 ) + ((pY - rY)**2) < rR**2:
    # if rX <= pX <= (rX + rW) and rY <= pY <= (rY + rH):
        return True
    else:
        return False
    # endelseif

# enddef

def updateAnnots(annots_obj, frame_n, im):

    joints = annots_obj.joints.keys()
    annot_df = annots_obj.joints_df[annots_obj.joints_df.frame_n == frame_n][joints]
    if annot_df.empty:
        return
    # This has to be below all of the other conditions
    # if pointInCircle(eX, eY, dragObj.outCircle.x, dragObj.outCircle.y, dragObj.outCircle.r):
    annots_obj.image = im
    annots_obj.frame_n = frame_n
    for joint in annot_df:
        annots_obj.joints[joint].x, annots_obj.joints[joint].y, _score = annot_df[joint].values[0].split('-')

    clearCanvasNDraw(annots_obj)
    return

def mouseDoubleClick(eX, eY, dragObj):

    # if pointInCircle(eX, eY, dragObj.outCircle.x, dragObj.outCircle.y, dragObj.outCircle.r):
    dragObj.returnflag = True
    cv2.destroyWindow(dragObj.wname)
    # endif
# enddef

def mouseDown(x, y, dragObj):
    if len(dragObj.selected_cell_masks) < 2:
        dragObj.state = "selecting"

    # get the pixels with the same label as the clicked point
    crt_labels = dragObj.labels_all_images[dragObj.frame_n, :, :]
    selected_label = crt_labels[y, x]
    selected_cell_mask = (crt_labels == selected_label)
    # cv2.imshow('mask', selected_cell_mask.astype('uint8')*255) # for debug

    # add the selected cell mask
    dragObj.selected_cell_masks.append(selected_cell_mask)

    # canny edge detector for edge detection
    # to be able to highlight the selected cell
    selected_cell_mask_boundary = cv2.Canny(selected_cell_mask.astype('uint8')*255, 100, 200) 
    # cv2.imshow('boundary', selected_cell_mask_boundary) # for debug
    dragObj.selected_cell_masks_boundary.append(selected_cell_mask_boundary)




def mouseMove(eX, eY, dragObj):

    if dragObj.selectedJoint:

        jt = dragObj.selectedJoint
        # jt.x = eX - dragObj.anchor[jt.label].x
        # jt.y = eY - dragObj.anchor[jt.label].y
        jt.x = eX
        jt.y = eY

        if jt.x < dragObj.keepWithin.x:
            jt.x = dragObj.keepWithin.x
        # endif
        if jt.y < dragObj.keepWithin.y:
            jt.y = dragObj.keepWithin.y
        # endif
        if (jt.x + jt.r) > (dragObj.keepWithin.x + dragObj.keepWithin.w - 1):
            jt.x = dragObj.keepWithin.x + dragObj.keepWithin.w - 1 - jt.r
        # endif
        if (jt.y + jt.r) > (dragObj.keepWithin.y + dragObj.keepWithin.h - 1):
            jt.y = dragObj.keepWithin.y + dragObj.keepWithin.h - 1 - jt.r
        # endif

        # update the joint with score 10 since this is done by a human annotator
        if dragObj.multiframe:
            dragObj.joints_df.loc[dragObj.joints_df['frame_n'] >= dragObj.frame_n, jt.label] = str(jt.x) + '-' + str(
                jt.y) + '-10'
        else:
            dragObj.joints_df.loc[dragObj.joints_df['frame_n'] == dragObj.frame_n, jt.label] = str(jt.x) + '-' + str(jt.y) + '-10'
        clearCanvasNDraw(dragObj)
        return
    # endif


# enddef

def mouseUp(eX, eY, dragObj):

    last_selected_cell_mask_boundary = dragObj.selected_cell_masks_boundary[-1]
    crt_shown_image = dragObj.crt_shown_image

    # (1d-array, 1d-array)
    # (y, x)
    non_zero_index = np.nonzero(last_selected_cell_mask_boundary)
    print len(non_zero_index[0])
    for i in range(len(non_zero_index[0])):
        y = non_zero_index[0][i]
        x = non_zero_index[1][i]
        cv2.circle(crt_shown_image, (x, y), 1, [0,0,0])

    cv2.imshow(dragObj.wname, crt_shown_image)
    
    if len(dragObj.selected_cell_masks)== 2:
        dragObj.state = "selected"
        

    return

# enddef

def disableResizeButtons(dragObj):
    dragObj.hold = False


# enddef

def clearCanvasNDraw(dragObj):
    # Draw
    tmp = dragObj.image.copy()
    tmp1 = dragObj.image.copy()
    for joint_name in dragObj.joints:
        joint = dragObj.joints[joint_name]
        if joint.x == 0:
            return
        cv2.circle(tmp, (int(joint.x), int(joint.y)),
               int(joint.r), dragObj.colorDict[joint_name], -1)
    # apply the overlay
    colorList = [[0, 0, 255], [0, 255, 0], [0, 255, 255]]
    qual = dragObj.joints_df['quality'][dragObj.frame_n]
    cv2.circle(tmp, (10, 10), 10, colorList[qual], -1)
    cv2.addWeighted(tmp, 0.5, tmp1, 0.5, 0, tmp1)
    cv2.imshow(dragObj.wname, tmp1)
    # cv2.waitKey()


# enddef
