# Copyright 2019 The OpenSDS Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import multivariate_normal
from sklearn.metrics import f1_score
from anomaly_detection.ml import dataset as ds
from anomaly_detection.ml.algorithm import AlgorithmBase
from anomaly_detection.ml import contants
import json


def feature_normalize(dataset):
    mu = np.mean(dataset, axis=0)
    sigma = np.std(dataset, axis=0)
    return (dataset - mu) / sigma


def estimate_gaussian(dataset):
    mu = np.mean(dataset, axis=0)
    sigma = np.cov(dataset.T)
    return mu, sigma


def multivariate_gaussian(dataset, mu, sigma):
    p = multivariate_normal(mean=mu, cov=sigma)
    return p.pdf(dataset)


def select_threshold_by_cv(probs,gt):
    best_epsilon = 0
    best_f1 = 0
    step_size = (max(probs) - min(probs)) / 1000
    epsilons = np.arange(min(probs), max(probs), step_size)
    for epsilon in np.nditer(epsilons):
        predictions = (probs < epsilon)
        f = f1_score(gt, predictions, average="binary")
        if f > best_f1:
            best_f1 = f
            best_epsilon = epsilon
    return best_f1, best_epsilon


class Gaussian(AlgorithmBase):
    def __init__(self):
        super(Gaussian, self).__init__(algorithm_name=contants.GAUSSIAN_MODEL)

    def create_training(self, training):
        cv_data = ds.read('../dataset/performance-cv.csv')
        gt_data = ds.read('../dataset/performance-gt.csv')
        tr_data = ds.read('../dataset/performance-tr.csv')
        mu, sigma = estimate_gaussian(tr_data)
        p_cv = multivariate_gaussian(cv_data, mu, sigma)
        f1score, ep = select_threshold_by_cv(p_cv, gt_data)
        model_update = {"mu": mu, "sigma": sigma, "epsilon": ep, "f1_score": f1score}
        return model_update

    def get_training_pic(self, training):
        test_data = ds.read('../dataset/performance-tr.csv')
        md = json.loads(training.metadata)
        mu = md.get("mu")
        sigma = md.get("sigma")
        ep = md.get("epsilon")

        p = multivariate_gaussian(test_data, mu, sigma)
        outliers = np.asarray(np.where(p < ep))
        plt.figure()
        plt.xlabel("Latency (ms)")
        plt.ylabel("Throughput (mb/s)")
        plt.plot(test_data[:, 0], test_data[:, 1], "bx")
        plt.plot(test_data[outliers, 0], test_data[outliers, 1], "ro")
        plt.imsave()

    def prediction(self, training, dataset):
        return dataset

    def get_prediction_pic(self, training, dataset):
        pass