import numpy as np


class Data:
    def __init__(self, array, move, rotation, block_id):
        self.array = array
        self.move = move
        self.rotation = rotation
        self.block_id = block_id

    def str(self):
        return f"R: {self.rotation} M: {self.move} B: {self.block_id}"

class Moves:

    def __init__(self, id_to_block):
        self.blocks_start_col = 3
        self.blocks_start_height = 0
        self.width = 10
        self.height = 20
        self.id_to_block = id_to_block

    def remove_row(self, block):
        count = 0
        block = block[~np.all(block == 0, axis=1)]
        idx = np.argwhere(np.all(block[..., :] == 0, axis=0))
        count_next = 1
        for i in idx:
            if i + 1 != count_next:
                break
            count += 1
            count_next += 1
        block = np.delete(block, idx, axis=1)
        return block, count

    def try_area(self, block_w, block_h, start, start_height, block, array):
        if start_height + block_h > self.height:
            return False
        for i in range(block_w):
            for j in range(block_h):
                x, y = start + i, start_height + j
                block_val = block[j, i]
                array_val = array[y, x]
                if block_val == 1 and array_val == 1:
                    return False
        return True

    def down_until_one(self, array, block, start):
        start_height = self.blocks_start_height
        block_w = len(block[0])
        block_h = len(block)

        # check if at wall
        if start + block_w > self.width:
            return None

        # simulate block going down
        while True:
            if self.try_area(block_w, block_h, start, start_height + 1, block, array):
                start_height += 1
            else:
                break

        # place block
        for i in range(block_w):
            for j in range(block_h):
                x, y = start + i, start_height + j
                array[y, x] = block[j, i] + array[y, x]
        return array

    def make_move(self, array, block, target_col):
        """
        move: -x: left, x: right
        """

        # remove useless 0's
        block, count = self.remove_row(block)

        # find piece left most 1 col coord
        real = self.blocks_start_col + count
        move = target_col - real

        # place block on array on start coord, start moving down
        array = self.down_until_one(array, block, target_col)
        return array, move

    def find_all_possible_moves(self, array, block_id, hold_id):
        o_block = self.id_to_block[block_id]
        o_hold = self.id_to_block[hold_id]
        all_places = []
        blocks = [(o_block, block_id), (o_hold, hold_id)]

        for block, b_id in blocks:

            if b_id == 6:
                rot = 1
            elif b_id == 0 or b_id == 1 or b_id == 5:
                rot = 2
            else:
                rot = 4
            for rotation in range(rot):
                for col in range(10):
                    array_copy = np.array(array, copy=True)
                    block_copy = np.array(block, copy=True)
                    array_copy, move = self.make_move(array_copy, block_copy, col)
                    data = Data(array_copy, move, rotation, b_id)
                    if data.array is not None:
                        # print(result)
                        all_places.append(data)
                block = np.rot90(block, k=1)
        # print(all_places)
        return all_places
