import argparse
import copy
import os
import json
import sys
import traceback

print('Kings Raid Skill Dumper v1.0')
print('By: cpp (Reddit: u/cpp_is_king, Discord: @cpp#0120)')
print('Paypal: cppisking@gmail.com')
print()

if sys.version_info < (3,5):
    print('Error: This script requires Python 3.5 or higher.  Please visit '
          'www.python.org and install a newer version.')
    print('Press any key to exit...')
    input()
    sys.exit(1)

args = None
creature_star_grade_data = None
creature_by_index = None
creature_by_name = None
skills_by_index = None
skill_level_factors = None
indent_level = 0

def print_line(message):
    global indent_level
    print(' ' * indent_level, end = '')
    print(message)

def indent(amount):
    global indent_level
    indent_level = indent_level + amount

def decode_file(path):
    codecs = ['utf-8-sig', 'utf-8']
    for c in codecs:
        try:
            with open(path, 'r', encoding=c) as fp:
                return fp.read()
        except:
            traceback.print_exc()
            pass
    return None

def parse_args():
    parser = argparse.ArgumentParser(description='Kings Raid Json Dumper.')
    parser.add_argument('--json_path', type=str, help='The folder containing json files')
    parser.add_argument('--star-grade-data', action='store_true', default=False, help='Dump Creature Star Grade Data')
    parser.add_argument('--heros', action='store_true', default=False, help='Dump Hero Skills')
    parser.add_argument('--hero', type=str, help='When --heros is specified, limit dumping to the specified hero (e.g. Kasel)')
    parser.add_argument('--books', type=str, help='Assume skills have the specified book upgrades (e.g. --books=1,3,2,1)')
    return parser.parse_args()

def max_numbered_key(obj, prefix):
    indices = set(map(lambda x : int(x[-1]),
                                filter(lambda x : x.startswith(prefix), obj.keys())))
    if len(indices) == 0:
        return None
    return max(indices)

def update_table(json_obj, indexes):
    for obj in json_obj:
        for key, table in indexes:
            value = obj[key]
            if value in table:
                print('Warning: {0}={1} appears more than once.  Ignoring subsequent occurrences...'.format(key, value))
                continue
            table[value] = obj

def load_creatures_table():
    print('Loading creatures...')
    global args
    global creature_by_index
    global creature_by_name

    path = os.path.join(args.json_path, 'CreatureTable.json')
    content = decode_file(path)
    json_obj = json.loads(content)
    creature_by_index = {}
    creature_by_name = {}
    update_table(json_obj, [('Index', creature_by_index), ('CodeName', creature_by_name)])

def load_skills_table():
    print('Loading skills...')
    global args
    global skills_by_index
    index = 0
    skills_by_index = {}
    path = os.path.join(args.json_path, 'SkillTable.json')
    while True:
        content = decode_file(path)
        json_obj = json.loads(content)
        update_table(json_obj, [('Index', skills_by_index)])
        index = index + 1
        path = os.path.join(args.json_path, 'SkillTable{0}.json'.format(index))
        if not os.path.exists(path):
            break

def is_playable_hero(creature):
    return 'OpenType' in creature

def load_creature_star_grade_data_table():
    print('Loading creature star grade data...')
    global creature_star_grade_data
    global creature_by_index

    def short_stat_name(stat):
        mapping = {
            "PhysicalCriticalChance" : "P. Crit",
            "PhysicalDodgeChance" : "P. Dodge",
            "PhysicalHitChance" : "P. Acc",
            "PhysicalPiercePower" : "P. Pen",
            "PhysicalToughness" : "P. Tough",
            "MagicalCriticalChance" : "M. Crit",
            "MagicalDodgeChance" : "M. Dodge",
            "MagicalHitChance" : "M. Acc",
            "MagicalPiercePower" : "M. Pen",
            "MagicalToughness" : "M. Tough",
            "AntiCcChance" : "CC Resist",
            "MaxMp" : "MP",
            "MpOnDamage" : "MP/DMG",
            "MpOnAttack" : "MP/ATK",
            "MpOnTime" : "MP/Time",
            "MpOnKill" : "MP/Kill",
            "MpRegenRatioM" : "MP Regen",
            "AttackSpeed" : "ASpd",
            "MoveSpeedMms" : "Move Spd",
            "LevelStatFactor" : "Lvl Factor",
            "MagicalBlockChance" : "M. Block",
            "MagicalBlockPower" : "M. Block DEF",
            "PhysicalBlockChance" : "P. Block",
            "PhysicalBlockPower" : "P. Block DEF",
            "PhysicalCriticalPower" : "P. Crit DMG",
            "MagicalCriticalPower" : "M. Crit DMG",
            "HpStealPower" : "Lifesteal",
            "MagicalDefensePower" : "M. DEF",
            "PhysicalDefensePower" : "P. DEF",
            }
        return mapping[stat]

    path = os.path.join(args.json_path, 'CreatureStarGradeStatTable.json')
    content = decode_file(path)
    json_obj = json.loads(content)
    creature_star_grade_data = {}

    for obj in json_obj:
        index = obj['CreatureIndex']
        if not index in creature_by_index:
            continue

        star = obj['Star']
        transcend = obj.get('Transcended', 0)
        effective_star = star + transcend
        table = None
        if not index in creature_star_grade_data:
            table = {}
            creature_star_grade_data[index] = table
        else:
            table = creature_star_grade_data[index]

        if effective_star in table:
            print('Warning: Creature star grade ({0}, {1}, {2}) appears more than once.  Ignoring subsequent occurrences...'.format(index, star, transcend))
            continue
        for stat in obj:
            if stat == 'CreatureIndex':
                continue
            if stat == 'Star':
                continue
            if stat == 'Transcended':
                continue
            stat_values = None
            short_stat = short_stat_name(stat)
            if not short_stat in table:
                stat_values = [None] * 10
                table[short_stat] = stat_values
            else:
                stat_values = table[short_stat]
            stat_values[effective_star - 1] = obj[stat]
    return

def generate_factors(obj):
    max_factor = max_numbered_key(obj, 'Factor')
    assert(max_factor is not None)

    result = {}
    for x in range(1, max_factor+1):
        key_name = 'Factor{0}'.format(x)
        if key_name in obj:
            result[x] = obj[key_name]
    return result

def load_skill_level_factors_table():
    print('Loading skill level factors...')
    global skill_level_factors

    skill_level_factors = {}
    path = os.path.join(args.json_path, 'SkillLevelFactorTable.json')
    content = decode_file(path)
    json_obj = json.loads(content)
    for obj in json_obj:
        skill_level_factors[obj['Level']] = generate_factors(obj)
    return

def generate_skill_operations(skill_obj):
    def generate_one_operation(index):
        op_fields = list(filter(lambda x : x.startswith('Operation') and x.endswith(str(index)), skill_obj.keys()))
        d = { x[len('Operation'):-1] : skill_obj[x] for x in op_fields }
        return None if len(d) == 0 else d

    max_operation = max_numbered_key(skill_obj, 'Operation')
    if max_operation is None:
        return []

    return [generate_one_operation(x) for x in range(1, max_operation+1)]

def format_skill_operation_key(operation, key, default=None):
    if not key in operation:
        return default
    value = operation[key]
    return str(value)

def dump_default_operation(operation, type):
    value_str = format_skill_operation_key(operation, 'Value')
    target_type_str = format_skill_operation_key(operation, 'TargetType', default='null target')
    value_factors_str = format_skill_operation_key(operation, 'ValueFactor')

    type = type + '({0})'.format(target_type_str)
    if value_str:
        type = type + ', values = {0}'.format(value_str)
    if value_factors_str:
        type = type + ', factors = {0}'.format(value_factors_str)
    suffix = type

    operation.pop('Value', None)
    operation.pop('TargetType', None)
    operation.pop('ValueFactor', None)
    return suffix

def get_operation_value(values, factors, index, default):
    if len(values) <= index:
        return 0

    global skill_level_factors
    if values[index][0] == '$':
        return values[index]

    if factors is None:
        return 0
    fi = index*2
    fi2 = index*2 + 1
    if len(factors) <= fi2:
        return 0

    # Not sure what the deal is with this, but special case it for now.
    if int(factors[fi]) == 0 and int(factors[fi2]) == 0:
        return float(values[index]) / 1000.0

    level_table = skill_level_factors[80]

    level_factor_index = int(factors[fi])
    skill_scale_factor = factors[fi2]
    level_scale_factor = level_table[level_factor_index]
    result = 8 * float(level_scale_factor) * float(skill_scale_factor)
    return float(result) / 1000.0

def dump_get_damage_r(operation, type : str):
    global skill_level_factors
    values = operation['Value']
    prefix = "physical" if "Physical" in type else "magical"
    if not 'ValueFactor' in operation:
        formula = 'ATK * {0}'.format(values[0])
    else:
        factors = operation['ValueFactor']
        v1 = get_operation_value(values, factors, 0, 0)
        v2 = get_operation_value(values, factors, 1, 0)
        if len(values) >= 2:
            if values[1][0] != '$':
                v2 = int(v2 + int(values[1]))

        formula = 'Floor[ATK * {0}] + {1}'.format(v1, v2)
    target_type = operation['TargetType']
    operation.pop('TargetType', None)
    operation.pop('Value', None)
    operation.pop('ValueFactor', None)
    return '{0} DMG = {1}'.format(prefix, formula)


def dump_one_skill_operation(index, operation):
    prefix = '[{0}]: '.format(index)
    suffix = '(null)'
    if not operation:
        print_line('{0}(null)'.format(prefix))
        return

    op_copy = copy.deepcopy(operation)

    type_str = format_skill_operation_key(op_copy, 'Type')
    op_copy.pop('Type', None)
    operation_handlers = {
        'GetPhysicalDamageR' : dump_get_damage_r,
        'GetMagicalDamageR' : dump_get_damage_r
        }

    if type_str:
        if type_str in operation_handlers:
            suffix = operation_handlers[type_str](op_copy, type_str)
        else:
            suffix = dump_default_operation(op_copy, type_str)
    print_line('{0}{1}'.format(prefix, suffix))

    def should_dump(op_key_value):
        k, v = op_key_value
        if k == 'ConditionType' and v == 'None':
            return False
        return True

    op_list = [op_key_value for op_key_value in op_copy.items() if should_dump(op_key_value)]
    indent(5)
    while len(op_list) > 0:
        components = []
        for I in range(0, 3):
            if len(op_list) == 0:
                break
            k, v = op_list.pop(0)
            components.append('{0}={1}'.format(k, str(v)))
        print_line(', '.join(components))
    indent(-5)

def format_skill_header(skill_obj):
    attr = skill_obj['AttrType']
    target_type = skill_obj['TargetType']
    components = []
    if attr != 'None':
        components.append(attr.lower())
    if 'TriggerType' in skill_obj:
        trigger = skill_obj['TriggerType']
        if trigger != 'None' and trigger != 'NextSkill':
            components.append('trigger = {0}'.format(trigger))
    if 'DurationTimeMs' in skill_obj:
        duration = skill_obj['DurationTimeMs']
        components.append('duration = {0}'.format(str(duration)))
    if 'TargetCount' in skill_obj:
        target_count = skill_obj['TargetCount']
        if target_count != 1:
            components.append('target {0} {1}'.format(target_count, target_type))
        else:
            components.append('target {0}'.format(target_type))
    else:
        components.append('target {0}'.format(target_type))
    return ', '.join(components)

def dump_one_skill(name, index=None, book_mods=None):
    global skills_by_index
    skill_obj = skills_by_index[index]
    print_line('Skill: {0} ({1})'.format(name, format_skill_header(skill_obj)))
    operations = generate_skill_operations(skill_obj)

    indent(4)
    for index, op in enumerate(operations):
        dump_one_skill_operation(index, op)

    phase = 1
    while 'NextIndex' in skill_obj:
        next_index = skill_obj['NextIndex']
        skill_obj = skills_by_index[next_index]
        print_line('-> phase {0}: {1}'.format(phase, format_skill_header(skill_obj)))
        operations = generate_skill_operations(skill_obj)

        indent(12)
        for index, op in enumerate(operations):
            dump_one_skill_operation(index, op)
        phase = phase + 1
        indent(-12)
    indent(-4)

def dump_heroes():
    global creature_by_index
    for hero in filter(is_playable_hero, creature_by_index.values()):
        print_line(hero['CodeName']);
        indent(2)
        dump_one_skill('Auto Attack', index=hero['BaseSkillIndex']);
        for i in range(4):
            index_str = 'SkillIndex{0}'.format(i+1)
            book_str = 'SkillExtend{0}'.format(i+1)
            dump_one_skill("S{0}".format(i+1), index=hero[index_str], book_mods=hero[book_str])
        indent(-2)

def dump_creature_star_grade_table():
    global creature_star_grade_data
    global creature_by_index
    for index, data in creature_star_grade_data.items():
        creature = creature_by_index[index]
        print('Name: {0}'.format(creature['CodeName']))
        print('              |   1*   |   2*   |   3*   |   4*   |   5*   |   T1   |   T2   |   T3   |   T4   |   T5   |')
        for k, v in data.items():
            if k == 'CreatureIndex':
                continue
            if k == 'Star':
                continue
            if k == 'Transcended':
                continue
            print('{0:>13} | {1:>6} | {2:>6} | {3:>6} | {4:>6} | {5:>6} | {6:>6} | {7:>6} | {8:>6} | {9:>6} | {10:>6} |'.format(
                k, str(v[0]), str(v[1]), str(v[2]), str(v[3]), str(v[4]), str(v[5]), str(v[6]), str(v[7]), str(v[8]), str(v[9])))
        pass

def main():
    load_creatures_table()
    load_skills_table()
    load_skill_level_factors_table()
    load_creature_star_grade_data_table()

    if args.heros:
        dump_heroes()

    if args.star_grade_data:
        dump_creature_star_grade_table()

try:
    args = parse_args()
    main()
except:
    print('An unknown error occurred.  Please report this bug.')
    traceback.print_exc()