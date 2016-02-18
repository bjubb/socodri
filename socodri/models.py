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


class Action(models.Model):
    pixel = models.ForeignKey(AdsObject)
    name = models.CharField(max_length=255)
    tag = models.CharField(max_length=255)

    def __unicode__(self):
        return unicode(self.tag)


class Settings(models.Model):
    hash_id = models.CharField(max_length=32, primary_key=True)
    view_window = models.CharField(max_length=32, null=True)
    view_multiplier = models.FloatField(default=1.0)
    click_window = models.CharField(max_length=32, null=True)
    click_multiplier = models.FloatField(default=1.0)
    #  in the event we wish to use uniques
    action_total_type = models.CharField(max_length=32, default="total_actions")
    #  for roas or roi
    revenue_source = models.CharField(null=True, max_length=32)


class Initiative(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='get_full_name')
    brand_id = models.PositiveIntegerField()
    brand_name = models.CharField(max_length=255)
    settings = models.ForeignKey(Settings)
    adaccount = models.ForeignKey(AdsObject, related_name='initiative_adaccounts')
    conversion_name = models.CharField(max_length=32)
    #  limit to these campigns else use all
    campaigns = models.ManyToManyField(AdsObject, related_name='initiative_campaigns')
    actions = models.ManyToManyField(Action, related_name='initiative_actions')

    class Meta:
        unique_together = ('brand_id', 'name')

    def __unicode__(self):
        return self.name

    def get_full_name(self):
        return u'%s-%s' % (self.brand_name, self.name)


class Window(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = AutoSlugField(populate_from='name')
    adaccount = models.ForeignKey(AdsObject, related_name='window')
    campaigns = models.ManyToManyField(AdsObject, related_name='windows')
    initiative = models.ForeignKey(Initiative, null=True, related_name='windows')
    view_window = models.CharField(max_length=32, null=True)
    view_multiplier = models.FloatField(default=1.0)
    click_window = models.CharField(max_length=32, null=True)
    click_multiplier = models.FloatField(default=1.0)
    action_total_type = models.CharField(max_length=32, default="total_actions")
    revenue_source = models.CharField(max_length=32, default="Facebook")
    label_fn = models.CharField(max_length=32, null=True)

    def __unicode__(self):
        return self.name

    @property
    def conversion_name(self):
        return 'Lead'


class Stage(models.Model):
    name = models.CharField(max_length=255)
    window = models.ForeignKey(Window)
    actions = models.ManyToManyField(Action)
    number = models.PositiveIntegerField()

    def __unicode__(self):
        return self.name


class Label(models.Model):
    window = models.ForeignKey(Window, related_name='labels')
    category = models.CharField(max_length=32)
    text = models.CharField(max_length=255)
    object_type = models.CharField(max_length=32)
    object_id = models.CharField(max_length=32)
    platform = models.CharField(max_length=32)

    def __unicode__(self):
        return u'%s - %s' % (self.category, self.text)
