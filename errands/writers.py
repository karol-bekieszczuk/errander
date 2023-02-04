import csv
from django.http import StreamingHttpResponse


class CSVBuffer:
    def write(self, value):
        return value


class CSVStream:
    def export(self, filename, iterator):
        writer = csv.writer(CSVBuffer())
        response = StreamingHttpResponse((writer.writerow(data) for data in iterator),
                                         content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={filename}.csv'

        return response
