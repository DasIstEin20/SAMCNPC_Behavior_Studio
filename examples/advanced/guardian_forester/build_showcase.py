"""Rebuild the data-only Guardian/Forester demonstration using the shipped Studio catalog."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
STUDIO = HERE.parents[2]
sys.path.insert(0, str(STUDIO))
from engine import Graph, ACTIONS, CHANNELS, dump, atomic_write, export_zip, require_export


def test(name, **args):
    value = {'condition': 'samcnpc:' + name}
    if args:
        value['args'] = args
    return {'test': value}


def all_of(*values): return {'all': list(values)}
def any_of(*values): return {'any': list(values)}
def neg(value): return {'not': value}
def act(name, **args): return {'action': 'samcnpc:' + name, **({'args': args} if args else {})}
def health(operator, value): return test('health_fraction', operator=operator, value=value)
def stock(query, count=1, minimum=0.0): return test('inventory_count', query=query, operator='gte', count=count, minimumDurability=minimum)
def equipped(query, destination='MAIN_HAND', minimum=0.0): return test('equipment_matches', query=query, destination=destination, minimumDurability=minimum)

active = any_of(*(test('task_status', status=s) for s in ('RUNNING', 'WAITING', 'PAUSED')))
idle = neg(active)
paused = test('task_status', status='PAUSED')
online = all_of(test('has_summoner'), test('summoner_online'))
target = test('has_attack_target')
# The entire 0..40% range abstains from ordinary melee. No oscillation at 25%.
endangered = any_of(health('lte', 0.25), all_of(health('lte', 0.40), any_of(target, test('was_hurt_recently', withinTicks=100))))
calm = all_of(idle, neg(target), neg(endangered))
ready_to_fight = all_of(idle, target, health('gt', 0.40))
source = dict(endpoint='SOURCE', index=0)
destination = dict(endpoint='DESTINATION', index=0)
inventory = all_of(neg(paused), test('task_inventory_ready'))
request = all_of(neg(paused), test('task_inventory_requested'))
rules = []
groups = {}

def rule(group, name, priority, when, *actions):
    rules.append(dict(id=name, priority=priority, when=when, actions=list(actions)))
    groups[name] = group

rule('01_SAFETY', 'a01_respect_manual_pause', 4000, paused, act('stop_movement'))
rule('01_SAFETY', 'a02_abort_risky_retaliation', 3900, all_of(idle, endangered, target), act('clear_attack_target'))
rule('01_SAFETY', 'a03_emergency_return_to_summoner', 3800, all_of(idle, endangered, online), act('move_to_summoner', speed=1.2, stopDistance=3.0, startDistance=4.0))
rule('01_SAFETY', 'a04_emergency_hold_without_summoner', 3790, all_of(idle, endangered, neg(online)), act('stop_movement'))
rule('01_SAFETY', 'a05_unarmed_disengage', 3700, all_of(ready_to_fight, neg(stock('@melee_weapon', minimum=0.10))), act('clear_attack_target'))

rule('02_DEFENSE', 'b01_accept_one_recent_attacker', 3400,
     all_of(idle, health('gt', 0.40), test('has_unhandled_damage'), test('was_hurt_recently', withinTicks=80), stock('@melee_weapon', minimum=0.10)),
     act('set_attack_target_from_recent_attacker', leash=12.0, durationTicks=240, allowPlayers=False))
rule('02_DEFENSE', 'b02_equip_carried_melee_weapon', 3300,
     all_of(ready_to_fight, stock('@melee_weapon', minimum=0.10), neg(equipped('@melee_weapon', minimum=0.10))),
     act('ensure_equipment', query='@melee_weapon', destination='MAIN_HAND', minimumDurability=0.10))
rule('02_DEFENSE', 'b03_equip_carried_shield', 3290,
     all_of(ready_to_fight, stock('@shield', minimum=0.20), neg(equipped('@shield', 'OFF_HAND', 0.20))),
     act('ensure_equipment', query='@shield', destination='OFF_HAND', minimumDurability=0.20))
rule('02_DEFENSE', 'b04_bounded_pursuit', 3200,
     all_of(ready_to_fight, stock('@melee_weapon', minimum=0.10)), act('move_to_target', speed=1.1, stopDistance=2.4))
rule('02_DEFENSE', 'b05_attack_with_suitable_weapon', 3190,
     all_of(ready_to_fight, equipped('@melee_weapon', minimum=0.10)), act('attack_target'))

rule('03_DURABLE_TASKS', 'c01_begin_authorized_task_reaction', 2800,
     all_of(neg(paused), test('task_reaction_ready')), act('begin_task_reaction'))
rule('03_DURABLE_TASKS', 'c02_advance_combat_or_patrol', 2700,
     all_of(neg(paused), test('task_combat_ready')), act('run_combat_task'))
rule('03_DURABLE_TASKS', 'c03_recover_inventory_space', 2600,
     all_of(request, test('inventory_free_slots', operator='lt', count=2)), act('begin_task_inventory'))
rule('03_DURABLE_TASKS', 'c04_prepare_missing_usable_axe', 2590,
     all_of(request, neg(stock('@axe', minimum=0.25))), act('begin_task_inventory'))
rule('03_DURABLE_TASKS', 'c05_begin_other_authorized_logistics', 2580,
     request, act('begin_task_inventory'))
rule('03_DURABLE_TASKS', 'c06_collect_observed_exact_coal', 2520,
     all_of(inventory, test('container_observed', **source), test('container_count', **source, query='minecraft:coal', operator='gt', count=0),
            neg(stock('minecraft:coal', count=2))), act('run_inventory_task'))
rule('03_DURABLE_TASKS', 'c07_collect_observed_tool', 2510,
     all_of(inventory, test('container_observed', **source), test('container_count', **source, query='@axe', operator='gt', count=0),
            neg(stock('@axe', minimum=0.25))), act('run_inventory_task'))
rule('03_DURABLE_TASKS', 'c08_approach_unobserved_container', 2500,
     all_of(inventory, neg(test('container_observed', **source)), neg(test('container_observed', **destination))), act('run_inventory_task'))
rule('03_DURABLE_TASKS', 'c09_unload_to_observed_destination', 2490,
     all_of(inventory, test('container_observed', **destination), test('container_free_slots', **destination, operator='gt', count=0),
            test('inventory_free_slots', operator='lt', count=2)), act('run_inventory_task'))
# A full chest can still accept a compatible partial stack. Unknown stock is not empty.
# The bounded task observes/executes/fails; the rule must not suppress its recovery.
rule('03_DURABLE_TASKS', 'c10_continue_inventory_reobserve_and_verify', 2480, inventory, act('run_inventory_task'))

for offset, (slot, suffix) in enumerate((('HEAD', 'helmet'), ('CHEST', 'chestplate'), ('LEGS', 'leggings'), ('FEET', 'boots'))):
    query = '|'.join('minecraft:' + material + '_' + suffix for material in ('leather', 'chainmail', 'iron', 'golden', 'diamond', 'netherite'))
    rule('04_EQUIPMENT', f'd0{offset+1}_prepare_{slot.lower()}', 1800-offset*10,
         all_of(calm, stock(query, minimum=0.20), neg(equipped(query, slot, 0.20))),
         act('ensure_equipment', query=query, destination=slot, minimumDurability=0.20))
rule('04_EQUIPMENT', 'd05_prepare_shield', 1750,
     all_of(calm, stock('@shield', minimum=0.20), neg(equipped('@shield', 'OFF_HAND', 0.20))),
     act('ensure_equipment', query='@shield', destination='OFF_HAND', minimumDurability=0.20))
rule('04_EQUIPMENT', 'd06_replace_worn_carried_axe', 1740,
     all_of(calm, equipped('@axe'), test('durability_fraction', destination='MAIN_HAND', operator='lt', value=0.25), stock('@axe', minimum=0.25)),
     act('ensure_equipment', query='@axe', destination='MAIN_HAND', minimumDurability=0.25))
rule('04_EQUIPMENT', 'd07_prepare_carried_work_tool', 1730,
     all_of(calm, stock('@axe', minimum=0.25), neg(equipped('@axe', minimum=0.25))),
     act('ensure_equipment', query='@axe', destination='MAIN_HAND', minimumDurability=0.25))

rule('05_RESULTS', 'e01_return_for_help_after_logistics_failure', 1400,
     all_of(calm, online, test('task_status', status='FAILED'), any_of(*(test('last_task_failure', reason=r) for r in
            ('MISSING_RESOURCE', 'INVENTORY_FULL', 'STORAGE_FULL', 'SOURCE_UNAVAILABLE', 'RECOVERY_EXHAUSTED')))),
     act('move_to_summoner', speed=0.85, stopDistance=3.0, startDistance=5.0))
rule('05_RESULTS', 'e02_return_after_completed_task', 1390,
     all_of(calm, online, test('task_status', status='COMPLETED')), act('move_to_summoner', speed=0.9, stopDistance=3.0, startDistance=5.0))
rule('05_RESULTS', 'e03_wait_through_bounded_retry_backoff', 1380,
     all_of(test('task_status', status='WAITING'), test('task_attempts_remaining', operator='gt', count=0),
            neg(test('task_ready')), neg(test('task_combat_ready')), neg(test('task_inventory_ready')), neg(test('task_inventory_requested')), neg(test('task_reaction_ready'))),
     act('stop_movement'))

rule('06_ESCORT', 'f01_catch_up_to_summoner', 500,
     all_of(calm, online, test('distance_to_summoner', operator='gt', blocks=12.0)),
     act('move_to_summoner', speed=1.15, stopDistance=3.0, startDistance=5.0))
rule('06_ESCORT', 'f02_follow_with_hysteresis', 490,
     all_of(calm, online), act('move_to_summoner', speed=0.9, stopDistance=3.0, startDistance=5.0))
rule('06_ESCORT', 'f03_wait_when_summoner_unavailable', 480,
     all_of(calm, neg(online)), act('stop_movement'))

pack = dict(schemaVersion=1, id='showcase:guardian_forester',
            description='Guardian / Forester: deterministic escort, bounded retaliation, retreat, carried equipment and authorized durable logistics. Keep the original controller pack for a running task. No LLM, commands or scripts in this pack.',
            priority=750, channels=CHANNELS[:], rules=rules)
graph = Graph.from_pack(pack)
# Deterministic node IDs make the saved example reviewable and reproducible.
ids = {old: f'n{i:04d}' for i, old in enumerate(graph.nodes, 1)}
graph.nodes = {ids[old]: node for old, node in graph.nodes.items()}
for node_id, node in graph.nodes.items(): node.id = node_id
graph.edges = [(ids[a], ids[b]) for a,b in graph.edges]
# Six distinct areas, readable by panning/zooming. Wires never cross sections.
# 01..03 occupy the top row, 04..06 the bottom row.
sections = {}
for node in list(graph.nodes.values()):
    if node.kind != 'rule': continue
    section = groups[node.rule_id]
    members = set()
    def walk(nid):
        if nid in members: return
        members.add(nid)
        for parent in graph.incoming(nid): walk(parent)
    walk(node.id)
    members.update(graph.outgoing(node.id))
    sections.setdefault(section, []).append(members)
max_width = max(n.x for n in graph.nodes.values()) + 520
row_heights = []
section_nodes = {}
for section, branches in sections.items():
    top = 80.0
    selected = set()
    for members in branches:
        branch_min = min(graph.nodes[n].y for n in members)
        branch_max = max(graph.nodes[n].y for n in members)
        for nid in members:
            graph.nodes[nid].y += top - branch_min
        top += branch_max - branch_min + 220
        selected.update(members)
    row_heights.append(top)
    section_nodes[section] = sorted(selected)
row_height = max(row_heights[:3]) + 400
for index, section in enumerate(sections):
    dx=(index%3)*max_width
    dy=(index//3)*row_height
    for nid in section_nodes[section]:
        graph.nodes[nid].x += dx
        graph.nodes[nid].y += dy
checked, report = require_export(graph)
assert checked == pack
assert Graph.from_project(graph.to_project()).to_pack() == pack
atomic_write(HERE/'guardian_forester.samgraph', dump(graph.to_project()))
atomic_write(HERE/'guardian_forester.json', dump(pack))
export_zip(HERE/'guardian_forester.zip', graph, overwrite=True)
manifest = dict(pack=pack['id'], rules=len(rules), nodes=len(graph.nodes), edges=len(graph.edges),
                sections=section_nodes, warnings=report.warnings,
                jsonBytes=len(dump(pack).encode('utf-8')),
                schema=graph.to_project()['targetCommit'])
atomic_write(HERE/'graph_manifest.json', dump(manifest))
print(json.dumps({k:v for k,v in manifest.items() if k!='sections'}, ensure_ascii=False, indent=2))
