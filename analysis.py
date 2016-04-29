#! /usr/bin/python3

from PIL import Image, ImageDraw
import numpy as np
import random
import matplotlib.pyplot as plot
import math
import os, sys

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# Operators and test sequences
#
laplasian = [1, -2, 1, -2, 4, -2, 1, -2, 1]
laplasian_2 = [-1, -1, -1, -1, 8, -1, -1, -1, -1]
laplasian_3 = [0. -1, 0, -1, 4, -1, 0, -1, 0]
block_noisy = [0, 255]*32
block_smooth = [100, 120, 130, 140, 150, 160, 170, 180]*8
block_simple = [250]*64
block_random = [random.randint(0, 255) for i in range(64)]
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# Classic blockiness detection algorithm implementation
#
def old_alg(x):
    Shb = .0
    Shnb = .0
    length = len(x)
    i = 4
    while i < length:
        sub = x[i-1] - x[i] if x[i-1] > x[i] else x[i] - x[i-1]
        subNext = x[i+1] - x[i] if x[i+1] > x[i] else x[i] - x[i+1]
        subPrev = x[i-2] - x[i-1] if x[i-2] > x[i-1] else x[i-1] - x[i-2]
        sumn = (1.0*subNext) + subPrev
        if (sumn == .0):
            sumn = 1.
        else:
            sumn = sumn / 2.0
        if ((i%8) != 0):
            Shnb += (1.0*sub)/sumn
        else:
            Shb += (1.0*sub)/sumn
        i += 4
    return Shb/Shnb
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# Plain new blockiness detection algorithm implementation
# 
# Based on comparison of the average luminence values and noises of
# the blocks
#
def different_p(noise, lum):
    if lum > 4 and noise > 0.90:
        return True
    else:
        return False

def block_blob_alg(pic, width, height):
    w_blocks = int(width / 8)
    h_blocks = math.ceil(height / 8)
    length = len(pic)
    block_matrix = [0.0] * w_blocks*h_blocks
    block_avg_lum = [0.0] * w_blocks*h_blocks
    noise_result = [0.0] * w_blocks*h_blocks
    lum_result = [0.0] * w_blocks*h_blocks
    # vc - luma difference visibility threshold
    # b - black, g - grey, w - white
    bvc = 4
    gvc = 6
    wvc = bvc

    wl = 200
    bl = 50

    for y in range(height-1):
        for x in range(width-1):
            if ((x+1) % 8 != 0) and ((y+1) % 8 != 0):
                b_index = int(x / 8) + int(y / 8)*w_blocks
                cur = int(pic[x + y*width])
                right = int(pic[(x+1) + y*width])
                down = int(pic[x + (y+1)*width])
                block_avg_lum[b_index] += cur
                if (cur < wl) or (cur > bl):
                    diff = bvc
                else:
                    diff = gvc
                if (abs(cur - right) >= diff):
                    block_matrix[b_index] += 1
                if (abs(cur - down) >= diff):
                    block_matrix[b_index] += 1

    block_matrix = list(map(lambda x: 1.0 - (x / (7.0*8.0*2.0)), block_matrix))
    block_avg_lum = list(map(lambda x: x / 64.0, block_avg_lum))
    #print(block_matrix)
    #print(block_avg_lum)
    for y in range(1, h_blocks-1):
        for x in range(1, w_blocks-1):
            b_index = x + y*w_blocks
            coef_noise = 0.0
            coef_lum = 0.0
            #print("Block:")
            #print(x, y)
            #print("vals:")
            for k,el in enumerate(laplasian):
                x_coord = int(k%3 - 1)
                y_coord = int(k/3) - 1
                index = b_index + y_coord*w_blocks + x_coord
                coef_lum += el*block_avg_lum[index]
                #coef_noise += block_matrix[index]
                #print(block_matrix[index])
            coef_lum = abs(coef_lum)
            #coef_noise = (abs(coef_noise) / 9.0)
            coef_noise = block_matrix[b_index]
            noise_result[b_index] = coef_noise
            lum_result[b_index] = coef_lum
            #result[b_index] = coef_lum
    #print(list(filter(lambda x: x >= 0.9, block_matrix)))
    #print(tmp_result)
    result = list(map(lambda x, y: different_p(x, y), noise_result, lum_result))
    return (result, w_blocks, h_blocks)
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# Another new blockiness detection algorithm implementation
# 
# Based on comparison of the border luminence values and noises of
# the blocks
#
def border_diff_alg(pic, width, height):
    w_blocks = int(width / 8)
    h_blocks = math.ceil(height / 8)
    length = len(pic)
    # noise, right_diff, down_diff
    block_matrix = [[0.0, 0.0, 0.0] for x in range(w_blocks*h_blocks)]
    # vc - luma difference visibility threshold
    # b - black, g - grey, w - white
    bvc = 6
    gvc = 4
    wvc = bvc
    wl = 200
    bl = 50

    for y in range(height-2):
        for x in range(width-2):
            b_index = int(x / 8) + int(y / 8)*w_blocks
            cur = int(pic[x + y*width])
            if ((x+1) % 8 != 0) and ((y+1) % 8 != 0):
                right = int(pic[(x+1) + y*width])
                down = int(pic[x + (y+1)*width])
                if (cur < wl) or (cur > bl):
                    diff = bvc
                else:
                    diff = gvc
                if (abs(cur - right) >= diff):
                    block_matrix[b_index][0] += 1
                if (abs(cur - down) >= diff):
                    block_matrix[b_index][0] += 1
            else:
                right_diff = 0.0
                down_diff = 0.0
                right = int(pic[(x+1) + y*width])
                down = int(pic[x + (y+1)*width])
                if ((x+1) % 8 == 0):
                    right_diff = abs(right - cur)
                if ((y+1) % 8 == 0):
                    down_diff = abs(down - cur)
                block_matrix[b_index][1] += right_diff
                block_matrix[b_index][2] += down_diff
    # normalising matrix
    block_matrix = list(map(lambda lst: [1.0 - (lst[0] / (7.0*8.0*2.0)),
                                         lst[1]/8.0,
                                         lst[2]/8.0],
                            block_matrix))
    return (block_matrix, w_blocks, h_blocks)
    #print(block_matrix)
    
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


#file_names = ["lena.tif", "5.jpg", "baby.JPG.bmp"]
#file_names = ["0.jpg", "1.jpg", "2.jpg", "3.jpg", "9.jpg"]
#file_names = ["9.jpg"]
#file_names = ["0.jpg", "baby.JPG.bmp", "lena.tif", "5.jpg", "b1.bmp", "9.jpg"]
#file_names = ["mri.tif", "einstein.tif", "lena.tif"]
#file_names = ["lena.tif"]
#file_names = ["b1.bmp"]

def main(path, pics):
    for pic in pics:
        result_path = os.path.join(path, "results")
        img = Image.open(str(os.path.join(path, pic))).convert("YCbCr")
        arr = np.array(img)
        Y = arr[:,:,0]
        height = len(Y)
        width = len(Y[0])
        Y = np.concatenate(Y)
        result_old = old_alg(Y)
    
        #result, wb, hb = block_blob_alg(Y, width, height)
        result, wb, hb = border_diff_alg(Y, width, height)
        
        i = 0+wb
        counter = 0
        while i < len(result)-1:
            borders = [result[i][1], result[i][2], result[i-1][1], result[i - wb][2]]
            if ((result[i][0] > 0.95 and (len(list(filter(lambda x: x > 4, borders))) >= 2)) or
                (result[i][0] > 0.50 and (len(list(filter(lambda x: x > 30, borders))) >= 2))):
                x = int(i % wb)*8
                y = int(i / wb)*8
                draw = ImageDraw.Draw(img)
                draw.rectangle([x, y, x+8, y+8], fill=None, outline=0xffffff)
                del draw
                counter += 1
            i += 1
        if not (os.path.exists(result_path)):
            os.mkdir(result_path)
        img.convert("RGB").save(str(os.path.join(result_path, pic + "_result.bmp")), "BMP")
        # plotting the result
        i = 0
        noise_matrix = []
        while i < len(result):
            noise_matrix.append(list(map(lambda x: x[0], result[i:i+wb])))
            i += wb
        fig = plot.figure(frameon=False)
        x = np.arange(0, wb, 1)
        y = np.arange(0, hb, 1)
        x,y = np.meshgrid(x,y)
        z = np.array(noise_matrix[::-1])
        im1 = plot.imshow(z, interpolation='nearest')
        plot.show()
        #plot.savefig(str(os.path.join(result_path, pic + "_plot_inverse_noise.png")))
        #plot.show()
        
        print(pic + "\told_alg: " + str(result_old) + "\tnew_alg: " + str((100.0*counter) / (wb*hb)) + "%")

if __name__ == "__main__":
    args = sys.argv
    if (len(args) < 3):
        print("Usage: " + args[0] + " /path/to/folder picture.ext picture2.ext pictureN.ext")
        exit(1)
    main(args[1], args[2:])
