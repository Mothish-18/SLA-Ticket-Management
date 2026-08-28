from datetime import timedelta
from django.utils import timezone


BUSINESS_START_HOUR = 9
BUSINESS_END_HOUR = 18


def add_business_hours(start_datetime, hours):

    current = start_datetime
    remaining = hours

    while remaining > 0:

        # Skip Saturday and Sunday
        if current.weekday() >= 5:
            current += timedelta(days=1)

            current = current.replace(
                hour=BUSINESS_START_HOUR,
                minute=0,
                second=0,
                microsecond=0
            )

            continue

        # Before business hours
        if current.hour < BUSINESS_START_HOUR:
            current = current.replace(
                hour=BUSINESS_START_HOUR,
                minute=0,
                second=0,
                microsecond=0
            )

        # After business hours
        if current.hour >= BUSINESS_END_HOUR:
            current += timedelta(days=1)

            current = current.replace(
                hour=BUSINESS_START_HOUR,
                minute=0,
                second=0,
                microsecond=0
            )

            continue

        end_of_day = current.replace(
            hour=BUSINESS_END_HOUR,
            minute=0,
            second=0,
            microsecond=0
        )

        available_hours = (
            end_of_day - current
        ).total_seconds() / 3600

        if remaining <= available_hours:

            current += timedelta(hours=remaining)

            remaining = 0

        else:

            remaining -= available_hours

            current += timedelta(days=1)

            current = current.replace(
                hour=BUSINESS_START_HOUR,
                minute=0,
                second=0,
                microsecond=0
            )

    return current


def calculate_business_hours(start_datetime, end_datetime):

    if start_datetime >= end_datetime:
        return 0

    total_seconds = 0
    current = start_datetime

    while current < end_datetime:

        # Skip weekends
        if current.weekday() >= 5:

            current += timedelta(days=1)

            current = current.replace(
                hour=BUSINESS_START_HOUR,
                minute=0,
                second=0,
                microsecond=0
            )

            continue

        # Before business hours
        if current.hour < BUSINESS_START_HOUR:

            current = current.replace(
                hour=BUSINESS_START_HOUR,
                minute=0,
                second=0,
                microsecond=0
            )

        # After business hours
        if current.hour >= BUSINESS_END_HOUR:

            current += timedelta(days=1)

            current = current.replace(
                hour=BUSINESS_START_HOUR,
                minute=0,
                second=0,
                microsecond=0
            )

            continue

        end_of_day = current.replace(
            hour=BUSINESS_END_HOUR,
            minute=0,
            second=0,
            microsecond=0
        )

        period_end = min(
            end_of_day,
            end_datetime
        )

        total_seconds += (
            period_end - current
        ).total_seconds()

        current = period_end

        if current < end_datetime:

            current += timedelta(days=1)

            current = current.replace(
                hour=BUSINESS_START_HOUR,
                minute=0,
                second=0,
                microsecond=0
            )

    return total_seconds


def resume_sla(ticket):

    if not ticket.on_hold_at:
        return ticket

    now = timezone.now()

    hold_seconds = calculate_business_hours(
        ticket.on_hold_at,
        now
    )

    hold_duration = timedelta(
        seconds=hold_seconds
    )

    ticket.total_hold_seconds += int(
        hold_seconds
    )

    if ticket.response_due_at:
        ticket.response_due_at += hold_duration

    if ticket.resolution_due_at:
        ticket.resolution_due_at += hold_duration

    ticket.on_hold_at = None

    ticket.save(
        update_fields=[
            "response_due_at",
            "resolution_due_at",
            "on_hold_at",
            "total_hold_seconds",
        ]
    )

    return ticket


def calculate_sla(ticket, policy):

    response_due = add_business_hours(
        ticket.created_at,
        policy.response_hours
    )

    resolution_due = add_business_hours(
        ticket.created_at,
        policy.resolution_hours
    )

    return response_due, resolution_due


def check_sla_breach(ticket):

    now = timezone.now()

    # Response SLA breach
    if (
        ticket.response_due_at
        and now > ticket.response_due_at
        and ticket.status not in ["Resolved", "Closed", "On Hold"]    ):
        ticket.response_breached = True

    # Resolution SLA breach
    if (
        ticket.resolution_due_at
        and now > ticket.resolution_due_at
        and ticket.status not in ["Resolved", "Closed", "On Hold"]    ):
        ticket.resolution_breached = True

    # Overall breach
    ticket.is_breached = (
        ticket.response_breached
        or ticket.resolution_breached
    )

    ticket.save(
        update_fields=[
            "response_breached",
            "resolution_breached",
            "is_breached",
        ]
    )

    return ticket.is_breached