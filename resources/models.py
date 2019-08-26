from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django_fsm import FSMField, transition, has_transition_perm, get_all_FIELD_transitions, get_available_FIELD_transitions, get_available_user_FIELD_transitions

from .transitions import TRANS_HUMAN
from accounts.groups import VERBALISANT_GROUPS, INTERCEPTIE_GROUPS




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


class InterDeskQuerySet(models.QuerySet):
    def verb_aanvraag_queryset(self):
        #return self.exclude(created_by__is_verbalisastatus='aangemaakt')
        qs = self.all()
        #users = [(q.created_by, q.created_by.is_verbalisant) for q in qs if q.created_by is not None and not(q.status=='aangemaakt'  and q.created_by.is_verbalisant)]
        #print(f"users: {users}")
        #filtered = [q.created_by for q in qs if q.created_by is not None and not(q.status=='aangemaakt'  and q.created_by.is_verbalisant)]
        #print(f"filtered: {filtered}")
        #return qs.filter(created_by__in=filtered) 
        
        filtered = [q.created_by for q in qs if q.created_by is not None and q.status=='aangemaakt'  and q.created_by.is_verbalisant]
        print(f"filtered: {filtered}")
        return qs.exclude(created_by__in=filtered) 
    

class InterDeskManager(models.Manager):

    def get_queryset(self):
        return InterDeskQuerySet(self.model, using=self._db)

    def verb_aanvragen(self):
        return self.get_queryset().verb_aanvraag_queryset()
        

class VerbalisantQuerySet(models.QuerySet):
    def verb_aanvraag_queryset(self, user):
        return self.filter(created_by=user)
    

class VerbalisantManager(models.Manager):

    def get_queryset(self):
        return VerbalisantQuerySet(self.model, using=self._db)

    def verb_aanvragen(self, user):
        return self.get_queryset().verb_aanvraag_queryset(user)
        


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

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='created_aanvragen', null=True,blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='updated_aanvragen', null=True,blank=True)

    status = FSMField(default='aangemaakt')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # custom managers
    objects = models.Manager()
    interdesk_manager = InterDeskManager()
    verb_manager = VerbalisantManager()


    class Meta:
        verbose_name_plural = 'BOB aanvragen'

    def __str__(self):
        return f"#{self.id}) - PV: {self.dvom_aanvraagpv}"

    def get_absolute_url(self):
        return reverse('bobaanvraag-detail', args=[str(self.id)])

    def clean(self):
        print("BOBAanvraag::clean()...")


    # aangemaakt -> * 
    @transition(field=status, source='aangemaakt', target='ingediend',
                permission=lambda instance, user: user.has_perm('resources.can_indienen'))
    def indienen(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        :return: value will be discarded.
        """
        print("Aanvraag indienen...")

    @transition(field=status, source='aangemaakt', target='geannuleerd', 
                permission=lambda instance, user: user.has_perm('resources.can_annuleren'))
    def annuleren(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        :return: value will be discarded.
        """
        print("Aanvraag annuleren...")

    # ingediend -> * 
    @transition(field=status, source='ingediend', target='inbehandeling',
                permission=lambda instance, user: user.has_perm('resources.can_behandelen'))
    def behandelen(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        :return: value will be discarded.
        """
        print("Aanvraag behandelen...")
        

    # inbehandling -> * 
    @transition(field=status, source=['inbehandeling'], target='goedgekeurd', 
                permission=lambda instance, user: user.has_perm('resources.can_goedkeuren'))
    def goedkeuren(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        :return: value will be discarded.
        """
        print("Aanvraag goedkeuren...")

    @transition(field=status, source=['inbehandeling'], target='afgekeurd',
                permission=lambda instance, user: user.has_perm('resources.can_afkeuren'))
    def afkeuren(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        :return: value will be discarded.
        """
        print("Aanvraag afkeuren...")


    @transition(field=status, source='inbehandeling', target='afgerond', 
                permission=lambda instance, user: user.has_perm('resources.can_afronden'))
    def afronden(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        :return: value will be discarded.
        """
        print("Aanvraag afronden...")

    @transition(field=status, source=['ingediend', 'inbehandeling'], target='in_de_wacht',
                permission=lambda instance, user: user.has_perm('resources.can_in_de_wacht_zetten'))
    def in_de_wacht_zetten(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        :return: value will be discarded.
        """
        print("Aanvraag in de wacht zetten...")

        
    @transition(field=status, source='goedgekeurd', target='verzonden_OM',
                permission=lambda instance, user: user.has_perm('resources.can_verzenden_om'))
    def verzenden_OM(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        :return: value will be discarded.
        """
        print("Aanvraag verzenden naar OM...")
        

    @transition(field=status, source='verzonden_OM', target='goedgekeurd_OM',
                permission=lambda instance, user: user.has_perm('resources.can_goedkeuren_om'))
    def goedkeuren_OM(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        :return: value will be discarded.
        """
        print("Aanvraag goedgekeurd door OM...")
        
    @transition(field=status, source='verzonden_OM', target='afgekeurd_OM',
                permission=lambda instance, user: user.has_perm('resources.can_afkeuren_om'))
    def afkeuren_OM(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        :return: value will be discarded.
        """
        print("Aanvraag afgekeurd door OM...")



    @property
    def is_editable(self):
        generator = self.get_available_user_status_transitions(user=self.created_by)
        available_transitions = [(t.name, t.name) for t in generator]
        print(f"ID:{self.pk} - transitions: {available_transitions}")
    
        if not self.created_by is None:
            if self.created_by.groups.filter(name__in=INTERCEPTIE_GROUPS).exists():
                return True
        return len(available_transitions) > 0


    
