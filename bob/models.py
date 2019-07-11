from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


ONDERZOEK_TYPES = (
    ('SO', 'Strafrechtelijk Onderzoek'),
    ('SF', 'Strafrechtelijk Financieel Onderzoek'),
    ('SE', 'Strafrechtelijk Executie Onderzoek'),
)

BOOL_CHOICES = ((True, 'Ja'), (False, 'Nee'))

VERLENING_PERIODES = (
    ('DD', 'Dag/Dagen'),
    ('WW', 'Week/Weken'),
    ('MM', 'Maand/Maanden'),
)


class BobHandeling(models.Model):
    dvom_bobhandelingid = models.AutoField(primary_key=True)
    dvom_bobhandeling = models.CharField('BOB handeling', max_length=100, help_text='Naam van de bob handeling')
    dvom_aanvraagpv = models.CharField('Aanvraag PV', max_length=50)
    dvom_datumpv = models.DateField()
    dvom_verbalisant  = models.CharField('Verbalisant', max_length=100, help_text='Naam van de verbalisant')
    dvom_verbalisantcontactgegevens = models.EmailField(verbose_name='Verbalisant',
                                                        help_text='Contactgegevens van de verbalisant')
    dvom_onderzoeksinstantiecontactpersoon = models.CharField('Contactpersoon onderzoeksinstantie', max_length=100,
                                                              help_text='Contactpersoon bij de opsporingsinstantie')

    dvom_onderzoeksinstantieid = models.CharField('Onderzoeksinstantie', max_length=100, blank=True, null=True,
                                                 help_text="""ID van de opsporingsinstantie (NB: zit in Onderzoek)""")

    dvom_onderzoekssubjectid = models.CharField('Onderzoekssubject', max_length=100, blank=True, null=True,
                                                 help_text="""ID van het onderzoekssubject """)

    dvom_onderzoekstype = models.CharField('Onderzoekstype', max_length=2, choices=ONDERZOEK_TYPES,
                                           help_text='Type onderzoek (wordt afgeleid van de bevoegdheid)')
    dvom_strafvorderlijkebevoegdheidid = models.CharField('Bevoegdheid', max_length=100, default='', help_text="""ID van de 
                                                          bevoegdheid """)

    dvom_heterdaad = models.BooleanField(choices=BOOL_CHOICES, verbose_name='Heterdaad', default=False)
    dvom_heeftverlenging = models.BooleanField(choices=BOOL_CHOICES, verbose_name='Heeft verlenging', default=False)
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

    dvom_voorgaandebobhandelingid = models.CharField('Voorgaande BOB handeling', max_length=100,
                                                     help_text='ID voorgaande BOB handeling (igv verlenging)')
    dvom_oorspronkelijkebobhandelingid = models.CharField('Oorspronkelijke BOB handeling', max_length=100,
                                                          help_text="""ID van de 1e BOB handeling waar 
                                                          de verlenging bij hoort""")


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

    # Machtiging fields
    dvom_machtigingdoorid = models.CharField('Machtiging door', max_length=10, help_text="""RC die de machtiging 
                                             afgeeft (id van de gebruiker in de applicatie)""")

    dvom_machtigingop = models.DateField(verbose_name='Machtiging op', help_text="""Datum waarop de machtiging is 
                                        afgegeven""")
    dvom_machtigingstartdatum = models.DateField(verbose_name='Machtiging startdatum / op', help_text="""Startdatum
                                                 van de machtiging""")
    dvom_machtigingeinddatum = models.DateField(verbose_name='Machtiging einddatum', help_text="""Einddatum
                                                 van de machtiging""")

    dvom_machtiging_aantal = models.PositiveIntegerField('Machtiging aantal (periode)', default=0,
                                                         validators=[MinValueValidator(1), MaxValueValidator(100)],
                                                         help_text="""Periode van de machtiging  
                                             (aantal i.c.m.volgend veld)""")

    dvom_machtiging_periode = models.CharField('Machtiging periode (eenheid)', max_length=2, choices=VERLENING_PERIODES,
                                               help_text="""Eenheid van de periode van de machtiging """)

    def __str__(self):
        return self.dvom_bobhandeling

    def get_absolute_url(self):
        return reverse('bobhandeling-detail', args=[str(self.dvom_bobhandelingid)])

