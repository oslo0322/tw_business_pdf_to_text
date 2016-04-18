# from sklearn.neighbors.nearest_centroid import NearestCentroid
from sklearn.neighbors import KNeighborsClassifier
# from sklearn.neighbors import RadiusNeighborsClassifier
import pandas


def get_model_result():
    sample = pandas.read_csv("sample_data.csv")
    X = sample[["x0", "y1"]]
    y = sample["column"]
    clf = KNeighborsClassifier(1, weights="distance", algorithm="auto")
    clf.fit(X, y)
    return clf
