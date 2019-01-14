import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score


class KMeansClustering(object):
    NONE_CHAR = 'unknown'
    SEPARATOR = ';'

    def __init__(self, text_data, n_clusters=5):
        self.text_data = text_data
        self.n_clusters = n_clusters
        self.stop_words = [self.NONE_CHAR, self.SEPARATOR]
        self.vectorizer = TfidfVectorizer(stop_words=self.stop_words)

    def vectorize_text(self):
        return self.vectorizer.fit_transform(self.text_data)

    def solve(self, max_iter=100):
        model = KMeans(n_clusters=self.n_clusters, init='k-means++', max_iter=max_iter, n_init=1)
        prepared_data = self.vectorize_text()
        model.fit(prepared_data)
        return model

    def get_result(self):
        print("Top terms per cluster:")
        model = self.solve()
        order_centroids = model.cluster_centers_.argsort()[:, ::-1]
        terms = self.vectorizer.get_feature_names()
        for i in range(self.n_clusters):
            print(f"Cluster {i}:")
            for ind in order_centroids[i, :10]:
                print(f' {terms[ind]}')


if __name__ == '__main__':
    file_name = 'collection.txt'
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), file_name)) as f:
        content = f.readlines()
    data = [x.strip() for x in content]
    analysis_obj = KMeansClustering(text_data=data, n_clusters=10)
    analysis_obj.get_result()
