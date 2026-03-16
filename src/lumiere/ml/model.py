import numpy as np
from sklearn.decomposition import TruncatedSVD

class LumiereSVD:
    def __init__(self, n_components=50, random_state=42):
        self.n_components = n_components
        self.random_state = random_state
        self.model = TruncatedSVD(n_components=self.n_components, random_state=self.random_state)
        self.user_means = None
        self.user_idx_map = {}
        self.movie_idx_map = {}
        self.user_features = None
        self.item_features = None

    def fit(self, ratings_df, target_col="Rating"):
        pivot_df = ratings_df.pivot(index="UserID", columns="MovieID", values=target_col)
        self.user_idx_map = {user_id: idx for idx, user_id in enumerate(pivot_df.index)}
        self.movie_idx_map = {movie_id: idx for idx, movie_id in enumerate(pivot_df.columns)}
        R = pivot_df.values
        self.user_means = np.nanmean(R, axis=1)
        R_demeaned = np.nan_to_num(R - self.user_means.reshape(-1, 1), nan=0.0)
        self.user_features = self.model.fit_transform(R_demeaned)
        self.item_features = self.model.components_

    def predict_est(self, uid, iid):
        if uid not in self.user_idx_map or iid not in self.movie_idx_map:
            return 3.0
        u_idx = self.user_idx_map[uid]
        i_idx = self.movie_idx_map[iid]
        prediction = self.user_means[u_idx] + np.dot(self.user_features[u_idx, :], self.item_features[:, i_idx])
        return np.clip(prediction, 1.0, 5.0)