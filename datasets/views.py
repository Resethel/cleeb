from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from datasets.models import Dataset, DatasetCategory


# ======================================================================================================================
# Dataset Main view (search)
# ======================================================================================================================

class DatasetsSearchView(ListView):

    model = Dataset
    template_name = 'datasets/datasets_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = DatasetCategory.objects.all()

        # Add to the context which category is selected
        category = self.request.GET.get('category')
        context['selected_category'] = DatasetCategory.objects.get(slug=category) if category else None

        # Add to the context the search query
        search = self.request.GET.get('search')
        context['search'] = search if search else None


        return context

    def get_queryset(self):
        datasets = Dataset.objects.filter(public=True)

        # Filter by category
        category = self.request.GET.get('category')
        if category:
            categories = DatasetCategory.objects.filter(slug=category)


            datasets = datasets.filter(categories__in=categories)

        # Filter by search query
        search = self.request.GET.get('search')
        if search:
            # TODO: add search by category
            datasets = datasets.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        return datasets
# End def datasets_filter_view

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