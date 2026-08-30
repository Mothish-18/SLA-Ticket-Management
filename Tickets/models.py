from django.db import models
from django.contrib.auth.models import User


class SLAPolicy(models.Model):

    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
        ("Critical", "Critical"),
    ]

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        unique=True
    )

    response_hours = models.IntegerField()

    resolution_hours = models.IntegerField()

    def __str__(self):
        return self.priority


class Ticket(models.Model):

    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
        ("Critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("Open", "Open"),
        ("In Progress", "In Progress"),
        ("On Hold", "On Hold"),
        ("Resolved", "Resolved"),
        ("Closed", "Closed"),
    ]

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Open"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_tickets"
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    response_due_at = models.DateTimeField(
        null=True,
        blank=True
    )

    resolution_due_at = models.DateTimeField(
        null=True,
        blank=True
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    on_hold_at = models.DateTimeField(
        null=True,
        blank=True
    )

    total_hold_seconds = models.PositiveIntegerField(
        default=0
    )

    response_breached = models.BooleanField(
    default=False
    )

    resolution_breached = models.BooleanField(
    default=False
    )

    is_breached = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.title


class TicketHistory(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE
    )

    old_status = models.CharField(
        max_length=20
    )

    new_status = models.CharField(
        max_length=20
    )

    changed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    changed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.ticket.title} - {self.new_status}"


class TicketComment(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.ticket.title} - {self.user.username}"

    
class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"