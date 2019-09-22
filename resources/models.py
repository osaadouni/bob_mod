from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django_fsm import FSMField, transition, has_transition_perm, get_all_FIELD_transitions, get_available_FIELD_transitions, get_available_user_FIELD_transitions



BOOL_CHOICES = ((True, 'Ja'), (False, 'Nee'))

VERLENING_PERIODES = (
    ('DD', 'Dag/Dagen'),
    ('WW', 'Week/Weken'),
    ('MM', 'Maand/Maanden'),
)

VERSTREKKING_GEGEVENS_TARGETS = (
    ('verba', 'Verbalisant'),
    ('ander', 'Anders'),
)




def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    #return 'user_{0}/{1}'.format(instance.user.id, filename)
    return 'user_{0}/{1}'.format(instance.user.username, filename)


class BOBAanvraag(models.Model):

    naam_ovj = models.CharField(max_length=100, null=True, blank=null)
    parket_nummer =  models.CharField(max_length=100, null=True, blank=null)
    naam_onderzoek = models.CharField(max_length=200, null=True, blank=True)
    rc_nummer = models.CharField(max_length=100, null=True, blank=True)
    mondeling_aanvraag_bevestiging = models.BooleanField(choices=BOOL_CHOICES,
                                             verbose_name='Mondelinge aanvraag',
                                             help_text='Betreft het een bevestiging mondelinge aanvraag',
                                             default=False)
    mondeling_aanvraag_datum = models.DateField(blank=True, null=True)


    # pv fields
    pv_nummer = models.CharField('PV nummer', max_length=50)

    onderzoeksbelang_toelichting = models.TextField('Toelichting op het onderzoeksbelang:', null=True, blank=True)

    # verbalisant fields
    verstrekking_gegevens_aan = models.CharField('Aan wie gegevens verstrekken:', max_length=5,
                                               choices=VERSTREKKING_GEGEVENS_TARGETS,
                                               blank=True, null=True,
                                               help_text="""Eenheid van de periode waarvoor 
                                                            de verlenging van de handeling gevraagd wordt""")
    verbalisant  = models.CharField('Naam verbalisant', max_length=100, help_text='Naam van de verbalisant')
    verbalisant_email = models.EmailField(verbose_name='E-mail verbalisant',
                                          help_text='Contactgegevens van de verbalisant')

    bijlage_toevoegen = models.BooleanField(choices=BOOL_CHOICES,
                                   verbose_name='Bijlagen',
                                   help_text='',
                                   default=False)
    bijlage = models.FileField('Bijlage', upload_to='documents/%Y/%m/%d', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='bob_aanvragen', null=True,blank=True)

    status = FSMField(default='aangemaakt')

    def __str__(self):
        return f"#{self.id}) - PV: {self.dvom_aanvraagpv}"

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
        generator = self.get_available_user_status_transitions(user=self.owner)
        available_transitions = [(t.name, t.name) for t in generator]
        if len(available_transitions)>0:
            return True
        return False

    
