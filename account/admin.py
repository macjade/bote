from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import Bote, UserProfile, TwoFAToken, ResetToken, UserSetting

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'username', 'firstname', 'lastname', 'admin', 'staff', 'active', 'email_confirmation')
    list_filter = ('admin', 'staff', 'user', 'active', 'email_confirmation')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'firstname', 'lastname', 'date_of_joining')}),
        ('Permissions', {'fields': ('active', 'is_blocked', 'admin', 'staff', 'user', 'email_confirmation')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(Bote, UserAdmin)
admin.site.register(UserProfile)
admin.site.register(UserSetting)
admin.site.register(TwoFAToken)
admin.site.register(ResetToken)
