from django.shortcuts import render
from django.views.generic import DetailView

from datasets.models import Dataset


# ======================================================================================================================
# Dataset Detail View
# ======================================================================================================================

class DatasetDetailView(DetailView):
    model = Dataset
    template_name = 'datasets/datasets_detail.html'
    context_object_name = 'dataset'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dataset_versions'] = []
        for version in context['object'].versions.all():
            v = {'id': version.id, 'date': version.date.strftime("%d %B %Y"), 'file': version.file}
            context['dataset_versions'].append(v)
        #
        # for version in context['dataset'].versions.all():
        #     version.date = version.date.strftime("%d %B %Y")
        #
        # print(context)
        return context
# End class DatasetDetailView