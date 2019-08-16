from django.conf import settings
from django.apps import apps


print(apps.get_model('polls', 'question'))





if __name__ == '__main__':
    import django

    django.setup()