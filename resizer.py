from PIL import Image
import argparse

class Resizer():
    def __init__(self, filename, logger=False):
        self.filename = filename
        #top, right, bottom, left
        self.edges = [-1, -1, -1, -1]
        self.modify = [0, 0, 0, 0]
        self.expand_flag = False
        self.edge_color = None
        self.logger = logger
        self.old_width, self.old_height = 0, 0
        self.new_width, self.new_height = 0, 0
        try:
            self.img = Image.open(filename)
        except:
            raise("Unable to open " + filename)
        self.calculate_attributes()

    def calculate_wh(self):
        '''
        given the img
        return the correct width and height
        such that the w/h ratio is 16:9
        and no less than 1920*1080 (if expand is True)
        no bigger than 3200*1800
        '''
        width, height = self.img.size
        if self.expand_flag is False:
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

    def resize_img_keep_ratio(self):
        '''
        given the img
        return an img such that
        width <= 3200 and height <= 1800
        '''
        width, height = self.img.size
        if width < 3200 and height < 1800:
            return self.img
        if width > 3200:
            ratio = 3200/width
            return self.img.resize((3200, int(height*ratio)), resample=Image.LANCZOS)
        if height > 1800:
            ratio = 1800/height
            return self.img.resize((int(width*ratio), 1800), resample=Image.LANCZOS)

    def get_modify_edges(self):
        '''
        return a list of 4 elements which indicates rows to modify
        the img in 4 directions [top, right, bottom, left]
        '''
        width, height = self.img.size

        modify = [0, 0, 0, 0]
        if self.expand_flag is True:
            if self.edges[0] != -1 or self.edges[2] != -1:
                if self.edges[0] != -1 and self.edges[2] != -1:
                    modify[0] = int((self.new_height - width) / 2)
                    modify[2] = self.new_height - height - modify[0]
                elif self.edges[0] == -1:
                    modify[2] = self.new_height - height
                else:
                    modify[0] = self.new_height - height
            if self.edges[3] != -1 or self.edges[1] != -1:
                if self.edges[3] != -1 and self.edges[1] != -1:
                    modify[3] = int((self.new_width - width) / 2)
                    modify[1] = self.new_width - width - modify[3]
                elif self.edges[3] == -1:
                    modify[1] = self.new_width - width
                else:
                    modify[3] = self.new_width - width
        else:
            modify[0] = int((height - self.new_height) / 2)
            modify[2] = height - self.new_height - modify[0]
            modify[3] = int((width - self.new_width) / 2)
            modify[1] = width - self.new_width - modify[3]

        if self.logger:
            print("pixels to modify (t r b l): ", *modify)
        return modify

    def manually_set_edges_to_expand(self, directions):
        """
        directions is a list, [top, right, bottom, left];
        each attribute can be boolean
        e.g: if directions = [True, False, False, True],
        then it means that the img needs to be expanded
        in top and left directions
        """
        edges = [0, 0, 0, 0]
        for i in range(0, 4):
            if directions[i]:
                edges[i] = 1
        self.edges = edges
        self.get_modify_edges()

    def save_and_overwrite_img(self, img, postfix=None):
        '''
        given the img and optional postfix
        save img to original path with original name + postfix
        e.g: if filename = aa, postfix = 1,
        outcome filname would be aa1
        '''
        ext_idx = self.filename.rfind(".")
        ext = self.filename[ext_idx:]
        img.save(self.filename[:ext_idx] + postfix + ext, quality=95)
        if self.logger:
            print("Image saved as " + self.filename[:ext_idx] + postfix + ext)

    #resize image
    def expand_or_crop_image(self):
        """
        given calculated width,height
         return the final processed image
        """
        w, h = self.new_width, self.new_height
        if self.expand_flag:
            new_img = Image.new(mode='RGB', size=(w, h))
            new_img.paste(self.edge_color, (0, 0, w, h))
            new_img.paste(self.img, (self.modify[3], self.modify[0],
                            w-self.modify[1], h-self.modify[2]))
        else:
            new_img = self.img.crop((self.modify[3], self.modify[0],
                        self.img.size[0]-self.modify[1], self.img.size[1]-self.modify[2]))
        if self.logger:
            print("final size: ", *new_img.size)
        return new_img

    #calculate all attributes needed for resizing
    def calculate_attributes(self):

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

        if self.logger:
            print("now opening: ", self.filename)
            print("input size: ", *self.img.size)

        self.img = self.resize_img_keep_ratio()
        self.old_width, self.old_height = self.img.size[0], self.img.size[1]
        if self.logger:
            print("resized size: ", *self.img.size)

        self.edge_color = self.img.getpixel((0, 0))

        for i in range(0, 4):
            self.edges[i] = check_color_edge(self.img.rotate(90*i, expand=True))

        if self.logger:
            print("calculated edges (t r b l): ", *self.edges)

        # calculate correct size
        if sum(self.edges) != -4:
            self.expand_flag = True
        self.new_width, self.new_height = self.calculate_wh()
        if self.logger:
            print("expand mode: ", self.expand_flag)
            print("calculated size: ", self.new_width, self.new_height)
        self.modify = self.get_modify_edges()

if  __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="path of the image to be processed")
    parser.add_argument("-l", "--log", help="logging detailed info", action="store_true")
    parser.add_argument("-s", "--save", help="save processed image", action="store_true")
    args = parser.parse_args()

    if args.log:
        log_flag = True
    else:
        log_flag = False
    resizer = Resizer(args.filename, log_flag)
    resizer.calculate_attributes()
    img = resizer.expand_or_crop_image()

    if args.save:
        ext_idx = args.filename.rfind(".")
        ext = args.filename[ext_idx:]
        img.save(args.filename[:ext_idx] + '_m' + ext, quality=95)
        print("Image saved as " + args.filename[:ext_idx] + "_m" + ext)
    img.show()

# determine pure color bg edge and color
#  -> calculate correct Size
#  -> check which border(s) to be extended
#  -> set correct anchor point
#  -> create a new pic of the new Size w/ bg
#  -> paste original pic to new pic with anchor point
