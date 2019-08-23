# _*_ coding:utf-8 _*_
__author__ = 'pan'
"""
桥接模式
模版模式
"""

# # 具体实现者1/2
# class DrawingAPI1(object):
#
#     def draw_circle(self, x, y, radius):
#         print('API1.circle at {}:{} 半径 {}'.format(x, y, radius))
#
#
# # 具体实现者2/2
# class DrawingAPI2(object):
#
#     def draw_circle(self, x, y, radius):
#         print('API2.circle at {}:{} 半径 {}'.format(x, y, radius))
#
# # 优雅的抽象
# class CircleShape(object):
#
#     def __init__(self, x, y, radius, drawing_api):
#         self._x = x
#         self._y = y
#         self._radius = radius
#         self._drawing_api = drawing_api
#
#     # 低层次的，即具体的的实现
#     def draw(self):
#         self._drawing_api.draw_circle(self._x, self._y, self._radius)
#
#     # 高层次的抽象
#     def scale(self, pct):
#         self._radius *= pct
#
#
# def main():
#     shapes = (
#         CircleShape(1, 2, 3, DrawingAPI1()),
#         CircleShape(5, 7, 11, DrawingAPI2())
#     )
#
#     for shape in shapes:
#         '''坐标--缩放变换'''
#         shape.scale(2.5)
#         shape.draw()
#
# if __name__ == '__main__':
#     main()





# class Shape():
#     name = ""
#     param = ""
#     def __init__(self,*param):
#         pass
#     def getName(self):
#         return self.name
#     def getParam(self):
#         return self.name,self.param
#
# class Pen():
#     shape = ""
#     type = ""
#     def __init__(self,shape):
#         self.shape = shape
#     def draw(self):
#         pass
#
# class Rectangle(Shape):
#     def __init__(self,long,width):
#         self.name = "Rectangle"
#         self.param = "Long:%s  Width:%s"%(long,width)
#
# class Circle(Shape):
#     def __init__(self,radius):
#         self.name = "Circle"
#         self.param = "Radius :%s"%(radius)
#
# class NormalPen(Pen):
#     def __init__(self,shape):
#         Pen.__init__(self,shape)
#         self.type = "Normal Line"
#     def draw(self):
#         print("draw ",self.type,self.shape.getName(),self.shape.getParam())
#
#
# class BrushPen(Pen):
#     def __init__(self, shape):
#         Pen.__init__(self, shape)
#         self.type = "BrushPen Line"
#
#     def draw(self):
#         print("draw ", self.type, self.shape.getName(), self.shape.getParam())
#
#
# if __name__ == "__main__":
#     rect = Rectangle("10","20")
#     cir = Circle("15")
#     n = NormalPen(rect)
#     n.draw()
#     n1 = NormalPen(cir)
#     n1.draw()
#     b = BrushPen(rect)
#     b.draw()



import abc
import os
import re
import tempfile
import Tkinter as tk

def has_methods(*methods):
    """
        类修饰器，功能判断*methods是否存在于类中，
        使用abc中的__subclasshook__实现
    """
    def decorator(Base):
        def __subclasshook__(Class, Subclass):
            if Class is Base:
                needed = set(methods)
                for Superclass in Subclass.__mro__:
                    for meth in needed.copy():
                        if meth in Superclass.__dict__:
                            needed.discard(meth)
                    if not needed:
                        return True
            return NotImplemented
        Base.__subclasshook__ = classmethod(__subclasshook__)
        return Base
    return decorator

@has_methods('initialize', 'draw_caption', 'draw_bar', 'finalize')
class BarRenderer(object):
    __metaclass__ = abc.ABCMeta

class BarCharter(object):
    def __init__(self, renderer):
        if not isinstance(renderer, BarRenderer):
            raise TypeError('is not BarCharter')
        self.__renderer = renderer

    def render(self, caption, pairs):
        maximux = max(value for _, value in pairs)
        self.__renderer.initialize(len(pairs), maximux)
        self.__renderer.draw_caption(caption)
        for name, value in pairs:
            self.__renderer.draw_bar(name, value)
        self.__renderer.finalize()

class TextBarRenderer(object):
    def __init__(self, scaleFactor=40):
        self.scaleFactor = scaleFactor

    def initialize(self, bars, maximum):
        assert bars > 0 and maximum > 0
        self.scale = self.scaleFactor / maximum

    def draw_caption(self, caption):
        print("{0:^{2}}\n{1:^{2}}".format(caption, "=" * len(caption),
                self.scaleFactor))

    def draw_bar(self, name, value):
        print("{} {}".format("*" * int(value * self.scale), name))

    def finalize(self):
        pass

class ImageBarRenderer(object):
    COLORS = ('red', 'green','blue', 'yellow', 'magenta', 'cyan')

    def __init__(self, stepHeight=10, barWidth=30, barGap=2):
        self.stepHeight = stepHeight
        self.barWidth = barWidth
        self.barGap = barGap

    def initialize(self, bars, maximum):
        assert bars > 0 and maximum > 0
        if tk._default_root is None:
            self.gui = tk.Tk()
            self.inGui = False
        else:
            self.gui = tk._default_root
            self.inGui = True
        self.index = 0
        self.width = bars * (self.barWidth + self.barGap)
        self.height = maximum * self.stepHeight
        self.image = tk.PhotoImage(width=self.width, height=self.height)
        self.image.put("white", (0, 0, self.width, self.height))

    def draw_caption(self, caption):
        self.filename = os.path.join(tempfile.gettempdir(),
                re.sub(r"\W+", "_", caption) + ".gif")


    def draw_bar(self, name, value):
        color = ImageBarRenderer.COLORS[self.index %
                len(ImageBarRenderer.COLORS)]
        x0 = self.index * (self.barWidth + self.barGap)
        x1 = x0 + self.barWidth
        y0 = self.height - (value * self.stepHeight)
        y1 = self.height - 1
        self.image.put(color, (x0, y0, x1, y1))
        self.index += 1


    def finalize(self):
        self.image.write(self.filename, "gif")
        print("wrote", self.filename)
        if not self.inGui:
            self.gui.quit()

def main():
    pairs = (('Mon', 16), ('Tue', 17), ('Wed', 19),
            ('Thu', 22), ('Fri', 24), ('Sat', 21),
            ('Sun', 19))
    textBarCharter = BarCharter(TextBarRenderer())
    textBarCharter.render('Forecast 6/8', pairs)
    imageBarCharter = BarCharter(ImageBarRenderer())
    imageBarCharter.render('Forecase 6/8', pairs)

if __name__ == '__main__':
    main()
