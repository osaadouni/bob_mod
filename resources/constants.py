
# TYPE VERDACHTEN
NP_ENTITY_TYPE = 'np'
RP_ENTITY_TYPE = 'rp'
ON_ENTITY_TYPE = 'on'
ENTITY_CHOICES = (
    (NP_ENTITY_TYPE, 'Natuurlijk persoon'),
    (RP_ENTITY_TYPE, 'Rechtspersoon'),
)

VERDACHTE = 'verdachte'
BETROKKENE =  'betrokkene'

VERDACHTE_CHOICES = (
    (VERDACHTE, 'Verdachte'),
    (BETROKKENE, 'Betrokkene'),
)

MALE = 'man'
FEMALE = 'vrouw'
GENDRE_CHOICES = (
    (MALE, 'Man'),
    (FEMALE, 'Vrouw'),
)

COUNTRIES = (
    ('NL', 'Nederland'),
    ('MA', 'Marokko'),
    ('TU', 'Turkije'),
    ('GE', 'Duitsland'),
    ('BE', 'Belgie'),
    ('PL', 'Polen')
)

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



