from sklearn.neighbors.nearest_centroid import NearestCentroid
import pandas


def get_model_result():
    sample = pandas.read_csv("sample_data.csv")
    X = sample[["x0", "y1"]]
    y = sample["group"]
    clf = NearestCentroid()
    clf.fit(X, y)
    return clf
