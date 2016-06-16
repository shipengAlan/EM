#! /usr/bin/env python
#coding=utf-8


class Data(object):
    """docstring for Data"""
    def __init__(self, filename='data.txt'):
        self.readFile(filename)
        self.beta = []
        self.alpha = []
        self.probZ1 = []
        self.probZ0 = []
        self.priorZ1 = []
        self.priorBeta = []
        self.priorAlpha = []
        # 初始化为默认值
        for j in range(0, self.numImages):
            self.priorBeta.append(1.0)
            self.priorZ1.append(self.paramPriorZ1)
            self.beta.append(0)
            self.probZ0.append(0)
            self.probZ1.append(0)
        for i in range(0, self.numLabelers):
            self.priorAlpha.append(1.0)
            self.alpha.append(0)

    def readFile(self, filename):
        with open(filename, 'r') as f:
            line = f.readline()
            # 第一行为参数，标签数量，标记者、图片数量，先验图片的真实类别为1的概率
            params = line.split(' ')
            self.numLabels = int(params[0])
            self.numLabelers = int(params[1])
            self.numImages = int(params[2])
            self.paramPriorZ1 = float(params[3])
            self.labelset = []
            for i in range(0, self.numLabels):
                line = f.readline()
                items = line.rstrip('\n').split(' ')
                label_dict = {}
                label_dict['image'] = int(items[0])
                label_dict['labeler'] = int(items[1])
                label_dict['label'] = int(items[2])
                self.labelset.append(label_dict)

if __name__ == "__main__":
    data = Data()
