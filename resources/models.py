import uuid
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django_fsm import FSMField, transition, has_transition_perm, get_all_FIELD_transitions, get_available_FIELD_transitions, get_available_user_FIELD_transitions
from django.conf import  settings


BOOL_CHOICES = ((True, 'Ja'), (False, 'Nee'))

VERLENING_PERIODES = (
    ('DD', 'Dag/Dagen'),
    ('WW', 'Week/Weken'),
    ('MM', 'Maand/Maanden'),
)

VERSTREKKING_GEGEVENS_TARGETS = (
    ('verba', 'Verbalisant'),
    ('ander', 'Andere'),
)


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    #return 'user_{0}/{1}'.format(instance.user.id, filename)
    return 'user_{0}/{1}'.format(instance.user.username, filename)


##################################
# Model: Persoon
##################################
class Persoon(models.Model):
    voornaam = models.CharField('Voornaam', max_length=100)
    achternaam = models.CharField('Achternaam', max_length=100)
    email = models.EmailField()
    mobiel = models.CharField('Mobiel', max_length=20)


##################################
# Model: NatuurlijkPersoon
##################################
class NatuurlijkPersoon(Persoon):
    pass


##################################
# Model: RechtsPersoon
##################################
class RechtsPersoon(Persoon):
    pass




##################################
# Model: Verbalisant
##################################
class Verbalisant(models.Model):
    naam = models.CharField('Naam', max_length=100)
    email = models.EmailField()
    rang = models.CharField('Rang', max_length=100)

    def __str__(self):
        return f"{self.naam} (#{self.pk})"


##################################
# Model: PvVerdenking
##################################
class PvVerdenking(models.Model):
    pv_nummer = models.CharField('PV nummer', max_length=50)
    bvh_nummer = models.CharField('BVH nummer', max_length=50)
    naam_ovj = models.CharField('Naam Officier van Justitie', max_length=100, null=True, blank=True)
    parket_nummer =  models.CharField(max_length=100, null=True, blank=True)
    rc_nummer = models.CharField(max_length=100, null=True, blank=True)

    verbalisanten = models.ManyToManyField(Verbalisant, blank=True)

    rechtspersoon = models.ForeignKey(RechtsPersoon, on_delete=models.SET_NULL, null=True)
    natuurlijkpersoon = models.ForeignKey(NatuurlijkPersoon, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"PV Verdenking - {self.pv_nummer} (#{self.pk})"


##################################
# Model: BOBAanvraag
##################################
class BOBAanvraag(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # unique id`
    naam_ovj = models.CharField('Naam Officier van Justitie', max_length=100, null=True, blank=True)
    parket_nummer =  models.CharField(max_length=100, null=True, blank=True)
    naam_onderzoek = models.CharField(max_length=200, null=True, blank=True)
    rc_nummer = models.CharField(max_length=100, null=True, blank=True)
    mondeling_aanvraag_bevestiging = models.BooleanField(choices=BOOL_CHOICES,
                                             verbose_name='Bevestiging mondelinge aanvraag?',
                                             help_text='Betreft het een bevestiging mondelinge aanvraag',
                                             default=False)
    mondeling_aanvraag_datum = models.DateField(blank=True, null=True)


    onderzoeksbelang_toelichting = models.TextField('Toelichting op het onderzoeksbelang:', null=True, blank=True)

    # verbalisant fields
    verstrekking_gegevens_aan = models.CharField('Aan wie gegevens verstrekken:', max_length=5,
                                               choices=VERSTREKKING_GEGEVENS_TARGETS,
                                               blank=True, null=True,
                                               help_text="")
    verbalisant  = models.CharField('Naam verbalisant', max_length=100, help_text='Naam van de verbalisant')
    verbalisant_email = models.EmailField(verbose_name='E-mail verbalisant',
                                          help_text='Contactgegevens van de verbalisant')

    bijlage_toevoegen = models.BooleanField(choices=BOOL_CHOICES,
                                   verbose_name='Bijlagen',
                                   help_text='',
                                   default=False)
    bijlage = models.FileField('Bijlage', upload_to='documents/%Y/%m/%d', blank=True, null=True)

    status = FSMField(default='aangemaakt')

    # PV FKs
    pv_verdenking = models.ForeignKey(PvVerdenking, on_delete=models.SET_NULL, null=True, blank=True)

    # owner of instance
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   related_name='created_bob_aanvragen', null=True,blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   related_name='updated_bob_aanvragen', null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<BOB aanvraag #{self.id}>"

    def get_absolute_url(self):
        return reverse('bobaanvraag-detail', args=[str(self.id)])

    def clean(self):
        print("BOBAanvraag::clean()...")


    @transition(field=status, source='aangemaakt', target='ingediend')
    def indienen(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        :return: value will be discarded.
        """
        print("Aanvraag indienen...")


    @property
    def is_editable(self):
        generator = self.get_available_user_status_transitions(user=self.created_by)
        available_transitions = [(t.name, t.name) for t in generator]
        if len(available_transitions)>0:
            return True
        return False

    
