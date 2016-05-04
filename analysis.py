#! /usr/bin/python3

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random
import matplotlib.pyplot as plot
import math
import os, sys

# CONSTANTS
WH_LVL = 200
BL_LVL = 50

WH_DIFF = 4
GR_DIFF = 2
NOISY_DIFF = 20
NOISE_LVL = 0.9
NOISE_LVL2 = 0.3
L_DIFF = 5/8.
H_DIFF = 8/8.

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# Functions
#
def plot_noise(noise, result_path, pic):
    fig = plot.figure(frameon=False)
    x = np.arange(0, len(noise[0]), 1)
    y = np.arange(0, len(noise), 1)
    x,y = np.meshgrid(x,y)
    z = np.array(noise)
    im1 = plot.imshow(z, label='Block noise level', interpolation="nearest")
    plot.xlabel('width')
    plot.ylabel('height')
    plot.colorbar(label='Noise level, %')
    plot.savefig(str(os.path.join(result_path, pic + "_plot_noise.png")))

def plot_diff(diff, result_path, pic):
    fig = plot.figure(frameon=False)
    x = np.arange(0, len(diff[0]), 1)
    y = np.arange(0, len(diff), 1)
    x,y = np.meshgrid(x,y)
    z = np.array(diff)
    im1 = plot.imshow(z, label='Block borders difference level', interpolation="nearest")
    plot.xlabel('width')
    plot.ylabel('height')
    plot.colorbar(label='Difference level, %')
    plot.savefig(str(os.path.join(result_path, pic + "_plot_diff.png")))

def grade(N):
    if N < 3:
        return 'Excellent'
    elif N < 20:
        return 'Acceptable'
    else:
        return 'Bad'
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

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
    # noise, right_diff, down_diff, right_diff_high, down_diff_high
    block_matrix = [[0.0, 0.0, 0.0, 0.0, 0.0] for x in range(w_blocks*h_blocks)]

    for y in range(height-2):
        for x in range(width-2):
            b_index = int(x / 8) + int(y / 8)*w_blocks
            cur = int(pic[x + y*width])
            if ((x+1) % 8 != 0) and ((y+1) % 8 != 0):
                right = int(pic[(x+1) + y*width])
                down = int(pic[x + (y+1)*width])
                if (cur < WH_LVL) or (cur > BL_LVL):
                    diff = WH_DIFF
                else:
                    diff = GR_DIFF
                if (abs(cur - right) >= diff):
                    block_matrix[b_index][0] += 1
                if (abs(cur - down) >= diff):
                    block_matrix[b_index][0] += 1
            else:
                right_diff = 0.0
                down_diff = 0.0
                right = int(pic[(x+1) + y*width])
                down = int(pic[x + (y+1)*width])
                if (cur < WH_LVL) or (cur > BL_LVL):
                    diff = WH_DIFF
                else:
                    diff = GR_DIFF
                if ((x+1) % 8 == 0):
                    right_diff = abs(right - cur)
                if ((y+1) % 8 == 0):
                    down_diff = abs(down - cur)
                if right_diff >= diff:
                    block_matrix[b_index][1] += 1
                if down_diff >= diff:
                    block_matrix[b_index][2] += 1
                if right_diff >= 45:
                    block_matrix[b_index][3] += 1
                if down_diff >= 45:
                    block_matrix[b_index][4] += 1
    # normalising matrix
    block_matrix = list(map(lambda lst: [1.0 - (lst[0] / (7.0*8.0*2.0)),
                                         lst[1]/8.0,
                                         lst[2]/8.0,
                                         lst[3]/8.0,
                                         lst[4]/8.0],
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
        img.convert("L").save(str(os.path.join(result_path, pic + "_Y.bmp")), "BMP")
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
        while i < len(result)-wb:
            cur_noise = result[i][0]
            noises = [result[i-1][0], result[i+1][0], result[i-wb][0], result[i+wb][0]]
            flats = list(map(lambda x: (x > NOISE_LVL) or (cur_noise > NOISE_LVL), noises))
            noised = list(map(lambda x: (x > NOISE_LVL2) or (cur_noise > NOISE_LVL2), noises))
            borders = [result[i][1], result[i][2], result[i-1][1], result[i - wb][2]]
            borders_high = [result[i][3], result[i][4], result[i-1][3], result[i - wb][4]]
            tmp_results = list(zip(flats, noised, borders, borders_high))
            if len(list(filter(lambda x: (x[0] and (x[2] >= L_DIFF)), tmp_results))) >= 2: #or
            #if len(list(filter(lambda x: (x[0] and (x[2] >= L_DIFF)) or (x[1] and (x[3] >= H_DIFF)), tmp_results))) >= 2: #or
                x = int(i % wb)*8
                y = int(i / wb)*8
                draw = ImageDraw.Draw(img)
                draw.rectangle([x, y, x+8, y+8], fill=None, outline=0xffffff)
                del draw
                counter += 1
            i += 1

        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (170, 16)], fill=(255,128,128), outline=None)
        fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 12)

        blck_perc = (100.0*counter) / ((wb-2)*(hb-2))
        text = "visible blocks: " + ('%.2f%%' % blck_perc)
        draw.text((0, 0), text, font=fnt, fill=(0,128,128))
        del draw
        if not (os.path.exists(result_path)):
            os.mkdir(result_path)
        img.convert("RGB").save(str(os.path.join(result_path, pic + "_result.bmp")), "BMP")
        # plotting the result
        i = 0
        noise_matrix = []
        diff_matrix = []
        while i < len(result)/wb:
            j = 0
            tmp_noise = []
            tmp_diff = []
            while j < wb:
                up_diff = 0
                down_diff = result[i*wb + j][2]
                left_diff = 0
                right_diff = result[i*wb + j][1]
                if i > 1:
                    up_diff = result[(i-1)*wb + j][2]
                if j > 1:
                    left_diff = result[i*wb + j - 1][1]
                borders = [up_diff, down_diff, left_diff, right_diff]
                tmp_noise.append((1.0 - result[i*wb + j][0])*100)
                tmp_diff.append(sum(borders))
                j += 1
            noise_matrix.append(tmp_noise)
            diff_matrix.append(tmp_diff)
            i += 1
        # noise:
        plot_noise(noise_matrix, result_path, pic)
        # difference
        plot_diff(diff_matrix, result_path, pic)

        percent = (100.0*counter) / ((wb-2)*(hb-2))
        
        print(pic + "\told_alg: " + str(result_old) + "\tnew_alg: " + str(percent) + "% "+ grade(percent))
        

if __name__ == "__main__":
    args = sys.argv
    if (len(args) < 3):
        print("Usage: " + args[0] + " /path/to/folder picture.ext picture2.ext pictureN.ext")
        exit(1)
    main(args[1], args[2:])
