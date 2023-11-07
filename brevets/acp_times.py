"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_acp.html
and https://rusa.org/pages/rulesForRiders
"""



import arrow

    
# Constants for the minimum and maximum speeds in km/hr
MIN_SPEEDS = {0: 15, 200: 15, 400: 15, 600: 11.428, 1000: 13.333}
MAX_SPEEDS = {200: 34, 300: 32, 400: 30, 600: 28, 1000: 26}


def get_speed(control_dist_km, brevet_dist_km, speed_dict):
    """
    Helper function to determine the applicable speed from the speed_dict
    based on the control distance and the brevet distance.
    """
    applicable_speed = speed_dict[min(brevet_dist_km, control_dist_km)]
    for distance in sorted(speed_dict.keys(), reverse=True):
        if control_dist_km > distance:
            applicable_speed = speed_dict[distance]
            break
    return applicable_speed
    

def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Calculate the open time for a control point.
    
    Args:
        control_dist_km:  number, control distance in kilometers
        brevet_dist_km: number, nominal distance of the brevet
            in kilometers, which must be one of 200, 300, 400, 600,
            or 1000 (the only official ACP brevet distances)
        brevet_start_time:  An arrow object
        
    Returns:
        An arrow object indicating the control open time.
        This will be in the same time zone as the brevet start time.
    """

    total_time = 0
    last_distance = 0

    control_points = [(200, 34), (400, 32), (600, 30), (1000, 28), (1300, 26)]

    for (dist, speed) in control_points:
        if control_dist_km > last_distance:
            segment_dist = min(control_dist_km, dist) - last_distance
            segment_time = segment_dist / speed
            total_time += segment_time
            last_distance = dist
        else:
            break

    if control_dist_km > brevet_dist_km:
        excess_dist = control_dist_km - brevet_dist_km
        total_time += excess_dist / MIN_SPEEDS[brevet_dist_km]

    hours = int(total_time)
    minutes = int((total_time - hours) * 60) 

    open_time = brevet_start_time.shift(hours=hours, minutes=minutes)
    
    return open_time
    


def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Calculate the close time for a control point.
    
    Args:
        control_dist_km:  number, control distance in kilometers
        brevet_dist_km: number, nominal distance of the brevet
            in kilometers, which must be one of 200, 300, 400, 600, or 1000
            (the only official ACP brevet distances)
        brevet_start_time:  An arrow object
    
    Returns:
       An arrow object indicating the control close time.
       This will be in the same time zone as the brevet start time.
    """
    
    if control_dist_km == 0:
        return brevet_start_time.shift(hours=+1)

    total_time = 0  # Total time in hours

    segments = [(1000, MIN_SPEEDS[600]), (600, MIN_SPEEDS[400]), (400, MIN_SPEEDS[200]), (200, MIN_SPEEDS[0]), (0, MIN_SPEEDS[0])]
    
    for seg_start, speed in segments:
        if control_dist_km > seg_start:
            segment_time = (control_dist_km - seg_start) / speed
            total_time += segment_time
            control_dist_km = seg_start

    if control_dist_km <= 60:
        total_time = max(total_time, control_dist_km / MIN_SPEEDS[0])

    hours = int(total_time)
    minutes = (total_time - hours) * 60
    minutes = int(minutes)

    close_time = brevet_start_time.shift(hours=hours, minutes=minutes)
    
    return close_time
    
