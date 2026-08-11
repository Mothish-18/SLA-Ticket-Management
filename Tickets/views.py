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
            "breached_tickets": breached_tickets,
            "recent_tickets": recent_tickets,
            "role": role_label,
        }
    )



@login_required
def create_ticket(request):

    if request.method == 'POST':

        form = TicketForm(request.POST)

        if form.is_valid():

            ticket = form.save(commit=False)

            ticket.created_by = request.user

            policy = SLAPolicy.objects.get(
                priority=ticket.priority
            )

            ticket.save()

            response_due, resolution_due = calculate_sla(
                ticket,
                policy
            )

            ticket.response_due_at = response_due
            ticket.resolution_due_at = resolution_due

            ticket.save()

            return redirect('ticket_list')

    else:

        form = TicketForm()

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
    )

    status_filter = request.GET.get(
        "status",
        ""
    )

    if "admin" in user_groups:

        tickets = Ticket.objects.all()

    elif "customer" in user_groups:

        tickets = Ticket.objects.filter(
            created_by=user
        )

    elif (
        "engineer" in user_groups
        or "support engineer" in user_groups
        or "support_engineer" in user_groups
    ):

        tickets = Ticket.objects.filter(
            Q(assigned_to=user) |
            Q(created_by=user)
        ).distinct()

    else:

        tickets = Ticket.objects.none()

    if status_filter == "open":

        tickets = tickets.filter(
            status="Open"
        )

    elif status_filter == "resolved":

        tickets = tickets.filter(
            status="Resolved"
        )

    elif status_filter == "breached":

        breached_ids = []

        for ticket in tickets:

            if check_sla_breach(ticket):

                breached_ids.append(
                    ticket.id
                )

        tickets = tickets.filter(
            id__in=breached_ids
        )

    if search_query:

        tickets = tickets.filter(
            title__icontains=search_query
        )

    for ticket in tickets:

        ticket.is_breached = check_sla_breach(
            ticket
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

    total_tickets = tickets.count()

    open_tickets = tickets.filter(
        status="Open"
    ).count()

    resolved_tickets = tickets.filter(
        status="Resolved"
    ).count()

    breached_tickets = sum(
        1
        for ticket in tickets
        if ticket.is_breached
    )

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

            "search_query": search_query,

            "status_filter": status_filter,
        }
    )



@user_passes_test(
    lambda user: is_admin(user) or is_engineer(user)
)
@login_required
def update_ticket(request, pk):

    ticket = Ticket.objects.get(pk=pk)

    old_status = ticket.status

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

            if old_status != updated_ticket.status:

                TicketHistory.objects.create(

                    ticket=updated_ticket,

                    old_status=old_status,

                    new_status=updated_ticket.status,

                    changed_by=request.user

                )

            comment = comment_form.save(
                commit=False
            )

            if comment.comment:

                comment.ticket = updated_ticket

                comment.user = request.user

                comment.save()

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