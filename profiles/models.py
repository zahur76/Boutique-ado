from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_countries.fields import CountryField


class UserProfile(models.Model):
    """
    A user profile model for maintaining default
    delivery information and order history
    """
    # Foreign key placed in Order to obtain orders for that user: user.Userprofile.Order.all()
    # onetoonefield same as foreign key but only one userprofile can have one user
    # https://docs.djangoproject.com/en/3.1/ref/models/fields/#onetoonefield
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # The following comes from the order model
    # all optional since using blank=True
    default_phone_number = models.CharField(max_length=20, null=True, blank=True)
    default_street_address1 = models.CharField(max_length=80, null=True, blank=True)
    default_street_address2 = models.CharField(max_length=80, null=True, blank=True)
    default_town_or_city = models.CharField(max_length=40, null=True, blank=True)
    default_county = models.CharField(max_length=80, null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_country = CountryField(blank_label='Country', null=True, blank=True)

    def __str__(self):
        return self.user.username

# This will update userprofile everytime the user is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile
    """
    # If created means if a new record was created
    # https://docs.djangoproject.com/en/3.1/ref/signals/#post-save
    if created:
        # means updating userprofile by populating it with user information
        UserProfile.objects.create(user=instance)
    # Existing users: just save the profile
    instance.userprofile.save()
