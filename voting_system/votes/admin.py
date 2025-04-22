# votes/admin.py
from django.contrib import admin
from .models import Candidate, Vote, Result

class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'created_at')
    search_fields = ('name', 'title')

class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'candidate', 'voted_at')
    list_filter = ('candidate', 'voted_at')

class ResultAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'votes_count', 'is_published', 'published_at')
    list_editable = ('is_published',)
    actions = ['publish_results']

    def publish_results(self, request, queryset):
        for result in queryset:
            result.is_published = True
            result.save()
    publish_results.short_description = "Publish selected results"

admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Result, ResultAdmin)