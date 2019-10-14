import uuid
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django_fsm import FSMField, transition, has_transition_perm, get_all_FIELD_transitions, get_available_FIELD_transitions, get_available_user_FIELD_transitions
from django.conf import  settings
from polymorphic.models import PolymorphicModel

from .constants import ENTITY_CHOICES, NP_ENTITY_TYPE, RP_ENTITY_TYPE, ON_ENTITY_TYPE, VERDACHTE_CHOICES,VERDACHTE,\
    BETROKKENE, FEMALE, MALE,GENDRE_CHOICES, COUNTRIES, BOOL_CHOICES, VERSTREKKING_GEGEVENS_TARGETS, VERLENING_PERIODES



##################################
# Model: NatuurlijkPersoon
##################################
class NatuurlijkPersoonProcesVerbaal(models.Model):
    voornaam = models.CharField(max_length=30, null=True, blank=True)
    voorvoegsel = models.CharField(max_length=10, null=True, blank=True)
    achternaam = models.CharField(max_length=30)
    geslacht = models.CharField(max_length=5, choices=GENDRE_CHOICES,   null=True, blank=True)
    geboortedatum = models.DateField(null=True, blank=True)
    geboorteland = models.CharField(max_length=2, choices=COUNTRIES, null=True, blank=True)
    nationaliteit = models.CharField(max_length=100, null=True, blank=True)
    adres = models.CharField(max_length=200, null=True, blank=True)
    postcode = models.CharField(max_length=10, null=True, blank=True)
    plaats = models.CharField("Woonplaats", max_length=100, null=True, blank=True)
    land = models.CharField("Land", max_length=2, choices=COUNTRIES, null=True, blank=True)
    keno_nummer = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.achternaam


##################################
# Model: RechtsPersoon
##################################
class RechtsPersoonProcesVerbaal(models.Model):
    naam = models.CharField(max_length=40, null=True, blank=True)
    rechtsvorm = models.CharField(max_length=40, null=True, blank=True)
    statutaire_adres = models.CharField(max_length=100, null=True, blank=True)
    vestiging_adres = models.CharField(max_length=100, null=True, blank=True)
    post_adres = models.CharField(max_length=100, null=True, blank=True)
    kvk_nummer = models.CharField(max_length=50, null=True, blank=True)
    vertegenwoordiger = models.CharField(max_length=50)
    functie = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.naam


##################################
# Model: Verbalisant
##################################
class VerbalisantProcesVerbaal(models.Model):
    naam = models.CharField('Naam', max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    rang = models.CharField('Rang', max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.naam} (#{self.pk})"


##################################
# Default Model: ProcesVerbaal
##################################
class ProcesVerbaal(PolymorphicModel):
    pv_nummer = models.CharField('PV nummer', max_length=50)
    bvh_nummer = models.CharField('BVH nummer', max_length=50, null=True, blank=True)
    naam_ovj = models.CharField('Naam Officier van Justitie', max_length=100, null=True, blank=True)
    parket_nummer =  models.CharField(max_length=100, null=True, blank=True)
    rc_nummer = models.CharField(max_length=100, null=True, blank=True)
    toelichting = models.CharField(max_length=255, null=True, blank=True)
    pdf_document = models.FileField("PDF bijlage", upload_to="documents/%Y/%m/%d")

    verbalisanten = models.ManyToManyField(VerbalisantProcesVerbaal, blank=True)
    entity_type = models.CharField('Onderzoek richt zich op', max_length=2, choices=ENTITY_CHOICES,
                                   blank=True,
                                   default=NP_ENTITY_TYPE)
    jegens_persoon = models.ForeignKey(NatuurlijkPersoonProcesVerbaal, on_delete=models.SET_NULL, null=True, blank=True)
    jegens_rechtspersoon = models.ForeignKey(RechtsPersoonProcesVerbaal, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"PV Verbaal - {self.pv_nummer} (#{self.pk})"


##################################
# Child PVs, subclass ProcesVerbaal
##################################
class ProcesVerbaalVerdenking(ProcesVerbaal):
    pass

class ProcesVerbaalAanvraag(ProcesVerbaal):
    pass


class ProcesVerbaalHistorischeGegevens(ProcesVerbaalAanvraag):
    jegens_verdachte = models.CharField('Jegens verdachte', max_length=20, choices=VERDACHTE_CHOICES)
    start_datum = models.DateField()
    eind_datum = models.DateField()
    rekeningnummer = models.CharField('IBAN nummer', max_length=30)
    financiele_instelling = models.CharField('Financiele instelling', max_length=100)


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
    pv_verdenking = models.ForeignKey(ProcesVerbaalVerdenking, on_delete=models.SET_NULL, null=True, blank=True)
    pv_aanvraag = models.ForeignKey(ProcesVerbaalAanvraag, on_delete=models.SET_NULL, null=True, blank=True)

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

    
