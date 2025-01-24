import cw_parser as cw
from cw_parser import Mod, mod_doc_path
from cw_parser import registered_mods as mods

cw.configure('mod_docs_path',"C:\\Users\\kuyan\\OneDrive\\Documents\\Paradox Interactive\\Stellaris\\mod")
cw.configure('workshop_path',"C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\281990")
cw.set_vanilla_path("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Stellaris")

Mod(
	is_base = True,
	mod_path = mod_doc_path("scripted_trigger_undercoat"),
    workshop_item='2868680633',
)
Mod(
	is_base = True,
	mod_path = mod_doc_path("repeating_script_templates"),
)

Mod(
	key = 'plandiv',
	workshop_item='819148835',
	compat_var = "has_planetary_diversity",
)
Mod(
	key = 'plandiv_unique',
	workshop_item='1740165239',
	compat_var = "has_planetary_diversity",
	parents=[
		mods['plandiv']
	],
)

Mod(
	key = 'ancientcaches',
	workshop_item='1419304439',
	compat_var = "has_ancient_caches",
)

Mod(
	key = 'dtraits',
	mod_path = mod_doc_path('dtraits_for_3'),
	compat_var ='has_diagraphers_trait_mod',
)
Mod(
	key = 'intel_expanded',
	mod_path = mod_doc_path('empire_inspector_3'),
	compat_var = 'has_intel_expanded',
)
Mod(
	key = 'ethical_gestalts',
	mod_path = mod_doc_path('ethical_gestalts_4'),
	compat_var = 'has_ethical_gestalts',
)
Mod(
	key = 'more_corporate_auths',
	mod_path = mod_doc_path('more_corporate_auths'),
	compat_var = 'has_more_corporate_authorities',
)
Mod(
	key = 'more_presapient_portraits',
	mod_path = mod_doc_path('presapient_portraits_base'),
	compat_var = 'has_premium_presapient_portraits',
)
Mod(
	key = 'ooc',
	mod_path = mod_doc_path('ooc_37'),
	compat_var = 'has_origins_of_civilization',
)
Mod(
	key = 'dfaction',
	mod_path = mod_doc_path('pop_ethics_more_demands'),
	compat_var = 'has_diagraphers_faction_and_ethic_mod',
)
Mod(
	key = 'rapid_evolution',
	mod_path = mod_doc_path('rapid_evolution_2'),
	compat_var = 'has_rapid_evolution',
)
Mod(
	key = 'real_space_nebulae',
	mod_path = mod_doc_path('real_space_nebulae'),
	compat_var = 'has_real_space_nebulae',
)

Mod(
	key = 'gigas',
	workshop_item = '1121692237',
	compat_var = "has_gigastructures",
)

Mod(
	key = 'evolved',
	workshop_item = '2602025201',
	parents = [
		mods['plandiv_unique'],
		mods['plandiv'],
	],
	compat_var = "has_stellaris_evolved",
)

Mod(
	key = 'bugbranch',
	workshop_item = '2517213262',
	compat_var = "has_bug_branch",
)

Mod(
	key = 'more_events',
	workshop_item = '727000451',
	compat_var = "has_more_events_mod",
)
Mod(
	key = 'dynamic_political_events',
	workshop_item = '1227620643',
	compat_var = "has_dynamic_political_events",
)
Mod(
	key = 'wild_space',
	workshop_item = '2860980668',
	compat_var = "has_wild_space_mod",
)
Mod(
	key = 'aggressive_crisis_engine',
	workshop_item = '2268189539',
	compat_var = "has_aggressive_crisis_engine",
)
Mod(
	key = 'starnet',
	workshop_item = '1712760331',
	compat_var = "has_starnet_or_startech",
)
Mod(
	key = 'starnet_friendship',
	workshop_item = '1724817916',
	compat_var = "str_is_friendship_patch_loaded",
	parents=[
		mods['starnet'],
	],
)
Mod(
	key = 'starnet_mixed_fleet',
	workshop_item = '2473773085',
	compat_var = "str_is_mixed_fleet_loaded",
	parents=[
		mods['starnet'],
	],
)