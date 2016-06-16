#! /usr/bin/env python
#coding=utf-8

from EM.EM import EM
import sys
import os
import time

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
    for k in [0.5, 1, 1.5, 2, 2.5]:
        sum_eA = 0
        sum_eP = 0
        sum_eR = 0
        sum_eF = 0
        sum_mA = 0
        sum_mP = 0
        sum_mR = 0
        sum_mF = 0
        print k
        for t in range(10):
            os.popen('python shuffle.py %s' % k)
            # time.sleep(2)
            input_file = 'Tag_data%s.txt' % str(k)
            truth_file = 'Tag_truth.txt'
            em = EM(filename=input_file, compare_file=truth_file, output='EMresult.txt')
            eA, eP, eR, eF = em.Main()
            print 'Majority Vote'
            mA, mP, mR, mF = MajorityVote(filename=input_file, compare_file=truth_file)
            sum_eA += eA
            sum_eP += eP
            sum_eR += eR
            sum_eF += eF
            sum_mA += mA
            sum_mP += mP
            sum_mR += mR
            sum_mF += mF
        sum_eA /= 10.0
        sum_eP /= 10.0
        sum_eR /= 10.0
        sum_eF /= 10.0
        sum_mA /= 10.0
        sum_mP /= 10.0
        sum_mR /= 10.0
        sum_mF /= 10.0
        print sum_eA, sum_eP, sum_eR, sum_eF
        print sum_mA, sum_mP, sum_mR, sum_mF