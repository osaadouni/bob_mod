from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator



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
    dvom_verlengingingaandop = models.DateField()
    dvom_verlengingeinddatum = models.DateField()
    dvom_verlenging_aantal = models.PositiveIntegerField('Periode verlenging (aantal)', default=0,
                                validators=[MinValueValidator(1), MaxValueValidator(100)],
                                help_text="""Voor hoe lang wordt de verlenging van de handeling gevraagd 
                                             (aantal i.c.m.volgend veld)""")

    dvom_verlenging_periode = models.CharField('Periode verlenging (eenheid)', max_length=2, choices=VERLENING_PERIODES,
                                           help_text="""Eenheid van de periode waarvoor 
                                           de verlenging van de handeling gevraagd wordt""")


    # Vordering tot machtiging
    dvom_vtmstartdatum = models.DateField(verbose_name='VTMStartdatum / Op')
    dvom_vtmeinddatum = models.DateField(verbose_name='VTMEinddatum')

    dvom_periode_aantal = models.PositiveIntegerField('Aantal (periode)', default=0,
                                                         validators=[MinValueValidator(1), MaxValueValidator(100)],
                                                         help_text="""Periode vordering tot machtiging  
                                             (aantal i.c.m.volgend veld)""")

    dvom_periode_periode = models.CharField('Periode (eenheid)', max_length=2, choices=VERLENING_PERIODES,
                                               help_text="""Eenheid van de periode tot vordering tot machtiging  
                                           """)

    pdf_document = models.FileField('PDF Document', upload_to='documents/%Y/%m/%d', blank=True, null=True)

    def __str__(self):
        return f"#{self.id}) - PV: {self.dvom_aanvraagpv}"

    def get_absolute_url(self):
        return reverse('bobaanvraag-detail', args=[str(self.id)])

    def clean(self):
        print("BOBAanvraag::clean()...")
