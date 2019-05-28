import os
import sys
import PIL
from PIL import Image

class GIFHelper:

    def __init__(self):
        self.image = None
        self.closeImage()

    def createGIF(self, path, frames, duration):
        frames[0].save(path, save_all=True, append_images=frames[1:], duration=duration, loop=0)

    def openImage(self, path):
        self.closeImage()
        self.path = path
        self.mode = self.analyseImage(path)['mode']
        self.image = Image.open(path)
        self.palette = self.image.getpalette()
        self.ref_frame = self.image.convert('RGBA')

    def closeImage(self):
        self.path = None
        self.mode = None
        if self.image != None:
            self.image.close()
            self.image = None
        self.palette = None
        self.ref_frame = None
        self.count = 0

    def nextFrame(self):
        try:
            self.image.seek(self.count)
            if not self.image.getpalette():
                self.image.putpalette(palette)
            new_frame = Image.new('RGBA', self.image.size)
            if self.mode == 'partial': # kind of P-frame in video stream
                new_frame.paste(self.ref_frame, (0, 0))
            new_frame.paste(self.image, (0, 0), self.image.convert('RGBA'))
            self.count += 1
            return new_frame
        except EOFError:
            return None

    def analyseImage(self, path):
        im = Image.open(path)
        results = {
            'size': im.size,
            'mode': 'full',
        }
        try:
            while True:
                if im.tile:
                    tile = im.tile[0]
                    update_region = tile[1]
                    update_region_dimensions = update_region[2:]
                    if update_region_dimensions != im.size:
                        results['mode'] = 'partial'
                        break
                im.seek(im.tell() + 1)
        except EOFError:
            pass
        im.close()
        return results

def process(template_path, face_path):
    template_size = (50, 65)
    target_size = (50, 100)
    head_size = (40, 40)
    head_positions = [
        (10, 5), (9, 6), (8, 6), (7, 7), (6, 7), (5, 8), (5, 8),
        (5, 8), (5, 7), (4, 7), (3, 6), (2, 6), (1, 5), (0, 5), (0, 5),
        (0, 5), (1, 4), (2, 4), (3, 3), (4, 3), (5, 2), (5, 2), (5, 1),
        (6, 1), (7, 1), (8, 2), (9, 2), (10, 3), (10, 4), (10, 4), (10, 5)
    ]
    gif = GIFHelper()
    gif.openImage(template_path)
    face = Image.open(face_path).resize(head_size, resample=PIL.Image.BICUBIC).convert('RGBA')

    frames = []
    i = 0
    while True:
        template = gif.nextFrame()
        if not template:
            break
        new_frame = Image.new('RGBA', target_size, color='white')
        new_frame.paste(template, (target_size[0] - template_size[0], target_size[1] - template_size[1]), template.convert('RGBA'))
        new_frame.paste(face, head_positions[i], face.convert('RGBA'))
        frames.append(new_frame)
        i += 1
    gif.closeImage()
    gif.createGIF('out.gif', frames, 50)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: run.py input.jpg/png")
        exit(0)
    process('images/template.gif', sys.argv[1])