import numpy as np
import random


class Logic:
    def __init__(self):
        pass

    def scorer(self, values):
        best_choice = None
        best_score = -99999999
        for data in values:
            array = data.array
            lines = 0
            for row in array:
                if np.all(row == 1):
                    lines += 1

            array = np.transpose(array)
            height = 0
            holes = 0
            bumpiness = 0
            prev = 0
            h0 = False

            for row in array:
                mark = True
                h = 0

                for i in range(len(row)):
                    if row[i] == 1 and mark:
                        h = 20 - i
                        height += h
                        mark = False
                    elif row[i] == 0 and not mark:
                        holes += 1
                if not h0:
                    bumpiness -= h
                    h0 = True
                bumpiness += abs(prev - h)
                prev = h

            a = -0.510066
            b = 0.760666
            c = -0.35663
            d = -0.184483

            score = a * height + b * lines + c * holes + d * bumpiness
            if score > best_score:
                best_choice = data
                best_score = score
        return best_choice

if __name__ == '__main__':
    l = Logic()
    array = np.zeros([20, 10], dtype=int)
    array[19, 1] = 1
    array[19, 2] = 1
    array[18, 1] = 1
    array[17, 9] = 1

    l.scorer([(array, 0,0,0)])


