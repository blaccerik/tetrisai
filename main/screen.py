import mss
import cv2
import numpy as np
import time
from find_moves import Moves
from logic import Logic
import pyautogui
import pydirectinput

pyautogui.PAUSE = 0
# pyautogui.FAILSAFE = False
# pyautogui.
# pyautogui.

from PIL import Image
# import win32com.client
# import win32gui, win32api, win32con

class Screen:
    def __init__(self):
        self.sct = mss.mss()
        self.width = 10
        self.height = 20
        self.start = 13 + 175
        self.change = 26
        self.threshold = 10
        # 0: [][]
        #      [][]

        # 1:   [][]
        #    [][]

        # 2:   []
        #    [][][]

        # 3:     []
        #    [][][]

        # 4: []
        #    [][][]

        # 5: [][][][]

        # 6: [][]
        #    [][]
        # color values of the blocks
        self.color_values = {
            106: 0,
            143: 1,
            124: 2,
            131: 3,
            139: 4,
            168: 5,
            146: 6
        }
        self.color_on_board_to_id = {
            78: 2,
            128: 6,
            22: 0,
            106: 3,
            162: 5,
            131: 4,
            137: 1
        }


        self.id_to_block = [
            np.array([[1, 1, 0], [0, 1, 1], [0, 0, 0]]),
            np.array([[0, 1, 1], [1, 1, 0], [0, 0, 0]]),
            np.array([[0, 1, 0], [1, 1, 1], [0, 0, 0]]),
            np.array([[0, 0, 1], [1, 1, 1], [0, 0, 0]]),
            np.array([[1, 0, 0], [1, 1, 1], [0, 0, 0]]),
            np.array([[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]]),
            np.array([[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]])
        ]
        self.moves = Moves(self.id_to_block)
        self.logic = Logic()

    def show(self, array, next_id, hold_id):
        string = ""
        if array is not None:
            for i in range(self.height):
                for j in range(self.width):
                    value = array[i, j]
                    if value == 1:
                        string += "[]"
                    else:
                        string += "__"
                string += "\n"

        if next_id is not None and hold_id is not None:
            string += "NEXT______HOLD_____\n"
            if next_id is None:
                block = [[0]]
            else:
                block = self.id_to_block[next_id]
            if hold_id is None:
                hold = [[0]]
            else:
                hold = self.id_to_block[hold_id]

            for i in range(3):
                add = ""
                if i < len(block):
                    for j in block[i]:
                        if j == 1:
                            add += "[]"
                        else:
                            add += "__"
                add = '{:10}'.format(add)
                if i < len(hold):
                    for j in hold[i]:
                        if j == 1:
                            add += "[]"
                        else:
                            add += "__"
                add = '{:20}'.format(add)
                add += "\n"
                string += add
        print(string)

    def take_picture(self, monitor):
        return cv2.cvtColor(np.array(self.sct.grab(monitor)), cv2.COLOR_RGBA2GRAY)

    def get_data_from_picture(self, current_queue, t):

        monitor = {"top": 282, "left": 600, "width": 430, "height": 520}
        array = None
        next_queue = []
        # print()

        # check if the queue has moved, if has then means board has been updated
        while next_queue == current_queue or len(next_queue) == 0:

            # get blocks data
            picture = self.take_picture(monitor)

            array = np.zeros([self.height, self.width], dtype=int)
            width = 13
            for i in range(self.width):
                height = 13
                for j in range(self.height):
                    value = picture[height, width]
                    picture[height, width] = 255
                    if value > self.threshold:
                        array[j, i] = 1
                    height += self.change
                width += self.change

            # check if there is a uncleared "1" row
            # todo dont know if this is needed
            remove = [0,1,2,3]
            for i in range(len(array)):
                row = array[i]
                if np.all(row == 1):
                    remove.append(i)
            remove.reverse()
            for i in remove:
                array = np.delete(array, i, 0)

            while len(array) < 20:
                array = np.insert(array, 0, np.zeros(10), 0)

            # get 3 next block values
            next_id1 = None
            next_id2 = None
            next_id3 = None
            value = picture[105, 395]
            if value in self.color_values:
                next_id1 = self.color_values[value]
            value = picture[105 + 68, 395]
            if value in self.color_values:
                next_id2 = self.color_values[value]
            value = picture[105 + 68 + 68, 395]
            if value in self.color_values:
                next_id3 = self.color_values[value]

            next_queue = [next_id1, next_id2, next_id3]


            # cv2.imshow("picture", picture)
            # if cv2.waitKey(25) & 0xFF == ord("q"):
            #     cv2.destroyAllWindows()
            #     return

            time.sleep(0.001)
        return array, next_queue

    def press(self, key):

        # pyautogui.keyDown(key)
        # for i in range(times):
        #     time.sleep(0.02)
        # time.sleep(0.005)
        pyautogui.press(key)
        # 20 ms for game
        time.sleep(0.04)  # 0.05 is stable only 1 mistake -> 153k
        # 0.04 is kinda 2 mistakes -> 152k

        # pyautogui.keyUp(key)
        # time.sleep(0.05)
        # pyautogui.press(key)

    def press_keys(self, data, current_id, hold_id):
        move = data.move
        b_id = data.block_id
        rot = data.rotation
        # switch to hold
        if b_id == hold_id:
            self.press('c')
        if rot == 3:
            self.press('x')
        else:
            for i in range(rot):
                self.press('z')
        while move != 0:
            if move > 0:
                move -= 1
                self.press('right')
            elif move < 0:
                move += 1
                self.press('left')
        self.press('space')
        if b_id == hold_id:
            return current_id
        else:
            return hold_id

    def main(self):

        # hold_id = None
        time.sleep(5)

        prev_img = None
        prev_array = None
        prev_combo = None
        current_id = None
        hold_id = None
        next_queue = []
        current_queue = []

        for t in range(1000):
            print("info", t)
            array, next_queue = self.get_data_from_picture(current_queue, t)

            print(f"next: {next_queue} h: {hold_id} c: {current_id}")

            m = True
            # make dummy move so hold and block are not None
            if hold_id is not None and current_id is not None:

                start = time.time()
                data = self.logic.scorer(self.moves.find_all_possible_moves(array, current_id, hold_id))

                if prev_img is not None:
                    for i in prev_img:
                        if np.all(i == 1):
                            m = False
                            break

                if not np.array_equal(array, prev_img) and m:
                    print("------")
                    self.show(array, None, None)

                    self.show(prev_img, None, None)

                    # print(prev_array)
                    #
                    # print(prev_combo)
                    # print(prev_img)
                    # print(values[0], values[1], values[2])
                    # if t > 10:
                    #     return

                prev_img = data.array
                hold_id = self.press_keys(data, current_id, hold_id)

                end = time.time()
                print("took", end - start)

            if current_id is None:
                self.press("space")
            elif hold_id is None:
                self.press("c")
                hold_id = current_id

            current_queue = next_queue
            current_id = current_queue[0]


if __name__ == '__main__':
    # time.sleep(5)

    # time.sleep(5)
    # s = Screen()
    # for ii in range(10):
    #     for i in range(4):
    #         s.press("z")
    #     # s.press("c")
    #     for i in range(3):
    #         # s.press("z")
    #         s.press("right")
    #     # for i in range(3):
    #     #     s.press("left")
    #     s.press("space")
    #     time.sleep(0.05)

    s = Screen()
    s.main()

    # array = np.zeros([s.height, s.width], dtype=int)

    # # # array = c c c c c  np.arangec(200).reshape(20, -1)
    # # # print(array)
    # for i in range(10):
    #     array[19, i] = 1
    #     array[18, i] = 1
    #     array[17, i] = 1
    # array[19, 0] = 0
    # array[18, 0] = 0
    # array[17, 0] = 0
    # # array[18, 1] = 1
    # # array[19, 2] = 1
    # # array[19, 0] = 1
    # # array[19, 3] = 1
    # # array[19, 4] = 1
    # # array[19, 5] = 1
    # # array[19, 6] = 1
    # # array[19, 7] = 1
    # # array[19, 8] = 1
    # # array[19, 9] = 1
    # #
    # # # a = np.array([[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]])
    # # a = s.id_to_block[3]
    # # a = np.rot90(a, k=1)
    # #
    #
    # s.moves.find_all_possible_moves(arr, 1, 1)
    # #
    # # # target = 1
    # # # s.make_move(array, a, target)
    # # # print(a)
