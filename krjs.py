import argparse
import copy
import itertools
import os
import json
import re
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

def print_line(message, add_newline=True, is_continuation=False):
    global indent_level
    if not is_continuation:
        print(' ' * indent_level, end = '')

    if add_newline:
        print(message)
    else:
        print(message, end='')

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
    parser.add_argument('--auto-attacks', action='store_true', default=True, help='With --heros, dump auto attack info')
    parser.add_argument('--skills', action='store_true', default=False, help='With --heros, dump skill info')
    parser.add_argument('--hero', type=str, help='When --heros is specified, limit dumping to the specified hero (e.g. Kasel)')
    parser.add_argument('--style', type=str, default='verbose', choices=['verbose', 'brief'], help='Level of skill detail to display')
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
        table = creature_star_grade_data.setdefault(index, {})

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
            stat_values = table.setdefault(short_stat, [None] * 10)
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

def generate_ticks(skill_obj, operations):
    ticks = skill_obj.get('TickTimeValue', None)
    if not ticks:
        return [(0, operations)]
    tick_expr = re.compile(r'(?P<t>[^\[]*)(?:\[(?P<op>.*)\])?')
    def one_tick_operations(t):
        match = tick_expr.match(t)
        if not match:
            print("The tick expression '{0}' for skill '{1}' is in an unrecognized format".format(t, skill_obj['Index']))
            return None
        time, op = match.group('t', 'op')
        if op is None:
            non_null_opers = list(filter(lambda x : x is not None, operations))
            return (int(time), non_null_opers)

        op_indices = list(map(lambda x : int(x) - 1, op.split(':')))
        op_indices = list(filter(lambda x : x < len(operations) and operations[x], op_indices))
        actions = list(map(lambda x : operations[x], op_indices))

        return (int(time), actions)
    return [one_tick_operations(t) for t in ticks]

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

def get_operation_level_value(creature_index, star, trans, factor1, factor2):
    global skill_level_factors
    global creature_star_grade_data

    sgd = creature_star_grade_data[creature_index]
    lsf = float(sgd['Lvl Factor'][star + trans - 1]) / 1000.0

    level_table = skill_level_factors[80]

    level_factor_index = factor1
    skill_scale_factor = factor2
    level_scale_factor = level_table.get(level_factor_index, 0)
    result = lsf * float(level_scale_factor) * float(skill_scale_factor)
    return float(result)

def get_operation_value(creature_index, star, trans, values, factors, index, default):
    if len(values) <= index:
        return 0

    # This is an expression, which we don't handle yet.
    if values[index][0] == '$':
        return values[index]

    if factors is None:
        return 0
    fi = index*2
    fi2 = index*2 + 1
    if len(factors) <= fi2:
        return 0

    level_value = get_operation_level_value(creature_index, star, trans, int(factors[fi]), int(factors[fi2]))

    return (float(values[index]) + level_value) / 1000.0

def dump_get_damage_r(creature_index, star, trans, operation, type : str):
    global skill_level_factors
    values = operation['Value']
    prefix = "physical" if "Physical" in type else "magical"
    if not 'ValueFactor' in operation:
        formula = 'ATK * {0}'.format(values[0])
    else:
        factors = operation['ValueFactor']
        power = get_operation_value(creature_index, star, trans, values, factors, 0, 0)
        level_factor = get_operation_value(creature_index, star, trans, values, factors, 1, 0)

        formula = 'Floor[ATK * {0} + {1}]'.format(power, level_factor)
    target_type = operation['TargetType']
    operation.pop('TargetType', None)
    operation.pop('Value', None)
    operation.pop('ValueFactor', None)
    return '{0} DMG = {1}'.format(prefix, formula)


def dump_one_skill_operation(creature_index, star, trans, index, operation):
    global args
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
            suffix = operation_handlers[type_str](creature_index, star, trans, op_copy, type_str)
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

def dump_one_skill(creature_index, star, trans, name, index=None, book_mods=None):
    global skills_by_index
    skill = skills_by_index[index]

    def skill_absolute_time(skill):
        acting_time = int(skill.get('ActingTimeMs', 0))
        duration_time = sum(map(int, skill.get('DurationTimeMs', [0])))
        return acting_time + duration_time

    print_line('Skill: {0} [Duration = {1}]'.format(name, skill_absolute_time(skill)))

    indent(4)

    damaging_oper_types = ['GetPhysicalDamageR', 'GetMagicalDamageR', 'GetPhysicalDotR', 'GetMagicalDotR', 'GetStateDamageR']

    def is_aoe(tick):
        return 'RadiusMm' in tick

    def damaging_tick_label(tick):
        type = tick['Type']
        assert(type in damaging_oper_types)
        damage_type = 'P.DMG' if 'Physical' in type else 'M.DMG'
        styles = []
        if is_aoe(tick):
            s = 'AOE'
            if 'ExcludeTarget' in tick.get('Flags', []):
                s = s + '-'
            styles.append(s)
        if 'Dot' in type:
            styles.append('DoT')
        style_str = '({0})'.format(','.join(styles)) if len(styles) > 0 else ''
        return damage_type + style_str

    def tick_scaling_formula(tick):
        values = tick['Value']
        if not 'ValueFactor' in tick:
            value = values[0]
            try:
                value = float(value) / 1000.0
            except:
                pass
            return 'ATK*{0}'.format(value)

        factors = tick['ValueFactor']
        power = get_operation_value(creature_index, star, trans, values, factors, 0, 0)
        level_factor = get_operation_value(creature_index, star, trans, values, factors, 1, 0)

        return 'ATK*{0}+{1}'.format(power, level_factor)

    def format_one_damaging_tick(tick):
        label = damaging_tick_label(tick)
        scaling = tick_scaling_formula(tick)
        return '{0}[{1}]'.format(label, scaling)

    def format_tick_one_line(tick_operations):
        do = list(filter(lambda x : x.get('Type', None) in damaging_oper_types, tick_operations))
        if len(do) == 0:
            return '[Non-damaging tick]'
        formatted_ticks = [format_one_damaging_tick(x) for x in do]
        return ' + '.join(formatted_ticks)

    def dump_skill_attacks(atk_index, skill_obj):
        indent(2)
        id = skill_obj['Index']
        print_line('Hit {0} (id {1}): '.format(atk_index, id), add_newline=False)

        ilvl = 13 + len(str(id))
        indent(ilvl)
        operations = generate_skill_operations(skill_obj)
        ticks = generate_ticks(skill_obj, operations)
        is_continuation = True
        for t in enumerate(ticks):
            index, time, ops = t[0], t[1][0], t[1][1]
            print_line('[{0}] (t={1}): {2}'.format(index, time, format_tick_one_line(ops)), is_continuation=is_continuation)
            is_continuation = False
        indent(-ilvl)
        indent(-2)
        return

    atk_index = 1
    dump_skill_attacks(atk_index, skill)

    while 'NextIndex' in skill:
        atk_index = atk_index + 1
        skill = skills_by_index[skill['NextIndex']]
        dump_skill_attacks(atk_index, skill)

    indent(-4)

def dump_heroes():
    global creature_by_index
    global args
    for hero in filter(is_playable_hero, creature_by_index.values()):
        print_line(hero['CodeName']);
        indent(2)
        if args.auto_attacks:
            dump_one_skill(hero['Index'], 5, 5, 'Auto Attack', index=hero['BaseSkillIndex']);
        if args.skills:
            for i in range(4):
                index_str = 'SkillIndex{0}'.format(i+1)
                book_str = 'SkillExtend{0}'.format(i+1)
                dump_one_skill(hero['Index'], 5, 5, "S{0}".format(i+1), index=hero[index_str], book_mods=hero[book_str])
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
except SystemExit as e:
    if e.code != 0:
        print('An unknown error occurred.  Please report this bug.')
        traceback.print_exc()
except:
    print('An unknown error occurred.  Please report this bug.')
    traceback.print_exc()