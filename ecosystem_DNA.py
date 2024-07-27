# Need to think how to make AI without AI
# Mb make DNA - Gen - Protein - char - smhow AI
import math
import time

# Try to add more hormons

# wtf with mass and food

# Imports
# import matplotlib.pyplot as plt
import pygame
from random import randint as rand
from random import choices
from collections import defaultdict
from pylcs import lcs_sequence_length as lcs_sl

# Variables
# Start arrays
entities = []
died_entities = []
where_is_sun = []
# Field
field_size: int = 750  # for entities xy
window_size: int = 750  # 800 too big for me
field_x_window: float = window_size / field_size

# Start nums
start_DNA_len: int = 1000
start_num_of_entities: int = 10
start_num_of_old_entities: int = 0
num_of_entities_for_saving: int = 100
start_marker_size: int = 25

mutation_rate: float = 0.05
base_to_bits = {'0': 0b00, '1': 0b01, '2': 0b10, '3': 0b11}

not_pause: bool = True
painting: bool = True
play: bool = True
stopper: int = 30
generations_counter: int = 0

# Math
Pi_2: float = 2 * math.pi


# Functions
def eco_start():
    global entities, died_entities, start_marker_size, start_num_of_entities, start_num_of_old_entities, \
        num_of_entities_for_saving, start_DNA_len, generations_counter
    generations_counter += 1
    if entities or died_entities: save_dna_to_file(entities, died_entities, num_of_entities_for_saving)
    entities = []
    died_entities = []
    old_dna = []
    if start_num_of_old_entities > 0:
        old_dna = read_dna_from_file()
        if old_dna:
            if len(old_dna) > start_num_of_old_entities:
                sum_wellness = sum(wellness for wellness, _ in old_dna)
                old_dna = choices(
                    population=old_dna,
                    weights=[wellness / sum_wellness for wellness, _ in old_dna],
                    k=start_num_of_old_entities
                )

            for i in range(min(len(old_dna), start_num_of_old_entities)):
                entities.append(Biotic(x=rand(1, int(field_size*0.99)-1), y=rand(1, int(field_size*0.99)-1),
                                       dna=old_dna[i][1], marker_size=start_marker_size))
    for i in range(start_num_of_entities-min(len(old_dna), start_num_of_old_entities)):
        start_dna: int = rand(0, 3)
        for _ in range(start_DNA_len - 1):
            start_dna *= 10
            start_dna += rand(0, 3)
        entities.append(Biotic(x=rand(1, int(field_size*0.99)-1), y=rand(1, int(field_size*0.99)-1),
                               dna=str(start_dna), marker_size=start_marker_size))


def drawing():
    # game.fill((0,0,0))
    drawstring()
    win.blit(game, (25, 25))
    pygame.display.update()


def drawstring():
    global entities, died_entities, generations_counter
    info_string.fill((100, 100, 100))
    try: info_string.blit(font.render("FPS " + str(int(clock.get_fps())), 0, (250, 250, 250)), [0, 0])
    except Exception as ex: info_string.blit(font.render("FPS  inf", 0, (250, 250, 250)), [0, 0])
    info_string.blit(font.render("N of Cells " + str(len(entities)), 0, (250, 250, 250)), [100, 0])
    info_string.blit(font.render("N of Dead cells " + str(len(died_entities)), 0, (250, 250, 250)), [200, 0])
    info_string.blit(font.render("Generation N " + str(generations_counter), 0, (250, 250, 250)), [500, 0])

    win.blit(info_string, (0, 0))


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
        codon += ((mutation_type % 2)*2-1)*10**(mutation_type//2)
        codon = str(codon)
        if codon[0] == '-': codon = '3' + codon[1:]
    return codon


def save_dna_to_file(a_entities, d_entities, num_for_saving):
    global field_size
    # Create a dictionary to map entity IDs to their corresponding wellness scores
    entity_dict = defaultdict(lambda: {"number_of_descendants": 0, "children": []})

    # Helper function to add entities to the dictionary
    def add_entities_to_dict(entities_list):
        for entity2 in entities_list:
            entity_dict[entity2.id]["number_of_descendants"] = entity2.number_of_descendants
            parent_id = '-'.join(entity2.id.split('-')[:-1])
            if parent_id:
                entity_dict[parent_id]["children"].append(entity2.id)

    # Add all entities to the dictionary
    add_entities_to_dict(entities)
    add_entities_to_dict(died_entities)

    # Function to recursively update wellness scores
    def update_number_of_descendants(entity_id):
        number_of_descendants = entity_dict[entity_id]["number_of_descendants"]
        for child_id in entity_dict[entity_id]["children"]:
            number_of_descendants += update_number_of_descendants(child_id)//2
        entity_dict[entity_id]["number_of_descendants"] = number_of_descendants
        return number_of_descendants

        # Update wellness scores for all top-level entities (those without a parent)

    for entity in a_entities + d_entities:
        if '-' not in entity.id:
            update_number_of_descendants(entity.id)
    # Collect current entities with their updated wellness scores
    current_entities = [(entity_dict[entity.id]["number_of_descendants"] * entity.how_long_living, entity.dna) for entity in a_entities + d_entities]

    # Open Before_field_best_dna.txt file and read existing entries
    best_entities = read_dna_from_file(str(field_size))
    # Combine current entities with those from the file and sort by wellness score
    best_entities.extend(current_entities)
    best_entities = sorted(best_entities, key=lambda x: x[1], reverse=False)

    best_entities_uniq = []
    prev = [0, 0]
    for item in best_entities:
        if item[1] != prev:
            best_entities_uniq.append(item)
            prev = item[1]

    best_entities_uniq = sorted(best_entities_uniq, key=lambda x: x[0], reverse=True)[:num_for_saving]
    # Save the top 10 entities to Before_field_best_dna.txt file
    how_many_new_saved = 0
    with open("Field_" + str(field_size) + "_best_dna.txt", 'w') as file:
        for entity2 in best_entities_uniq:
            if entity2[0] > 0:
                file.write(f"{int(entity2[0])}\t\t{entity2[1]}\n")
                if entity2 in current_entities:
                    print("Saved new dna with wellness =", entity2[0])
                    how_many_new_saved += 1
    print("Saved", how_many_new_saved, "new DNAs")
    file.close()


def read_dna_from_file(f_size='0'):
    old_entities = []
    try:
        with open("Field_" + f_size + "_best_dna.txt", 'r') as file:
            lines = file.readlines()
            for line in lines:
                wellness, dna = line.strip().split('\t\t')
                old_entities.append((int(wellness), dna))
    except FileNotFoundError:
        pass  # If the file doesn't exist, we will create it later
    return old_entities


# Classes
class Biotic:
    def __init__(self, **parent):
        global mutation_rate
        self.x: int = parent.get('x', 0)
        self.y: int = parent.get('y', 0)
        self.id: str = parent.get('id', '') + str(rand(0, 1000))
        self.marker_size = parent.get('marker_size', 10)
        self.dna: str = parent.get('dna', '')
        self.dna_len: int = len(self.dna)
        self.temp_dna: str = ''
        self.mutation_rate: float = parent.get('mutation_rate', mutation_rate)
        self.when_ready_to_die: int = parent.get('when_ready_to_die', 10)
        self.vel_x: float = parent.get('vel_x', rand(-2, 2))
        self.vel_y: float = parent.get('vel_y', rand(-2, 2))
        self.food_in_stomach_for_hunger_count: float = parent.get('hunger_count', self.marker_size)
        self.hp: float = parent.get('hp', int(self.marker_size))
        self.not_sibling_dict = dict()
        self.number_of_descendants: int = 0
        self.how_long_living: int = 0

        # Control bools
        self.alive: bool = True
        self.create_new_entity: bool = False

        # Codons must be the last here for normal parameters printing
        # 0** - most important
        # 1** - nums and factors for ai
        # 2** - Bools for funcs
        # Naming: 'num' + num of nums + min value + max value + name
        # Between '_'   | if num of nums=1 min and max value will /10 float
        #    or 'bool' + i_factor (/10) + bigger then (/10) + name
        #    Between '_' | if for def - part after 'can_' must be same as def name
        self.start_codons = {
            '000': 'bool_00_00_can_replication',

            '100': 'num_1_-045_045_mass_change_factor',
            '101': 'num_2_0_010_max_velocity',
            '102': 'num_3_0_256_color',
            '103': 'num_1_0_062_vision_angle',
            '110': 'num_1_0_9999_vision_distance',
            '111': 'num_1_0_010_when_is_sibling',
            '112': 'num_1_0_009_parent_mass_to_child',
            '113': 'num_1_0_99999_when_ready_to_create_max',
            '120': 'num_2_0_300_min_and_max_mass',

            '200': 'bool_45_00_can_eat_alives',
            '201': 'bool_45_00_can_eat_deads',
            '202': 'bool_45_00_can_photosynthesize',
        }
        self.finish_codons = {
            '000': '333',

            '100': '332',
            '101': '331',
            '102': '330',
            '103': '320',
            '110': '313',
            '111': '312',
            '112': '311',
            '113': '310',
            '120': '303',

            '200': '323',
            '201': '322',
            '202': '321',
        }

        self.dna_sequencing()

        self.when_ready_to_create: int = int(self.when_ready_to_create_max)
        if self.min_and_max_mass[0] > self.min_and_max_mass[1]:
            self.min_and_max_mass[0], self.min_and_max_mass[1] = self.min_and_max_mass[1], self.min_and_max_mass[0]
        self.dict_can_attr = []
        for parameter in self.start_codons:
            char_name = self.start_codons[parameter][11:]
            action = self.__dict__.get(char_name, False)
            if action:
                action = self.__getattribute__(char_name[4:])
                if callable(action):
                    self.dict_can_attr.append(action)
                else:
                    print("_____There must be error in def name for", char_name[4:], "_____", action)
        self.dict_can_attr_len = max(len(self.dict_can_attr), 1) - 1

    def __getattr__(self, item):
        if item == 'color':
            self.color = (125, 125, 125)
            return [125, 125, 125]
        elif item == 'max_velocity':
            self.max_velocity = [0, 0]
            return [0, 0]
        elif item == 'min_and_max_mass':
            self.min_and_max_mass = [0, 10]
            return [0, 0]
        else: return 0

    # technic and update block
    def draw_circle(self):
        global field_x_window
        # can draw smaller, to save space
        circle_x = int(self.x * field_x_window)
        circle_y = int(self.y * field_x_window)
        circle_r = self.marker_size * field_x_window  # Check mb need to *2 or 3, if too small
        # try:
        pygame.draw.circle(game, self.color, (circle_x, circle_y), circle_r, 0)
        # except e as ex:
        #     self.color = (125, 125, 125)

        if self.can_eat_alives: pygame.draw.circle(game, (255, 0, 0), (circle_x, circle_y), 10, 0)
        if self.can_eat_deads: pygame.draw.circle(game, (100, 100, 100), (circle_x + 5, circle_y + 5), 8, 0)
        if self.can_photosynthesize: pygame.draw.circle(game, (0, 255, 0), (circle_x-5, circle_y - 5), 8, 0)

    def show_parameters(self):
        temp_dict = self.__dict__.copy()
        del temp_dict['start_codons']
        del temp_dict['finish_codons']
        del temp_dict['dict_can_attr']
        temp_dict = dict(sorted(temp_dict.items()))
        print("\n\n\t\t Biota parameters START\n")
        for parameter in temp_dict:
            print('{} : {}'.format(parameter, temp_dict[parameter]))
        print("\n\t\t Biota parameters END\n")

    def interact(self, second_x: int, second_y: int, second_marker_size: float = 0):
        if (second_x - self.x) ** 2 + (second_y - self.y) ** 2 < (self.marker_size + second_marker_size) ** 2:
            return True
        else:
            return False

    def is_in_sight(self, entity2):
        global Pi_2
        dx = entity2.x - self.x
        dy = entity2.y - self.y
        distance = dx ** 2 + dy ** 2
        if distance > self.vision_distance ** 2:
            return False
        angle = math.atan2(dy, dx) % Pi_2
        vision_angle_start = (self.get_orientation() - self.vision_angle / 2) % Pi_2
        vision_angle_end = (self.get_orientation() + self.vision_angle / 2) % Pi_2
        if vision_angle_start < vision_angle_end:
            return vision_angle_start <= angle <= vision_angle_end
        else:  # Случай, когда угол зрения пересекает 0 градусов
            return angle >= vision_angle_start or angle <= vision_angle_end

    def get_orientation(self):
        return math.atan2(self.vel_y, self.vel_x)

    def add_to_sibling_dict(self, second_id='', second_dna=''):
        self.not_sibling_dict[second_id] = (
                (lcs_sl(self.dna, second_dna) / (min(self.dna_len, len(second_dna)))) <= self.when_is_sibling)

    def movement_factor(self):
        return (self.hp / (self.marker_size * 2)) / ((self.food_in_stomach_for_hunger_count / self.marker_size * 1.5) *
                                                     ((self.marker_size - 9.9) / 90) + 0.0001)

    def update(self):
        global entities, died_entities
        if self.when_ready_to_die <= 0: self.alive = False

        if self.alive:
            self.how_long_living += 1
            if self.hp > self.marker_size * 2:
                self.hp = self.marker_size * 2
            elif self.hp <= 0:
                self.alive = False
                self.hp = 0

            self.move()

            for action in self.dict_can_attr:  # I think, i will not use too many 'can' actions, so i can make it inside move cucle
                action()
            if self.marker_size <= 0: print(self.id, "ms after move =", self.marker_size)

            self.hunger()
            self.mass_change()
            if self.marker_size <= 0: print(self.id, "ms after mchange =", self.marker_size)

            if self.when_ready_to_create: self.when_ready_to_create -= 1
            else: self.create_new_entity = True

        elif self.marker_size <= 0:
            died_entities.append(self)
            entities.pop(entities.index(self))

        else:
            self.marker_size -= self.marker_size / 100 + 0.5
            self.color = (self.color[0]//1.01, self.color[1]//1.01, self.color[2]//1.01)

    # DNA block
    def dna_sequencing(self):
        for i in range(self.dna_len - 2):
            codon = self.dna[i:i+3]
            if codon in self.start_codons and self.finish_codons[codon] in self.dna[i:]:
                self.temp_dna = self.dna[i:]
                self.add_characteristic(self.start_codons.get(codon), self.finish_codons[codon])

    def replication(self, start_codon='000', finish_codon='333'):
        if self.create_new_entity and self.hp > self.marker_size:
            global start_marker_size
            new_dna: str = ''
            self.temp_dna = ''
            for i in range(self.dna_len):
                if self.dna[i:i+3] == start_codon and finish_codon in self.dna[i:]:
                    self.temp_dna = self.dna[i:]
                    break
            if self.temp_dna == '':
                return None
            for i in range(int(len(self.temp_dna)/3)):
                if int(self.temp_dna[0]) > 3: codon = '0'
                else: codon = self.temp_dna[0]
                if int(self.temp_dna[1]) > 3: codon += '0'
                else: codon += self.temp_dna[1]
                if int(self.temp_dna[2]) > 3: codon += '0'
                else: codon += self.temp_dna[2]
                if rand(0, 1000) < mutation_rate * 1000: codon = codon_mutation(codon)
                new_dna += codon
                if finish_codon in self.temp_dna[:5] and not (finish_codon in self.temp_dna[5:]):
                    new_dna += self.temp_dna[3:5]
                    entities.append(Biotic(x=self.x + 10, y=self.y + 10,
                                           dna=new_dna, id=self.id + '-',
                                           color=self.color, marker_size=self.marker_size * self.parent_mass_to_child))
                    self.number_of_descendants += 1
                    break
                self.temp_dna = self.temp_dna[3:]
            self.create_new_entity = False
            self.marker_size *= 1-self.parent_mass_to_child
            self.hp *= 0.9
            self.when_ready_to_create = int(self.when_ready_to_create_max)
            self.when_ready_to_die -= 1

    def add_characteristic(self, char_name, finish_codon):
        chars = char_name.split('_')
        if chars[0] == 'bool':
            char_i_factor = float(chars[1]) / 10
            char_bigger_then = float(chars[2]) / 10
            char_name = '_'.join(chars[3:])
            attr = self.__dict__.get(char_name, 2)
            if attr == 2:
                sum_nucs: int = 0
                for i in range(int(len(self.temp_dna) / 3)):
                    codon = self.temp_dna[:3]
                    if finish_codon in codon + self.temp_dna[3:5]:
                        setattr(self, char_name, (sum_nucs - i * char_i_factor > char_bigger_then))
                        break
                    self.temp_dna = self.temp_dna[3:]
                    codon = int(codon)
                    sum_nucs += codon // 100 + codon % 10 + ((codon // 10) % 10)

        elif chars[0] == 'num':
            char_num_of_nums = int(chars[1])
            char_min_value = int(chars[2])
            char_max_value = int(chars[3])
            char_name = '_'.join(chars[4:])
            attr = self.__dict__.get(char_name, False)
            if not attr:
                nums = []
                sum_nums: int
                mean_nums: int
                median_nums: int
                len_nums: int
                for i in range(int(len(self.temp_dna) / 3)):
                    codon = self.temp_dna[:3]
                    nums.append(int(codon))
                    if finish_codon in codon + self.temp_dna[3:5]:
                        nums = sorted(nums)
                        len_nums = len(nums)
                        sum_nums = sum(nums)
                        mean_nums = sum_nums // len_nums
                        if len_nums % 2 == 0:
                            median_nums = (nums[len_nums // 2 - 1] + nums[len_nums // 2]) // 2
                        else:
                            median_nums = nums[len_nums // 2]
                        if char_num_of_nums == 1:
                            char_max_value = float(char_max_value)/10
                            char_min_value = float(char_min_value)/10
                            char_value = (float(median_nums) / 330) * (char_max_value - char_min_value) + char_min_value
                        else:
                            char_value = [sum_nums % (char_max_value - char_min_value) + char_min_value,
                                          mean_nums % (char_max_value - char_min_value) + char_min_value,
                                          median_nums % (char_max_value - char_min_value) + char_min_value]
                            char_value = char_value[:char_num_of_nums]
                        setattr(self, char_name, char_value)
                        break
                    self.temp_dna = self.temp_dna[3:]
        else: print("_____There is a problem with codon name in ", char_name, "_____")

    # AI block
    def eat_alives(self):
        for entity_2 in entities:
            if entity_2 == self: continue
            if (entity_2.alive and self.not_sibling_dict.get(entity_2.id, False)
                    and self.interact(entity_2.x, entity_2.y, entity_2.marker_size)):  # Can change is_sibling_dict logic - change to can_eat_it, to make less controlls ||| No, couldnt - alive can dead
                if self.marker_size < entity_2.marker_size and entity_2.can_eat_alives:
                    self.hp -= self.marker_size / 10 + 1
                    entity_2.food_in_stomach_for_hunger_count += self.marker_size / 10 + 1
                elif self.marker_size < entity_2.marker_size and not entity_2.can_eat_alives:
                    self.food_in_stomach_for_hunger_count += entity_2.marker_size / 10 + 1
                    entity_2.hp -= entity_2.marker_size / 10 + 1
                elif self.marker_size > entity_2.marker_size and not entity_2.can_eat_alives:
                    self.food_in_stomach_for_hunger_count += entity_2.marker_size / 10 + 1
                    entity_2.hp -= entity_2.marker_size / 10 + 1

    def eat_deads(self):
        for entity_2 in entities:
            if (not entity_2.alive and self.not_sibling_dict.get(entity_2.id, False)
                    and self.interact(entity_2.x, entity_2.y, entity_2.marker_size)):
                if self.marker_size > entity_2.marker_size:
                    self.food_in_stomach_for_hunger_count += entity_2.marker_size / 30 + 1
                    entity_2.marker_size -= entity_2.marker_size / 30 + 1
                if self.marker_size < entity_2.marker_size:
                    self.food_in_stomach_for_hunger_count += entity_2.marker_size / 50 + 1
                    entity_2.marker_size -= entity_2.marker_size / 50 + 1

    def photosynthesize(self):
        # make smth for better sunlight imitation
        global where_is_sun
        is_in_sun = False
        for place_ in where_is_sun:
            if place_.free_sun_amount > 0 and self.interact(place_.x, place_.y, place_.r):
                is_in_sun = True
                place_.update_free_sun_amount(self.marker_size)
                break
        self.food_in_stomach_for_hunger_count += 10 * is_in_sun / (self.max_velocity[0] + self.max_velocity[1] + 0.1)  # 0.35

    def hunger(self):
        hunger_count = self.marker_size/500 + 0.05 * self.dict_can_attr_len + 0.01 * (abs(self.vel_x) + abs(self.vel_y))
        self.food_in_stomach_for_hunger_count -= hunger_count

        # If there's enough food, maintain or increase hp
        if self.food_in_stomach_for_hunger_count > 0:
            self.hp += 0.5
        else:
            # If there's not enough food, decrease hp
            self.hp -= 1
            self.marker_size -= self.marker_size / 100
            self.food_in_stomach_for_hunger_count = 0

        # If the entity is starving, decrease hp more
        if self.hp < self.min_and_max_mass[0]:
            self.marker_size -= self.min_and_max_mass[0] - self.hp
            self.hp = self.min_and_max_mass[0]

        if self.food_in_stomach_for_hunger_count > self.marker_size:
            self.hp += 0.5
            self.marker_size += self.marker_size / 100
            self.food_in_stomach_for_hunger_count = min(self.food_in_stomach_for_hunger_count, self.marker_size * 1.5)

    def mass_change(self):  # wtf with mass????
        mass_change = self.mass_change_factor + self.hp / (self.marker_size * 2) - (self.marker_size / 120 - 0.5)
        self.marker_size += mass_change
        if self.marker_size > self.min_and_max_mass[1]:
            self.hp -= (self.marker_size - self.min_and_max_mass[1])
            self.marker_size = self.min_and_max_mass[1]
        elif self.marker_size < self.min_and_max_mass[0]:
            if self.hp <= self.food_in_stomach_for_hunger_count:
                self.marker_size += self.food_in_stomach_for_hunger_count
                self.food_in_stomach_for_hunger_count = 0
            else:
                self.marker_size += self.hp/2 + 2
                self.hp -= self.hp/2 + 2

    def move(self):
        global entities, field_size, where_is_sun

        # Need to make smth for plants, and other mooving when stomach is full
        # if self.food_in_stomach_for_hunger_count > self.marker_size * 1.25: return None
        # Determine the new velocity based on some conditions
        closest_distance = float('inf')
        closest_aim = None
        if self.can_eat_alives or self.can_eat_deads:
            for entity_2 in entities:
                if entity_2 == self: continue
                if self.not_sibling_dict.get(entity_2.id, 2) == 2:  # || entity_2.id not in self.not_sibling_dict:
                    self.add_to_sibling_dict(entity_2.id, entity_2.dna)

                if (self.not_sibling_dict[entity_2.id] and self.is_in_sight(entity_2)
                        and ((entity_2.alive and self.can_eat_alives)
                             or (not entity_2.alive and self.can_eat_deads))):
                    distance = ((entity_2.x - self.x) ** 2 + (entity_2.y - self.y) ** 2) ** 0.5 + 0.001
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_aim = entity_2

            if closest_aim and closest_aim.can_eat_alives and closest_aim.marker_size > self.marker_size:
                closest_distance *= -1

        if self.can_photosynthesize:
            closest_r = 100000
            for place_ in where_is_sun:
                if place_.free_sun_amount > 0:
                    distance = ((place_.x - self.x) ** 2 + (place_.y - self.y) ** 2) ** 0.5 - place_.r / 2
                    if distance < abs(closest_distance):
                        closest_distance = distance
                        closest_aim = place_
                        closest_r = place_.r
            if abs(closest_distance) <= closest_r: closest_distance = 1000

        if closest_aim:
            m_f = self.movement_factor()
            self.vel_x = (closest_aim.x - self.x) / closest_distance * self.max_velocity[0] * m_f
            self.vel_y = (closest_aim.y - self.y) / closest_distance * self.max_velocity[1] * m_f

        if self.vel_x > self.max_velocity[0]: self.vel_x = self.max_velocity[0]
        elif self.vel_x < -self.max_velocity[0]: self.vel_x = -self.max_velocity[0]
        if self.vel_y > self.max_velocity[1]: self.vel_y = self.max_velocity[1]
        elif self.vel_y < -self.max_velocity[1]: self.vel_y = -self.max_velocity[1]

        self.x += self.vel_x
        self.y += self.vel_y

        # Ensure the entity stays within field boundaries
        if self.x < self.marker_size:
            self.x = self.marker_size
            self.vel_x *= -1
        elif self.x > field_size - self.marker_size:
            self.x = field_size - self.marker_size
            self.vel_x *= -1

        if self.y < self.marker_size:
            self.y = self.marker_size
            self.vel_y *= -1
        elif self.y > field_size - self.marker_size:
            self.y = field_size - self.marker_size
            self.vel_y *= -1


    # Add variables for movement, like braveness, etc
    # add control what to do - hunt to small or run from big and braveness
    # chane hunt func to cooperate factor and size*braveness
    # add mitos mass, mass parent/child factor
    # Finally make normal sibls score


class Abiotic:
    def __init__(self, x=0, y=0, r=0, place_type='sun'):
        self.x: int = x
        self.y: int = y
        self.r: int = r
        self.max_sun_amount: int = r
        self.free_sun_amount: int = r
        self.type: str = place_type
        self.color = (125, 125, 0)

    def draw_circle(self):
        global field_x_window
        # can draw smaller, to save space
        circle_x = int(self.x * field_x_window)
        circle_y = int(self.y * field_x_window)
        circle_r = self.r * field_x_window  # Check mb need to *2 or 3, if too small
        pygame.draw.circle(game, self.color, (circle_x, circle_y), circle_r, 0)

    def update_free_sun_amount(self, entity_marker_size):
        self.free_sun_amount -= entity_marker_size


pygame.init()
win = pygame.display.set_mode((window_size*1.1, window_size*1.1))
pygame.display.set_caption('Ecosystem')
game = pygame.Surface((window_size, window_size))
info_string = pygame.Surface((window_size, window_size/19.2))

win.fill((100, 100, 100))

clock = pygame.time.Clock()
pygame.key.set_repeat(200, 50)

pygame.font.init()  # инициализируем шрифты
font = pygame.font.SysFont('arial', 15)
# ['arial', 'arialblack', 'bahnschrift', 'calibri', 'cambria', 'cambriamath', 'candara', 'comicsansms', 'consolas', 'constantia', 'corbel', 'couriernew', 'ebrima', 'franklingothicmedium', 'gabriola', 'gadugi', 'georgia', 'impact', 'inkfree', 'javanesetext', 'leelawadeeui', 'leelawadeeuisemilight', 'lucidaconsole', 'lucidasans', 'malgungothic', 'malgungothicsemilight', 'microsofthimalaya', 'microsoftjhenghei', 'microsoftjhengheiui', 'microsoftnewtailue', 'microsoftphagspa', 'microsoftsansserif', 'microsofttaile', 'microsoftyahei', 'microsoftyaheiui', 'microsoftyibaiti', 'mingliuextb', 'pmingliuextb', 'mingliuhkscsextb', 'mongolianbaiti', 'msgothic', 'msuigothic', 'mspgothic', 'mvboli', 'myanmartext', 'nirmalaui', 'nirmalauisemilight', 'palatinolinotype', 'sansserifcollection', 'segoefluenticons', 'segoemdl2assets', 'segoeprint', 'segoescript', 'segoeui', 'segoeuiblack', 'segoeuiemoji', 'segoeuihistoric', 'segoeuisemibold', 'segoeuisemilight', 'segoeuisymbol', 'segoeuivariable', 'simsun', 'nsimsun', 'simsunextb', 'sitkatext', 'sylfaen', 'symbol', 'tahoma', 'timesnewroman', 'trebuchetms', 'verdana', 'webdings', 'wingdings', 'yugothic', 'yugothicuisemibold', 'yugothicui', 'yugothicmedium', 'yugothicuiregular', 'yugothicregular', 'yugothicuisemilight', 'holomdl2assets', 'agencyfbполужирный', 'agencyfb', 'algerian', 'bookantiquaполужирный', 'bookantiquaполужирныйкурсив', 'bookantiquaкурсив', 'arialполужирный', 'arialполужирныйкурсив', 'arialкурсив', 'arialrounded', 'baskervilleoldface', 'bauhaus93', 'bell', 'bellполужирный', 'bellкурсив', 'bernardcondensed', 'bookantiqua', 'bodoniполужирный', 'bodoniполужирныйкурсив', 'bodoniblackкурсив', 'bodoniblack', 'bodonicondensedполужирный', 'bodonicondensedполужирныйкурсив', 'bodonicondensedкурсив', 'bodonicondensed', 'bodoniкурсив', 'bodonipostercompressed', 'bodoni', 'bookmanoldstyle', 'bookmanoldstyleполужирный', 'bookmanoldstyleполужирныйкурсив', 'bookmanoldstyleкурсив', 'bradleyhanditc', 'britannic', 'berlinsansfbполужирный', 'berlinsansfbdemiполужирный', 'berlinsansfb', 'broadway', 'brushscriptкурсив', 'bookshelfsymbol7', 'californianfbполужирный', 'californianfbкурсив', 'californianfb', 'calisto', 'calistoполужирный', 'calistoполужирныйкурсив', 'calistoкурсив', 'castellar', 'centuryschoolbook', 'centaur', 'century', 'chiller', 'colonna', 'cooperblack', 'copperplategothic', 'curlz', 'dubai', 'dubaimedium', 'dubairegular', 'elephant', 'elephantкурсив', 'engravers', 'erasitc', 'erasdemiitc', 'erasmediumitc', 'felixtitling', 'forte', 'franklingothicbook', 'franklingothicbookкурсив', 'franklingothicdemi', 'franklingothicdemicond', 'franklingothicdemiкурсив', 'franklingothicheavy', 'franklingothicheavyкурсив', 'franklingothicmediumcond', 'freestylescript', 'frenchscript', 'footlight', 'garamond', 'garamondполужирный', 'garamondкурсив', 'gigi', 'gillsansполужирныйкурсив', 'gillsansполужирный', 'gillsanscondensed', 'gillsansкурсив', 'gillsansultracondensed', 'gillsansultra', 'gillsans', 'gloucesterextracondensed', 'gillsansextcondensed', 'centurygothic', 'centurygothicполужирный', 'centurygothicполужирныйкурсив', 'centurygothicкурсив', 'goudyoldstyle', 'goudyoldstyleполужирный', 'goudyoldstyleкурсив', 'goudystout', 'harlowsolid', 'harrington', 'haettenschweiler', 'hightowertext', 'hightowertextкурсив', 'imprintshadow', 'informalroman', 'blackadderitc', 'edwardianscriptitc', 'kristenitc', 'jokerman', 'juiceitc', 'kunstlerscript', 'widelatin', 'lucidabright', 'lucidacalligraphy', 'leelawadee', 'leelawadeeполужирный', 'lucidafaxregular', 'lucidafax', 'lucidahandwriting', 'lucidasansregular', 'lucidasansroman', 'lucidasanstypewriterregular', 'lucidasanstypewriter', 'lucidasanstypewriteroblique', 'magnetoполужирный', 'maiandragd', 'maturascriptcapitals', 'mistral', 'modernno20', 'microsoftuighurполужирный', 'microsoftuighur', 'monotypecorsiva', 'extra', 'niagaraengraved', 'niagarasolid', 'ocraextended', 'oldenglishtext', 'onyx', 'msoutlook', 'palacescript', 'papyrus', 'parchment', 'perpetuaполужирныйкурсив', 'perpetuaполужирный', 'perpetuaкурсив', 'perpetuatitlingполужирный', 'perpetuatitling', 'perpetua', 'playbill', 'poorrichard', 'pristina', 'rage', 'ravie', 'msreferencesansserif', 'msreferencespecialty', 'rockwellcondensedполужирный', 'rockwellcondensed', 'rockwell', 'rockwellполужирный', 'rockwellполужирныйкурсив', 'rockwellextra', 'rockwellкурсив', 'centuryschoolbookполужирный', 'centuryschoolbookполужирныйкурсив', 'centuryschoolbookкурсив', 'script', 'showcardgothic', 'snapitc', 'stencil', 'twcenполужирныйкурсив', 'twcenполужирный', 'twcencondensedполужирный', 'twcencondensedextra', 'twcencondensed', 'twcenкурсив', 'twcen', 'tempussansitc', 'vinerhanditc', 'vivaldiкурсив', 'vladimirscript', 'wingdings2', 'wingdings3']
# print(pygame.font.get_fonts())

for i in range(3):
    where_is_sun.append(Abiotic(x=rand(1, field_size), y=rand(1, field_size), r=rand(50, 200), place_type='sun'))


eco_start()

while play:
    clock.tick(0)

    for e in pygame.event.get():
        if e.type == pygame.QUIT: play = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE: play = False
            if e.key == pygame.K_SPACE: not_pause = not not_pause
            if e.key == pygame.K_p: painting = not painting
            if e.key == pygame.K_r:
                print("\n\n RESTART")
                eco_start()
            if e.key == pygame.K_UP and stopper > 0:
                stopper //= 1.1
                print(stopper)
            if e.key == pygame.K_DOWN and stopper < 400:
                stopper = int(stopper * 1.1) + 1
                print(stopper)

        if not not_pause and e.type == pygame.MOUSEBUTTONDOWN:
            mouse_xy = pygame.mouse.get_pos()
            mouse_xy = (mouse_xy[0]-25, mouse_xy[1]-25)
            pygame.draw.circle(game, (255, 255, 255), mouse_xy, 2, 0)
            win.blit(game, (25, 25))
            pygame.display.update()
            mouse_xy = (mouse_xy[0] / field_x_window, mouse_xy[1] / field_x_window)

            for entity in entities:
                if entity.interact(mouse_xy[0], mouse_xy[1]):
                    entity.show_parameters()
                    break

    if not_pause:
        if len(entities) == 0:
            print("\n\n RESTART\t Gen =", generations_counter)
            eco_start()
        if painting:
            game.fill((30, 30, 30))
            for place in where_is_sun:
                place.free_sun_amount = place.max_sun_amount
                place.draw_circle()
            for entity in entities:
                entity.update()
                entity.draw_circle()
            drawing()
            pygame.time.delay(int(stopper))
        else:
            for entity in entities:
                entity.update()

save_dna_to_file(entities, died_entities, num_of_entities_for_saving)
pygame.quit()


# import time
# a = {'1': 1, '2': 2, '3': 3}
# start = time.time()
# for i in range(50000000):
#     if a.get(str(i), '') == 'q': a[str(i)] = i
# print("Time 1 " + str(time.time() - start))
#
# a = {'1': 1, '2': 2, '3': 3}
# start = time.time()
# for i in range(50000000):
#     if str(i) not in a.keys(): a[str(i)] = i
# print("Time 2 " + str(time.time() - start))
