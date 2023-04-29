#!/usr/bin/python
from pychart import *  
 
class zap_y_coord(linear_coord.T):  
    def get_canvas_pos(self, size, val, min, max):  
        if val <= 70:  
            return linear_coord.T.get_canvas_pos(self, size, val, 0, 110)  
        elif val <= 240:  
            return linear_coord.T.get_canvas_pos(self, size, 70, 0, 110)  
        else:  
            return linear_coord.T.get_canvas_pos(self, size, val - 170, 0, 110)  
    def get_tics(self, min, max, interval):  
        tics = linear_coord.T.get_tics(self, min, max, interval)  
        return [x for x in tics if x < 65 or x > 256]  
 
# can = canvas.default_canvas()  
can = canvas.init('flykite.png')  
theme.scale_factor=3  
theme.use_color=True 
theme.reinitialize()  
data = [(10, 20, 30, 5), (20, 265, 33, 5),  
        (30, 255, 30, 5), (40, 45, 51, 7), (50, 25, 27, 3)]  
 
chart_object.set_defaults(area.T, size = (150, 120), y_range = (0, 280),  
                          y_coord = zap_y_coord(),  
                          x_coord = category_coord.T(data, 0))  
chart_object.set_defaults(bar_plot.T, data = data)  
 
bar_plot.fill_styles.reset();  
plot1=bar_plot.T(label="foo", cluster=(0,3))  
plot2=bar_plot.T(label="bar", hcol=2, cluster=(1,3))  
plot3=bar_plot.T(label="baz", hcol=3, cluster=(2,3))  
 
ar = area.T(loc=(250,0),  
            x_axis=axis.X(label="X label", format="/a-30{}%d"),  
            y_axis=axis.Y(label="Y label", tic_interval=10))  
ar.add_plot(plot1, plot2, plot3)  
ar.draw()  
for x in (ar.x_pos(10) - 20, ar.x_pos(20)- 10, ar.x_pos(30) - 10):  
    zap.zap_horizontally(can, line_style.default, fill_style.white,  
                         x, ar.y_pos(65), x+16, ar.y_pos(65) + 4, 4, 4) 