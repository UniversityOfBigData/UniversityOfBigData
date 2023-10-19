from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _

from .models import LogBox, ManagementLogBox
# Create your views here.
class LogBoxListView(LoginRequiredMixin, ListView):
    """「ユーザーログ一覧」ページ."""

    template_name = 'view_log.html'
    model = LogBox

    def get_context_data(self, *args, **kwargs):
        context = super(LogBoxListView, self).get_context_data(*args, **kwargs)
        my_objects = self.get_object()
        objects = []
        for obj in my_objects:
            obj_dict = {}
            obj_dict['name'] = obj.name
            log_field = obj.log_field
            manage_logs = log_field.replace('\r', '')
            log_field_list = manage_logs.split(', \n')
            log_field_list.reverse()
            obj_dict['log_field'] = log_field_list
            objects.append(obj_dict)
        context['objects'] = objects
        return context

    def get_object(self):
        try:
            my_object = LogBox.objects.all()
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))


class ManagementLogBoxListView(LoginRequiredMixin, ListView):
    """「管理ログ一覧」ページ."""

    template_name = 'view_management_log.html'
    model = ManagementLogBox

    def get_context_data(self, *args, **kwargs):
        context = super(ManagementLogBoxListView, self).get_context_data(
                *args, **kwargs)
        my_object = self.get_object()
        obj = my_object
        objects = []
        obj_dict = {}
        obj_dict['name'] = obj.name
        log_field = obj.log_field
        manage_logs = log_field.replace('\r', '')
        log_field_list = manage_logs.split(', \n')
        log_field_list.reverse()
        obj_dict['log_field'] = log_field_list
        objects.append(obj_dict)
        context['objects'] = objects
        return context

    def get_object(self):
        try:
            my_object = ManagementLogBox.objects.get(name='management_log')
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))