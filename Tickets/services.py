from django.utils import timezone


def check_sla_breach(ticket):

    if ticket.status in ['Resolved', 'Closed']:
        return False

    if ticket.resolution_due_at:

        if timezone.now() > ticket.resolution_due_at:
            return True

    return False