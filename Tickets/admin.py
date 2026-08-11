from django.contrib import admin
from .models import *


admin.site.register(SLAPolicy)
admin.site.register(Ticket)
admin.site.register(TicketHistory)
admin.site.register(TicketComment)