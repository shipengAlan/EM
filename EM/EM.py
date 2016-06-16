#! /usr/bin/env python
#coding=utf-8
from Data import Data
import math


def Beta(betaJ):
    return math.exp(betaJ)


def log(inParam):
    return math.log(inParam, math.e)


def exp(inParam):
    return math.exp(inParam)


class EM(object):
    """docstring for EM"""
    def __init__(self, filename, compare_file, output='result.txt'):
        self.filename = filename
        self.output = output
        self.compare_file = compare_file

    def logP(self, lij, Z, alphaI, betaJ):
        if lij == Z:
            return -1 * log(1.0 + exp(-1.0 * alphaI * Beta(betaJ)))
        else:
            return -1 * log(1.0 + exp(alphaI * Beta(betaJ)))

    def Estep(self, data):
        # 计算隐变量Z的概率
        # 技巧：先log在e幂
        for j in range(data.numImages):
            data.probZ1[j] = math.log(data.priorZ1[j])
            data.probZ0[j] = math.log(1.0 - data.priorZ1[j])
        for k in range(data.numLabels):
            j = data.labelset[k]['image']
            i = data.labelset[k]['labeler']
            lij = data.labelset[k]['label']
            data.probZ1[j] += self.logP(lij, 1, data.alpha[i], data.beta[j])
            data.probZ0[j] += self.logP(lij, 0, data.alpha[i], data.beta[j])

        # 还原e幂，并归一化
        for j in range(data.numImages):
            data.probZ1[j] = exp(data.probZ1[j])
            data.probZ0[j] = exp(data.probZ0[j])
            # 归一化
            data.probZ1[j] = data.probZ1[j] / (data.probZ1[j] + data.probZ0[j])
            data.probZ0[j] = 1.0 - data.probZ1[j]

    def logistic(self, x):
        return 1.0 / (1 + exp(-x))

    def logSigma(self, alphaI, betaJ):
        return -1 * log(1.0 + exp(-1.0 * alphaI * Beta(betaJ)))

    def logOneMinusSigma(self, alphaI, betaJ):
        return -1 * log(1.0 + exp(alphaI * Beta(betaJ)))

    def computeQ(self, data):
        Q = 0
        for j in range(data.numImages):
            Q += data.probZ1[j] * log(data.priorZ1[j]) + data.probZ0[j] * log(1 - data.priorZ1[j])
        for k in range(data.numLabels):
            i = data.labelset[k]['labeler']
            j = data.labelset[k]['image']
            lij = data.labelset[k]['label']
            alpha = data.alpha[i]
            beta = data.beta[j]
            log_sigma = 0
            log_one_minus_sigma = 0
            try:
                log_sigma = self.logSigma(alpha, beta)
            except OverflowError:
                log_sigma = exp(beta) * alpha
            try:
                log_one_minus_sigma = self.logOneMinusSigma(alpha, beta)
            except OverflowError:
                log_one_minus_sigma = -1.0 * exp(beta) * alpha
            Q += data.probZ1[j] * (lij * log_sigma + (1 - lij) * log_one_minus_sigma)
            Q += data.probZ0[j] * ((1 - lij) * log_sigma + lij * log_one_minus_sigma)
        return Q

    def deltaAlphaBeta(self, data):
        dA = []
        dB = []
        for i in range(data.numLabelers):
            dA.append(-(data.alpha[i] - data.priorAlpha[i]))
        for j in range(data.numImages):
            dB.append(-(data.beta[j] - data.priorBeta[j]))
        for k in range(data.numLabels):
            i = data.labelset[k]['labeler']
            j = data.labelset[k]['image']
            lij = data.labelset[k]['label']
            sigma = self.logistic(data.alpha[i] * Beta(data.beta[j]))
            dA[i] += (data.probZ1[j] * lij + data.probZ0[j] * (1 - lij) - sigma) * Beta(data.beta[j])
            dB[j] += (data.probZ1[j] * lij + data.probZ0[j] * (1 - lij) - sigma) * data.alpha[i] * Beta(data.beta[j])
        return dA, dB

    def Mstep(self, data):
        # 取参数 alpha 和 beta 使得 Q 取得极值
        iterator = 0
        l = 0.01
        threshold = 1
        while 1:
            lastQ = self.computeQ(data)
            dA, dB = self.deltaAlphaBeta(data)
            # 更新alpha 和 beta
            for i in range(data.numLabelers):
                data.alpha[i] += l * dA[i]
            for j in range(data.numImages):
                data.beta[j] += l * dB[j]
            Q = self.computeQ(data)
            if Q - lastQ < threshold:
                break
            iterator += 1
            print 'iterator', iterator

    def outputResult(self, data):
        with open(self.output, 'w') as out:
            for i in range(data.numLabelers):
                out.write('Alpha[%s] = %s\n' % (str(i), str(self.logistic(data.alpha[i]))))
            for j in range(data.numImages):
                out.write('Beta[%s] = %s\n' % (str(j), str(exp(data.beta[j]))))
            for j in range(data.numImages):
                out.write('P(Z(%s)=1) = %s\n' % (str(j), str(data.probZ1[j])))
        with open('label.txt', 'w') as out:
            for j in range(data.numImages):
                if data.probZ1[j] > 0.5:
                    out.write('1\n')
                else:
                    out.write('0\n')

    def compare(self, data):
        count = 0
        TP = 0
        TN = 0
        FN = 0
        FP = 0
        real_result = []
        with open(self.compare_file, 'r') as f:
            while 1:
                line = f.readline()
                if not line:
                    break
                result = line.strip('\n')
                if result == '1' and data.probZ1[count] > 0.5:
                    TP += 1
                if result == '1' and data.probZ1[count] <= 0.5:
                    FN += 1
                if result == '0' and data.probZ0[count] > 0.5:
                    TN += 1
                if result == '0' and data.probZ0[count] <= 0.5:
                    FP += 1
                real_result.append(result)
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

    def Main(self):
        data = Data(self.filename)
        self.threshold = 0.001
        # 初始化
        for i in range(data.numLabelers):
            data.alpha[i] = data.priorAlpha[i]
        for j in range(data.numImages):
            data.beta[j] = data.priorBeta[j]
        self.Estep(data)
        Q = self.computeQ(data)
        step = 0
        while 1:
            lastQ = Q
            self.Mstep(data)
            Q = self.computeQ(data)
            if abs((lastQ - Q) / lastQ) < self.threshold:
                break
            self.Estep(data)
            # print 'EM step', step,',Q ', Q, ',lastQ ', lastQ
            print 'EM step', step, abs((lastQ - Q)/lastQ)
            step += 1
        self.outputResult(data)
        return self.compare(data)


