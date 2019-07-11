from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
DVOM_LOCATIES = ()

DVOM_CLASSIFICATIE_OPTIES = (
    ('FR', 'Fraude'),
    ('JE', 'Jeugd'),
    ('MH', 'Mensenhandel'),
    ('MI', 'Militair'),
    ('TR', 'Terrorisme'),
)
DVOM_AFSLUITENONDERZOEK_OPTIES = (
    ('1', 'Er is geen verdachte'),
    ('2', 'Klappen zaak - de verdacht wordt vervolgd'),
    ('3', 'Sepot'),
)

class Onderzoek:
    dvom_onderzoekid = models.AutoField('Onderzoek', primary_key=True)
    dvom_locatieid = models.CharField('Parket', max_length=10, choices=DVOM_LOCATIES, default='')
    dvom_naam = models.CharField('Onderzoeksnaam', max_length=100, blank=True, null=True)
    dvom_codenaam = models.CharField('Codenaam', max_length=100, blank=True, null=True)
    dvom_onderzoeksinstantieid = models.CharField('Onderzozeksinstantie', max_length=10,  choices=())
    dvom_procesverbaalnummer = models.CharField('Process verbaal nummer',max_length=100, )
    dvom_classificatie = models.CharField('Classificatie', max_length=2, choices=DVOM_CLASSIFICATIE_OPTIES)
    dvom_naamcsv = models.CharField('Naam CSV', max_length=100)
    dvom_omschrijvingcsv = models.CharField('Omschrijving CSV', max_length=2000)
    dvom_zaakgriffierid = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Zaaksgriffier')
    dvom_zaakovjid = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='ZaaksOvJ')
    dvom_zaakparketsecrid = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Zaakssecretaris')
    dvom_zaakrcid = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='ZaaksRC')
    dvom_afsluitenonderzoek = models.CharField('Afsluiten onderzoek',
                                               max_length=1,
                                               choices=DVOM_AFSLUITENONDERZOEK_OPTIES)

    np_bobaanvraagid = models.IntegerField()

    class Meta:
        ordering = ['-dvom_onderzoekid']
        verbose_name_plural = 'Onderzoeken'

    def __str__(self):
        return f"{self.dvom_naam} - {self.dvom_codenaam}"

    def get_absolute_url(self):
        return reverse('onderzoek-detail', args=[str(self.dvom_onderzoekid)])


