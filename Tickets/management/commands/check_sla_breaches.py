from django.core.management.base import BaseCommand

from Tickets.models import Ticket
from Tickets.utils import check_sla_breach


class Command(BaseCommand):

    help = "Check SLA breaches for active tickets"

    def handle(self, *args, **kwargs):

        tickets = Ticket.objects.filter(
            status__in=[
                "Open",
                "In Progress",
                
            ]
        )

        checked = 0
        breached = 0

        for ticket in tickets:

            was_breached = ticket.is_breached

            check_sla_breach(ticket)

            checked += 1

            if ticket.is_breached:

                breached += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Ticket #{ticket.id} - SLA BREACHED"
                    )
                )

            elif not was_breached:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Ticket #{ticket.id} - SLA OK"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nChecked: {checked} tickets"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f"Breached: {breached} tickets"
            )
        )