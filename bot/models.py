from django.db import models


# Create your models here.
class User(models.Model):
    user_id = models.CharField(max_length=20)
    username = models.CharField(max_length=30)
    is_admin = models.BooleanField(
        default=False,
    )


class Presentations(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    presentation = models.FileField(verbose_name="Файл презентации", upload_to="uploads/%Y/%m/%d/pres/", null=True,
                                    blank=True)
    adress = models.CharField(max_length=100, default="0")
    square = models.CharField(max_length=20, default="0")
    power = models.CharField(max_length=20, default="0")
    water_supply = models.CharField(max_length=30, default="0")
    height = models.CharField(max_length=20, default="0")
    rate = models.CharField(max_length=20, default="0")
    type_rent = models.CharField(max_length=20, default="0")
    plan = models.ImageField(verbose_name="План помещения", upload_to="uploads/%Y/%m/%d/plan/", null=True, blank=True)
    photo_inside = models.ImageField(verbose_name="Фото внутри", upload_to="uploads/%Y/%m/%d/inside/", null=True, blank=True)
    photo_outside = models.ImageField(verbose_name="Фото снаружи", upload_to="uploads/%Y/%m/%d/outside/", null=True, blank=True)
    additives = models.CharField(max_length=200, default="0", null=True, blank=True)

    def __str__(self):
        return str(self.user_id)

    class Meta:
        verbose_name = 'Презентация'
        verbose_name_plural = 'Презентации'
