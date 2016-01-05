from copy import copy
from django.db import models
from autoslug import AutoSlugField

REVENUE_SOURCES = (
    'Facebook', 'DFA'
)


class AdsObject(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return unicode(self.id)


class Funnel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = AutoSlugField(populate_from='name')
    adaccount = models.ForeignKey(AdsObject, related_name='funnel')
    campaigns = models.ManyToManyField(AdsObject, related_name='funnels')
    view_window = models.CharField(max_length=32, null=True)
    view_multiplier = models.FloatField(default=1.0)
    click_window = models.CharField(max_length=32, null=True)
    click_multiplier = models.FloatField(default=1.0)
    action_total_type = models.CharField(max_length=32, default="total_actions")
    revenue_source = models.CharField(max_length=32, default="Facebook")

    def __unicode__(self):
        return self.name

class Action(models.Model):
    pixel = models.ForeignKey(AdsObject)
    name = models.CharField(max_length=255)
    tag = models.CharField(max_length=255)

    def __unicode__(self):
        return unicode(self.tag)


class Stage(models.Model):
    name = models.CharField(max_length=255)
    funnel = models.ForeignKey(Funnel)
    actions = models.ManyToManyField(Action)
    number = models.PositiveIntegerField()

    def __unicode__(self):
        return self.name
