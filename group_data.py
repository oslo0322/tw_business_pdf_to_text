# from sklearn.neighbors.nearest_centroid import NearestCentroid
from sklearn.neighbors import KNeighborsClassifier
# from sklearn.neighbors import RadiusNeighborsClassifier
import pandas
import matplotlib.pyplot as plt
import numpy as np


def get_model_result():
    sample = pandas.read_csv("sample_data.csv")
    X = sample[["x0", "y1"]]
    y = sample["column"]
    clf = KNeighborsClassifier(1, weights="distance", algorithm="auto")
    clf.fit(X, y)
    return clf


def plot_result(knn, step):
    sample = pandas.read_csv("sample_data.csv")
    sample = sample[sample["column"] < 10]
    X = sample[["x0", "y1"]]
    y = sample["column"]
    h = step
    knn = knn
    clf = KNeighborsClassifier(knn, weights="distance", algorithm="auto")
    clf.fit(X, y)

    x_min, x_max = X["x0"].min() - 50, X["x0"].max() + 50
    y_min, y_max = X["y1"].min() - 50, X["y1"].max() + 50
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))

    # xx, yy = np.meshgrid(X["x0"], X["y1"])
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    # Put the result into a color plot
    Z = Z.reshape(xx.shape)

    plt.figure(figsize=(16, 9), dpi=60)
    plt.pcolormesh(xx, yy, Z, cmap='gist_rainbow')
    # # Plot also the training points
    plt.scatter(X["x0"], X["y1"], c=y, cmap='gist_rainbow')
    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    plt.title("Classification Result (k = %s, weights = '%s')" % (knn, "distance"))
    plt.subplots_adjust(bottom=0.04, left=0.03, right=0.98, top=0.95)
    plt.savefig("KNN_%s_STEP_%s.png" % (knn, step))
    # plt.show()

if __name__ == "__main__":
    plot_result(knn=1, step=3)
    plot_result(knn=2, step=3)
    plot_result(knn=4, step=3)
    plot_result(knn=5, step=3)
    plot_result(knn=10, step=3)
