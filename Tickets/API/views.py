from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from Tickets.models import *
from .serializers import *
from Tickets.views import is_admin,is_engineer,is_customer
from .permissions import *
from Tickets.utils import calculate_sla
from django.db.models import Q
from .pagination import TicketPagination


class TicketViewSet(viewsets.ModelViewSet):

    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, TicketPermission]
    pagination_class = TicketPagination

    def get_queryset(self):

        user = self.request.user

        # Role-based queryset
        if is_admin(user):
            queryset = Ticket.objects.all()

        elif is_engineer(user):
            queryset = Ticket.objects.filter(
               Q(assigned_to=user)|
               Q(created_by=user)
            )

        elif is_customer(user):
            queryset = Ticket.objects.filter(
                created_by=user
            )

        else:
            return Ticket.objects.none()

        # Filter by status
        status = self.request.query_params.get("status")

        if status:
            queryset = queryset.filter(
                status=status
            )

        # Filter by priority
        priority = self.request.query_params.get("priority")

        if priority:
            queryset = queryset.filter(
                priority=priority
            )

        # Filter by SLA breach
        is_breached = self.request.query_params.get(
            "is_breached"
        )

        if is_breached:
            queryset = queryset.filter(
                is_breached=is_breached.lower() == "true"
            )

        search = self.request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        ordering = self.request.query_params.get("ordering")

        if ordering:
            allowed_fields = [
                "created_at",
                "priority",
                "status",
                "updated_at",
            ]

            field = ordering.lstrip("-")

            if field in allowed_fields:
                queryset = queryset.order_by(ordering)

        return queryset


    def perform_create(self, serializer):

        ticket = serializer.save(
            created_by=self.request.user
        )

        policy = SLAPolicy.objects.get(
            priority=ticket.priority
        )

        response_due, resolution_due = calculate_sla(
            ticket,
            policy
        )

        ticket.response_due_at = response_due
        ticket.resolution_due_at = resolution_due

        ticket.save(
            update_fields=[
                "response_due_at",
                "resolution_due_at"
            ]
        )
    def perform_update(self, serializer):

        ticket = self.get_object()

        old_status = ticket.status

        updated_ticket = serializer.save()

        if old_status != updated_ticket.status:

            TicketHistory.objects.create(
                ticket=updated_ticket,
                old_status=old_status,
                new_status=updated_ticket.status,
                changed_by=self.request.user
            )

class DashboardAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        # Role-based tickets
        if is_admin(user):

            tickets = Ticket.objects.all()

        elif is_engineer(user):

            tickets = Ticket.objects.filter(
                Q(assigned_to=user) |
                Q(created_by=user)
            ).distinct()

        elif is_customer(user):

            tickets = Ticket.objects.filter(
                created_by=user
            )

        else:

            tickets = Ticket.objects.none()

        total_tickets = tickets.count()

        open_tickets = tickets.filter(
            status="Open"
        ).count()

        resolved_tickets = tickets.filter(
            status="Resolved"
        ).count()

        breached_tickets = tickets.filter(
            is_breached=True
        ).count()

        response_breaches = tickets.filter(
            response_breached=True
        ).count()

        resolution_breaches = tickets.filter(
            resolution_breached=True
        ).count()

        compliant_resolved = tickets.filter(
            status="Resolved",
            is_breached=False
        ).count()

        sla_compliance = 0

        if resolved_tickets > 0:

            sla_compliance = round(
                (compliant_resolved / resolved_tickets) * 100,
                2
            )

        return Response({

            "total_tickets": total_tickets,

            "open_tickets": open_tickets,

            "resolved_tickets": resolved_tickets,

            "breached_tickets": breached_tickets,

            "response_sla_breaches": response_breaches,

            "resolution_sla_breaches": resolution_breaches,

            "sla_compliance_percentage": sla_compliance

        })    
class TicketCommentViewSet(viewsets.ModelViewSet):

    serializer_class = TicketCommentSerializer

    permission_classes = [IsAuthenticated,CommentPermission]

    def get_queryset(self):

        user = self.request.user

        if is_admin(user):
            return TicketComment.objects.all()

        if is_engineer(user):
            return TicketComment.objects.filter(
                    Q(ticket__assigned_to=user) |
                    Q(ticket__created_by=user)
                )
        if is_customer(user):
            return TicketComment.objects.filter(
                ticket__created_by=user
            )

        return TicketComment.objects.none()

    def perform_create(self, serializer):

        serializer.save(
            user=self.request.user
        )
class TicketHistoryViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = TicketHistorySerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        user = self.request.user

        if is_admin(user):
            return TicketHistory.objects.all()

        if is_engineer(user):
            return TicketHistory.objects.filter(
                Q(ticket__assigned_to=user) |
                Q(ticket__created_by=user)
            )

        if is_customer(user):
            return TicketHistory.objects.filter(
                ticket__created_by=user
            )

        return TicketHistory.objects.none()