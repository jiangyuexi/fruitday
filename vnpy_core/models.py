# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desidered behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class User(models.Model):
    user_name = models.CharField(primary_key=True, max_length=255)
    user_pass_word = models.CharField(max_length=255, blank=True, null=True)
    user_permission = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'


class Min1(models.Model):
    min1_timestamp = models.BigIntegerField(primary_key=True)
    min1_open = models.TextField(blank=True, null=True)  # This field type is a guess.
    min1_high = models.TextField(blank=True, null=True)  # This field type is a guess.
    min1_low = models.TextField(blank=True, null=True)  # This field type is a guess.
    min1_close = models.TextField(blank=True, null=True)  # This field type is a guess.
    min1_volume = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'min1'


class Money(models.Model):
    money_user_id = models.TextField(primary_key=True)  # This field type is a guess.
    money_balance = models.FloatField(blank=True, null=True)
    money_available = models.FloatField(blank=True, null=True)
    money_frozen = models.FloatField(blank=True, null=True)
    money_accountid = models.TextField(primary_key=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'money'
        unique_together = (('money_user_id', 'money_accountid'),)


class Fundingrate(models.Model):
    timestamp = models.TextField(primary_key=True)  # This field type is a guess.
    symbol = models.TextField(blank=True, null=True)  # This field type is a guess.
    fundingrate = models.FloatField(db_column='fundingRate', blank=True, null=True)  # Field name made lowercase.
    fundingratedaily = models.FloatField(db_column='fundingRateDaily', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'fundingRate'


class Candle1Hour(models.Model):
    timestamp = models.TextField(primary_key=True)  # This field type is a guess.
    open = models.FloatField(blank=True, null=True)
    high = models.FloatField(blank=True, null=True)
    low = models.FloatField(blank=True, null=True)
    close = models.FloatField(blank=True, null=True)
    vol = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'candle_1hour'


class Position(models.Model):
    position_user_id = models.TextField(primary_key=True)  # This field type is a guess.
    position_accountid = models.TextField(primary_key=True)  # This field type is a guess.
    position_symbol = models.TextField(blank=True, null=True)  # This field type is a guess.
    position_currentqty = models.FloatField(db_column='position_currentQty', blank=True, null=True)  # Field name made lowercase.
    position_liqprice = models.FloatField(db_column='position_liqPrice', blank=True, null=True)  # Field name made lowercase.
    position_markprice = models.FloatField(db_column='position_markPrice', blank=True, null=True)  # Field name made lowercase.
    position_lastprice = models.FloatField(db_column='position_lastPrice', blank=True, null=True)  # Field name made lowercase.
    position_avgentryprice = models.FloatField(db_column='position_avgEntryPrice', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'position'
        unique_together = (('position_user_id', 'position_accountid'),)


