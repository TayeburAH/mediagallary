from django.contrib.auth.decorators import user_passes_test


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in. """

    def in_groups(user):
        """the user is actually request.user  Not sure why"""
        if user.is_authenticated:
            if bool(user.groups.filter(name__in=group_names)) or user.is_superuser:
                return True
        return False

    return user_passes_test(in_groups, login_url='')
    # you have to put something here otherwise it redirects to allauth signup

'''
1. group_required is called
2. return user_passes_test(in_groups, login_url=''), calling in_groups func
3. def in_groups(user): works giving True or False
4. return user_passes_test(True | False, login_url='')

'''