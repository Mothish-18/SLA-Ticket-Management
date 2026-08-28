from rest_framework import serializers
from django.utils import timezone
from Tickets.utils import resume_sla
from Tickets.models import *


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket

        fields = [
            "id",
            "title",
            "description",
            "priority",
            "status",
            "created_by",
            "assigned_to",
            "created_at",
            "updated_at",
            "response_due_at",
            "resolution_due_at",
            "resolved_at",
            "on_hold_at",
            "total_hold_seconds",
            "response_breached",
            "resolution_breached",
            "is_breached",
        ]

        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
            "response_due_at",
            "resolution_due_at",
            "resolved_at",
            "on_hold_at",
            "total_hold_seconds",
            "response_breached",
            "resolution_breached",
            "is_breached",
        ]

    def update(self, instance, validated_data):

        old_status = instance.status
        new_status = validated_data.get(
            "status",
            instance.status
        )

        # Entering ON HOLD
        if (
            old_status != "On Hold"
            and new_status == "On Hold"
        ):
            instance.on_hold_at = timezone.now()

            instance.save(
                update_fields=["on_hold_at"]
            )

        # Leaving ON HOLD
        elif (
            old_status == "On Hold"
            and new_status != "On Hold"
        ):
            instance = resume_sla(instance)

        # Resolved
        if new_status == "Resolved":
            instance.resolved_at = timezone.now()

        return super().update(
            instance,
            validated_data
        )

    def validate_assigned_to(self, value):

        if value is None:
            return value

        if not value.groups.filter(
            name="Support Engineer"
        ).exists():
            raise serializers.ValidationError(
                "Ticket can only be assigned to a Support Engineer."
            )

        return value

class TicketCommentSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    class Meta:
        model = TicketComment

        fields = [
            "id",
            "ticket",
            "user",
            "username",
            "comment",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "username",
            "created_at",
        ]

class TicketHistorySerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="changed_by.username",
        read_only=True
    )

    class Meta:

        model = TicketHistory

        fields = [
            "id",
            "ticket",
            "old_status",
            "new_status",
            "username",
            "remarks",
            "changed_at",
        ]

        read_only_fields = [
            "id",
            "ticket",
            "old_status",
            "new_status",
            "username",
            "remarks",
            "changed_at",
        ]