import csv

from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse

__all__ = ["ExportCsvMixin"]


class ExportCsvMixin:
    @staticmethod
    def batch_qs(qs, batch_size):
        count = qs.count()
        for i in range(0, count, batch_size):
            start = i
            yield i, count, qs[start : start + batch_size]

    def export_as_csv(self, request: HttpRequest, queryset: QuerySet) -> HttpResponse:
        meta = self.model._meta
        if hasattr(self, "export_fields"):
            field_names = self.export_fields
        else:
            field_names = [
                field.name for field in meta.fields if field.name != "password"
            ]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
        writer = csv.writer(response)
        writer.writerow(field_names)

        for current, total, qs in self.batch_qs(queryset, 500):
            for obj in qs:
                writer.writerow(
                    [
                        getattr(obj, field)
                        if hasattr(obj, field)
                        else getattr(self, field)(obj)
                        for field in field_names
                    ]
                )

        return response

    export_as_csv.short_description = "Export Selected"
