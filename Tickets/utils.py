from datetime import timedelta


def calculate_sla(ticket, policy):

    response_due = (
        ticket.created_at +
        timedelta(hours=policy.response_hours)
    )

    resolution_due = (
        ticket.created_at +
        timedelta(hours=policy.resolution_hours)
    )

    return response_due, resolution_due