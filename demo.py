#!/usr/bin/env python

# This is a demo script for SplatGL
# It made available under the CC0 license (Public Domain)
# http://creativecommons.org/publicdomain/zero/1.0/

import ctypes
from sdl2 import *
from sdl2.sdlimage import IMG_Load_RW
import splatgl

class DemoException(Exception):
    pass

class Demo:
    def load_image(self, filename):
        # Load the file into memory
        with open(filename, "rb") as f:
            buffer = f.read()

        # Create a RWops for the buffer
        ops = SDL_RWFromConstMem(ctypes.c_char_p(buffer), len(buffer))
        if ops is None:
            raise DemoException("Couldn't obtain SDL_RWops for image file '{}'".format(filename))

        # Load the image using SDL_image
        lp_surf = IMG_Load_RW(ops, SDL_TRUE)
        if not lp_surf:
            raise DemoException("Couldn't load image from file '{}'.  SDL error was '{}'".format(filename, SDL_GetError()))

        # Create the Splat image from the surface
        image = splatgl.create_image(lp_surf)
        if not image:
            raise DemoException("Splat image creation failed:  {}".format(splatgl.get_error()))

        return image

    def prepare(self):
        # 640x480 window
        self.width = 640
        self.height = 480

        # Image starts at 0, 0 (upper left corner)
        self.x = 0
        self.y = 0
        self.offset = 3
        self.abs_offset = self.offset

        # Create the SDL window
        self.window = SDL_CreateWindow("SplatGL Python Demo".encode("utf-8"), SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, self.width, self.height, SDL_WINDOW_OPENGL | SDL_WINDOW_SHOWN)
        if not self.window:
            raise DemoException("SDL window creation failed:  {}".format(SDL_GetError()))

        # Set up Splat to render
        splatgl.prepare(self.window, self.width, self.height) # Viewport width and height can be different (result will be scaled to window size)

        # Create a canvas for the window
        self.canvas = splatgl.create_canvas()

        # Create a single layer for the canvas
        self.layer = splatgl.create_layer(self.canvas)

        # Load the test image
        self.image = self.load_image("test.png")

        # Save off the image width
        width, height = splatgl.get_image_size(self.image)
        self.image_width = width

        # Create an instance of that image on the canvas
        self.instance = splatgl.create_instance(self.image, # Image
                                              self.layer, # Layer to attach the instance
                                              self.x, self.y, # X/Y canvas coordinates.
                                              0.0, 0.0, 1.0, 1.0, # Texture coordinates, we use the full image
                                              0) # Flags (none)

    def tick(self):
        # Every frame, move the instance, bouncing it from one side of the window to another
        # This assumes the image is not as wide as the window
        self.x += self.offset
        if self.x >= self.width - self.image_width:
            self.offset = -self.abs_offset
            # Just for fun, flip the image
            splatgl.set_instance_flags(self.instance, splatgl.Flags.MIRROR_X)
        elif self.x < 1:
            self.offset = self.abs_offset
            # Unflip the image
            splatgl.set_instance_flags(self.instance, 0)

        # Update the instances position
        splatgl.set_instance_position(self.instance, self.x, self.y)

        # Render the canvas
        splatgl.render(self.canvas)

    def finish(self):
        # Cleanup
        splatgl.destroy_instance(self.instance)
        self.instance = None

        splatgl.destroy_image(self.image)
        self.image = None

        splatgl.destroy_layer(self.layer)
        self.layer = None

        splatgl.destroy_canvas(self.canvas)
        self.canvas = None

        SDL_DestroyWindow(self.window)
        self.window = None

    def loop(self):
        # Prepare to render
        self.prepare()

        # Main loop
        while True:
            # Frame tick
            self.tick()

            # Handle SDL input events
            event = self.get_event()
            while event is not None:
                # Terminate on ESC keydown or SDL_QUIT event
                if event.type == SDL_QUIT or (event.type == SDL_KEYDOWN and event.key.keysym.sym == SDLK_ESCAPE):
                    self.finish()
                    return

                event = self.get_event()

    def get_event(self):
        lp_event = ctypes.POINTER(SDL_Event)(SDL_Event())
        if SDL_PollEvent(lp_event) == 0:
            return

        return lp_event.contents

if __name__ == "__main__":
    Demo().loop()
