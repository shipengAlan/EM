#! /usr/bin/env python
#coding=utf-8

from EM.EM import EM
import sys


def MajorityVote(filename, compare_file):
    image = {}
    with open(filename, 'r') as f:
        line = f.readline()
        # 第一行为参数，标签数量，标记者、图片数量，先验图片的真实类别为1的概率
        params = line.split(' ')
        numLabels = int(params[0])
        # numLabelers = int(params[1])
        # numImages = int(params[2])
        for i in range(0, numLabels):
            line = f.readline()
            items = line.rstrip('\n').split(' ')
            image_id = int(items[0])
            # labeler_id = int(items[1])
            label = int(items[2])
            if str(image_id) not in image:
                image[str(image_id)] = 0
            if label == 1:
                image[str(image_id)] += 1
            else:
                image[str(image_id)] -= 1
    count = 0
    TP = 0
    TN = 0
    FN = 0
    FP = 0
    with open(compare_file, 'r') as f:
        while 1:
            line = f.readline()
            if not line:
                break
            result = line.strip('\n')
            if result == '1' and image[str(count)] >= 0:
                TP += 1
            if result == '1' and image[str(count)] < 0:
                FN += 1
            if result == '0' and image[str(count)] < 0:
                TN += 1
            if result == '0' and image[str(count)] >= 0:
                FP += 1
            count += 1
        A = float(TP + TN) / (TP + FN + TN + FP)
        P = float(TP) / (TP + FP)
        R = float(TP) / (TP + FN)
        F = 2.0 * float(TP) / (2 * TP + FP + FN)
        print 'Accuracy:', A
        print 'Precision:', P
        print 'Recall:', R
        print 'F1 score:', F
        return A, P, R, F


if __name__ == '__main__':
    input_file = 'Tag_data.txt'
    truth_file = 'Tag_truth.txt'
    #input_file = 'Wiki_data.txt'
    #truth_file = 'Wiki_truth.txt'
    em = EM(filename=input_file, compare_file=truth_file, output='EMresult.txt')
    em.Main()
    print 'Majority Vote'
    MajorityVote(filename=input_file, compare_file=truth_file)
    