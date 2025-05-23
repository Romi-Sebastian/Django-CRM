from django.contrib import admin
from .models import Record, Note, Task, RecordFile

admin.site.register(Record)
admin.site.register(Note)
admin.site.register(Task)
admin.site.register(RecordFile)
