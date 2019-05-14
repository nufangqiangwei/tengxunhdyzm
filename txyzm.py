

class GetGap(object):
    def __init__(self, image):
        """
        :param image: 传入Image打开的图片文件对象，已经二值化之后的结果
        """
        self.image = image

    def get_rgb_fengbu(self, w1, w2, h1, h2):
        """
        获取给定区域内的所有像素点符合条件的像素点进行数量累加
        每一行为一个数值储存在列表中并返回这个列表
        """
        numbers = []
        for i in range(w1, w2):
            number = 0
            for j in range(h1, h2):
                rgb = self.image.load()[i, j]
                if rgb >= 100:  # 这里的取值最好和二值化的取值一样
                    number += 1
            numbers.append(number)
        return numbers

    def square(self, a):
        """
        查寻每一行中的白色像素点不少于20个
        符合条件的总行数大于20行就认定这个是一个都是白色方块构成的区域
        """
        x = [x for x in a if x > 9]
        return True if len(x) > 9 else False

    def bump(self, a):
        """
        判断是否为内凹方块
        判断依据是将列表分为两个部分进行是否增长判断，后半段的进行倒叙判断
        不符合条件的发去判读是否为纯白区域判断
        """
        x = a[0]
        if len(a) == 12:
            for i in a[1:6]:
                if i < x:
                    return self.square(a)
                x = i
            x = a[6]
            for i in a[6::-1]:
                if i < x:
                    return self.square(a)
                x = i
        else:
            for i in a[1:8]:
                if i < x:
                    return self.square(a)
                x = i
            x = a[8]
            for i in a[8::-1]:
                if i < x:
                    return self.square(a)
                x = i

        return True

    def verify(self, x, y, W, H):
        """
        验证坐标是否为验证码缺口，
        将图片切割为九个方块四个顶角和中间的直接验证是否大部分都是白色方块
        四个缺口验证白色方块数量是否为递增在递减，如不是的话发去正方形函数验证是否为白色正方形
        :param x y: 要验证的坐标
        :param W H: 图片的长与宽
        """
        if W < x + 40 or H < y + 40 or x < 40:
            return False

        valid = 0
        valid += 1 if self.square(self.get_rgb_fengbu(x, x + 12, y, y + 12)) else 0
        valid += 1 if self.bump(self.get_rgb_fengbu(x + 12, x + 28, y, y + 12)) else 0
        valid += 1 if self.square(self.get_rgb_fengbu(x + 28, x + 40, y, y + 12)) else 0

        valid += 1 if self.bump(self.get_rgb_fengbu(x, x + 12, y + 12, y + 28)) else 0
        valid += 1 if self.square(self.get_rgb_fengbu(x + 12, x + 28, y + 12, y + 28)) else 0
        valid += 1 if self.bump(self.get_rgb_fengbu(x + 28, x + 40, y + 12, y + 28)) else 0

        valid += 1 if self.square(self.get_rgb_fengbu(x, x + 12, y + 28, y + 40)) else 0
        valid += 1 if self.bump(self.get_rgb_fengbu(x + 12, x + 28, y + 28, y + 40)) else 0
        valid += 1 if self.square(self.get_rgb_fengbu(x + 28, x + 40, y + 28, y + 40)) else 0

        if valid >= 7:
            return x - 10  # 因为小图有15的外边框所以减去10
        else:
            return False

    def loop_find(self):
        W, H = self.image.size
        for i in range(W):
            coordinate = 0
            for j in range(H):
                # 竖直方向查找找到有一条明显高亮的线条为止
                rgb = self.image.load()[i, j]
                if rgb >= 100:
                    coordinate += 1
                    if coordinate == 12:
                        result = self.verify(i, j - 12, W, H)
                        if result:
                            return result
                        coordinate = 0
                elif coordinate > 0:
                    coordinate = 0


if __name__ == '__main__':
    image = ''
    print(GetGap(image).loop_find())
