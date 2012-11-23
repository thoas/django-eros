def get_ip(request):
    """
    Gets the true client IP address of the request
    Contains proxy handling involving HTTP_X_FORWARDED_FOR and multiple addresses
    """
    ip = request.META.get('REMOTE_ADDR', None)
    if (not ip or ip == '127.0.0.1') and 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META.get('HTTP_X_FORWARDED_FOR', None)

    return ip.replace(',', '').split()[0] if ip else None
