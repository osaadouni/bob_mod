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




def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    #return 'user_{0}/{1}'.format(instance.user.id, filename)
    return 'user_{0}/{1}'.format(instance.user.username, filename)


class BOBAanvraag(models.Model):

    # pv fields
    dvom_aanvraagpv = models.CharField('Aanvraag PV', max_length=50)
    dvom_datumpv = models.DateField()

    # verbalisant fields
    dvom_verbalisant  = models.CharField('Naam verbalisant', max_length=100, help_text='Naam van de verbalisant')
    dvom_verbalisantcontactgegevens = models.EmailField(verbose_name='E-mail verbalisant',
                                                        help_text='Contactgegevens van de verbalisant')

    # bevoegdheid field
    dvom_strafvorderlijkebevoegdheidid = models.CharField('Bevoegdheid', max_length=100, default='', help_text="""ID van de 
                                                          bevoegdheid """)

    # verlenging
    dvom_verlenging = models.BooleanField(choices=BOOL_CHOICES, verbose_name='Verlenging', default=False)
    dvom_verlengingingaandop = models.DateField(null=True, blank=True)
    dvom_verlengingeinddatum = models.DateField(null=True, blank=True)
    dvom_verlenging_aantal = models.PositiveIntegerField('Periode verlenging (aantal)', default=0,
                                                         blank=True, null=True,
                                validators=[MinValueValidator(0), MaxValueValidator(100)],
                                help_text="""Voor hoe lang wordt de verlenging van de handeling gevraagd 
                                             (aantal i.c.m.volgend veld)""")

    dvom_verlenging_periode = models.CharField('Periode verlenging (eenheid)', max_length=2,
                                               choices=VERLENING_PERIODES,
                                               blank=True, null=True,
                                               help_text="""Eenheid van de periode waarvoor 
                                                            de verlenging van de handeling gevraagd wordt""")


    # Vordering tot machtiging
    dvom_vtmstartdatum = models.DateField(verbose_name='VTMStartdatum / Op', null=True, blank=True)
    dvom_vtmeinddatum = models.DateField(verbose_name='VTMEinddatum', null=True, blank=True)

    dvom_periode_aantal = models.PositiveIntegerField('Aantal (periode)', default=0, null=True, blank=True,
                                                         validators=[MinValueValidator(0), MaxValueValidator(100)],
                                                         help_text="""Periode vordering tot machtiging  
                                                                      (aantal i.c.m.volgend veld)""")

    dvom_periode_periode = models.CharField('Periode (eenheid)', max_length=2, choices=VERLENING_PERIODES,
                                            null=True, blank=True,
                                            help_text="""Eenheid van de periode tot vordering tot machtiging""")

    pdf_document = models.FileField('PDF Document', upload_to='documents/%Y/%m/%d', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='bob_aanvragen', null=True,blank=True)

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

    
