import csv


class ModelMetadata:

    def __init__(self):
        self.rows = []

    def build(self, valid_idxs, img_locations):
        for idx in valid_idxs:
            self.rows.append([img_locations[idx]])

    def save(self, path):
        csv.writer(open(path, "w")).writerows(self.rows)