"""Runnable custom rule packs and clearly marked upstream task references."""
from engine import Graph, CHANNELS

def test(name,args=None):
    v={'condition':'samcnpc:'+name}
    if args is not None:v['args']=args
    return {'test':v}
def action(name,args=None):
    v={'action':'samcnpc:'+name}
    if args is not None:v['args']=args
    return v

def pack(id,description,priority,channels,rules):
    return dict(schemaVersion=1,id=id,description=description,priority=priority,channels=channels,rules=rules)

def follow():
    return pack('example:follow','Podążaj za przywołującym. Dystans zatrzymania 2, wznowienia 4 bloki.',100,['movement','look'],[
        dict(id='follow_summoner',priority=100,when={'all':[test('has_summoner'),test('summoner_online')]},
             actions=[action('move_to_summoner',dict(speed=1.0,stopDistance=2.0))])])

def cautious():
    return pack('example:cautious_follow','Nie podążaj przy zdrowiu poniżej 30%. To nie jest leczenie ani ucieczka.',100,['movement','look'],[
        dict(id='stop_when_hurt',priority=500,when=test('health_fraction',dict(operator='lt',value=0.3)),actions=[action('stop_movement')]),
        dict(id='follow_when_healthy',priority=100,when={'all':[test('summoner_online'),test('health_fraction',dict(operator='gte',value=0.3))]},actions=[action('move_to_summoner',dict(speed=1.0,stopDistance=2.0))])])

def retaliate():
    return pack('example:retaliate','Reakcja melee na nowego napastnika. Bez atakowania graczy. Oparta na wbudowanej paczce.',500,['movement','look','combat','main_hand'],[
        dict(id='acquire_attacker',priority=1000,when={'all':[test('has_unhandled_damage'),{'not':test('has_attack_target')}]},actions=[action('set_attack_target_from_recent_attacker',dict(leash=24.0,durationTicks=600,allowPlayers=False))]),
        dict(id='approach_and_attack',priority=500,when={'all':[test('has_attack_target'),test('target_alive')]},actions=[action('move_to_target',dict(speed=1.1,stopDistance=2.4)),action('attack_target')])])

def demo_reference():
    return pack('samcnpc:demo_lumberjack','REFERENCJA: krok istniejącego demo joba. Samo przypisanie tej paczki NIE uruchamia drwala.',100000,
                ['movement','look','main_hand','block_action','inventory','interaction'],[
        dict(id='advance_demo_job',priority=100000,when=test('always'),actions=[action('run_lumberjack_demo')])])

def task_reference():
    rows=[('new_damage',1000,'task_reaction_ready','begin_task_reaction'),
          ('advance_combat',900,'task_combat_ready','run_combat_task'),
          ('begin_inventory',800,'task_inventory_requested','begin_task_inventory'),
          ('advance_inventory',700,'task_inventory_ready','run_inventory_task')]
    rules=[dict(id=id,priority=p,when=test(c),actions=[action(a)]) for id,p,c,a in rows]
    rules.append(dict(id='advance_lumberjack',priority=100,when={'all':[test('task_ready'),{'not':test('task_combat_ready')}]},actions=[action('run_lumberjack_task')]))
    return pack('samcnpc:task_lumberjack','REFERENCJA: arbiter istniejącego zadania drwala, walki i logistyki. Nie tworzy taska.',100,CHANNELS[:],rules)

def tool_preparation():
    return pack('example:tool_preparation','Equip a carried usable axe. Chest acquisition uses durable ENSURE or authorized task preparation.',200,
                ['inventory','main_hand','off_hand'],[
        dict(id='equip_usable_axe',priority=100,when={'all':[
            test('inventory_count',dict(query='@axe',operator='gte',count=1,minimumDurability=0.2)),
            {'not':test('equipment_matches',dict(query='@axe',destination='MAIN_HAND',minimumDurability=0.2))}]},
            actions=[action('ensure_equipment',dict(query='@axe',destination='MAIN_HAND',minimumDurability=0.2))])])

EXAMPLES={
 'Podążanie — pierwszy działający przykład':follow,
 'Tool preparation':tool_preparation,
 'Ostrożne podążanie — warunek zdrowia':cautious,
 'Odwet melee — kilka reguł':retaliate,
 'Drwal: demo — referencja wbudowana':demo_reference,
 'Drwal: task i przerwania — referencja':task_reference,
}

def load_example(name): return Graph.from_pack(EXAMPLES[name]())
