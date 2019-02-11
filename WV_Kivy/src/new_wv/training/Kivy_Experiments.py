from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.window import Window
from kivy.graphics.instructions import InstructionGroup
import math
import time
from random import randint
import sys

import new_wv.controller.State as EOGState


GOAL_DIAMETER = 100
EXPERIMENT_DURATION = 20
GOAL_AMOUNT = 80
POINTER_DIAMETER = 10
DRAW_LENGTH = 10


class Point(object):
    def __init__(self, x, y):
        self.X = x
        self.Y = y

    def getX(self):
        return self.X

    def getY(self):
        return self.Y

    def distance(self, other):
        dx = self.X - other.X
        dy = self.Y - other.Y
        return math.sqrt(dx ** 2 + dy ** 2)


##############################################################################


class GoalBox():
    def screen_size(self):
        return (1920, 1080)

    def __init__(self, X, Y):
        self.origin = Point(X, Y)
        self.width = Window.width
        self.height = Window.height
        self.goal = self.create_random_point()
        self.nr_goals = 0

    def get_nr_goals(self):
        return self.nr_goals

    def get_goal(self):
        return self.goal

    def get_origin(self):
        return self.origin

    def create_new_goal(self, X, Y):
        self.origin = Point(X, Y)
        self.goal = self.create_random_point()
        self.nr_goals += 1

    def create_random_point(self):
        return Point(randint(0, 700), randint(0, 500))


##############################################################################


class ExperimentsWidget(Widget):

    def draw_goal(self):
        with self.canvas:
            Color(0, 1, 0)
            Ellipse(pos=(self.goals.get_goal().getX(), self.goals.get_goal().getY()),
                    size=(GOAL_DIAMETER, GOAL_DIAMETER))
            Ellipse(pos=(self.goals.get_origin().getX(), self.goals.get_origin().getY()), size=(2, 2))
        self.starttime = time.time()

    def update_pos(self, *args):
        pnt = Point(self.goals.get_goal().getX() + GOAL_DIAMETER / 2,
                    self.goals.get_goal().getY() + GOAL_DIAMETER / 2)
        xpos = self.current_position_X
        ypos = self.current_position_Y
        last = self.path[-1]
        with self.canvas:
            Line(points=[last.getX(), last.getY(), xpos, ypos], width=2)
        self.path.append(Point(xpos, ypos))
        if self.goals.get_nr_goals() > GOAL_AMOUNT:
            self.exportData()
            self.exportData2()
            sys.exit("")
        elif (Point(self.current_position_X, self.current_position_Y).distance(
                pnt) < GOAL_DIAMETER / 2 or self.over_time()):
            self.reset_goals()
            self.goalTime = time.time() * 1000
        self.draw_point()

    pointer = InstructionGroup()

    def draw_point(self):
        self.pointer.clear()
        self.pointer.add(Color(1, 0, 0, 1))
        self.pointer.add(Ellipse(pos=(
            self.current_position_X - POINTER_DIAMETER / 2, self.current_position_Y - POINTER_DIAMETER / 2),
                                 size=(POINTER_DIAMETER, POINTER_DIAMETER)))

    def reset_goals(self):
        self.dist_eval()
        self.time_eval()
        self.canvas.clear()
        self.canvas.add(self.boxes)
        self.canvas.add(self.pointer)
        self.path = [Point(self.current_position_X, self.current_position_Y)]
        self.goals.create_new_goal(self.current_position_X, self.current_position_Y)
        self.draw_goal()

    def __init__(self, **kwargs):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.path = []
        super(ExperimentsWidget, self).__init__(**kwargs)
        self.canvas.add(self.boxes)
        self.canvas.add(self.pointer)
        self.goals = GoalBox(self.current_position_X, self.current_position_Y)
        self.timeval = []
        self.disteval = []
        self.starttime = 0
        self.goalTime = time.time() * 1000
        self.fileName = "EXPtest.txt"
        self.start_experiment()

    def start_experiment(self):
        self.path = [Point(self.current_position_X, self.current_position_Y)]
        self.goals.create_new_goal(self.current_position_X, self.current_position_Y)
        self.draw_goal()

    def over_time(self):
        if time.time() * 1000 - self.goalTime > EXPERIMENT_DURATION * 1000:
            return True
        else:
            return False

##### EVALUATION OF A SESSION (stored in timeval & disteval)######

    # time it takes to reach the goal (sec) divided by the optimal distance
    def time_eval(self):
        duration = time.time() - self.starttime
        optimal_duration = self.get_manhatten_distance() / (10 * DRAW_LENGTH)  #(Assuming the loopsPerSec = 10)
        if optimal_duration == 0:
            optimal_duration = duration
        self.timeval.append(duration / optimal_duration)  ## Nr of times the real time exceeds the optimal time

    #difference between the distance of the path followed, and the manhatten distance.
    def dist_eval(self):
        accum_diff = 0
        for i in range(0, len(self.path) - 2):
            accum_diff += self.path[i].distance(self.path[i + 1])
        accum_diff += 10  ##Hardcoded fix. Check later
        if self.get_manhatten_distance() == 0:
            self.disteval.append(0)
        else:
            self.disteval.append(accum_diff / self.get_manhatten_distance())

    def get_manhatten_distance(self):
        lastPoint = self.path[-1]
        manh_x = abs(lastPoint.getX() - self.goals.get_origin().getX())
        manh_y = abs(lastPoint.getY() - self.goals.get_origin().getY())
        return manh_x + manh_y

    def exportData(self):
        average_timeval = sum(self.timeval) / len(self.timeval)
        average_disteval = sum(self.disteval) / len(self.disteval)
        f = open(self.fileName, 'w')
        f.write("normalised distance evaluations: " + str(self.disteval) + '\n')
        f.write("average normalised distance evaluation: " + str(average_disteval) + '\n')
        f.write("time/optimal_time evaluations: " + str(self.timeval) + '\n')
        f.write("average time/optimal_time evaluation: " + str(average_timeval) + '\n')
        print(f.name)
        f.close()

    def exportData2(self):
        filename = self.fileName + ".csv"
        f = open(filename, 'w')
        f.write("NDistance;NTime" + '\n')
        for x in range(0, len(self.disteval)):
            f.write(str(self.disteval[x]) + ";" + str(self.timeval[x]) + '\n')
        f.close()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'up':
            self.draw_up()
        if keycode[1] == 'left':
            self.draw_left()
        if keycode[1] == 'down':
            self.draw_down()
        if keycode[1] == 'right':
            self.draw_right()

##### DRAW FUNCTIONS FOR EOG INTEGRATION #####

    writing = False
    current_position_X = 200
    current_position_Y = 200

    def draw_up(self):
        y = self.current_position_Y + DRAW_LENGTH
        if self.is_valid_pos_Y(y):
            self.current_position_Y = y
        self.update_pos()

    def draw_left(self):
        x = self.current_position_X - DRAW_LENGTH
        if self.is_valid_pos_X(x):
            self.current_position_X = x
        self.update_pos()

    def draw_down(self):
        y = self.current_position_Y - DRAW_LENGTH
        if self.is_valid_pos_Y(y):
            self.current_position_Y = y
        self.update_pos()

    def draw_right(self):
        x = self.current_position_X + DRAW_LENGTH
        if self.is_valid_pos_X(x):
            self.current_position_X = x
        self.update_pos()

    def draw_mid(self):
        self.update_pos()

    def is_valid_pos_X(self, x):
        return (x > 0 and x <= Window.width)

    def is_valid_pos_Y(self, y):
        return (y > 0 and y <= Window.height)


    ################ FLASHY FEEDBACK ############
    boxes = InstructionGroup()

    def drawState(self, state):
        bar_thickness = 30
        if state == EOGState.Up:
            pos = (0, Window.height - bar_thickness)
            size = (Window.width, bar_thickness)
            self.draw_box(pos, size, Color(0, 1, 1, 1))
        elif state == EOGState.Left:
            pos = (0, 0)
            size = (bar_thickness, Window.height)
            self.draw_box(pos, size, Color(0.5, 0.5, 0.5, 1))
        elif state == EOGState.Down:
            pos = (0, 0)
            size = (Window.width, bar_thickness)
            self.draw_box(pos, size, Color(1, 1, 0, 1))
        elif state == EOGState.Right:
            pos = (Window.width - bar_thickness, 0)
            size = (bar_thickness, Window.height)
            self.draw_box(pos, size, Color(0, 1, 0, 1))
        elif state == EOGState.Calibrating:
            pos = (Window.width / 2 - bar_thickness * 3, Window.height / 2 - bar_thickness * 3)
            size = (bar_thickness * 6, bar_thickness * 6)
            self.draw_box(pos, size, Color(1, 0, 0, 1))
        elif state == EOGState.Mid:
            pos = (Window.width / 2 - bar_thickness, Window.height / 2 - bar_thickness)
            size = (bar_thickness * 2, bar_thickness * 2)
            self.draw_box(pos, size, Color(1, 0, 1, 1))
        else:
            self.boxes.clear()

    def draw_box(self, pos, size, color):
        self.boxes.clear()
        self.boxes.add(color)
        self.boxes.add(Rectangle(pos=pos, size=size))


##############################################################################


class ExperimentsApp(App):
    painter = None

    def __init__(self):
        global painter
        painter = ExperimentsWidget()
        Window.fullscreen = True
        super(ExperimentsApp, self).__init__()

    def build(self):
        global painter
        parent = Widget()
        parent.add_widget(painter)
        return parent

    def draw(self, state):
        global painter
        if state == EOGState.Up:
            painter.draw_up()
        elif state == EOGState.Left:
            painter.draw_left()
        elif state == EOGState.Down:
            painter.draw_down()
        elif state == EOGState.Right:
            painter.draw_right()
        elif state == EOGState.Mid:
            painter.draw_mid()

        painter.drawState(state)

    def set_file_name(self, filename):
        global painter
        painter.fileName = filename

#############################################################################
if __name__ == '__main__':
    from kivy.core.window import Window
    Window.fullscreen = True
    ExperimentsApp().run()

