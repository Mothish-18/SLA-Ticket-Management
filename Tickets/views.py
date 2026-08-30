from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import *
from .forms import *
from .utils import *
from .services import *
from django.db.models import *
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import HttpResponseForbidden
from django.contrib.auth.models import *

from django.db.models import Q



@login_required
def dashboard(request):

    user = request.user

    user_groups = [
        group.name.lower()
        for group in user.groups.all()
    ]

    if "admin" in user_groups:

        tickets = Ticket.objects.all()

        role_label = "Admin"

    elif "customer" in user_groups:

        tickets = Ticket.objects.filter(
            created_by=user
        )

        role_label = "Customer"

    elif any(
        group in user_groups
        for group in [
            "engineer",
            "support engineer",
            "support_engineer"
        ]
    ):

        tickets = Ticket.objects.filter(
            Q(assigned_to=user) |
            Q(created_by=user)
        ).distinct()

        role_label = "Support Engineer"

    else:

        tickets = Ticket.objects.none()

        role_label = "No Role Assigned"

    for ticket in tickets:

        ticket.is_breached = check_sla_breach(
            ticket
        )

    total_tickets = tickets.count()

    open_tickets = tickets.filter(
        status="Open"
    ).count()

    progress_tickets = tickets.filter(
        status="In Progress"
    ).count()

    hold_tickets = tickets.filter(
        status="On Hold"
    ).count()

    resolved_tickets = tickets.filter(
        status="Resolved"
    ).count()

    closed_tickets = tickets.filter(
        status="Closed"
    ).count()

    critical_priority = tickets.filter(
    priority="Critical"
    ).count()

    high_priority = tickets.filter(
        priority="High"
    ).count()

    medium_priority = tickets.filter(
        priority="Medium"
    ).count()

    low_priority = tickets.filter(
        priority="Low"
    ).count()

    breached_tickets = sum(
        1
        for ticket in tickets
        if getattr(
            ticket,
            "is_breached",
            False
        )
    )

    recent_tickets = tickets.order_by(
        "-created_at"
    )[:5]

    return render(
        request,
        "dashboard.html",
        {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "progress_tickets": progress_tickets,
            "hold_tickets": hold_tickets,
            "resolved_tickets": resolved_tickets,
            "closed_tickets": closed_tickets,
            "critical_priority": critical_priority,
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority,
            "breached_tickets": breached_tickets,
            "recent_tickets": recent_tickets,
            "role": role_label,
        }
    )



@login_required
def create_ticket(request):

    if request.method == 'POST':

        form = TicketForm(request.POST,user=request.user)

        if form.is_valid():

            ticket = form.save(commit=False)

            ticket.created_by = request.user

            policy = SLAPolicy.objects.get(
                priority=ticket.priority
            )

            ticket.save()

            admins = User.objects.filter(
                groups__name__iexact="Admin"
            ).distinct()

            for admin in admins:

                Notification.objects.create(
                    user=admin,
                    ticket=ticket,
                    title="New Ticket Created",
                    message=(
                        f"Ticket #{ticket.id} "
                        f"has been created by "
                        f"{ticket.created_by.username}."
                    )
                )

            response_due, resolution_due = calculate_sla(
                ticket,
                policy
            )

            ticket.response_due_at = response_due
            ticket.resolution_due_at = resolution_due

            ticket.save()

            return redirect('ticket_list')

    else:

        form = TicketForm(user=request.user)

    return render(
        request,
        'create_ticket.html',
        {
            'form': form
        }
    )



@login_required
def ticket_detail(request, pk):

    ticket = get_object_or_404(
        Ticket,
        pk=pk
    )

    if request.user.groups.filter(
        name="admin"
    ).exists():

        pass

    elif request.user.groups.filter(
        name="support engineer"
    ).exists():

        if ticket.assigned_to != request.user:

            return HttpResponseForbidden(
                "You are not allowed to view this ticket."
            )

    else:

        if ticket.created_by != request.user:

            return HttpResponseForbidden(
                "You are not allowed to view this ticket."
            )

    history = TicketHistory.objects.filter(
        ticket=ticket
    ).order_by(
        "-changed_at"
    )

    return render(
        request,
        "ticket_detail.html",
        {
            "ticket": ticket,
            "history": history
        }
    )


@login_required
def ticket_list(request):

    user = request.user 
    user_groups = [
        group.name.lower()
        for group in user.groups.all()
    ]

    search_query = request.GET.get(
        "search",
        ""
    ).strip()

    status_filter = request.GET.get(
        "status",
        ""
    ).strip().lower()

    priority_filter = request.GET.get(
        "priority",
        ""
    ).strip().lower()

    breached_filter = request.GET.get(
        "breached",
        ""
    ).strip().lower()

    if "admin" in user_groups:

        base_tickets = Ticket.objects.all()

    elif "customer" in user_groups:

        base_tickets = Ticket.objects.filter(
            created_by=user
        )

    elif (
        "engineer" in user_groups
        or "support engineer" in user_groups
        or "support_engineer" in user_groups
    ):

        base_tickets = Ticket.objects.filter(
            Q(assigned_to=user) |
            Q(created_by=user)
        ).distinct()

    else:

        base_tickets = Ticket.objects.none()

    for ticket in base_tickets:

        ticket.is_breached = check_sla_breach(
            ticket
        )

    total_tickets = base_tickets.count()

    open_tickets = base_tickets.filter(
        status="Open"
    ).count()

    resolved_tickets = base_tickets.filter(
        status="Resolved"
    ).count()

    breached_tickets = sum(
        1
        for ticket in base_tickets
        if ticket.is_breached
    )

    tickets = base_tickets

    if status_filter:

        status_map = {

            "open": "Open",

            "in progress": "In Progress",

            "in_progress": "In Progress",

            "on hold": "On Hold",

            "on_hold": "On Hold",

            "resolved": "Resolved",

            "closed": "Closed",

        }

        actual_status = status_map.get(
            status_filter
        )

        if actual_status:

            tickets = tickets.filter(
                status=actual_status
            )

    if priority_filter:

        priority_map = {

            "critical": "Critical",

            "high": "High",

            "medium": "Medium",

            "low": "Low",

        }

        actual_priority = priority_map.get(
            priority_filter
        )

        if actual_priority:

            tickets = tickets.filter(
                priority=actual_priority
            )


    if breached_filter == "true":

        breached_ids = [

            ticket.id

            for ticket in base_tickets

            if ticket.is_breached

        ]

        tickets = tickets.filter(
            id__in=breached_ids
        )


    if search_query:

        tickets = tickets.filter(
            title__icontains=search_query
        )

    created_by_me = tickets.filter(
        created_by=user
    )

    assigned_to_me = tickets.filter(
        assigned_to=user
    )

    other_tickets = tickets.exclude(
        created_by=user
    ).exclude(
        assigned_to=user
    )

    filtered_tickets_count = tickets.count()


    if status_filter:

        active_filter = status_filter.replace(
            "_",
            " "
        ).title()

    elif priority_filter:

        active_filter = (
            priority_filter.title()
            + " Priority"
        )

    elif breached_filter == "true":

        active_filter = "SLA Breached"

    else:

        active_filter = "All Tickets"

    return render(
        request,
        "ticket_list.html",
        {

            "tickets": tickets.order_by(
                "-created_at"
            ),

            "created_by_me": created_by_me.order_by(
                "-created_at"
            ),

            "assigned_to_me": assigned_to_me.order_by(
                "-created_at"
            ),

            "other_tickets": other_tickets.order_by(
                "-created_at"
            ),


            "total_tickets": total_tickets,

            "open_tickets": open_tickets,

            "resolved_tickets": resolved_tickets,

            "breached_tickets": breached_tickets,

            "filtered_tickets_count": filtered_tickets_count,

            "search_query": search_query,

            "status_filter": status_filter,

            "priority_filter": priority_filter,

            "breached_filter": breached_filter,

            "active_filter": active_filter,

        }
    )

@user_passes_test(
    lambda user: is_admin(user) or is_engineer(user)
)
@login_required
def update_ticket(request, pk):

    ticket = get_object_or_404(
        Ticket,
        pk=pk
    )

    old_status = ticket.status
    old_assigned_to = ticket.assigned_to

    if request.method == 'POST':

        ticket_form = TicketUpdateForm(
            request.POST,
            instance=ticket
        )

        comment_form = TicketCommentForm(
            request.POST
        )

        if ticket_form.is_valid() and comment_form.is_valid():

            updated_ticket = ticket_form.save()


            if old_assigned_to != updated_ticket.assigned_to:

                if updated_ticket.assigned_to:

                    Notification.objects.create(
                        user=updated_ticket.assigned_to,
                        ticket=updated_ticket,
                        title="New Ticket Assigned",
                        message=(
                            f"Ticket #{updated_ticket.id} "
                            f"has been assigned to you."
                        )
                    )


            if old_status != updated_ticket.status:

                TicketHistory.objects.create(

                    ticket=updated_ticket,

                    old_status=old_status,

                    new_status=updated_ticket.status,

                    changed_by=request.user

                )

                if updated_ticket.created_by:

                    if updated_ticket.status == "Resolved":

                        Notification.objects.create(
                            user=updated_ticket.created_by,
                            ticket=updated_ticket,
                            title="Ticket Resolved",
                            message=(
                                f"Ticket #{updated_ticket.id} "
                                f"has been resolved."
                            )
                        )

                    elif updated_ticket.status == "Closed":

                        Notification.objects.create(
                            user=updated_ticket.created_by,
                            ticket=updated_ticket,
                            title="Ticket Closed",
                            message=(
                                f"Ticket #{updated_ticket.id} "
                                f"has been closed."
                            )
                        )

                    else:

                        Notification.objects.create(
                            user=updated_ticket.created_by,
                            ticket=updated_ticket,
                            title="Ticket Status Updated",
                            message=(
                                f"Ticket #{updated_ticket.id} status "
                                f"changed to {updated_ticket.status}."
                            )
                        )



            comment = comment_form.save(
                commit=False
            )

            if comment.comment:

                comment.ticket = updated_ticket

                comment.user = request.user

                comment.save()


                if is_customer(request.user):

                    # Customer commented
                    # Notify assigned engineer

                    if updated_ticket.assigned_to:

                        Notification.objects.create(
                            user=updated_ticket.assigned_to,
                            ticket=updated_ticket,
                            title="New Customer Comment",
                            message=(
                                f"Customer added a comment "
                                f"to Ticket #{updated_ticket.id}."
                            )
                        )


                elif is_engineer(request.user):

                    # Engineer commented
                    # Notify ticket customer

                    if updated_ticket.created_by:

                        Notification.objects.create(
                            user=updated_ticket.created_by,
                            ticket=updated_ticket,
                            title="New Engineer Comment",
                            message=(
                                f"Engineer added a comment "
                                f"to Ticket #{updated_ticket.id}."
                            )
                        )

            return redirect(
                'ticket_detail',
                pk=ticket.pk
            )

    else:

        ticket_form = TicketUpdateForm(
            instance=ticket
        )

        comment_form = TicketCommentForm()

    return render(
        request,
        'update_ticket.html',
        {
            'ticket': ticket,
            'ticket_form': ticket_form,
            'comment_form': comment_form
        }
    )


def login_view(request):

    if request.user.is_authenticated:

        return redirect('dashboard')

    if request.method == "POST":

        username = request.POST.get('username')

        password = request.POST.get('password')

        user = authenticate(

            request,

            username=username,

            password=password

        )

        if user is not None:

            login(

                request,

                user

            )

            return redirect('dashboard')

        else:

            messages.error(

                request,

                "Invalid username or password."

            )

    return render(

        request,

        'login.html'

    )


def logout_view(request):

    logout(request)

    return redirect('login')

def is_admin(user):

    return user.groups.filter(
        name='Admin'
    ).exists()


def is_engineer(user):

    return user.groups.filter(
        name='Support Engineer'
    ).exists()


def is_customer(user):

    return user.groups.filter(
        name='Customer'
    ).exists()


def register_view(request):

    if request.method == 'POST':

        form = RegisterForm(
            request.POST
        )

        if form.is_valid():

            user = form.save()

            customer_group = Group.objects.get(
                name='customer'
            )

            user.groups.add(
                customer_group
            )

            return redirect(
                'login'
            )

    else:

        form = RegisterForm()

    return render(
        request,
        'register.html',
        {
            'form': form
        }
    )

@login_required
def notification_click(request, pk):

    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user
    )

    notification.is_read = True
    notification.save(update_fields=["is_read"])

    if notification.ticket:
        return redirect(
            "ticket_detail",
            pk=notification.ticket.pk
        )

    return redirect("dashboard")

@login_required
def delete_notification(request, pk):

    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user
    )

    notification.delete()

    return redirect("dashboard")