from cw_parser import scopesContext, in_common, globalData, Mod, match, CWElement, onActionScopes
from cw_parser import configure as config
from typing import Generator

dlc_list = [
	'Arachnoid Portrait Pack',
	'Plantoids Species Pack',
	'Creatures of the Void Portrait Pack',
	'Leviathans Story Pack',
	'Horizon Signal',
	'Utopia',
	'Anniversary Portraits',
	'Synthetic Dawn Story Pack',
	'Apocalypse',
	'Humanoids Species Pack',
	'Distant Stars Story Pack',
	'Ancient Relics Story Pack',
	'Lithoids Species Pack',
	'Federations',
	'Necroids Species Pack',
	'Nemesis',
	'Aquatics Species Pack',
	'Overlord',
	'Toxoids Species Pack',
	'Symbols of Domination',
	'Paradox Account Sign-up Bonus',
	'Original Game Soundrack',
]

scope_types = {
	'none':'global',
	'pop_faction':'pop_faction',
	'first_contact':'first_contact',
	'situation':'situation',
	'agreement':'agreement',
	'federation':'federation',
	'archaeological_site':'archaeology',
	'spy_network':'spynetwork',
	'espionage_asset':'espionage_asset',
	'megastructure':'megastructure',
	'planet':'planet',
	'country':'country',
	'ship':'ship',
	'pop':'pop',
	'fleet':'fleet',
	'galactic_object':'star',
	'leader':'leader',
	'army':'army',
	'ambient_object':'ambient_object',
	'species':'species',
	'design':'design',
	'war':'war',
	'alliance':'alliance',
	'starbase':'starbase',
	'deposit':'deposit',
	'observer':'observer',
	'sector':'sector',
	'astral_rift':'astral_rift',
	'espionage_operation':'espionage_operation',
	'design':'design',
	'cosmic_storm':'storm',
}

flag_effects = {}
timed_flag_effects = {}
flag_triggers = {}

for scope in scope_types:
	scope_alt = scope_types[scope]
	flag_effects[f'set_{scope_alt}_flag']=scope
	timed_flag_effects[f'set_{scope_alt}_flag']=scope
	flag_triggers[f'set_{scope_alt}_flag']=scope

effectLocations = {
	in_common('button_effects'):{
		'*':{
			'effect':scopesContext('[EFFECT_BUTTON_SCOPE]','country')
		},
	},
	in_common('agreement_term_values'):{
		'*':{
			'activate_effect':scopesContext('agreement'),
			'deactivate_effect':scopesContext('agreement'),
		},
	},
	in_common('anomalies'):{
		'*':{
			'on_spawn':scopesContext('planet','ship'),
		},
	},
	in_common('archaeological_site_types'):{
		'*':{
			'on_create':scopesContext('archaeological_site'),
			'on_visible':scopesContext('country','archaeological_site'),
			'on_roll_failed':scopesContext('fleet','archaeological_site'),
		},
	},
	in_common('armies'):{
		'*':{
			'on_queued':scopesContext('planet'),
			'on_unqueued':scopesContext('planet'),
		},
	},
	in_common('artifact_actions'):{
		'*':{
			'effect':scopesContext('country'),
		},
	},
	in_common('ascension_perks'):{
		'*':{
			'on_enabled':scopesContext('country'),
			'tradition_swap':{
				'on_enabled':scopesContext('country'),
			}
		},
	},
	in_common('astral_actions'):{
		'*':{
			'effect':scopesContext('country'),
		},
	},
	in_common('astral_rifts'):{
		'*':{
			'on_create':scopesContext('astral_rift'),
			'on_roll_failed':scopesContext('astral_rift'),
		},
	},
	in_common('buildings'):{
		'*':{
			'on_queued':scopesContext('planet'),
			'on_unqueued':scopesContext('planet'),
			'on_built':scopesContext('planet'),
			'on_destroy':scopesContext('planet'),
			'on_repaired':scopesContext('planet'),
		},
	},
	in_common('bypass'):{
		'*':{
			'on_pre_explore':scopesContext('bypass','fleet','megastructure',),
		},
	},
	in_common('council_agendas'):{
		'*':{
			'init_effect':scopesContext('country'),
			'effect':scopesContext('country'),
		},
	},
	in_common('country_types'):{
		'*':{
			'fleet_manager':{
				'on_contract_started':scopesContext('fleet','country','country','country'),
				'on_contract_expired':scopesContext('fleet','country','country','country'),
				'on_contract_cancelled':scopesContext('fleet','country','country','country'),
				'on_contract_broken':scopesContext('fleet','country','country','country'),
			}
		},
	},
	in_common('crisis_levels'):{
		'*':{
			'on_unlock':scopesContext('country'),
		},
	},
	in_common('decisions'):{
		'*':{
			'effect':scopesContext('planet'),
			'on_queued':scopesContext('planet'),
			'on_unqueued':scopesContext('planet'),
			'abort_effect':scopesContext('planet'),
		},
	},
	in_common('deposits'):{
		'*':{
			'on_cleared':scopesContext('planet'),
		},
	},
	in_common('diplomatic_actions'):{
		'*':{
			'on_accept':scopesContext('country','country'),
			'on_decline':scopesContext('country','country'),
		},
	},
	in_common('districts'):{
		'*':{
			'on_queued':scopesContext('planet'),
			'on_unqueued':scopesContext('planet'),
			'on_built':scopesContext('planet'),
		},
	},
	in_common('dust_clouds'):{
		'*':{
			'on_system_added':scopesContext('galactic_object','country'),
			'on_system_removed':scopesContext('galactic_object','country'),
		},
	},
	in_common('edicts'):{
		'*':{
			'effect':scopesContext('country'),
		},
	},
	in_common('espionage_operations'):{
		'*':{
			'on_create':scopesContext('espionage_operation'),
			'on_roll_failed':scopesContext('espionage_operation'),
		},
	},
	in_common('fallen_empires'):{
		'*':{
			'create_country_effect':scopesContext('country'),
		},
	},
	in_common('federation_laws'):{
		'*':{
			'on_enact':scopesContext('federation'),
		},
	},
	in_common('federation_perks'):{
		'*':{
			'on_activate':scopesContext('federation'),
			'on_deactivate':scopesContext('federation'),
		},
	},
	in_common('federation_types'):{
		'*':{
			'on_create':scopesContext('federation'),
		},
	},
	in_common('first_contact'):{
		'*':{
			'on_roll_failed':scopesContext('first_contact'),
		},
	},
	in_common('galactic_focuses'):{
		'*':{
			'effect':scopesContext('country'),
		},
	},
	in_common('megastructures'):{
		'*':{
			'on_build_start':scopesContext('galactic_object','country','megastructure',),
			'on_build_cancel':scopesContext('galactic_object','country','megastructure',),
			'on_build_complete':scopesContext('galactic_object','country','megastructure',),
			'on_dismantle_start':scopesContext('galactic_object','country','megastructure',),
			'on_dismantle_cancel':scopesContext('galactic_object','country','megastructure',),
			'on_dismantle_complete':scopesContext('galactic_object','country','megastructure',),
		},
	},
	in_common('menace_perks'):{
		'*':{
			'on_unlock':scopesContext('country'),
		},
	},
	in_common('missions'):{
		'*':{
			'on_success':scopesContext('country'),
			'on_stop':scopesContext('country'),
			'on_daily':scopesContext('country'),
			'on_monthly':scopesContext('country'),
		},
	},
	in_common('policies'):{
		'*':{
			'on_activate':scopesContext('country'),
			'option':{
				'on_enabled':scopesContext('country'),
				'on_disabled':scopesContext('country'),
			},
		},
	},
	in_common('pop_faction_types'):{
		'*':{
			'on_create':scopesContext('pop_faction'),
			'on_destroy':scopesContext('country'),
			'actions':{
				'*':{
					'effect':scopesContext('pop_faction'),
				},
			},
		},
	},
	in_common('relics'):{
		'*':{
			'active_effect':scopesContext('country'),
		},
	},
	in_common('resolution'):{
		'*':{
			'effect':scopesContext('country','country'),
			'fail_effects':scopesContext('country','country'),
		},
	},
	in_common('situations'):{
		'*':{
			'on_start':scopesContext('situation'),
			'on_fail':scopesContext('situation'),
			'on_abort':scopesContext('situation'),
			'on_progress_complete':scopesContext('situation'),
			'approach':{
				'on_select':scopesContext('situation'),
			},
			'stages':{
				'*':{
					'on_first_enter':scopesContext('situation'),
				},
			},
		},
	},
	in_common('specialist_subject_perks'):{
		'*':{
			'on_activate':scopesContext('agreement'),
			'on_deactivate':scopesContext('agreement'),
		},
	},
	in_common('specialist_subject_types'):{
		'*':{
			'on_progress_complete':scopesContext('agreement'),
		},
	},
	in_common('starbase_buildings'):{
		'*':{
			'on_finished':scopesContext('starbase','country'),
			'on_destroyed':scopesContext('starbase','country'),
		},
	},
	in_common('starbase_modules'):{
		'*':{
			'on_finished':scopesContext('starbase','country'),
			'on_destroyed':scopesContext('starbase','country'),
		},
	},
	in_common('storm_types'):{
		'*':{
			'on_start':scopesContext('cosmic_storm'),
			'on_finished':scopesContext('cosmic_storm'),
			'on_moved':scopesContext('cosmic_storm'),
		},
	},
	in_common('terraform'):{
		'*':{
			'effect':scopesContext('country','planet'),
		},
	},
	in_common('tradable_actions'):{
		'*':{
			'on_traded_effect':scopesContext('country','country'),
			'on_deal_ended_sender_effect':scopesContext('country','country'),
			'on_deal_ended_recipient_effect':scopesContext('country','country'),
		},
	},
	in_common('traditions'):{
		'*':{
			'on_enabled':scopesContext('country'),
			'tradition_swap':{
				'on_enabled':scopesContext('country'),
			}
		},
	},
	in_common('traits'):{
		'*':{
			'on_gained_effect':scopesContext('leader'),
		},
	},
	in_common('war_goals'):{
		'*':{
			'on_set':scopesContext('country','country'),
			'on_accept':scopesContext('country','country'),
			'on_status_quo':scopesContext('country','country'),
		},
	},
}

effectNesting = {
	'hidden_effect':None,
	'if':None,
	'else_if':None,
	'else':None,
	'random_list':{
		'*':None
	},
	'locked_random_list':{
		'*':None
	},
	'random':None,
	'while':None,
	'switch':{
		'*':None
	},
	'inverted_switch':{
		'*':None
	},
	'add_random_research_option':{
		'fail_effects':None
	},
	'start_storm_area_placing':{
		'on_confirm':None,
		'on_cancel':None,
	},
	'create_starbase':{
		'effect':'starbase'
	},
	'declare_war':{
		'effect':'war'
	},
	'create_species':{
		'effect':'species'
	},
	'create_country':{
		'effect':'country'
	},
	'create_rebels':{
		'effect':'country'
	},
	'create_army':{
		'effect':'army'
	},
	'create_leader':{
		'effect':'leader'
	},
	'clone_leader':{
		'effect':'leader'
	},
	'modify_species':{
		'effect':'species'
	},
	'spawn_natural_wormhole':{
		'init_effect':'bypass'
	},
	'effect_on_blob':{
		'effect':'galactic_object'
	},
	'activate_saved_leader':{
		'effect':'leader'
	},
	'create_ambient_object':{
		'effect':'ambient_object'
	},
	'create_army_transport':{
		'effect':'ship'
	},
	'create_fleet':{
		'effect':'fleet'
	},
	'create_military_fleet':{
		'effect':'fleet'
	},
	'create_mining_station':{
		'effect':'ship'
	},
	'create_pop':{
		'effect':'pop'
	},
	'create_research_station':{
		'effect':'ship'
	},
	'create_saved_leader':{
		'effect':'leader'
	},
	'create_ship':{
		'effect':'ship'
	},
	'spawn_megastructure':{
		'effect':'megastructure'
	},
	'spawn_planet':{
		'init_effect':'planet'
	},
	'spawn_system':{
		'effect':'galactic_object'
	},
	'create_half_species':{
		'effect':'species'
	},
	'create_espionage_asset':{
		'effect':'espionage_asset'
	},
	'create_nebula':{
		'effect':'galactic_object'
	},
	'start_situation':{
		'effect':'situation'
	},
	'spawn_astral_rift':{
		'effect':'astral_rift'
	},
	'storm_apply_aftermath_modifier':{
		'severity':{
			'effect':'planet'
		}
	},
}

listBuilders = {
	'agreement':'agreement',
	'ambient_object':'ambient_object',
	'system_ambient_object':'ambient_object',
	'archaeological_site':'archaeological_site',
	'owned_army':'army',
	'planet_army':'army',
	'ground_combat_defender':'army',
	'ground_combat_attacker':'army',
	'astral_rift':'astral_rift',
	'bypass':'bypass',
	'cosmic_storm':'cosmic_storm',
	'system_within_storm':'galactic_object',
	'cosmic_storm_start_position':'galactic_object',
	'cosmic_storm_end_position':'galactic_object',
	'system_added_to_storm':'galactic_object',
	'system_removed_from_storm':'galactic_object',
	'owned_storm_influence_field':'cosmic_storm_influence_field',
	'system_in_cosmic_storm_influence_field':'galactic_object',
	'country':'country',
	'relation':'country',
	'neighbor_country':'country',
	'country_neighbor_to_system':'country',
	'rival_country':'country',
	'federation_ally':'country',
	'playable_country':'country',
	'subject':'country',
	'available_debris':'debris',
	'pre_ftl_within_border':'country',
	'observed_pre_ftl_within_border':'country',
	'owned_design':'design',
	'spynetwork':'spy_network',
	'espionage_operation':'espionage_operation',
	'espionage_asset':'espionage_asset',
	'federation':'federation',
	'first_contact':'first_contact',
	'active_first_contact':'first_contact',
	'galaxy_fleet':'fleet',
	'combatant_fleet':'fleet',
	'fleet_in_system':'fleet',
	'owned_fleet':'fleet',
	'controlled_fleet':'fleet',
	'fleet_in_orbit':'fleet',
	'ordered_orbital_station':'fleet',
	'galcom_member':'country',
	'council_member':'country',
	'owned_leader':'leader',
	'pool_leader':'leader',
	'envoy':'leader',
	'megastructure':'megastructure',
	'owned_megastructure':'megastructure',
	'system_megastructure':'megastructure',
	'member':'country',
	'associate':'country',
	'system_planet':'planet',
	'system_colony':'planet',
	'planet_within_border':'planet',
	'owned_planet':'planet',
	'controlled_planet':'planet',
	'galaxy_planet':'planet',
	'deposit':'deposit',
	'moon':'planet',
	'owned_pop':'pop',
	'species_pop':'pop',
	'pop_faction':'pop_faction',
	'galaxy_sector':'sector',
	'owned_sector':'sector',
	'owned_ship':'ship',
	'controlled_ship':'ship',
	'ship_in_system':'ship',
	'situation':'situation',
	'targeting_situation':'situation',
	'owned_pop_species':'species',
	'galaxy_species':'species',
	'owned_species':'species',
	'enslaved_species':'species',
	'owned_starbase':'starbase',
	'owned_nonprimary_starbase':'starbase',
	'system':'galactic_object',
	'rim_system':'galactic_object',
	'system_within_border':'galactic_object',
	'neighbor_system':'galactic_object',
	'neighbor_system_euclidean':'galactic_object',
	'owned_ship':'ship',
	'war_participant':'country',
	'attacker':'country',
	'defender':'country',
	'war':'war',
}

for lb in listBuilders:
	value = listBuilders[lb]
	for prefix in ['random','ordered','every']:
		effectNesting[f'{prefix}_{lb}'] = value

scopeTransitions = {
	'background_planet':'target',
	'army_leader':'leader',
	'orbit':'planet',
	'planet':'planet',
	'star':'planet',
	'last_added_deposit':'deposit',
	'branch_office_owner':'country',
	'pop':'pop',
	'species':'species',
	'assembling_species':'species',
	'built_species':'species',
	'declining_species':'species',
	'fleet':'fleet',
	'design':'design',
	'capital_scope':'planet',
	'owner':'country',
	'controller':'country',
	'target_system':'galactic_object',
	'home_planet':'planet',
	'last_created_fleet':'fleet',
	'owner_main_species':'species',
	'last_created_country':'country',
	'last_created_species':'species',
	'alliance':'federation',
	'overlord':'country',
	'federation':'federation',
	'research_station':'fleet',
	'mining_station':'fleet',
	'last_created_pop':'pop',
	'last_created_system':'galactic_object',
	'planet_owner':'country',
	'last_created_ambient_object':'ambient_object',
	'last_created_ship':'ship',
	'orbital_station':'fleet',
	'last_created_leader':'leader',
	'owner_species':'species',
	'last_created_army':'army',
	'last_created_design':'design',
	'envoy_location_country':'country',
	'contact_country':'country',
	'sector_capital':'planet',
	'observation_outpost_owner':'country',
	'observation_outpost':'fleet',
	'federation_leader':'country',
	'associated_federation':'federation',
	'sector':'sector',
	'pop_faction':'pop_faction',
	'last_created_pop_faction':'pop_faction',
	'unhappiest_pop':'pop',
	'heir':'leader',
	'explorer':'country',
	'founder_species':'species',
	'last_refugee_country':'country',
	'starbase':'starbase',
	'capital_star':'planet',
	'system_star':'planet',
	'creator':'country',
	'no_scope':'none',
	'archaeological_site':'archaeological_site',
	'excavator_fleet':'fleet',
	'reverse_first_contact':'first_contact',
	'spynetwork':'spy_network',
	'growing_species':'species',
	'galactic_emperor':'country',
	'galactic_custodian':'country',
	'orbital_defence':'fleet',
	'attacker':'country',
	'defender':'country',
	'leader':'leader',
	'solar_system':'galactic_object',
	'space_owner':'country',
	'ruler':'leader',
	'astral_rift':'astral_rift',
	'lock_country':'country',
	'storm_influence_field':'cosmic_storm_influence_field',
	'last_created_cosmic_storm':'cosmic_storm',
	'last_created_cosmic_storm_influence_field':'cosmic_storm_influence_field',
}

eventTypes = {
	'event':'none',
	'espionage_operation_event':'espionage_operation',
	'cosmic_storm_event':'cosmic_storm',
	'cosmic_storm_influence_field_event':'cosmic_storm_influence_field',
	'country_event':'country',
	'planet_event':'planet',
	'ship_event':'ship',
	'pop_event':'pop',
	'fleet_event':'fleet',
	'pop_faction_event':'pop_faction',
	'observer_event':'country',
	'first_contact_event':'first_contact',
	'starbase_event':'starbase',
	'system_event':'galactic_object',
	'leader_event':'leader',
	'situation_event':'situation',
	'agreement_event':'agreement',
	'astral_rift_event':'astral_rift',
	'bypass_event':'bypass',
}

hardcodedOnActions = {
	'on_game_start':scopesContext('none'),
	'on_game_start_country':scopesContext('country'),
	'on_single_player_save_game_load':scopesContext('none'),
	'on_monthly_pulse':scopesContext('none'),
	'on_yearly_pulse':scopesContext('none'),
	'on_bi_yearly_pulse':scopesContext('none'),
	'on_five_year_pulse':scopesContext('none'),
	'on_decade_pulse':scopesContext('none'),
	'on_mid_game_pulse':scopesContext('none'),
	'on_late_game_pulse':scopesContext('none'),
	'on_monthly_pulse_country':scopesContext('country'),
	'on_yearly_pulse_country':scopesContext('country'),
	'on_bi_yearly_pulse_country':scopesContext('country'),
	'on_five_year_pulse_country':scopesContext('country'),
	'on_decade_pulse_country':scopesContext('country'),
	'on_mid_game_pulse_country':scopesContext('country'),
	'on_late_game_pulse_country':scopesContext('country'),
	'on_initialize_advanced_colony':scopesContext('planet','country'),
	'on_become_advanced_empire':scopesContext('country'),
	'on_press_begin':scopesContext('country'),
	'on_custom_diplomacy':scopesContext('country','country'),
	'on_first_contact':scopesContext('country','country','none','galactic_object'),
	'on_first_contact_finished':scopesContext('first_contact','country'),
	'on_enforce_borders':scopesContext('country','country','fleet','galactic_object'),
	'on_ground_combat_started':scopesContext('planet','country'),
	'on_planet_attackers_win':scopesContext('country','country','planet'),
	'on_planet_attackers_lose':scopesContext('country','country','planet'),
	'on_planet_defenders_win':scopesContext('country','country','planet'),
	'on_planet_defenders_lose':scopesContext('country','country','planet'),
	'on_system_first_visited':scopesContext('country','galactic_object'),
	'on_entering_system_first_time':scopesContext('ship','galactic_object','country'),
	'on_entering_system':scopesContext('ship','galactic_object','country'),
	'on_entering_system_fleet':scopesContext('fleet','galactic_object'),
	'on_crossing_border':scopesContext('planet','country'),
	'on_survey_planet':scopesContext('ship','planet'),
	'on_survey_astral_rift':scopesContext('ship','astral_rift'),
	'on_planet_surveyed':scopesContext('planet','country','fleet'),
	'on_astral_rift_surveyed':scopesContext('astral_rift','country','fleet'),
	'on_system_survey':scopesContext('country','galactic_object','fleet'),
	'on_system_survey_ship':scopesContext('ship','galactic_object'),
	'on_colonization_started':scopesContext('planet','ship'), # from here is used but not documented, could also be fleet
	'on_colonized':scopesContext('planet'),
	'on_colony_destroyed':scopesContext('planet'),
	'on_entering_battle':scopesContext('country','country','ship','ship'),
	'on_ship_destroyed_victim':scopesContext('country','country','ship','ship'),
	'on_ship_destroyed_perp':scopesContext('country','country','ship','ship'),
	'on_starbase_destroyed':scopesContext('starbase','fleet'),
	'on_starbase_disabled':scopesContext('starbase','fleet'),
	'on_ship_disengaged_victim':scopesContext('country','country','ship','ship'),
	'on_ship_disengaged_perp':scopesContext('country','country','ship','ship'),
	'on_fleet_destroyed_victim':scopesContext('country','country','fleet','fleet'),
	'on_fleet_destroyed_perp':scopesContext('country','country','fleet','fleet'),
	'on_space_battle_won':scopesContext('country','country','fleet','fleet'),
	'on_space_battle_lost':scopesContext('country','country','fleet','fleet'),
	'on_space_battle_over':scopesContext('country','country','fleet','fleet'),
	'on_fleet_disbanded':scopesContext('country','fleet'),
	'on_ship_disbanded':scopesContext('country','ship'),
	'on_army_disbanded':scopesContext('country','army'),
	'on_fleet_auto_move_arrival':scopesContext('country','fleet','planet'),
	'on_fleet_contract_started':scopesContext('fleet','country','country'),
	'on_fleet_contract_expired':scopesContext('fleet','country','country','country'),
	'on_fleet_contract_cancelled':scopesContext('fleet','country','country','country'),
	'on_fleet_contract_broken':scopesContext('fleet','country','country','country'),
	'on_destroying_station':scopesContext('ship',['planet','astral_rift']),
	'on_losing_station_control':scopesContext('ship',['planet','astral_rift']),
	'on_gaining_station_control':scopesContext('ship',['planet','astral_rift']),
	'on_entering_war':scopesContext('country','country'),
	'on_fleet_detected':scopesContext('country','fleet'),
	'on_ship_disabled':scopesContext('ship','ship'),
	'on_ship_enabled':scopesContext('ship'),
	'on_uplift_completion':scopesContext('planet','species'),
	'on_terraforming_begun':scopesContext('planet','country'),
	'on_terraforming_complete':scopesContext('planet','country'),
	'on_planet_class_changed':scopesContext('planet'),
	'on_planet_bombarded':scopesContext('planet','country'),
	'on_planet_zero_pops':scopesContext('planet','country'),
	'on_planet_zero_pops_ground_combat':scopesContext('planet','country'),
	'on_pop_abducted':scopesContext('pop','planet'),
	'on_pop_enslaved':scopesContext('pop'),
	'on_pop_emancipated':scopesContext('pop'),
	'on_pop_resettled':scopesContext('pop','planet'),
	'on_pre_communications_established':scopesContext('country','country'),
	'on_post_communications_established':scopesContext('country','country'),
	'on_post_communications_established_always_fire':scopesContext('country','country'),
	'on_presence_revealed':scopesContext('country','country'),
	'on_pop_bombed_to_death':scopesContext('planet','country','fleet'),
	'on_new_heir':scopesContext('leader'),
	'on_heir_promoted_to_ruler':scopesContext('leader'),
	'on_ruler_created':scopesContext('country','leader'),
	'on_leader_death_notify':scopesContext('country','leader'),
	'on_leader_death_no_notify':scopesContext('country','leader'),
	'on_leader_death':scopesContext('country','leader'),
	'on_leader_hired':scopesContext('leader'),
	'on_leader_fired':scopesContext('country','leader'),
	'on_leader_level_up':scopesContext('country','leader'),
	'on_leader_assigned':scopesContext('leader'),
	'on_leader_unassigned':scopesContext('leader'),
	'on_ruler_set':scopesContext('country'),
	'on_ruler_removed':scopesContext('country','leader'),
	'on_blocker_cleared':scopesContext('planet'),
	'on_ship_order':scopesContext('ship','country'),
	'on_policy_changed':scopesContext('country'),
	'on_ship_built':scopesContext('ship','planet'),
	'on_ship_designed':scopesContext('country'),
	'on_ship_upgraded':scopesContext('ship'),
	'on_war_beginning':scopesContext('country','war'),
	'on_war_ended':scopesContext('country','country'),
	'on_country_released_in_war':scopesContext('country','country','country','war'),
	'on_tech_increased':scopesContext('country'),
	'on_modification_complete':scopesContext('country','species'),
	'on_planet_occupied':scopesContext('planet','country','country'),
	'on_planet_returned':scopesContext('planet','country','country'),
	'on_emergency_ftl':scopesContext('fleet','galactic_object','galactic_object'),
	'on_army_recruited':scopesContext('planet','army'),
	'on_army_killed_in_combat':scopesContext('country','army','country','planet'),
	'on_army_killed_no_combat':scopesContext('country','army'),
	'on_building_complete':scopesContext('planet'),
	'on_building_queued':scopesContext('planet'),
	'on_building_unqueued':scopesContext('planet'),
	'on_building_upgraded':scopesContext('planet'),
	'on_building_demolished':scopesContext('planet'),
	'on_building_repaired':scopesContext('planet'),
	'on_district_complete':scopesContext('planet'),
	'on_building_replaced':scopesContext('planet'),
	'on_building_downgraded':scopesContext('planet'),
	'on_district_queued':scopesContext('planet'),
	'on_district_unqueued':scopesContext('planet'),
	'on_district_demolished':scopesContext('planet'),
	'on_auto_colony_type_changed':scopesContext('planet'),
	'on_tutorial_level_changed':scopesContext('country'),
	'on_war_won':scopesContext('country','country','war'),
	'on_war_lost':scopesContext('country','country','war'),
	'on_status_quo':scopesContext('country','country','country','country','war'),
	'on_status_quo_forced':scopesContext('country','country','country','country','war'),
	'on_pop_added':scopesContext('pop','planet'),
	'on_pop_rights_change':scopesContext('pop'),
	'on_pop_grown':scopesContext('planet','country','pop'),
	'on_pop_assembled':scopesContext('planet','country','pop'),
	'on_pop_purged':scopesContext('planet','country','pop'),
	'on_pop_declined':scopesContext('planet','country','pop'),
	'on_pop_displaced':scopesContext('planet','country','pop'),
	'on_rebels_take_planet':scopesContext('country','planet','war'),
	'on_rebels_take_planet_owner_switched':scopesContext('country','planet','war'),
	'on_planet_ownerless':scopesContext('country','country','planet'),
	'on_planet_transfer':scopesContext('planet','country','country'),
	'on_planet_conquer':scopesContext('planet','country','country'),
	'on_capital_changed':scopesContext('planet','planet'),
	'on_fleet_enter_orbit':scopesContext('fleet',['planet','starbase','megastructure']),
	'on_join_federation':scopesContext('country','country'),
	'on_leave_federation':scopesContext('country','country'),
	'on_federation_law_vote_succeed':scopesContext('country','country'),
	'on_federation_law_vote_failed':scopesContext('country','country'),
	'on_federation_leader_elections':scopesContext('country','country'),
	'on_federation_new_leader':scopesContext('country','country'),
	'on_federation_leader_challenge':scopesContext('country','country'),
	'on_country_destroyed':scopesContext('country','country'),
	'on_megastructure_built':scopesContext('country','megastructure','galactic_object','fleet'),
	'on_megastructure_upgrade_begin':scopesContext('country','megastructure','galactic_object'),
	'on_megastructure_upgraded':scopesContext('country','megastructure','galactic_object'),
	'on_colony_1_year_old':scopesContext('planet'),
	'on_colony_2_years_old':scopesContext('planet'),
	'on_colony_3_years_old':scopesContext('planet'),
	'on_colony_4_years_old':scopesContext('planet'),
	'on_colony_5_years_old':scopesContext('planet'),
	'on_colony_6_years_old':scopesContext('planet'),
	'on_colony_7_years_old':scopesContext('planet'),
	'on_colony_8_years_old':scopesContext('planet'),
	'on_colony_9_years_old':scopesContext('planet'),
	'on_colony_10_years_old':scopesContext('planet'),
	'on_colony_25_years_old':scopesContext('planet'),
	'on_colony_monthly_pulse':scopesContext('planet'),
	'on_colony_yearly_pulse':scopesContext('planet'),
	'on_colony_5_year_pulse':scopesContext('planet'),
	'on_colony_10_year_pulse':scopesContext('planet'),
	'on_leader_spawned':scopesContext('country','leader'),
	'on_added_to_leader_pool':scopesContext('country','leader'),
	'empire_init_add_technologies':scopesContext('country'),
	'empire_init_capital_planet':scopesContext('planet','species','species'),
	'empire_init_create_ships':scopesContext('country'),
	'on_election_started':scopesContext('country'),
	'on_election_ended':scopesContext('country'),
	'on_jump_drive':scopesContext('ship'),
	'on_ship_quantum_catapult':scopesContext('ship','galactic_object','galactic_object'),
	'on_fleet_quantum_catapult':scopesContext('fleet','galactic_object','galactic_object'),
	'on_pirate_spawn':scopesContext('country'),
	'on_starbase_transfer':scopesContext('ship','country'),
	'on_fleet_combat_joined_attacker':scopesContext('fleet','fleet','fleet'),
	'on_fleet_combat_joined_defender':scopesContext('fleet','fleet','fleet'),
	'on_system_lost':scopesContext('galactic_object','country','country'),
	'on_system_gained':scopesContext('galactic_object','country','country'),
	'on_slave_sold_on_market':scopesContext('pop','country','country'),
	'on_relic_received':scopesContext('country'),
	'on_relic_activated':scopesContext('country'),
	'on_relic_lost':scopesContext('country'),
	'on_arch_stage_finished':scopesContext('fleet','archaeological_site'),
	'on_arch_site_finished':scopesContext('fleet','archaeological_site'),
	'on_resolution_passed':scopesContext('country','country'),
	'on_resolution_failed':scopesContext('country','country'),
	'on_galactic_community_formed':scopesContext('country'),
	'on_galactic_council_established':scopesContext('country'),
	'on_add_community_member':scopesContext('country'),
	'on_remove_community_member':scopesContext('country'),
	'on_add_to_council':scopesContext('country'),
	'on_remove_from_council':scopesContext('country'),
	'on_join_alliance':scopesContext('country'),
	'on_leave_alliance':scopesContext('country'),
	'on_sign_commercial_pact':scopesContext('country','country'),
	'on_sign_defensive_pact':scopesContext('country','country'),
	'on_sign_migration_pact':scopesContext('country','country'),
	'on_sign_non_aggression_pact':scopesContext('country','country'),
	'on_sign_research_pact':scopesContext('country','country'),
	'on_becoming_subject':scopesContext('country','country'),
	'on_subject_integrated':scopesContext('country','country'),
	'on_released_as_vassal':scopesContext('country','country'),
	'on_ask_to_leave_federation_declined':scopesContext('country','country'),
	'on_spynetwork_formed':scopesContext('country','spy_network'),
	'on_add_to_imperial_council':scopesContext('country','country'),
	'on_remove_from_imperial_council':scopesContext('country','country'),
	'on_branch_office_established':scopesContext('planet','country'),
	'on_branch_office_closed':scopesContext('planet','country'),
	'on_system_occupied':scopesContext('galactic_object','country','country'),
	'on_system_controller_changed':scopesContext('galactic_object','country','country'),
	'on_system_returned':scopesContext('galactic_object','country','country'),
	'on_orbital_defense_planet_ownerless':scopesContext('starbase','planet','country'),
	'on_operation_chapter_finished':scopesContext('espionage_operation','[TARGET]'),
	'on_operation_finished':scopesContext('espionage_operation','[TARGET]'),
	'on_operation_cancelled':scopesContext('espionage_operation','[TARGET]'),
	'on_pre_government_changed':scopesContext('country'),
	'on_post_government_changed':scopesContext('country'),
	'on_custodian_term_ends':scopesContext('country'),
	'on_tradition_picked':scopesContext('country'),
	'on_ascension_perk_picked':scopesContext('country'),
	'on_megastructure_change_owner':scopesContext('country','megastructure','country'),
	'on_megastructure_ownerless':scopesContext('galactic_object','megastructure','country'),
	'on_establish_mercenary_enclave':scopesContext('fleet'),
	'on_debris_researched':scopesContext('country','debris','country','science_ship'),
	'on_debris_scavenged':scopesContext('country','debris','country','science_ship'),
	'on_debris_scavenged_and_researched':scopesContext('country','debris','country','science_ship'),
	'special_project_success':scopesContext('country','ship'),
	'anomaly_success':scopesContext('ship','planet'),
	'on_specialist_subject_conversion_started':scopesContext('agreement','country','country'),
	'on_specialist_subject_conversion_finished':scopesContext('agreement','country','country'),
	'on_specialist_subject_conversion_aborted':scopesContext('agreement','country','country'),
	'on_capitals_connected':scopesContext('country','country'),
	'on_agreement_change_accepted':scopesContext('agreement','country','country'),
	'on_astral_rift_spawned':scopesContext('astral_rift'),
	'on_astral_rift_exploration_start':scopesContext('country','astral_rift','fleet'),
	'on_astral_rift_pre_event_fire':scopesContext('country','astral_rift','fleet'),
	'on_astral_rift_exploration_complete':scopesContext('country','astral_rift','fleet'),
	'on_commercial_pact_broken':scopesContext('country','country'),
	'on_agenda_finished':scopesContext('country'),
	'on_cloaking_activated':scopesContext('fleet'),
	'on_cloaking_deactivated':scopesContext('fleet'),
	'on_awareness_level_increase':scopesContext('country','country'),
	'on_awareness_level_decrease':scopesContext('country','country'),
	'on_country_attacked':scopesContext('country','country'),
	'on_dimensional_lock_expired':scopesContext('bypass'),
	'on_space_storm_created':scopesContext('galactic_object'),
	'on_space_storm_destroyed':scopesContext('galactic_object'),
	'on_pop_ethic_changed':scopesContext('pop','country'),
	'on_galaxy_map_during_tutorial':scopesContext('country'),
	'on_truce_end':scopesContext('country','country'),
	'on_starbase_occupied':scopesContext('country','starbase'),
	'on_storm_entered_system':scopesContext('galactic_object','cosmic_storm'),
	'on_storm_left_system':scopesContext('galactic_object','cosmic_storm'),
	'on_storm_finished':scopesContext('cosmic_storm'),
	'on_storm_encountered':scopesContext('country','cosmic_storm'),
	'debug_spawn_storm_random_system':scopesContext('none'),
	'on_colony_destroyed_by_bombardment':scopesContext('planet','country'),
	'on_damage_taken':scopesContext('ship','ship'),
	'on_fleet_exit_battle':scopesContext('fleet'),
	'on_country_type_changed':scopesContext('country'),
	'on_debris_reanimated':scopesContext('country','debris','country','ship'),
	'on_snare_sent':scopesContext('fleet','fleet'),
	'on_specimen_acquired':scopesContext('country'),
	'on_specimen_sold':scopesContext('country'),
	'on_ship_engulfed':scopesContext('ship','ship'),
	'on_exhibit_unlocked':scopesContext('country'),
	'on_fauna_captured':scopesContext('ship','fleet'),
	'on_fauna_capture_ended':scopesContext('fleet'),
	'on_vivarium_populated':scopesContext('country'),
	'on_space_fauna_culled':scopesContext('country','design'),
	'on_leader_captured':scopesContext('leader','country','country','galactic_object'),
	'on_specimen_sold':scopesContext('country'),
	'on_specimen_sold':scopesContext('country'),
	'on_country_created':scopesContext('country','[COUNTRY_CREATION_ANTECEDENT]'),
}

def effectParseAdditionalSetup(mod:Mod):
	print(f'ad hoc preliminary setup for mod {str(mod)}')
	print(f'loading faction parameters')
	for faction in mod.read_folder( in_common('pop_faction_types') ).contents():
		for parameter in faction.getValue('parameters').contents():
			globalData['factionParameters'][parameter.name] = scopesContext( parameter.getValue('type',resolve=True) )

	eventScopes = globalData['eventScopes']

	print(f'setting up arc site events')
	arc_site_event_scopes = scopesContext( 'fleet', 'archaeological_site' )
	for arc_site in mod.read_folder( in_common('archaeological_site_types') ).contents():
		for stage in arc_site.getElements('stage'):
			eventScopes[stage.getValue('event',resolve=True)].add( arc_site_event_scopes )

	print(f'setting up espionage operation events')
	espionage_event_scopes = scopesContext( 'espionage_operation', 'country' )
	for operation in mod.read_folder( in_common('espionage_operation_types') ).contents():
		for stage in operation.getElements('stage'):
			eventScopes[stage.getValue('event',resolve=True)].add( espionage_event_scopes )

	# first contacts, astral rifts, and situations only provide root scope so far as I know, which can be derived from event type
	# print(f'setting up first contact events')
	# first_contact_event_scopes = scopesContext( 'first_contact' )
	# for first_contact_stage in mod.read_folder( in_common('first_contact') ).contents():
	# 	for stage_event in first_contact_stage.getElements('stage_event'):
	# 		eventScopes[stage_event.getValue('event',resolve=True)].add( first_contact_event_scopes )

	# print(f'setting up astral rift events')
	# rift_event_scopes = scopesContext( 'astral_rift' )
	# for rift in mod.read_folder( in_common('astral_rifts') ).contents():
	# 	eventScopes[rift.getValue('event',resolve=True)].add( rift_event_scopes )

	print(f'setting up anomaly events')
	anomaly_event_scopes = scopesContext( 'ship','planet' )
	for anomaly in mod.read_folder( in_common('anomalies') ).contents():
		on_success = anomaly.getElement('on_success')
		if not on_success.hasSubelements():
			eventScopes[on_success.resolve()].add(anomaly_event_scopes)
		else:
			for event in on_success.contents():
				if not event.hasSubelements():
					eventScopes[event.resolve()].add(anomaly_event_scopes)
				else:
					for element in event.contents():
						if match(element.name,'anomaly_event'):
							eventScopes[element.resolve()].add(anomaly_event_scopes)
						elif match(element.name,'ship_event'):
							eventScopes[element.resolve()].add(anomaly_event_scopes.firedContext())

	print(f'setting up bypass on_actions')
	bypass_event_scopes = scopesContext('fleet','galactic_object','galactic_object')
	for bypass in mod.read_folder( in_common('bypass') ).contents():
		if bypass.hasAttribute('on_action'):
			onActionScopes( bypass.getValue('on_action',resolve=True) ).add(bypass_event_scopes)

	print(f'setting up component action on_actions')
	component_action_event_scopes = scopesContext('planet','fleet')
	for component in mod.read_folder( in_common('component_templates') ).contents():
		if component.hasAttribute('scripted_action_name'):
			onActionScopes( component.getValue('scripted_action_name',resolve=True) ).add(component_action_event_scopes)
			if component.hasAttribute('scripted_action_on_cancel'):
				onActionScopes( component.getValue('scripted_action_on_cancel',resolve=True) ).add(component_action_event_scopes)
		if component.getValue('type',resolve=True) == 'planet_killer':
			onActionScopes( f'on_destroy_planet_with_{component.getValue('key',resolve=True)}' ).add(component_action_event_scopes)

	print(f'setting up station construction on_actions')
	construction_event_scopes = scopesContext('ship','planet')
	for shipsize in mod.read_folder( in_common('ship_sizes') ).contents():
		build_action_name = f'on_building_{shipsize.name}'
		onActionScopes(build_action_name).add(construction_event_scopes)

def process_initializer(initializer,scopes):
	for element in initializer.contents():
		if match(element.name,'init_effect'):
			yield (element,scopes)
		elif element.name.lower() in ['planet','moon']:
			yield from process_initializer(element,scopes.step('planet'))

def additionalEffectBlocks(mod:Mod) -> Generator[tuple[CWElement,scopesContext],None,None]:
	print(f'processing mod "{str(mod)}" special projects"')
	scopes1_root = scopesContext('country','planet')
	for project in mod.read_folder( in_common('special_projects') ).contents():
		event_scope = eventTypes[project.getValue('event_scope',resolve=True)]
		scopes1 = scopes1_root.step(event_scope)
		scopes2 = scopesContext('country',event_scope,'planet')
		for element in project.contents():
			if element.name.lower() in ['on_success','on_start','on_progress']:
				yield (element,scopes1)
			elif element.name.lower() in ['on_fail','on_cancel']:
				yield (element,scopes2)

	print(f'processing mod "{str(mod)}" solar system initializers')

	scopes_root = scopesContext('[SOLAR_SYSTEM_INITIALIZER_ANTECEDENT]','[SOLAR_SYSTEM_INITIALIZER_ANTECEDENT]','[SOLAR_SYSTEM_INITIALIZER_ANTECEDENT]','[SOLAR_SYSTEM_INITIALIZER_ANTECEDENT]','[SOLAR_SYSTEM_INITIALIZER_ANTECEDENT]')
	scopes_root.prev = scopes_root
	system_scopes = scopes_root.step('galactic_object')
	for initializer in mod.read_folder( in_common('solar_system_initializers') ).contents():
		yield from process_initializer(initializer,system_scopes)				

def configureCWP():
	config('effectLocations',effectLocations)
	config('effectNesting',effectNesting)
	config('scopeTransitions',scopeTransitions)
	config('eventTypes',eventTypes)
	config('hardcodedOnActions',hardcodedOnActions)
	config('effectParseAdditionalSetup',effectParseAdditionalSetup)
	config('additionalEffectBlocks',additionalEffectBlocks)