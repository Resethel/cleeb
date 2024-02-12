# -*- coding: utf-8 -*-
"""
Filters for the core application.
"""
from django.contrib.admin import SimpleListFilter
from django.db.models import Q

from core.models import Organization, Person


# ======================================================================================================================
# Person (Author, Contributor, etc.) filters
# ======================================================================================================================

class PersonFullNameFilter(SimpleListFilter):
    """Filter for the `Person` model's organizations."""
    title = "Nom complet"
    parameter_name = "full_name"

    def lookups(self, request, model_admin):
        """Return the list of tuples to use as choices for the filter."""
        return (
            ('a-g', "A-G"),
            ('h-n', "H-N"),
            ('o-t', "O-T"),
            ('u-z', "U-Z"),
        )

    def queryset(self, request, queryset) -> Q:
        """Return the filtered queryset."""
        all_models = Person.objects.all()
        match = set()
        first_char_map = {
            'a-g': "abcdefg",
            'h-n': "hijklmn",
            'o-t': "opqrst",
            'u-z': "uvwxyz"
        }

        first_chars = first_char_map.get(self.value())
        if first_chars is not None:
            for model in all_models:
                if model.full_name.casefold()[0] in first_chars:
                    match.add(model.id)
        else:
            return queryset

        return queryset.filter(id__in=match)
    # End def queryset
# End class PersonFullNameFilter


class PersonOrganizationsFilter(SimpleListFilter):
    """Filter for the `Person` model's organizations."""
    title = "Organisations"
    parameter_name = "organizations"

    def lookups(self, request, model_admin):
        """Return the list of tuples to use as choices for the filter."""
        org_ids = Person.objects.all().values_list('organizations').distinct()
        val = tuple((org[0], Organization.objects.get(id=org[0]).name) for org in org_ids if org[0] is not None)
        return val

    def queryset(self, request, queryset) -> Q:
        """Return the filtered queryset."""
        if self.value():
            return queryset.filter(organizations__id=self.value())
        else:
            return queryset

    # End def queryset
# End class PersonOrganizationsFilter