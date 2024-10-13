# CWParser
 Python library for parsing Stellaris (and hopefully other Clausewitz) script

Important functions for initial configuration of this module:
set_vanilla_path(path): tells the module where to find vanilla content
set_workshop_path(path): tells the module where to find steam workshop content
set_mod_docs_path(path): tells the module where to find your own content

\*\*\*

This package contains 3 files:

cw_parser contains a range of functions and modules for parsing clausewitz-style mods and game code.

mod_data contains *example code* of how one might set up mods; it is not usable as-is since it relies on computer-specific details of which mods are downloaded and which are locally built.

cwp_stellaris contains stellaris-specific configuration for effect parsing. However, cw_parser's effect parsing functionality currently still has serious bugs such that I don't recommend using it.

\*\*\*

<b>Central concepts</b>

This module represents stellaris code as a tree of CWList and CWElement objects, with CWList objects containing CWElements which in turn often contain CWList objects.

<b>CWElement objects</b>

The cw_parser.CWELement class is used to represent key-value pairs such as "cost = 5" or "effect = { kill_pop = yes }", and also to represent elements in arrays such as each tech in a "prerequisitea" block or trait in an "opposites" block.
A CWElement has the following properties:
	name: The left-hand key; str (for key-value pairs) or None (For elements in arrays such as "prerequisite" and "opposites" blocks).
	value: the right-hand value; str, cw_parser.inlineMathsUnit, cw_parser.CWListValue, or cw_parser.metaScript. Should only be set using the setValue() method.
	comparitor: an array generally containing one or more of the characters '=', '<', or '>'.
	metadata: a dictionary for storing freeform data.
	filename: file this element was read from.
	overwrite_type: string representing overwrite type, e.g. 'LIOS' or 'FIOS'.
	mod: mod this element was read from.

<b>CWList objects</b>

The CWList class, a subclass of UserList, is used to represent the contents of files and folders. Its subclass CWListValue is used to represent the contents of {} blocks. CWList lists should never contain objects of types other than CWElement.
The CWList.contents() method returns the contents of a CWList, if appropriate also looking in the expansions of any scripts.

<b>Mod objects</b>

The Mod class is used to represent mods. The special Mod object cw_parser.vanilla_mod_object is used to represent vanilla game contents.

For the purpose of full-file overwriting, mods are assumed to be loaded in the order in which they are created. The set_load_order function can be used to change this.

For the purpose of looking inside inline scripts, resolving global variables, and so on, the parser needs to know which mods to treat as loaded. This can be controlled using the Mod.is_base property, the Mod.parents property, and the Mod.activate() method.

At a given time, the game will assume that the following mods are active:
	- All mods where is_base=True (including cw_parser.vanilla_mod_object)
	- The current active mod, i.e. whichever mod *most recently* had its Mod.activate() method called.
	- All mods in the current active mod's Mod.parents list.

The Mod.read_folder() method reads the contents of a folder within a mod, returning a CWList object. It will also read from that mod's parents and from all mods where is_base is true if either:
	- the include_parents parameter is True
	- the include_parents parameter is not specified AND the mod's is_base value is True

The registered_mods dictionary is a dictionary containing all Mods where the 'key' parameter was specified on creation. cw_parser.vanilla_mod_object will be included with the key "base".

\*\*\*

functions:

set_expand_inlines( bool ):
	sets whether to look inside inline scripts by default when iterating over CWList contents (default False)

set_replace_local_variables( bool ):
	sets whether to replace local variables by default when parsing strings (default True)

set_parser_commands( list\[str\] ):
	Sets a list of strings that identify commands for the parser by default. By default, this is \["CW_PARSER"\], meaning that all file contents between "#CW_PARSER:skip" and "#CW_PARSER:/skip" will be ignored.

to_yesno( bool ):
	converts a boolean to a string "yes" or "no"

in_common( \*args ):
	shorthand for os.path.join('common',\*args)

escapeString( str ):
	escapes quotes and backslashes in a string

quote( str ):
	escapes quotes and backslashes in a string then wraps it in quotation marks

indent( str, count=1, initial_linebreak=False ):
	indents a string with tabs

numerify( str ):
	converts a string to an int or float if possible

valueString( object ):
	converts an object back to the corresponding string for use in stellaris script
	for objects from this module str() is equivalent, but this is useful if you might also receive a string containing spaces

match( string1, string2 ):
	checks that two strings are the same apart from case.

mod_doc_path(name):
	returns the path to one of your own mods; name is the folder name

resolveValue( value, vars=None ):
	attempts to solve inlineMathsBlocks and look up global variables to give a final value.
	e.g. resolveValue("@discovery_weight") returns "3"
	parameters:
		value( str or inlineMathsBlock ):
			object to resolve value of
		vars( Mod ):
			Mod to treat as active for the purpose of global variables lookup. If not specified, uses the current active mod.

stringToCW( string, filename=None, replace_local_variables=None, parser_commands=None, overwrite_type=None, mod=None, bracketClass=cw_parser.CWListValue ) -> CWList:
	parses a string into a CWList object.

	parameters:
		string (str):
			String to parse
		filename (str):
			Filename to assign to these objects
		replace_local_variables (bool):
			If True, local @ variable assignments (@key = value) in the string will be used to replace subsequent local @ variable usages (key = @variable) as appropriate.
			A default value for this parameter can be set with the set_replace_local_variables(bool) function. Initially this will be True.
		parser_commands (list[str]):
			List of strings to identify commands for the parser within the text.
			A default value for this parameter can be set with the set_parser_commands(list) function. Initially this will be ["CW_PARSER"].
			This means the following commands will function:
				#CW_PARSER:skip (begin ignoring text)
				#CW_PARSER:/skip (stop ignoring text)
				#CW_PARSER:add_metadata:<key>:<value> (add metadata to the next object)
				#CW_PARSER:add_block_metadata:<key>:<value> (start adding metadata to objects)
				#CW_PARSER:/add_block_metadata (undoes the most recent add_block_metadata effect)
		overwrite_type (str):
			string representing overwrite type. If equalt to 'LIOS' or 'FIOS' this can be used by certain methods to figure out what overwrites what.
		mod (cw_parser.Mod):
			mod this data belongs to
		bracketClass (type):
			set to cw_parser.metaScript for metascripts when parsing scripted effects, scripted triggers, and script values.

fileToCW( path, filename=None, parent=None, replace_local_variables=None, parser_commands=None, overwrite_type="LIOS", mod=None, bracketClass=cw_parser.CWListValue ) -> CWList:
	Parses a file using stringToCW.
	If filename is not given, defaults to using that file's filename.

\*\*\*

public classes in cw_parser:

<b>inlineMathsStep( operator, value, negative )</b>

object representing a step in an inline maths block
operator should be None (for first element of block), '+', '-', '*', '/', or '%'
value should be a number, a string representing a global variable, or an inlineMathsBlock

<b>inlineMathsBlock()</b>
UserList of inlineMathsSteps representing a bracket-enclosed inline maths subsection

<b>absValBlock()</b>
Subclass of inlineMathsBlock representing a ||-enclosed inline maths subsection

<b>inlineMathsUnit()</b>
Subclass of inlineLathsBlock representing a @[]-enclosed inline maths value.

<b>Mod( workshop_item=None, mod_path=None, parents=[], is_base=False, key=None, compat_var=None )</b>:

Class representing a mod (or vanilla).
Mod load order is assumed to correspond to the order in which mods are created. This can be changed using the cw_parser.set_load_order function, which takes a list of mods and moves those mods to the end of the assumed load order.
cw_parser.registered_mods is a dictionary to which mods can be automatically added on creation by assigning a key. The vanilla mod object is included in this dictionary with the key 'base'.

init parameters/properties:
	workshop_item (str): string (NOT int) containing this mod's steam workshop number.
	mod_path (str): path to this mod. If None, derive from workshop_item. Paths to your own mods can be generated with mod_doc_path('my_mod_filename')
	parents (list[cw_parser.Mod]): list of mods this mod object should assume are installed
	is_base (bool): if True, all mods should also assume this one is installed
	key (str): if not none, this mod will be included in the cw_parser.registered_mods dictionary
	compat_var (str): compatibility variable for this mod

additional public properties:
	content_dictionaries: dictionary of dictionaries generated by generate_content_dictionary
	content_lists: dictionary of CWLists read from folders in this mod, indexed by relative path or specified keys

public methods:
	load_metascripts():
		loads scripted triggers, scripted effects, and script values for this mod. Should only be done after metascripts for the mod's prerequisites have already been loaded so they can be inherited.

	getFiles( path, exclude_files=[], include_parents=None, file_suffix='.txt' ):
		Returns all file paths with a given file suffix in a given folder within this mod, except those the with filenames listed in exclude_files. If include_parents is True, also gets files from other mods this one assumes are loaded, except those that are full-file overwritten in the assumed configuration.
		include_parents defaults True for base mods (including the vanilla mod object), false otherwise.

	read_folder( path, exclude_files=[], replace_local_variables=None, include_parents=None, file_suffix='.txt', parser_commands=None, overwrite_type='LIOS', bracketClass=CWListValue, save=True, save_key=None print_filenames=False, always_read=False )
		provides a CWList object representing the contents of a specific folder in this mod, as per Mod.getFiles and cw_parser.stringToCW. Unless save=False, also saves the result to this mod's content_lists dictionary. Unless always_read=True, returns an existing CWList from the content_lists dictionary if one exists (in which case most other parameters will be ignored in favor of those used when that CWList was generated)

	inheritance():
		iterates over all mods this one should assume are loaded, in reverse load order (i.e. this mod, its parents, and all mods where is_base is True)

	inherits_from(mod):
		checks whether this mod assumes another mod is loaded

	generate_content_dictionary( key, folder_path, primary_key_rule=(lambda e:e.name), element_filter=(lambda _:True), **kwargs ):
		runs self.read_folder(**kwargs) and saves the results to self.content_dictionaries[key], with keys derived from primary_key_rule, so long as they meet element_filter.

	inherit_content_dictionary( key ):
		Merges this mod's content dictionary with the given key with those of its parents. Should not be used unless the objects in those dictionaries have overwrite type "LIOS" or "FIOS", since other overwrite types aren't handled well.

	folder(path):
		provides a folder within this mod, as per os.path.join starting with this mod's location

	global_variables(key):
		looks up a global variable in this mod

	scripted_triggers():
		returns a dictionary of scripted triggers from this mod

	scripted_effects():
		returns a dictionary of scripted effects from this mod

	script_values():
		returns a dictionary of scripted triggers from this mod

	events():
		shorthand for contents_lists['events'].contents() (with no parameters)

<b>CWList( *args, local_variables={}, bracketClass=cw_parser.CWListValue )</b>

Subclass of UserList for representing the contents of Stellaris files or folders (and see CWListValue)

init parameters/properties:
	local_variables: dictionary of local variables
	bracketClass: should be cw_parser.metaScript for metascripts, cw_parser.CWListValue otherwise.

other public properties:
	parent_element: if this is the right-hand-side value of a CWElement, returns that CWElement. This property should only be read, never written, outside of this module.

public methods:
	contents( expand_inlines=None, inlines_mod=None, expansion_exceptions=(lambda _: false) ):
		Yields from the contents of this CWList, looking inside inline scripts if appropriate.
		Default values for expand_inlines and inlines_mod can be set using set_expand_inlines and set_context_mod. Inline scripts for which expansion_exceptions evaluates true will be yielded rather than being looked inside.
	getElements(key,**kwargs):
		Yields results from self.contents(**kwargs) with a specific name.
	getElement( key, **kwargs ):
		Returns the first result from self.contents(**kwargs) with a specific name.
	hasAttribute( key, **kwargs ):
		Returns True if the CWList has an element with a specific name, False otherwise
	getValues( key, resolve=False, **kwargs ):
		Yields the right-hand-side values from getElements(key,**kwargs). If resolve=True, attempts to replace global variables with their values and solve inline maths blocks.
	getValue( key, default="no", resolve=False, **kwargs ):
		Returns the right-hand-side value of getElement(key,**kwargs). If resolve=True, attempts to replace global variables with their values and solve inline maths blocks. If the list contains no elements with the appropriate name, instead returns default.
	getValueBoolean( key, default="no" resolve=True, **kwargs ):
		As getValue, except "no" is converted to False and all other values are converted to True
	hasKeyValue( key, value, **kwargs ):
		Checks whether the list has an element with both the given name and the given value
	getArrayContents(key,**kwargs):
		For each array-type element in this list with the given name (e.g. prerequisite-tech blocks, trait opposite blocks), yields each value from that array (as a string, inlineMathsUnit, etc.)
	getArrayContentsFirst(key,default="no",**kwargs):
		Returns the first value from the first array in this list with the given name.
	getArrayElements(key,**kwargs):
		For each array-type element in this list with the given name (e.g. prerequisite-tech blocks, trait opposite blocks), yields each element from that array (as a CWElement)
	navigateByDict(directions):
		generator that navigates the CW-element tree according to a dictionary, returning tuples.
		for example
		CWList.navigateByDict(
			'planet_event':{
				'option':5,
				'initial':1,
			}
		)
		will find each planet event in this list, find each option block and initial block in those events, and yield (<option block>,5) for the option blocks and (<initial block>,1) for the initial blocks.
		Also allows '*' as a wildcard key.

<b>CWListValue( *args, local_variables={}, bracketClass=cw_parser.CWListValue )</b>

Subclass of CWListValue for representing bracket-enclosed right-hand-side-values. Behaves exactly like CWList except for its string representation. In hindsight this should have been a boolean property.

<b>ColorElement(format,*args)</b>:

Subclass of CWListValue used for representing colors. Like CWListValue except it has a 'format' property.

<b>CWElement( name=None, comparitor=[], value=None, filename=None, overwrite_type=None, mod=None, local_variables=None, scopes=None )</b>

Class for representing key-value pairs (e.g. "fire = yes" or "opposites = { trait_strong trait_weak }") or elements of arrays.

init parameters/properties:
	name: the key side of the key/value pair. For elements of arrays such as prerequisite tech blocks or trait opposite blocks, this is None.
	comparitor: list of '=', '<', or '>' characters used to connect the key and value.
	value: the value side of the key/value pair. should only be set using the setValue method.
	filename: name of the file this element comes from.
	overwrite_type: string representing overwrite type (e.g. "LIOS" or "FIOS")
	metadata: dictionary for storing freeform data


other public properties
	parent_list: the CWList containint this object. Should only be read, not written.
	scriptExpansions: dictionary with the expansions of an inline script, scripted effect, or scripted trigger, by mod title. Should only be read, not written

public methods:
	parent():
		returns the CWElement above this one in the tree, or None if no such element exists.
	
	setValue(value):
		Sets the right-hand-side value for this element.
		Value should be a string, inlineMathsUnit, CWListValue, or metaScript.
	
	resolve():
		returns the right-hand-side value, replacing global variables and solving inlineMathsUnits

	hasSubelements():
		returns True if this object's value is a CWListValue, False otherwise.

	def parent_hierarchy():
		yields this element, then the one that contains it, then the one that contains that one, and so on

	getRoot(self):
		returns the root CWElement of the tree containing this one

	convertGovernmentTrigger():
		converts government requirement block syntax to trigger syntax

	inlineScriptExpansion( mod=None, parser_commands=None, bracketClass=cw_parser.CWListValue, expansion_exceptions=(lambda _:False) ):
		yields from an inline script instance's expansion

	metaScriptExpansion( metascript_dict, parser_commands=None ):
		yields from a scripted effect or trigger instance's expansion.

	The following methods call the corresponding method in the element's value, if that value is a CWListValue:
		contents, getElements, getElement, hasAttribute, getValues, getValue, getValueBoolean, hasKeyValue, getArrayContents, getArrayContentsFirst, getArrayContentsElements, and navigateByDict

<b>metaScript()</b>
Class for representing the right-hand-side values of scripted effects, stripted triggers, and script values.

public methods:
	inst( params={} ):
		returns a CWList object matching the output of this metascript when given the parameter values in params (e.g. replacing "$VALUE$" with params["VALUE"]).