from django.db.models import Q


def q_set(start_time, end_time, start_data, end_data):
    q1 = Q(start_time_seance__range=(start_time, end_time))
    q2 = Q(end_time_seance__range=(start_time, end_time))
    q3 = Q(show_start_date__range=(start_data, end_data))
    q4 = Q(show_end_date__range=(start_data, end_data))
    q5 = Q(start_time_seance__lte=start_time, end_time_seance__gte=end_time)
    q6 = Q(show_start_date__lte=start_data, show_end_date__gte=end_data)
    return q1, q2, q3, q4, q5, q6
