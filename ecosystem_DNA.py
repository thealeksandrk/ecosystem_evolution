# Imports
import matplotlib.pyplot as plt
import pygame
from random import randint as rand
from math import log10

# Variables
# Start arrays
entities=[]
# Field
field_size : int = 500
# Start nums
start_DNA_lenght : int = 100
startnum_of_entities : int = 2
global mutation_rate
mutation_rate = 0.01

painting : bool = True
play : bool = True
stoper : int = 50


# Functions
def ecostart():
    # Start arrays
    global entities, field_size
    entities = []
    start_DNA: int
    # Start fieling
    for i in range(startnum_of_entities):
        start_DNA = rand(0, 3)
        for _ in range(start_DNA_lenght-1):
            start_DNA *= 10
            start_DNA += rand(0, 3)
        entities.append(Biotic(rand(1, int(field_size*0.99)-1), rand(1, int(field_size*0.99)-1), str(start_DNA)))



def drawing():
    game.fill((0,0,0))
    # Drawing points
    for (entity) in entities:
        entity.drawcircle()
    # Showing grafic
    drawstring()
    win.blit(game,(25,25))
    pygame.display.update()


def drawstring():
    global entities
    # dna_text = []
    # for i in entities:
    #     dna_text.append(i.dna)
    #print(dna_text)
    info_string.fill((150,150,150))
    info_string.blit(font.render("FPS " + str(int(clock.get_fps())),0,(250,250,250)),[0,0])
    info_string.blit(font.render("N of Cells " + str(len(entities)),0,(250,250,250)),[100,0])

    win.blit(info_string,(0,0))
#    info_string.fill((221,171,0))
#    pygame.display.update()


def codon_mutation(codon):
    mutation_type = rand(0, 10)
    if mutation_type == 0:
        codon *= 2
    elif mutation_type == 1:
        codon = codon[::-1]
    elif mutation_type == 2:
        codon = codon[0:2]
    elif mutation_type == 3:
        codon = codon[1:3]
    elif mutation_type == 4:
        codon = codon[0:3:2]
    elif mutation_type >= 5:
        mutation_type -= 5
        codon = int(codon)
        codon += ((mutation_type%2)*2-1)*10**(mutation_type//2)
        codon = str(codon)
        if codon[0] == '-': codon = '3' + codon[1:]
    return codon



# Classes
class Biotic:
    def __init__(self, x: int, y: int, dna: str, parent_id: str = ''):
        self.x: int = x
        self.y: int = y
        self.id: str = parent_id+str(rand(0, 1000))
        self.alive: bool = True
        self.color = "green"
        self.markersize: int = 10
        self.dna : str = dna
        self.dna_lenght: int = len(dna)
        self.temp_dna: str = ''
        self.mutation_rate: float = mutation_rate
        self.create_new_entity: bool = False
        self.when_ready_to_create: int = 10

        self.start_codons = {
            '000': self.replication,
            '101': self.mass_change,
            '102': "pass",
            '103': "pass",
            '111': "pass",
            '112': "pass",
            '113': "pass",
            '121': "pass",
            '122': "pass",
            '123': "pass",
        }
        self.finish_codons = {
            '000': '333',
            '101': '332',
        }

    def drawcircle(self):
        pygame.draw.circle(game, self.color, (int(self.x),int(self.y)), self.markersize,0)

    def update(self):
        if self.markersize>100: self.markersize=100
        elif self.markersize<1: self.markersize=1

    def dna_sequencing(self):
        self.temp_dna = self.dna
        for i in range(self.dna_lenght-2):
            codon = self.dna[i:i+3]
            action = self.start_codons.get(codon)
            if callable(action):
                self.temp_dna = self.dna[i:]
                if self.finish_codons[codon] in self.temp_dna:
                    print(" Action {} with cell ID {} \n With temp_dna {}".format(action.__name__, self.id, self.temp_dna))
                    action()
            #else: self.temp_dna = self.temp_dna[1:]
        if self.when_ready_to_create:
            self.when_ready_to_create -= 1
        else:
            self.when_ready_to_create = 5
            self.create_new_entity = True


    def replication(self):
        if self.create_new_entity:
            new_dna : str = ''
            for i in range(int(len(self.temp_dna)/3)):
                if int(self.temp_dna[0]) > 3: codon = '0'
                else: codon = self.temp_dna[0]
                if int(self.temp_dna[1]) > 3: codon += '0'
                else: codon += self.temp_dna[1]
                if int(self.temp_dna[2]) > 3: codon += '0'
                else: codon += self.temp_dna[2]
                if rand(0, 1000) < mutation_rate * 1000: codon = codon_mutation(codon)
                new_dna += codon
                #why dont replicating more than twice???????
                if codon == '333':
                    print("new dna ", new_dna)
                    entities.append(Biotic(self.x + 10, self.y + 10, new_dna, self.id+'-'))
                    break
                if codon == '333': print("ERRORR")

                self.temp_dna = self.temp_dna[3:]
            self.create_new_entity = False

    def mass_change(self):
        sum_nucs: int = 0
        for i in range(int(len(self.temp_dna)/3)):
            codon = self.temp_dna[:3]
            if codon == '332':
                print('size before ', self.markersize, end= ' ')
                self.markersize += sum_nucs - i * 1.5
                print("size after ", self.markersize)
                break
            if codon == '332': print("ERRORR in mass")
            self.temp_dna = self.temp_dna[3:]
            codon = int(codon)
            sum_nucs += codon//100 + codon%10 + ((codon//10)%10)



pygame.init()
win=pygame.display.set_mode((field_size*1.1, field_size*1.1))
pygame.display.set_caption('Ecosystem')
game=pygame.Surface((field_size, field_size))
info_string=pygame.Surface((field_size, field_size/19.2))

win.fill((150,150,150))

clock=pygame.time.Clock()
pygame.key.set_repeat(200,50)

pygame.font.init() #инициализируем шрифты
font = pygame.font.SysFont('arial', 15)
#['arial', 'arialblack', 'bahnschrift', 'calibri', 'cambria', 'cambriamath', 'candara', 'comicsansms', 'consolas', 'constantia', 'corbel', 'couriernew', 'ebrima', 'franklingothicmedium', 'gabriola', 'gadugi', 'georgia', 'impact', 'inkfree', 'javanesetext', 'leelawadeeui', 'leelawadeeuisemilight', 'lucidaconsole', 'lucidasans', 'malgungothic', 'malgungothicsemilight', 'microsofthimalaya', 'microsoftjhenghei', 'microsoftjhengheiui', 'microsoftnewtailue', 'microsoftphagspa', 'microsoftsansserif', 'microsofttaile', 'microsoftyahei', 'microsoftyaheiui', 'microsoftyibaiti', 'mingliuextb', 'pmingliuextb', 'mingliuhkscsextb', 'mongolianbaiti', 'msgothic', 'msuigothic', 'mspgothic', 'mvboli', 'myanmartext', 'nirmalaui', 'nirmalauisemilight', 'palatinolinotype', 'sansserifcollection', 'segoefluenticons', 'segoemdl2assets', 'segoeprint', 'segoescript', 'segoeui', 'segoeuiblack', 'segoeuiemoji', 'segoeuihistoric', 'segoeuisemibold', 'segoeuisemilight', 'segoeuisymbol', 'segoeuivariable', 'simsun', 'nsimsun', 'simsunextb', 'sitkatext', 'sylfaen', 'symbol', 'tahoma', 'timesnewroman', 'trebuchetms', 'verdana', 'webdings', 'wingdings', 'yugothic', 'yugothicuisemibold', 'yugothicui', 'yugothicmedium', 'yugothicuiregular', 'yugothicregular', 'yugothicuisemilight', 'holomdl2assets', 'agencyfbполужирный', 'agencyfb', 'algerian', 'bookantiquaполужирный', 'bookantiquaполужирныйкурсив', 'bookantiquaкурсив', 'arialполужирный', 'arialполужирныйкурсив', 'arialкурсив', 'arialrounded', 'baskervilleoldface', 'bauhaus93', 'bell', 'bellполужирный', 'bellкурсив', 'bernardcondensed', 'bookantiqua', 'bodoniполужирный', 'bodoniполужирныйкурсив', 'bodoniblackкурсив', 'bodoniblack', 'bodonicondensedполужирный', 'bodonicondensedполужирныйкурсив', 'bodonicondensedкурсив', 'bodonicondensed', 'bodoniкурсив', 'bodonipostercompressed', 'bodoni', 'bookmanoldstyle', 'bookmanoldstyleполужирный', 'bookmanoldstyleполужирныйкурсив', 'bookmanoldstyleкурсив', 'bradleyhanditc', 'britannic', 'berlinsansfbполужирный', 'berlinsansfbdemiполужирный', 'berlinsansfb', 'broadway', 'brushscriptкурсив', 'bookshelfsymbol7', 'californianfbполужирный', 'californianfbкурсив', 'californianfb', 'calisto', 'calistoполужирный', 'calistoполужирныйкурсив', 'calistoкурсив', 'castellar', 'centuryschoolbook', 'centaur', 'century', 'chiller', 'colonna', 'cooperblack', 'copperplategothic', 'curlz', 'dubai', 'dubaimedium', 'dubairegular', 'elephant', 'elephantкурсив', 'engravers', 'erasitc', 'erasdemiitc', 'erasmediumitc', 'felixtitling', 'forte', 'franklingothicbook', 'franklingothicbookкурсив', 'franklingothicdemi', 'franklingothicdemicond', 'franklingothicdemiкурсив', 'franklingothicheavy', 'franklingothicheavyкурсив', 'franklingothicmediumcond', 'freestylescript', 'frenchscript', 'footlight', 'garamond', 'garamondполужирный', 'garamondкурсив', 'gigi', 'gillsansполужирныйкурсив', 'gillsansполужирный', 'gillsanscondensed', 'gillsansкурсив', 'gillsansultracondensed', 'gillsansultra', 'gillsans', 'gloucesterextracondensed', 'gillsansextcondensed', 'centurygothic', 'centurygothicполужирный', 'centurygothicполужирныйкурсив', 'centurygothicкурсив', 'goudyoldstyle', 'goudyoldstyleполужирный', 'goudyoldstyleкурсив', 'goudystout', 'harlowsolid', 'harrington', 'haettenschweiler', 'hightowertext', 'hightowertextкурсив', 'imprintshadow', 'informalroman', 'blackadderitc', 'edwardianscriptitc', 'kristenitc', 'jokerman', 'juiceitc', 'kunstlerscript', 'widelatin', 'lucidabright', 'lucidacalligraphy', 'leelawadee', 'leelawadeeполужирный', 'lucidafaxregular', 'lucidafax', 'lucidahandwriting', 'lucidasansregular', 'lucidasansroman', 'lucidasanstypewriterregular', 'lucidasanstypewriter', 'lucidasanstypewriteroblique', 'magnetoполужирный', 'maiandragd', 'maturascriptcapitals', 'mistral', 'modernno20', 'microsoftuighurполужирный', 'microsoftuighur', 'monotypecorsiva', 'extra', 'niagaraengraved', 'niagarasolid', 'ocraextended', 'oldenglishtext', 'onyx', 'msoutlook', 'palacescript', 'papyrus', 'parchment', 'perpetuaполужирныйкурсив', 'perpetuaполужирный', 'perpetuaкурсив', 'perpetuatitlingполужирный', 'perpetuatitling', 'perpetua', 'playbill', 'poorrichard', 'pristina', 'rage', 'ravie', 'msreferencesansserif', 'msreferencespecialty', 'rockwellcondensedполужирный', 'rockwellcondensed', 'rockwell', 'rockwellполужирный', 'rockwellполужирныйкурсив', 'rockwellextra', 'rockwellкурсив', 'centuryschoolbookполужирный', 'centuryschoolbookполужирныйкурсив', 'centuryschoolbookкурсив', 'script', 'showcardgothic', 'snapitc', 'stencil', 'twcenполужирныйкурсив', 'twcenполужирный', 'twcencondensedполужирный', 'twcencondensedextra', 'twcencondensed', 'twcenкурсив', 'twcen', 'tempussansitc', 'vinerhanditc', 'vivaldiкурсив', 'vladimirscript', 'wingdings2', 'wingdings3']
#print(pygame.font.get_fonts())

ecostart()

while play:
    clock.tick(30)

    for e in pygame.event.get():
        if e.type==pygame.QUIT: play=False
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_ESCAPE: play=False
            if e.key==pygame.K_SPACE: painting = not painting
            if e.key==pygame.K_r:
                print("\n\n RESTART")
                ecostart()
            if e.key==pygame.K_UP and stoper<200: stoper-=2
            if e.key==pygame.K_DOWN and stoper>0: stoper+=2

    if painting:
        for entity in entities:
            #print("entity DNA ", entity.dna)
            entity.dna_sequencing()
            entity.update()

        drawing()
        pygame.time.delay(int(stoper))


pygame.quit()