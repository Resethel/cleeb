from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.text import slugify
from django.views.generic import DetailView, ListView

from datasets.models import Dataset, DatasetCategory, DatasetVersion


# ======================================================================================================================
# Dataset Main view (search)
# ======================================================================================================================

class DatasetsIndexView(ListView):

    model = Dataset
    template_name = 'datasets/dataset_index.html'

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
    template_name = 'datasets/dataset.html'
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

# ======================================================================================================================
# Dataset Download View
# ======================================================================================================================

def dataset_version_download_view(request: HttpRequest, slug: str, pk: int) -> HttpResponse:

    # Find the dataset mentioned by the slug
    dataset = Dataset.objects.get(slug=slug)
    if not dataset:
        return HttpResponse('Aucun jeu de données trouvé', status=404)

    # Find the version of the dataset
    if not pk:
        return HttpResponse('Aucune version de jeu de données spécifiée', status=400)

    data = DatasetVersion.objects.get(pk=pk)
    if not data:
        return HttpResponse('Aucune version de jeu de données trouvée', status=404)

    # Builds the file name for the dataset to get
    parent_name = data.dataset.name
    all_versions : QuerySet = data.dataset.versions.all()
    # Find which version is this one
    version = 1
    for v in all_versions:
        if v.date < data.date:
            version += 1
    file_name = f"{slugify(parent_name)}_v{version}.zip"

    response = HttpResponse(data.file, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    return response
# End def dataset_version_download_view
