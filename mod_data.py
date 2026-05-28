import cw_parser_5 as cw
from cw_parser_5 import mod_doc_path
from cw_parser_5 import registered_mods as mods
import pandas as pd
import re
import os
from numbers import Number
import zipfile as zip
from pathlib import Path
from time import sleep
from collections.abc import Iterable


workshop_path = r"D:\SteamLibrary\steamapps\workshop\content\281990"
steamcmd_workshop_path = r"D:\steamcmd\steamapps\workshop\content\281990"
cw.set_mod_docs_path(r"D:\Documents\Paradox Interactive\Stellaris\mod")
cw.set_workshop_path(workshop_path)

class Mod(cw.Mod):
	def __init__(
			self, workshop_item:str|int|None = None, mod_path:str|Path|zip.Path|None = None, parents:Iterable['Mod'] = [], children:Iterable['Mod'] = [], is_base:bool = False, key:str|None = None, compat_var:str|None = None, version:str|int|float|None = None, postpone_setup:bool=False, postpone_registration:bool=False, layer:Number|None=None,
			detection_mode=0 # -1 for dependency, 1 for compat patch
		):
		super().__init__(workshop_item, mod_path, parents, children, is_base, key, compat_var, version, postpone_setup, postpone_registration, layer)
		self.detection_mode = detection_mode
		self.direct_parents = []
		self.has_compat_patches = []

	def compat_vars(self):
		if self.detection_mode == 0:
			return { self.compat_var }
		
		elif self.detection_mode == -1: # dependency
			results = set()
			for mod in self.immediate_children:
				results = results.union(mod.compat_vars())
			return results
				
		elif self.detection_mode == 1: # compat patch
			results = set()
			for mod in self.immediate_parents:
				results = results.union(mod.compat_vars())
			return results

	def detectable(self):
		if self.detection_mode == 0:
			return True
		elif self.detection_mode == 1:
			for parent in self.parents:
				if parent.detection_mode == 0:
					return True
		elif self.detection_mode == -1:
			for child in self.children:
				if child.detection_mode == 0:
					return True
		return False


	def loaded_indicator(self,val:bool=True):
		compat_vars = list( self.compat_vars() )

		if len(compat_vars) == 1:
			if val:
				return compat_vars[0]
			else:
				return f"(1 - {compat_vars[0]} )"
		
		elif self.detection_mode == -1: # dependency; OR logic
			not_loadeds = [ f"( 1 - {var} )" for var in compat_vars ]
			not_loaded = " * ".join(not_loadeds)
			if val:
				return f"( 1 - ( {not_loaded} ) )"
			else:
				return not_loaded
		
		elif self.detection_mode == 1: # compat patch; AND logic
			loaded = " * ".join(compat_vars)
			if val:
				return loaded
			else:
				return f"( 1 - ( {loaded} ) )"

cw.set_vanilla_mod_subclass(Mod)
cw.set_vanilla_path(r"D:\SteamLibrary\steamapps\common\Stellaris")

Mod(
	is_base = True,
	mod_path = mod_doc_path("scripted_trigger_undercoat"), # comment this out if you're not me
	workshop_item='2868680633',
)
Mod(
	is_base = True,
	mod_path = mod_doc_path("repeating_script_templates"),
)

my_mods = {
	'has_diagraphers_trait_mod':'dtraits_for_3',
	'has_intel_expanded':'empire_inspector_3',
	'has_ethical_gestalts':'ethical_gestalts_4',
	'has_more_corporate_authorities':'more_corporate_auths',
	'has_premium_presapient_portraits':'presapient_portraits_base',
	'has_origins_of_civilization':'ooc_37',
	'has_diagraphers_faction_and_ethic_mod':'pop_ethics_more_demands',
	'has_rapid_evolution':'rapid_evolution_2',
	'has_real_space_nebulae':'real_space_nebulae',
}

raw_data = pd.read_csv("Compatibility Scripted Variables - Sheet1.csv")

# class VersionReq():
# 	def __init__(self,folder,min_version):
# 		self.version = cw.Version(min_version)
# 		self.folder = folder
	
# 	def passes(self,mod:Mod):
# 		return mod.version >= self.version or not mod.uses_folder(self.folder)

# versions = [
# 	VersionReq( ['common','jobs'], '4.0' ),
# 	VersionReq( ['common','pop_categories'], '4.0' ),
# 	VersionReq( ['common','traits'], '4.0' ),
# 	VersionReq( ['common','jobs'], '4.0' ),
# 	VersionReq( ['common','jobs'], '4.0' ),
# 	VersionReq( ['common','jobs'], '4.0' ),
# ]

def adapt_mod_name(s):
	s = s.replace('.','')
	s = s.replace("'",'')
	s = s.replace("’",'')
	s = re.sub( r'[^a-zA-z0-9_]+', '_', s )
	s = s.lower()
	return s

raw_data.columns = raw_data.columns.str.replace(' ','')

for row in raw_data.itertuples():
	mod_name = row.ModName
	mod_name = adapt_mod_name(mod_name)
	compat_var = row.CompatibilityVariable
	if isinstance(compat_var,str):
		compat_var = compat_var[1:]
	else:
		compat_var = None
	if pd.isna(compat_var):
		detection_mode = row.DetectionMode
	else:
		detection_mode = 0
	if compat_var in my_mods:
		mod_path = mod_doc_path(my_mods[compat_var])
	else:
		mod_id = str(row.WorkshopID)
		wp = os.path.join(workshop_path,mod_id)
		if os.path.exists( wp ):
			mod_path = wp
		else:
			mod_path = os.path.join(steamcmd_workshop_path,mod_id)
	layer = row.Layer
	if pd.isna(layer):
		layer = None
	mod = Mod(
		key=mod_name,
		workshop_item=mod_id,
		mod_path=mod_path,
		compat_var=compat_var,
		postpone_registration=True,
		layer=layer,
		detection_mode=detection_mode,
	)
	if mod.version.is_compatible('4') or mod.key in {"new_legendary_worlds"}:
		mod.register()
		print(f"registered mod {mod.mod_name}, Stellaris {mod.version}")
	else:
		print(f"outdated mod {mod.mod_name}, Stellaris {mod.version}")

def add_parent(child:Mod,parent:Mod):
	child = adapt_mod_name(child)
	parent = adapt_mod_name(parent)
	if child in cw.registered_mods and parent in cw.registered_mods:
		child = cw.registered_mods[child]
		parent = cw.registered_mods[parent]
		if child.detection_mode == 1 and parent.detection_mode == -1:
			raise Exception(f"forbidden parentage: {child.key} and {parent.key}")
		child.add_parent(parent)
		if not parent in child.direct_parents:
			child.direct_parents.append(parent)

print("defining relationships")
def define_relationships(mod,children=[],parents=[],compat_patches=[]):
	for child in children:
		add_parent(child,mod)
	for parent in parents:
		add_parent(mod,parent)
	for patch in compat_patches:
		pm = adapt_mod_name(patch)
		if pm in cw.registered_mods:
			pm = cw.registered_mods(pm)
			for p in pm.direct_parents:
				p.has_compat_patches.append(mod)
				mod.has_compat_patches.append(p)
		add_parent(patch,mod)

define_relationships(
	"Ancient Caches of Technologies",
	children = [
		"ACOT - Secrets Beyond The Gates",
		"Acquisition of Technologies",
		"ANZ Voidframe",
		"Secrets of the Shroud",
	],
	compat_patches = [
		"ACOT + ExpEvents Patch",
	],
)
define_relationships(
	"Gigastructural Engineering & More",
	children = [
		"ANZ Voidframe",
		"Frameworld Extra Goodies",
		"Playable Katzenartig Imperium",
	],
	# inbuilt_compat = [
	# 	"has_bug_branch",
	# 	"oxr_mdlc_mod",
	# ],
)
define_relationships(
	"Extra Ship Components NEXT",
	children = [
		"ESC NEXT: Overwrites: Component Progression",
		"ESC NEXT: Overwrites: Global Ship Designs",
	],
)
define_relationships(
	"Kurogane Expanded 2.0 Shipset",
	children = [
		"Kurosections Expanded",
	],
)
define_relationships(
	"Planetary Diversity",
	children = [
		"Planetary Diversity Unique Worlds",
		"Planetary Diversity - Exotic Worlds",
	],
	compat_patches = [
		"StarNet - PD compatibility",
	],
)
define_relationships(
	"Sartek Tradition - Ascension Perk Merger",
	children = [
		"Sartek District and Economy Merger Add-on",
		"Sartek TAP Merger - Ascension Path Fusion",
		"Sartek TAP Merger - Vanilla Preset",
	],
)
define_relationships(
	"All Ascension Paths",
	children = [
		"Sartek TAP Merger - Ascension Path Fusion",
	],
)
define_relationships(
	"Stellaris Evolved",
	children = [
		"Serente's Evolved Addon",
		"Planetary Diversity Unique Worlds", # not actually but things mostly work better this way
	],
	compat_patches = [
		"Evolved + MoR Patch",
	],
	# inbuilt_compat = [
	# 	"has_planetary_diversity_unique_worlds",
	# 	"has_ancient_caches",
	# 	"has_acquisition_of_tech",
	# 	"has_gigastructures",
	# 	"tec_giga_patch_addon_present",
	# 	"tec_pd_patch_addon_present",
	# 	"tec_serente_addon_present",
	# 	"tec_kes_addon_present",
	# 	"tec_modded_other_addon_present",
	# 	"tec_tec_experimental_addon_present",
	# 	"has_planetary_diversity_more_arcologies",
	# 	"has_planetary_diversity_ascension_worlds",
	# 	"has_planetary_diversity",
	# ],
)
define_relationships(
	"The Zenith of Fallen Empires",
	children = [
		"The Zenith of Fallen Empires Sandbox",
	],
)
define_relationships(
	"V_TRAITS",
	children = [
		"V_TRAITS No Ethic Restriction Patch",
		"V_TRAITS No Species Class Restriction Patch",
		"V_TRAITS Performance Patch",
	],
)
define_relationships(
	"Vengeance Shipset",
	children = [
		"Vengeance Sections Expanded",
	],
)
define_relationships(
	"Ariphaos's Unofficial Patch",
	children = [
		"Wild space 3 patched",
		"War of Wreaths",
	],
)
define_relationships(
	"StarNet AI",
	children = [
		"StarNet Friendship Patch",
		"StarNet Mixed Fleet",
		"StarNet for NSC2",
	],
	compat_patches = [
		"StarNet - PD compatibility",
	],
)
define_relationships(
	"A Deadly Tempest ",
	parents = [
		"Gray Tempest Shipset",
	],
)
define_relationships(
	"Shroud Rising",
	children = [
		"Daemonic Incursion",
	],
)
define_relationships(
	"Expanded Events",
	compat_patches = [
		"ACOT + ExpEvents Patch",
	],
)
define_relationships(
	"The Merger of Rules",
	compat_patches = [
		"Evolved + MoR Patch",
	],
	# inbuilt_compat = [
	# 	"has_prob_mod",
	# 	"has_gigastructures",
	# 	"origin_beings_mod",
	# ],
)
define_relationships(
	"Real Space",
	children = [
		"Real Space Nebulae",
	],
)
define_relationships(
	"All That Is GRIMDARK",
	parents = [
		"Ork Voice Advisor – Warhammer 40K",
		"Astartes Voice Over",
		"Remove Paradox Empires",
	],
)
define_relationships(
	"Universal Resource Patch",
	children = [
		"Destiny: Hive Portraits",
		"Ethics and Civics Alternative - FunEFork",
		"GirlsFrontline - NytoSpeciesEventsPack",
		"Unique Ascension Perks",
		"Expanded Events",
		"Expanded Governments",
		"Expanded Megastructures and Technology",
		"GirlsFrontline NytoSpeciesEventsPack",
	],
)
define_relationships(
	"Universal Modifier Patch",
	children = [
		"Ethics and Civics Alternative - FunEFork",
		"Unique Ascension Perks",
		"Expanded Events",
		"Expanded Governments",
		"Expanded Megastructures and Technology",
	],
)
define_relationships(
	"Fatherland: Frontier Worlds",
	children = [
		"Fatherland: Colonial Empires",
	],
)
define_relationships(
	"The Nanites Revolution",
	children = [
		"KDC Story Pack",
	],
)
define_relationships(
	"New Legendary Worlds",
	children = [
		"Legendary Worlds 4.0 patch",
	],
)
define_relationships(
	"Star System Cluster Range Weapon",
	children = [
		"Origin - F.C.S.S & M.C.S.S",
	],
)
define_relationships(
	"Stellaris General Fixes",
	children = [
		"Potent Rebellions Expanded",
		"Powerful & Realistic Orbital Bombardments",
		"Unique Ascension Perks",
	],
)
define_relationships(
	"WP’s Library",
	children = [
		"WP’s Planet View",
	],
)
define_relationships(
	"Sartek District and Economy Merger Add-on",
	parents = [
		"WP’s Planet View",
		"BPVR - More Building Slots",
	],
)
define_relationships(
	"NSC3 - Season 1",
	children = [
		"StarNet for NSC2",
	],
)
define_relationships(
	"Little Fox’s Framework",
	children = [
		"TimeMod",
	],
)
define_relationships(
	"Expanded Mods Base",
	children = [
		"Expanded Governments",
		"Expanded Events",
		"Expanded Megastructures and Technology",
	],
)
define_relationships(
	"V_TRAITS No Species Class Restriction Patch",
	parents = [
		"Nature Traits Mod",
		"Necroid & Spooky Traits",
		"Toxoid Traits",
	],
)
define_relationships(
	"Cybrxkhan's Assortment of Namelists",
	parents = [
		"Wild space 3 patched",
		"War of Wreaths",
	],
)
define_relationships(
	"Unique Ascension Perks",
	# inbuilt_compat = [
	# 	"has_eca_funefork",
	# 	"has_bug_branch",
	# 	"has_ecc_cog",
	# 	"post_revolutionary_re_revolution_years",
	# 	"has_emex_mod",
	# ],
)

print("removing undetectable mods")
for mod in cw.get_mod_order().copy():
	if not mod.detectable():
		mod.deregister()

print("detecting immediate parents and children")
for mod in cw.get_mod_order():
	mod.detect_immediate_parents_and_children()

cw.auto_set_load_order()
