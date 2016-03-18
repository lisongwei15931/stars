# -*- coding: utf-8 -*-
import django.dispatch


received_file_names_done = django.dispatch.Signal(providing_args=['file_names', 'the_day'])

download_files_done = django.dispatch.Signal(providing_args=['files', 'the_ady'])