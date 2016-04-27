from PIL import Image, ImageDraw
import numpy as np
import random
import matplotlib.pyplot as plot
import math

laplasian = [1, -2, 1, -2, 4, -2, 1, -2, 1]
laplasian_2 = [-1, -1, -1, -1, 8, -1, -1, -1, -1]
laplasian_3 = [0. -1, 0, -1, 4, -1, 0, -1, 0]
block_noisy = [0, 255]*32
block_smooth = [100, 120, 130, 140, 150, 160, 170, 180]*8
block_simple = [250]*64
block_random = [random.randint(0, 255) for i in range(64)]

def noise_block_eval(blc, filt, h, w):
    result = 0
    j = 1
    while (j < (h-1)):
        i = 1
        while (i < (w-1)):
            tmp = 0
            for k,el in enumerate(filt):
                x = int((k%3) - 1)
                y = int((k/3) - 1)
                tmp += el * blc[(i+x) + (j+y)*w]
            result += abs(tmp)
            i += 1
        j += 1
    return (math.sqrt(math.pi/2))*result/(6*(w-2)*(h-2))
                

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
    return (noise_result, lum_result, w_blocks, h_blocks)

def different_p(noise, lum):
    if lum > 4 and noise > 0.90:
        return True
    else:
        return False
    
#file_names = ["lena.tif", "5.jpg", "baby.JPG.bmp"]
file_names = ["0.jpg", "1.jpg", "2.jpg", "3.jpg", "9.jpg"]
#file_names = ["9.jpg"]
#file_names = ["0.jpg", "baby.JPG.bmp", "lena.tif"]
def main(pics):
    for pic in pics:
        print(pic)
        img = Image.open(str(pic)).convert("YCbCr")
        arr = np.array(img)
        Y = arr[:,:,0]
        height = len(Y)
        width = len(Y[0])
        Y = np.concatenate(Y)
        result_old = old_alg(Y)
        print(height, width)
        print(result_old)

        result, lum, wb, hb = block_blob_alg(Y, width, height)
        print(lum[32*wb:33*wb])
        print(result[32*wb:33*wb])
        #print(result)
        i = 0
        counter = 0
        while i < len(result)-1:
            #print(result[i])
            if different_p(result[i], lum[i]):
                x = int(i % wb)*8
                y = int(i / wb)*8
                draw = ImageDraw.Draw(img)
                draw.rectangle([x, y, x+8, y+8], fill=None, outline=0xffffff)
                del draw
                counter += 1
            i += 1
        img.show()

        print("new alg: " + str((100.0*counter) / (wb*hb)) + "%")

main(file_names)
