from haystack import indexes
from .models import VideoInfo


class VideoInfoIndex(indexes.Indexable, indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return VideoInfo
