from PIL import Image
import argparse

def check_color_edge(img):
    '''
    given the img
    return the biggest continuous pixel in height
    such that the image has the same color
    return -1 if all rows are the same or no rows
    has the same color
    '''
    width, height = img.size
    curr_rgb = img.getpixel((0, 0))
    for i in range(0, height):
        for j in range(0, width):
            if img.getpixel((j, i)) != curr_rgb:
                return i - 1
    return -1

def calculate_wh(img, expand):
    '''
    given the img
    return the correct width and height
    such that the w/h ratio is 16:9
    and no less than 1920*1080 (if expand is True)
    no bigger than 3200*1800
    '''
    width, height = img.size
    if expand is False:
        if width / height < 1.77:
            while int(width / 16 * 9) != height:
                height -= 1
        else:
            while int(height / 9 * 16) != width:
                width -= 1
    else:
        if height <= 1080 and width <= 1920:
            return 1920, 1080
        if width / height > 1.77:
            while int(width / 16 * 9) != width / 16 * 9:
                width += 1
            height = width / 16 * 9
        else:
            while int(height / 9 * 16) != height / 9 * 16:
                height += 1
            width = height / 9 * 16
    return int(width), int(height)

def resize_img_keep_ratio(img):
    '''
    given the img
    return an img such that
    width <= 3200 and height <= 1800
    '''
    width, height = img.size
    if width < 3200 and height < 1800:
        return img
    if width > 3200:
        ratio = 3200/width
        return img.resize((3200, int(height*ratio)), resample=Image.LANCZOS)
    if height > 1800:
        ratio = 1800/height
        return img.resize((int(width*ratio), 1800), resample=Image.LANCZOS)

def get_modify_edges(img, expand, new_width, new_height, edges):
    '''
    given the img, expand flag, calculated width, height,
    and edge pixels,
    return a list of 4 elements which indicates rows to modify
    the img in 4 directions [top, right, bot, left]
    '''
    width, height = img.size
    modify = [0, 0, 0, 0]
    if expand is True:
        if edges[0] != -1 or edges[2] != -1:
            if edges[0] != -1 and edges[2] != -1:
                modify[0] = int((new_height - width) / 2)
                modify[2] = new_height - height - modify[0]
            elif edges[0] == -1:
                modify[2] = new_height - height
            else:
                modify[0] = new_height - height
        if edges[3] != -1 or edges[1] != -1:
            if edges[3] != -1 and edges[1] != -1:
                modify[3] = int((new_width - width) / 2)
                modify[1] = new_width - width - modify[3]
            elif edges[3] == -1:
                modify[1] = new_width - width
            else:
                modify[3] = new_width - width
    else:
        modify[0] = int((height - new_height) / 2)
        modify[2] = height - new_height - modify[0]
        modify[3] = int((width - new_width) / 2)
        modify[1] = width - new_width - modify[3]
    return modify

#resize image
def expand_or_crop_image(img, expand, edge_color, w, h, mod_pixels):
    """
    given the img, expand_flag, edge_color, calculated width,height
     and list of pixels to modify
     return the final processed image
    """
    if expand:
        new_img = Image.new(mode='RGB', size=(w, h))
        new_img.paste(edge_color, (0, 0, w, h))
        new_img.paste(img, (mod_pixels[3], mod_pixels[0],
                        w-mod_pixels[1], h-mod_pixels[2]))
    else:
        new_img = img.crop((mod_pixels[3], mod_pixels[0],
                    img.size[0]-mod_pixels[1], img.size[1]-mod_pixels[2]))
    return new_img


parser = argparse.ArgumentParser()
parser.add_argument("filename", help="path of the image to be processed")
parser.add_argument("-l", "--log", help="logging detailed info", action="store_true")
args = parser.parse_args()


if args.log:
    log_flag = True
else:
    log_flag = False


# input
img = Image.open(args.filename)
if log_flag:
    print("now opening: ", args.filename)
    print("input size: ", *img.size)
img = resize_img_keep_ratio(img)

if log_flag:
    print("resized size: ", *img.size)
edge_color = img.getpixel((0, 0))

# determine pure color rows in 4 directions
#top, right, bottom, left
edge_pixels = [-1, -1, -1, -1]

for i in range(0, 4):
    edge_pixels[i] = check_color_edge(img.rotate(90*i, expand=True))

if log_flag:
    print("calculated edges (t r b l): ", *edge_pixels)

# calculate correct size
expand_flag = False
if sum(edge_pixels) != -4:
    expand_flag = True
new_width, new_height = calculate_wh(img, expand_flag)
if log_flag:
    print("expand mode: ", expand_flag)
    print("calculated size: ", new_width, new_height)

mod_pixels = get_modify_edges(
    img, expand_flag, new_width, new_height, edge_pixels)

if log_flag:
    print("pixels to modify (t r b l): ", *mod_pixels)

new_img = expand_or_crop_image(
    img, expand_flag, edge_color, new_width, new_height, mod_pixels)
new_img.show()
if log_flag:
    print("final size: ", *new_img.size)

#img_b2t.save('b2t' + '.png')


# determine pure color bg edge and color (optional)
#  -> crop pure color bg (optional)
#  -> calculate correct Size
#  -> check which border(s) to be extended
#  -> set correct anchor point
#  -> create a new pic of the new Size w/ bg
#  -> paste original pic to new pic with anchor point
