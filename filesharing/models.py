# -*- coding: utf-8 -*-
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import AbstractUser
import os
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from mptt.managers import TreeManager
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.manager import Manager
from django.db.utils import IntegrityError
from django.db.models.signals import pre_save, post_save
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    @property
    def home_directory(self):
        return Directory.objects.root_nodes().get(owner=self)


# создание домашней папки для каждого пользователя
@receiver(user_signed_up)
def make_home_dir(user, **kwargs):
    Directory.objects.create(name=user.username, owner=user)
    Token.objects.create(user=user)


class AccessType():
    NONE = 0
    GROUP = 1
    REGISTERED = 2
    ALL = 4

    GROUP_CHOICES = (
        (NONE, 'NONE'),
        (GROUP, 'GROUP'),
        (REGISTERED, 'REGISTERED'),
        (ALL, 'ALL')
    )


class DirectoryManager(TreeManager):
    """ Собственный менеджер для директорий.
    Добавляет возможность выбора директории по полному пути
    """
    def get_by_full_path(self, path):
        # TODO: переделать всю
        dirs_in_path = [i for i in path.split('/') if i]
        if not dirs_in_path:
            return None
        try:
            parent = self.root_nodes().get(name=dirs_in_path[0])
        except ObjectDoesNotExist:
            return None

        for d in dirs_in_path[1:]:
            try:
                parent = parent.get_children().get(name=d)
            except ObjectDoesNotExist:
                return None
        return parent

class Directory(MPTTModel):
    objects = DirectoryManager()
    name = models.CharField(max_length=256,
                            verbose_name="Имя")
    owner = models.ForeignKey(User, related_name="user_owner",
                              verbose_name="Владелец")
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children',
                            verbose_name="Родительская директория")
    access_type = models.IntegerField(choices=AccessType.GROUP_CHOICES,
                                      default=AccessType.NONE,
                                      verbose_name="Тип доступа")

    # пользователи, которым разрешён доступ (если таковые имеются)
    allowed_users = models.ManyToManyField(
        User, blank=True, related_name="users_allowed",
        verbose_name="Допущенные пользователи")

    def __str__(self):
        return self.full_path

    @property
    def full_path(self):
        return os.path.join(*[i.name for i in
                              self.get_ancestors(include_self=True)])

    def clean(self):
        if not has_access(self.parent, self.owner):
            raise ValidationError("Вы не имеете прав доступа к данной директории!")
        if '/' in self.name:
            raise ValidationError("Запрещено использовать такие знаки плохие в названии директории")
        try:
            Directory.objects.get(parent=self.parent, name=self.name)
        except Directory.DoesNotExist as err:
            pass
        else:
            raise ValidationError("Такая директория уже есть")

        try:
            File.objects.get(parent=self.parent, name=self.name)
        except File.DoesNotExist as err:
            pass
        else:
            raise ValidationError("Есть файл с таким именем")

    # TODO: тщательно протестировать
    # имеет ли пользователь доступ к папке


    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = "Директория"
        verbose_name_plural = "Директории"
        unique_together = ("parent", "name")


class FileManager(Manager):
    """ Собственный менеджер для файлов.
    Добавляет возможность поиска файла по полному пути
    """
    def get_by_full_path(self, path):
        path = path.rstrip('/')
        dirs_path, name = os.path.split(path)
        parent = Directory.objects.get_by_full_path(dirs_path)
        try:
            return self.get(name=name, parent=parent)
        except ObjectDoesNotExist:
            return None


class File(models.Model):
    objects = FileManager()
    my_file = models.FileField(verbose_name="Файл")
    parent = models.ForeignKey(Directory,
                               verbose_name="Родительская директория")
    name = models.CharField(max_length=256, verbose_name="Имя", blank=True)

    # при сохранении надо "вычислить" поле name
    def save(self, *args, **kwargs):
        # жизненный цикл файла не включает переименование
        # но filefield при пересохранении меняет физическое имя файла
        # так что есть проверка
        if not self.name:
            self.name = os.path.basename(self.my_file.name)
        super(File, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_path

    @property
    def full_path(self):
        return os.path.join(self.parent.full_path, self.name)

    def clean(self):
        name = os.path.basename(self.my_file.name)
        if '/' in name:
            raise ValidationError("Запрещено использовать такие знаки плохие в названии файла")
        if not has_access(self.parent, self.owner):
            raise ValidationError("Вы не имеете прав доступа к данной директории!")
        try:
            Directory.objects.get(parent=self.parent, name=name)
        except Directory.DoesNotExist as err:
            pass
        else:
            raise ValidationError("Директория с таким же именем уже есть")

        try:
            File.objects.get(parent=self.parent, name=name)
        except File.DoesNotExist as err:
            pass
        else:
            raise ValidationError("Есть файл с таким именем в данной директории")

    class Meta():
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"
        unique_together = ("parent", "name")


def has_access(dir, user):
    if dir.access_type == AccessType.ALL:
        return True
    elif dir.access_type == AccessType.NONE:
        return user == dir.owner
    elif dir.access_type == AccessType.GROUP:
        return user in dir.allowed_users
    elif dir.access_type == AccessType.REGISTERED:
        return user.is_authenticated()
    return None

# исключаем сохранение в одной директории
# файлов и директорий с одинаковыми именами
def check_duplicate(sender, instance, **kwargs):
    if sender == Directory:
        another_type = File
    else:
        another_type = Directory
    parent = instance.parent
    try:
        # если файла|директории нет - всё нормально
        # если есть - ошибка
        another_type.objects.get(parent=parent, name=instance.name)
    except another_type.DoesNotExist:
        return
    raise IntegrityError("В одной директории не может быть "
                         "файла и директории с одинаковыми именами")


pre_save.connect(check_duplicate, sender=Directory)
pre_save.connect(check_duplicate, sender=File)
