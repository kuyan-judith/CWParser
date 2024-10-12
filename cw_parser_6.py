# EXPERIMENTAL

import re
import os
from typing import Generator, Callable, Self
from numbers import Number
from abc import ABC, abstractmethod
from collections.abc import Iterator, Iterable
from collections import UserList, UserDict
from copy import copy, deepcopy
from time import sleep



globalSettings = {
	'parser_commands':None,
	'context_mod':None,
	'replace_local_variables':False,
	'expand_inlines':False,
	'debug_print':False,
	'debug_sleep':0,
	'max_from_depth':8,
	'effectLocations':{},
	'effectNesting':{},
	'scopeTransitions':{},
	'eventTypes':{},
	'hardcodedOnActions':{},
	'effectParseAdditionalSetup':lambda mod: None,
	'additionalEffectBlocks':lambda mod: [],
	'mod_docs_path':"C:\\Users\\kuyan\\OneDrive\\Documents\\Paradox Interactive\\Stellaris\\mod",
	'workshop_path': "C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\281990",
	'vanilla_path':"C:\\Program Files (x86)\\Steam\\steamapps\\common\\Stellaris",
}
globalData = {
	'eventTargets':{},
	'factionParameters':{},
	'onActionScopes':{},
	'eventScopes':{},
}

def defaultToGlobal(value,key):
	if value is None:
		return globalSettings[key]
	else:
		return value

def configure(key,value):
	global globalSettings
	globalSettings[key] = value

def printsleep(s):
	if globalSettings['debug_print']:
		print(s)
		sleep(globalSettings['debug_sleep'])

def modDocPath(name):
	return os.path.join(globalSettings['mod_docs_path'],name)

class ShallowFromsException(Exception):
	pass

class UndefinedCollision(Exception):
	pass

# placeholder class definitions
class Mod():
	pass
class CWOverwritable():
	pass
class CWElement(CWOverwritable):
	pass
class CWList(UserList):
	pass
class CWListValue(CWList):
	pass
class ColorElement(CWListValue):
	pass
class inlineMathsStep():
	pass
class inlineMathsBlock():
	pass
class inlineMathsUnit():
	pass
class modulusBlock():
	pass
class metascript():
	pass
class metascriptSubstitution():
	pass
class metascriptConditional():
	pass
# class metascriptInlineMathsBlock():
# 	pass
class metascriptList(UserList):
	pass
class scopeUnpackable(ABC):
	pass
class scopeSet(scopeUnpackable):
	pass
class scopesContext():
	pass

def escapeString(s:str) -> str:
	return s.replace('\\','\\\\').replace('"','\\"')

def quote(s:str) -> str:
	'''puts quote marks around a string'''
	return f'"{escapeString(s)}"'

def numerify(s:str) -> int|float|str:
	'''tries to convert a string to an integer or float'''
	try:
		return int(s)
	except(ValueError):
		try:
			return float(s)
		except(ValueError):
			return s

def indent( s:str, count:int=1, initial_linebreak=False ) -> str:
	'''indents a multi-line string using tabs'''
	tabs = '\n'
	for i in range(count):
		tabs += '\t'
	if initial_linebreak:
		s = '\n'+s
	return s.replace('\n',tabs)

def valueString(v) -> str:
	if isinstance(v,str):
		if ' ' in v or '\n' in v or '\t' in v or v=='':
			return quote(v)
		else:
			return(v)
	else:
		return str(v)

def generate_joined_folder(path:str,*args) -> str:
	'''like os.path.join, except it it will create a folder if it doesn't already exists'''
	for folder in args:
		path = os.path.join(path,folder)
		if not os.path.exists(path):
			os.mkdir(path)
	return path

def match( string1:str|None, string2:str|None, debug=False ) -> bool:
	'''checks that, of two strings, either both exist or nether exists, and both are the same except for case'''
	if isinstance(string1,str) and isinstance(string2,str):
		m = string1.lower() == string2.lower()
		return m
	else:
		return string1 == string2

def to_yesno(bool:bool) -> str:
	'''converts a boolean to the string "yes" or "no", to match Stellaris syntax'''
	if bool:
		return "yes"
	else:
		return "no"

def inCommon(*args:list[str]) -> str:
	return os.path.join('common',*args)

government_triggers = {
	'country_type':'is_country_type',
	'species_class':'is_species_class',
	'species_archetype':'is_species_class',
	'origin':'has_origin',
	'ethics':'has_ethic',
	'authority':'has_authority',
	'civics':'has_civic',
}

class Mod():
	'''class for representing mods.
	parameters:
	workshop_item (optional): The number for this mod in Steam Workshop.
	mod_path (optional): The path for this mod. If not specified it will be derived from workshop_item.
	parents (optional): List of other mods to assume are also loaded if this one is, in reverse load order. Default [].
	is_vanilla (optional): Boolean that indicates whether a mod object is vanilla. Default False.
	vanilla_object (optiona): overwrites the default vanilla mod object
	'''
	def __init__( self, workshop_item:str|None = None, mod_path:str|None = None, parents:list[Mod] = [], is_vanilla:bool=False, vanilla_object = None ) -> None:
		if mod_path is None:
			self.mod_path = os.path.join( globalSettings['workshop_path'], workshop_item )
		else:
			self.mod_path = mod_path
		if is_vanilla:
			self.inheritance_list = [self]+parents
		else:
			if vanilla_object is None:
				vanilla_object = vanilla_mod_object
			self.inheritance_list = [self]+parents+[vanilla_object]
		self.is_vanilla = is_vanilla
		self.content_dictionaries = {}
		self.content_lists = {}
		self.mod_name = '[UNNAMED]'
		self.load_global_variables()
		self.giveName()

	def __str__(self) -> str:
		return self.mod_name

	def load_global_variables(self) -> Self:
		self.generate_content_dictionary( 'global_variables', inCommon('scripted_variables'), primary_key_rule = lambda x: x.name[1:], replace_local_variables=False )
		self.inherit_content_dictionary('global_variables')
		return self

	def giveName(self):
		descriptor_path = os.path.join(self.mod_path,'descriptor.mod')
		if os.path.exists(descriptor_path):
			descriptor = fileToCW( descriptor_path )
			self.mod_name = descriptor.getValue('name')
		else:
			self.mod_name = "Vanilla"

	def load_metascripts(self) -> Self:
		self.generate_content_dictionary( 'scripted_triggers', inCommon('scripted_triggers'), metascript=True, replace_local_variables=True )
		self.generate_content_dictionary( 'scripted_effects', inCommon('scripted_effects'), metascript=True, replace_local_variables=True )
		self.generate_content_dictionary( 'script_values', inCommon('script_values'), metascript=True, replace_local_variables=True )
		self.inherit_content_dictionary('scripted_triggers')
		self.inherit_content_dictionary('scripted_effects')
		self.inherit_content_dictionary('script_values')
		return self

	def inheritance(self) -> Generator[Mod,None,None]:
		'''yields the mod, then each of its parents in reverse load order, then vanilla'''
		for mod in self.inheritance_list:
			yield mod

	def lookupInline(self,inline:str) -> str:
		'''returns the path to the file an inline script would find if used with this mod, its parents, and no other mods
		parameters:
		inline'''
		inline_breakdown = inline.split('/')
		inline_path = inCommon('inline_scripts')
		for folder in inline_breakdown:
			inline_path = os.path.join( inline_path, folder )
		inline_path = inline_path+'.txt'
		for mod in self.inheritance():
			try_path = os.path.join( mod.mod_path, inline_path )
			if os.path.exists(try_path):
				return try_path
			
	def folder( self, path:str ) -> str:
		return os.path.join( self.mod_path, path )
	
	def global_variables(self):
		return self.content_dictionaries['global_variables']
	
	def scripted_triggers(self):
		return self.content_dictionaries['scripted_triggers']
	
	def scripted_effects(self):
		return self.content_dictionaries['scripted_effects']
	
	def script_values(self):
		return self.content_dictionaries['script_values']

	def getFiles( self, path:str, exclude_files:list[str]=[], include_parents:bool=False, file_suffix:str='.txt' ):
		exclude_files = exclude_files.copy()
		for mod in self.inheritance_list:
			if (mod is self) or include_parents:
				folder = mod.folder(path)
				if os.path.exists(folder):
					for file in os.listdir(path=folder):
						if file.endswith(file_suffix) and not file in exclude_files:
							filepath = os.path.join(folder,file)
							exclude_files.append(file)
							yield filepath

	def read_folder( self, path:str, exclude_files:list[str]=[], replace_local_variables:bool|None=None, include_parents:bool=False, file_suffix:str='.txt', parser_commands:str|list[str]|None=None, overwrite_type:str|None='LIOS', metascript:bool=False, to_key=None ) -> CWList[CWElement]:
		'''reads and parses the files in the specified folder in this mod into a list of CWElements
		parameters:
		path: the path to the specified folder, relative to the mod
		exclude_files (optional): a lost of filenames to skip, e.g. because the entries within are dummy elements or because they're assumed to have been overwritten
		replace_local_variables (optional): if True, locally-defined scripted variables will be replaced with their values.
		include_parents (optional): if True, also load contents of parent folders that aren't file-overwritten
		file_suffix (optional): only files with this suffix will be read. Default '.txt'
		parser_commands (optional): if this is set to a string or list of strings, the following tags will be enabled (where KEY stands for any of the entered strings):
		"#KEY:skip", "#KEY:/skip": ignore everything between these tags (or from the "#KEY:skip" to the end of the string if "#KEY:/skip" is not encountered)
		"#KEY:add_metadata:<metadata key>:<metadata value>": set the specified attribute in the "metadata" dictionary to the specified value for the next object
		"#KEY:add_block_metadata:<metadata key>:<metadata value>", "#KEY:/add_block_metadata:<metadata key>": set the specified attribute in the "metadata" dictionary to the specified value for each top-level object between these tags
		'''
		CW_list = CWList()
		for filepath in self.getFiles( path, exclude_files=exclude_files, include_parents=include_parents, file_suffix=file_suffix ):
			CW_list = CW_list + fileToCW( filepath, replace_local_variables=replace_local_variables, parser_commands=parser_commands, overwrite_type=overwrite_type, metascript=metascript, mod=self )
		if to_key is not None:
			self.content_lists[to_key] = CW_list
		return CW_list

	def inherit_content_dictionary(self,key):
		new_dict = self.content_dictionaries.setdefault(key,{})
		for mod in self.inheritance_list:
			old_dict = mod.content_dictionaries[key]
			for k in old_dict:
				obj = old_dict[k]
				if ( not k in new_dict ) or ( obj.overwrites( new_dict[k], default = False ) ):
					new_dict[k] = obj

	def generate_content_dictionary( self, key, folder_path, primary_key_rule=lambda e:e.name, element_filter = lambda e:True, **kwargs ):
		list = self.read_folder( path=folder_path, **kwargs, to_key=key )
		content_dict = self.content_dictionaries.setdefault(key,{})
		for element in list:
			if element_filter(element):
				content_dict[ primary_key_rule(element) ] = element

	def load_events(self):
		eventTypes = globalSettings['eventTypes']
		self.content_dictionaries['events'] = {}
		events = self.read_folder('events',overwrite_type='FIOS',to_key='events')
		for event in events.contents():
			if event.hasSubelements():
				event_id = event.getValue('id',evaluate=True)
				self.content_dictionaries['events'][event_id] = event
				if event.name.lower() in eventTypes:
					globalData['eventScopes'][event_id] = scopesContext(eventTypes[event.name.lower()],lock=True)

	def load_on_actions(self):
		on_actions = self.read_folder( inCommon('on_actions'),overwrite_type='merge',to_key='on_actions')
		for on_action in on_actions.contents():
			globalData['onActionScopes'][on_action.name] = scopesContext()

	def activate_on_actions(self):
		eventScopes = globalData['eventScopes']
		onActionScopes = globalData['onActionScopes']
		for on_action in self.content_lists['on_actions'].contents():
			if on_action.hasAttribute('random_events'):
				for event in on_action.getElement('random_events').contents():
					event_key = event.eval()
					if event_key != 0:
						eventScopes[event_key].add( onActionScopes[on_action.name] )
			if on_action.hasAttribute('events'):
				for event in on_action.getElement('events').contents():
					event_key = event.eval()
					if event_key != 0:
						eventScopes[event_key].add( onActionScopes[on_action.name] )

	def events(self) -> Generator[CWElement,None,None]:
		yield from self.content_lists['events'].contents()

class parserCommandObject():
	def __init__(self,code,key,*args) -> None:
		self.code = code
		self.key = key
		self.parameters = args

	def isspace(self):
		return False

	def startswith(self,str:str):
		return False
	
	def restoreString(self,str:str):
		text_params = [self.key]+self.parameters
		return f"#{self.code}:({ ':'.join(text_params) })"

class tokenizer():
	def __init__(
		self,
		string:str,
		parser_commands:str|list[str]|None=None,
		debug=False,
	) -> None:
		self.debug = debug
		# replace parser command tokens with something that doesn't start with "#" so they don't get removed with comments
		if isinstance(parser_commands,str):
			parser_command_template = r"#{}:([^ \n]*)".format(parser_commands)
			string = re.sub( parser_command_template, r"@PARSER:{}:\1".format(parser_commands), string )
		elif isinstance(parser_commands,list):
			for key in parser_commands:
				parser_command_template = r"#{}:([^ \n]*)".format(key)
				string = re.sub( parser_command_template, r"@PARSER:{}:\1".format(key), string )
		# # remove comments
		# # if not include_formatting:
		# string = string+"\n"
		# string = re.sub(r"#.*\n",r" ",string)
		# prepare string for splitting
		# normal script and metascript special characters
		string = re.sub(r'(\s+)',r'‗\1‗',string)
		string = string.replace('#','‗#')
		string = string.replace('\n','‗\n')
		string = string.replace('=','‗=‗')
		string = string.replace('<','‗<‗')
		string = string.replace('>','‗>‗')
		string = string.replace('{','‗{‗')
		string = string.replace('}','‗}‗')
		string = string.replace('[','‗[‗')
		string = string.replace(']','‗]‗')
		string = re.sub(r'@(\\*)‗\[',r'‗@[',string)
		string = string.replace('$','‗$‗')
		string = string.replace('|','‗|‗')
		# inline maths special characters
		string = string.replace('"','‗"‗')
		# escaping
		string = string.replace('\\\\','‗\\\\‗')
		string = string.replace('\\‗"','‗\\"')
		string = string.replace('+','‗+‗')
		string = string.replace('-','‗-‗')
		string = string.replace('/','‗/‗')
		string = string.replace('@PARSER:‗/‗','@PARSER:/')
		string = string.replace('*','‗*‗')
		string = string.replace('%','‗%‗')
		string = string.replace('(','‗(‗')
		string = string.replace(')','‗)‗')
		string = re.sub(r'‗+',r'‗',string)
		# split by the metatoken delimeter
		tokenList = string.split('‗')
		# apply parser skip command
		i = 0
		while i < len(tokenList):
			token = tokenList[i]
			if token == '':
				tokenList.pop(i)
			elif token == '@PARSER:skip':
				while token != '@PARSER:/skip' and i < len(tokenList):
					token = tokenList.pop(i)
			else:
				if token.startswith('@PARSER'):
					parameters = token.split(':')
					parameters.pop(0)
					tokenList[i] = parserCommandObject(*parameters)
				i += 1
		tokenList.append('\n')
		self.metatokens = tokenList
		self.position = -1
		# self.nextAny = self.nextAny()
		# self.nextActive = self.nextActive()
		self.cwtokens = self.mode(
			special_tokens = [ '=', '{', '}', '"', '<', '>', '@[' ],
			split_on_whitespace = True,
			debug_name='cwtokens',
		)
		self.IMOperators = self.mode(
			end_token = [ '+', '-', '*', '/', '%', ']', ')', '|' ],
			start_token = [ '(', '[', '|' ],
			split_on_whitespace = True,
		)
		self.IMValues = self.mode(
			end_token = [ '(', '[', '|' ],
			start_token = [ '+', '-', '*', '/', '%', ']', ')', '|' ],
			split_on_whitespace = True,
		)
		self.metascriptTokens = self.mode(
			special_tokens = [ '{', '}', '"', '[', '@[', '$', 'optimize_memory' ],
			split_on_whitespace = False,
		)
		self.metascriptConditionalTokens = self.mode(
			special_tokens = [ ']', '"', '[', '@[', '$' ],
			split_on_whitespace = False,
		)
		self.metascriptSubstitutionTokens = self.mode(
			special_tokens = [ '|', '$' ],
			split_on_whitespace = False,
		)

	def current_mt(self) -> str|parserCommandObject:
		if self.position >= len(self.metatokens):
			return None
		else:
			return self.metatokens[ self.position ]

	def next_mt(self) -> str|parserCommandObject|None:
		if self.position + 1 >= len(self.metatokens):
			return None
		else:
			return self.metatokens[ self.position + 1 ]

	def step(self,skip_comments:bool=False,skip_whitespace:bool=False):
		# if self.debug:
		# 	printsleep('>->')
		while self.position <= len(self.metatokens):
			self.position += 1
			# if self.debug:
			# 	printsleep(f"({self.current_mt()}|{self.next_mt()})")
			if not isinstance(self.current_mt(),str):
				# printsleep(f'skipwhite:<{str(self.current_mt())}><{str(self.next_mt())}>')
				break
			if skip_comments and self.current_mt().startswith('#'):
				while not self.current_mt().startswith( '\n' ):
					self.position += 1
			if (not skip_whitespace) or (not self.current_mt().isspace()):
				# printsleep(f'skipwhite:<{str(self.current_mt())}><{str(self.next_mt())}>')
				break

	def mode(
		self,
		special_tokens:list[str]|None=None,
		end_token:list[str]|None=None,
		start_token:list[str]|None=None,
		skip_comments:bool = True,
		split_on_whitespace:bool = True,
		debug_name = '',
	) -> Generator[tuple[str|parserCommandObject|None,bool],None,None]:
		
		if end_token is None:
			end_token = special_tokens

		if start_token is None:
			start_token = special_tokens

		token = ''

		while True:
			self.step(skip_comments=skip_comments,skip_whitespace=split_on_whitespace)
			# printsleep(f'<{str(self.current_mt())}><{str(self.next_mt())}>')
			if self.position >= len(self.metatokens):
				# printsleep('mode_break')
				break
			elif not isinstance(self.current_mt(),str):
				# printsleep('mode_nonstring')
				yield self.current_mt()
			else:
				token += self.current_mt()
				# printsleep(f'mode_token <{token}>')
				if (
					(
						split_on_whitespace
						and
						(
							self.next_mt().isspace()
							or
							self.next_mt().startswith('#')
						)
					)
					or ( token in end_token )
					or ( self.next_mt() in start_token )
					or ( not isinstance( self.next_mt() ,str) )
				):
					# if self.debug:
					# 	printsleep(f'>>{debug_name}:<{str(token)}>')
					yield token
					token = ''

	def string_before(self,char:str) -> str:
		token = ''
		while True:
			self.step()
			# print(self.current_mt())
			if self.current_mt() == char:
				return(token)
			token += self.current_mt()
			# printsleep(f"sb:[{token}]")

	def getQuotedString(self) -> str:
		token = ''
		while True:
			self.step()
			# print(self.current_mt())
			if self.current_mt() == '"':
				return(token)
			elif self.current_mt() == '\\"':
				token += '"'
			elif self.current_mt() == '\\\\':
				token += '\\'
			else:
				token += self.current_mt()
			# printsleep(f"sb:[{token}]")

def CWValue(
	token:str,
	tokens:tokenizer,
	value_parse_params:dict={},
	element_params:dict={},
):
	if token == '"':
		return tokens.getQuotedString()
	elif token == '{':
		obj = CWListValue()
		obj.parse( tokens, element_params=element_params, **value_parse_params )
		return obj
	elif token == '@[':
		obj = inlineMathsUnit()
		obj.parse( tokens, **value_parse_params )
		return obj
	elif token in ('hsv','rgb'):
		obj = ColorElement(format=token)
		next( tokens.cwtokens )
		obj.parse( tokens, element_params=element_params, **value_parse_params )
		return obj
	else:
		return token
	
class CWOverwritable():
	def __init__(
		self,
		filename:str|None=None,
		overwrite_type:str|None=None,
		mod:Mod|None=None,
	) -> None:
		self.filename = filename
		self.overwrite_type = overwrite_type
		self.mod = mod

	def overwrites( self, other:CWOverwritable, default:bool ):
		if self.overwrite_type == 'LIOS':
			if self.filename < other.filename:
				return True
			elif self.filename > other.filename:
				return False
			else:
				return default
		if self.overwrite_type == 'FIOS':
			if self.filename > other.filename:
				return True
			elif self.filename < other.filename:
				return False
			else:
				return default




class inlineMathsStep():
	def __init__( self, operator:str|None=None, value=None ):
		self.operator = operator
		self.value = value

	def __str__(self) -> str:
		return f"{self.operator} {str(self.value)}"
	
	def __repr__(self) -> str:
		return f"{self.operator}({str(self.value)})"
	
	def apply(self,prev):
		if self.operator is None:
			return self.value
		elif self.operator == '+':
			return prev + self.value
		elif self.operator == '-':
			return prev - self.value
		elif self.operator == '*':
			return prev * self.value
		elif self.operator == '/':
			try:
				return prev / self.value
			except ZeroDivisionError:
				# Stellaris Evolved relies on this
				return 2147483647
		elif self.operator == '%':
			return prev % self.value

class inlineMathsBlock(UserList):
	endchar = ')'

	def __str__(self) -> str:
		contentstrings = map(str,self)
		return f"( {' '.join(contentstrings)} )"
	
	def __repr__(self) -> str:
		return f'({str(self.data)})'

	def parse(self,tokens:tokenizer,replace_local_variables:bool=False,local_variables:dict[str,str]=True,debug=False) -> Self:
		tree_params = {
			'replace_local_variables':replace_local_variables,
			'local_variables':local_variables,
		}
		self.append( inlineMathsStep() )
		for val in tokens.IMValues:
			if val == '(':
				value = inlineMathsBlock().parse(tokens,**tree_params)
			elif val == '|':
				value = modulusBlock().parse(tokens,**tree_params)
			else:
				if replace_local_variables and (val in local_variables):
					val = local_variables[val]
				value = numerify(val)
			self[-1].value = value
			nextOperator = next(tokens.IMOperators)
			if nextOperator == self.endchar:
				return self
			else:
				self.append(inlineMathsStep(nextOperator))

	def simplify( self, vars:Mod|None=None ):
		for step in self:
			if isinstance( step.value, inlineMathsBlock ):
				step.value = step.value.simplify( vars=vars )
			if isinstance(step.value,str) and isinstance(vars,Mod) and ( step.value in vars.global_variables() ):
				step.value = vars.global_variables()[step.value]
		while len(self) > 1:
			if not (
				isinstance( self[0].value, Number )
				and isinstance( self[1].value, Number )
			):
				return self
			else:
				self[0].value = self.pop(1).apply(self[0].value)
		if isinstance(self[0].value,Number):
			return self[0].value
		elif isinstance( self[0].value, str ):
			self[0].value
		elif type(self[0]) == inlineMathsBlock:
			return type(self)(self[0])
		else:
			return self

	def simplification( self, vars:Mod|None=None ):
		c = deepcopy(self)
		return c.simplify(vars=vars)

class inlineMathsUnit(inlineMathsBlock):
	startchar = '@['
	endchar = ']'

	def __str__(self) -> str:
		contentstrings = map(str,self)
		return f"@[ {' '.join(contentstrings)} ]"
	
	def __repr__(self) -> str:
		return f'@[{str(self.data)}]'

	def simplify( self, vars:Mod|None=None ):
		value = super().simplify( vars=vars )
		if isinstance( value, Number ):
			if isinstance(value,float) and value.is_integer():
				value = int(value)
			return str(value)
		elif isinstance( value, str ):
			return '@' + value
		else:
			return value

class modulusBlock(inlineMathsBlock):
	startchar = '|'
	endchar = '|'

	def __str__(self) -> str:
		contentstrings = map(str,self)
		return f"| {' '.join(contentstrings)} |"

	def __repr__(self) -> str:
		return f'|{str(self.data)}|'

	def simplify( self, vars:Mod|None=None ):
		value = super().simplify( vars=vars )
		if isinstance( value, Number ):
			return abs(value)
		elif isinstance( value, str ):
			return self
		else:
			return value

def resolveValue( value, vars:Mod|None=None ):
	vars = defaultToGlobal(vars,'context_mod')
	if vars is not None:
		if isinstance(value,inlineMathsBlock):
			value = value.simplification(vars=vars)
		if isinstance(value,str) and value.startswith('@'):
			key = value[1:]
			if key in vars.global_variables():
				value = vars.global_variables()[key].eval(vars)
	return value

class CWElement(CWOverwritable):
	def __init__(
		self,
		name:str|None=None,
		comparitor:list[str]=[],
		value=None,
		parent_list:CWList|None=None,
		filename:str|None=None,
		overwrite_type:str|None=None,
		mod:Mod|None=None,
		local_variables:dict[str,str]={},
		scopes:scopesContext|None=None,
	) -> None:
		super().__init__(filename,overwrite_type,mod)
		self.name = name
		self.comparitor = comparitor
		self.setValue( value )
		self.parent_list = parent_list
		self.local_variables = local_variables
		self.metadata = {}
		self.scriptExpansions = {}
		self.scopes = scopes

	# def __getitem__(self,*args):
	# 	return self.value[*args]
	
	def __deepcopy__(self,memo):
		dc = CWElement(
			self.name,
			deepcopy(self.comparitor,memo),
			deepcopy(self.value,memo),
			filename=self.filename,
			overwrite_type=self.overwrite_type,
			mod=self.mod,
			local_variables=deepcopy(self.local_variables,memo),
		)
		dc.metadata = deepcopy(self.metadata,memo)
		return dc

	def parent(self):
		return self.parent_list.parent_element
	
	def setValue(self,value):
		self.value = value
		if isinstance(value,CWList):
			value.parent_element = self

	def parse(self,tokens:tokenizer,replace_local_variables:bool=False,debug=False):
		for token in tokens.cwtokens:
			# if debug:
			# 	printsleep( f'token:<{token}>' )
			if token in ('=','<','>'):
				self.comparitor.append(token)
			else:
				self.setValue(
					CWValue(
						token,
						tokens,
						value_parse_params = {
							'replace_local_variables':replace_local_variables,
							'local_variables':self.local_variables.copy(),
							'debug':debug,
						},
						element_params = {
							'filename':self.filename,
							'mod':self.mod,
							'overwrite_type':self.overwrite_type,
						},
					)
				)
				break

	def __str__(self):
		if self.name is None:
			return valueString(self.value)
		else:
			return f"{self.name} {''.join(self.comparitor)} {valueString(self.value)}"

	def reprStem(self):
		if self.parent() is None:
			return self.name
		else:
			return f"{self.parent().reprStem()}>{self.name}"

	def __repr__(self) -> str:
		if self.hasSubelements():
			return f"{self.reprStem()}={{}}"
		else:
			return f"{self.reprStem()}={repr(self.value)}"
		
	def contents( self, expand_inlines:bool|None=None, inlines_mod:Mod|None=None, expansion_exceptions:Callable[[CWElement],bool]=lambda e: False ) -> Generator[CWElement,None,None]:
		yield from self.value.contents( expand_inlines=expand_inlines, inlines_mod=inlines_mod, expansion_exceptions=expansion_exceptions )
	
	def eval( self, vars:Mod|None=None ):
		return resolveValue(self.value,vars)

	def hasSubelements(self):
		return isinstance(self.value,CWList)

	def getElements( self, key:str|None, **kwargs ) -> Generator[CWElement,None,None]:
		'''yields each subelement of this block with the specified key'''
		yield from self.value.getElements(key,**kwargs)

	def hasAttribute( self, key:str|None, **kwargs ) -> bool:
		'''checks if a block contains a subelement with the given key'''
		if not self.hasSubelements():
			return False
		return self.value.hasAttribute(key,**kwargs)

	def getElement( self, key:str|None, **kwargs ) -> CWElement:
		'''returns the first subelement of this block with the specified key'''
		if self.hasSubelements():
			return self.value.getElement(key,**kwargs)
		else:
			return CWElement("")

	def getValue( self, key:str|None, evaluate=False, default:str="no", **kwargs ):
		'''returns the right-hand value of the first subelement of this block with the specified key'''
		if self.hasSubelements():
			return self.value.getValue(key,default,evaluate=evaluate,**kwargs)
		else:
			return default
	
	def getValueBoolean( self, key:str|None, default:str="no", **kwargs ):
		'''returns the right-hand value of the first subelement of this block with the specified key, as a boolean'''
		return self.getValue(key,default=default,evaluate=True,**kwargs) != 'no'

	def getValueBase(self,key:str|None,default:str="no",**kwargs):
		'''returns the right-hand value of the first subelement of this block with the specified key'''
		if self.hasSubelements():
			return self.value.getValueBase(key,default,**kwargs)
		else:
			return default

	def hasKeyValue(self,key:str|None,value:str,**kwargs):
		'''checks if the object has a subelement with the given key-value pair'''
		return self.value.hasKeyValue(key,value,**kwargs)

	def getValues(self,key:str|None,**kwargs):
		'''yields the right-hand value of each subelement of this block with the specified key'''
		yield from self.value.getValues(key,**kwargs)

	def getArrayContents(self,key:str|None,**kwargs):
		'''yields each string within the specified array subelement'''
		yield from self.value.getArrayContents(key,**kwargs)

	def getArrayContentsFirst( self, key:str, default:str="no", **kwargs ):
		'''returns the first string within the specified array subelement'''
		return self.value.getArrayContentsFirst(key,default,**kwargs)

	def getArrayContentsElements( self, key:str|None, **kwargs ) -> Generator[CWElement,None,None]:
		'''yeilds each element within the specified array subelement'''
		yield from self.value.getArrayContentsElements(key,**kwargs)

	def getRoot(self) -> CWElement:
		'''returns the top-level object containing this one'''
		if self.parent() is None:
			return self
		else:
			return self.parent().getRoot()

	def navigateByDict(self,directions:dict) -> Generator[tuple[CWElement,object],None,None]:
		if self.hasSubelements():
			yield from self.value.navigateByDict(directions)

	def convertGovernmentTrigger( self, trigger:str=None, **kwargs ) -> CWElement:
		# printsleep(f"converting:[{str(self)}]")
		'''returns a copy of a government requirements block converted to normal trigger syntax'''
		# text = <loc key> handled separately, at the next level up
		if match( self.name, 'text' ):
			return ""
		# convert "value = <whatever>" to "has_ethic = <whatever>", "has_authority = whatever" etc.
		elif match( self.name, 'value' ):
			output = CWElement(trigger,['='],self.value)
		# "always" and "host_has_dlc" checks remain unchanged
		elif match( self.name, 'always' ):
			output = CWElement('always',['='],self.value)
		elif match( self.name, 'host_has_dlc' ):
			output = CWElement('host_has_dlc',['='],self.value)
		# convert "ethic" blocks, "authority" blocks etc. into AND blocks if necessary
		elif self.name.lower() in government_triggers:
			# printsleep(kwargs)
			output = CWElement('AND',['='],CWListValue())
			for element in self.contents(**kwargs):
				# printsleep(repr(element))
				if not match( element.name, 'text' ):
					output.value.append( element.convertGovernmentTrigger( government_triggers[self.name], **kwargs ) )
			# no AND block needed for a single trigger
			if len( output.value ) == 1:
				output = output.value[0]
		# AND, OR etc. blocks remain unchanged
		else:
			output = CWElement(self.name,['='],CWListValue())
			# printsleep(kwargs)
			for element in self.contents(**kwargs):
				# printsleep(repr(element))
				if not match( element.name, 'text' ):
					output.value.append( element.convertGovernmentTrigger( trigger, **kwargs ) )
		# convert "text = <loc key>" to custom_tooltip
		if self.hasAttribute('text'):
			text_element = CWElement('text',['='],self.getValue('text'))
			if output.name == 'AND':
				return CWElement(
					'custom_tooltip',
					['='],
					CWListValue( [text_element] + output.value )
				)
			else:
				return CWElement(
					'custom_tooltip',
					['='],
					CWListValue( [text_element,output] )
				)
		else:
			return output

	def getArrayTriggers( self, block:str, trigger:str, mode=None, default='no', **kwargs ) -> str:
		'''generates a trigger or effect block (in string form) from the contents of an array, e.g. you can use this to convert a prerequisite block to something of the form
		"AND = { has_technology = <tech> has_technology = <tech> }"
		block: the name of the array, e.g. "prerequisities"
		trigger: the name of the trigger to use in the output, e.g. "has_technology"
		mode: whether the triggers should be combined as "AND", "OR", "NAND", or "NOR". Default is appropriate for effect blocks.
		default: value to return if the array is nonexistant or empty
		'''
		lines = []
		for item in self.getArrayContents(block,**kwargs):
			lines.append( '{} = {}'.format( trigger, item ) )
		if mode == 'OR':
			if len(lines) == 0:
				return default
			elif len(lines) == 1:
				return lines[0]
			else:
				lines_block = ' '.join(lines)
				return 'OR = {{ {} }}'.format(lines_block)
		elif mode == 'NOR':
			if len(lines) == 0:
				return default
			elif len(lines) == 1:
				return 'NOT = {{ {} }}'.format(lines[0])
			else:
				lines_block = ' '.join(lines)
				return 'NOR = {{ {} }}'.format(lines_block)
		elif mode == 'AND':
			if len(lines) == 0:
				return default
			elif len(lines) == 1:
				return lines[0]
			else:
				lines_block = ' '.join(lines)
				return 'AND = {{ {} }}'.format(lines_block)
		elif mode == 'NAND':
			if len(lines) == 0:
				return default
			elif len(lines) == 1:
				return 'NOT = {{ {} }}'.format(lines[0])
			else:
				lines_block = ' '.join(lines)
				return 'NAND = {{ {} }}'.format(lines_block)
		else:
			if len(lines) == 0:
				return default
			elif len(lines) == 1:
				return lines[0]
			else:
				lines_block = ' '.join(lines)
				return lines_block

	def parent_hierarchy( self ):
		next_obj = self
		while next_obj is not None:
			yield next_obj
			next_obj = next_obj.parent()

	def inlineScriptExpansion( self, mod:Mod|None=None, parser_commands:str|list[str]|None=None, expansion_exceptions:Callable[[CWElement],bool]=lambda e:False ) -> Generator[CWElement,None,None]:
		mod = defaultToGlobal[mod,'context_mod']
		parser_commands = defaultToGlobal[parser_commands,'parser_commands']
		if not ( mod.mod_path in self.scriptExpansions ):
			# if there are parameters, replace them before parsing
			if self.hasSubelements():
				# print('***expanding***')
				# print(f'{self.filename} {repr(self)}:')
				# print(self)
				script_path = self.getValue('script')
				# because quote escaping in inline scripts is too mysterious for me to simulate properly
				if script_path == 'generic_parts/giga_toggled_code':
					if self.getElement('toggle').eval(mod) == '1':
						inline_contents = stringToCW( self.getValue('code') )
					else:
						inline_contents = CWList()
				elif script_path == 'mod_support/tec_inlines_include':
					# I give up
					inline_contents = CWList()
				else:
					script = mod.lookupInline( script_path )
					if script is None:
						raise StopIteration
					else:
						file = open(script,"r")
						script = file.read()
						file.close()
						for param in self.value:
							script = script.replace( f'${param.name}$', param.eval(mod) )
						# print('***text***')
						# print(script)
						inline_contents = stringToCW( script, parser_commands=parser_commands, filename=self.filename, overwrite_type=self.overwrite_type, mod=self.mod )
				# print('***output***')
				# print(inline_contents)
			# if there are no parameters, read the file immediately
			else:
				script = mod.lookupInline( self.value )
				if script is None:
					raise StopIteration
				else:
					inline_contents = fileToCW(script,filename=self.filename,parser_commands=parser_commands,overwrite_type=self.overwrite_type,mod=self.mod)
			for subelement in inline_contents:
				subelement.parent_list = self.parent_list
			self.scriptExpansions[mod.mod_path] = inline_contents
		yield from self.scriptExpansions[mod.mod_path].contents(expand_inlines=True,inlines_mod=mod,expansion_exceptions=expansion_exceptions)

	def metaScriptExpansion( self, metascript_dict ) -> Generator[CWElement,None,None]:
		parser_commands = defaultToGlobal[parser_commands,'parser_commands']
		if self.name in metascript_dict:
			ms = metascript_dict[self.name]
			if self.hasSubelements():
				parameters = { p.name: p.eval() for p in self.contents( expand_inlines=True ) }
				return ms.inst(parameters)
			else:
				return ms.inst()


class CWList(UserList):
	is_metascript = False

	def __init__(self,*args,local_variables={}):
		super().__init__(*args)
		self.parent_element = None
		for element in self:
			element.parent_list = self
		self.local_variables = local_variables

	def __repr__(self):
		return f'{repr(self.parent_element)}[{len(self)}]'

	def append(self, item:CWElement|metascript) -> None:
		item.parent_list = self
		return super().append(item)

	def insert(self, i: int, item:CWElement|metascript) -> None:
		item.parent_list = self
		return super().insert(i, item)
	
	def __add__(self, other: Iterable) -> Self:
		new_list = super().__add__(other)
		for element in new_list:
			element.parent_list = new_list
		if isinstance(other,CWList):
			new_list.local_variables = self.local_variables|other.local_variables
		else:
			new_list.local_variables = self.local_variables
		return new_list

	def __iadd__(self, other: Iterable) -> Self:
		for element in other:
			element.parent_list = self
		if isinstance(other,CWList):
			self.local_variables.update(other.local_variables)
		return super().__iadd__(other)
	
	def __setitem__(self,key,value):
		# if isinstance(key,str):
		# 	self.getElement(key).setValue(value)
		# else:
		value.parent_list = self
		super().__setitem__(key,value)

	# def __getitem__(self,key,*args):
	# 	if isinstance(key,str):
	# 		return self.getElement(key,*args)
	# 	else:
	# 		return super().__getitem__(key,*args)

	def parse(
			self,
			tokens:tokenizer,
			replace_local_variables:bool = False,
			local_variables:dict[str,str] = {},
			element_params:dict[str,str] = {},
			debug = False,
		) -> Self:
		block_metadata = {}
		unit_metadata = {}
		for token in tokens.cwtokens:
			# if debug:
			# 	printsleep( f'token:<{token}>' )
			if isinstance(token,parserCommandObject):
				if token.key == 'add_block_metadata':
					if len(token.parameters)==1:
						block_metadata[token.parameters[0]] = True
					else:
						block_metadata[token.parameters[0]] = token.parameters[1]
				elif token.key == 'add_metadata':
					if len(token.parameters)==1:
						unit_metadata[token.parameters[0]] = True
					else:
						unit_metadata[token.parameters[0]] = token.parameters[1]
				elif token.key == '/add_block_metadata':
					block_metadata.pop(token.parameters[0])
			else:
				if token in ('=','<','>'):
					lastElement.comparitor = [token]
					lastElement.parse(
						tokens,
						replace_local_variables=replace_local_variables,
						debug = debug,
					)
					if lastElement.name.startswith('@'):
						lv_key = lastElement.name[1:]
						local_variables[lv_key] = lastElement.value
						if replace_local_variables:
							self.pop()
				elif token == '}':
					break
				else:
					lastElement = CWElement(
						local_variables=local_variables.copy(),
						**element_params
					)
					lastElement.metadata = unit_metadata
					unit_metadata = {}
					for key in block_metadata:
						lastElement.metadata.setdefault(key,block_metadata[key])
					self.append(lastElement)
					# if debug:
					# 	printsleep(f'>>adding element; result:{str(self)}')
					val = CWValue(
						token,
						tokens,
						value_parse_params={
							'replace_local_variables':replace_local_variables,
							'local_variables':local_variables.copy(),
							'debug':debug
						},
						element_params=element_params,
					)
					# if debug:
					# 	printsleep(f'>>assigning value:[{str(val)}]')
					if isinstance(val,str):
						lastElement.name = val
					else:
						lastElement.setValue(val)
		for element in self:
			if element.value is None:
				element.setValue( element.name )
				element.name = None
			if replace_local_variables:
				if isinstance(element.value,str) and element.value.startswith('@'):
					lv_key = element.value[1:]
					if lv_key in local_variables:
						element.setValue( local_variables[lv_key] )
		self.local_variables = local_variables
		return self

	def __str__(self):
		contentstrings = map(str,self)
		if len(self) > 1 or ( len(self) == 1 and not isinstance( self[0].value, str ) ):
			return '\n'.join(contentstrings)
		else:
			return ' '.join(contentstrings)

	# def __getattr__(self,attribute):
	# 	return self.getElement(attribute)
	
	def __deepcopy__(self,memo=None):
		return CWList( deepcopy(self.data,memo), local_variables=deepcopy(self.local_variables,memo) )

	def contents( self, expand_inlines:bool|None=None, inlines_mod:Mod|None=None, expansion_exceptions:Callable[[CWElement],bool]=lambda e: False ) -> Generator[CWElement,None,None]:
		expand_inlines = defaultToGlobal(expand_inlines,'expand_inlines')
		inlines_mod = defaultToGlobal(inlines_mod,'context_mod')
		for element in self:
			if expand_inlines and (element.name == 'inline_script') and (inlines_mod is not None) and not expansion_exceptions(element):
				yield from element.inlineScriptExpansion(mod=inlines_mod,expansion_exceptions=expansion_exceptions)
			else:
				yield element

	def getElements( self, key:str|None, **kwargs ) -> Generator[CWElement,None,None]:
		'''yields each subelement of this block with the specified key'''
		for element in self.contents(**kwargs):
			if match( element.name, key ):
				yield element

	def hasAttribute( self, key:str|None, **kwargs ) -> bool:
		'''checks if a block contains a subelement with the given key'''
		for element in self.getElements( key, **kwargs ):
			return True
		return False

	def getElement( self, key:str|None, **kwargs ) -> CWElement:
		'''returns the first subelement of this block with the specified key'''
		for element in self.getElements( key, **kwargs ):
			return element
		return CWElement("",parent_list=self)

	def getValue( self, key:str|None, default:str="no", evaluate:bool=False, **kwargs ):
		'''returns the right-hand value of the first subelement of this block with the specified key'''
		for element in self.getElements(key,**kwargs):
			if evaluate:
				return resolveValue(element.value)
			else:
				return element.value
		return default
	
	def getValueBoolean( self, key:str|None, default:str="no", **kwargs ):
		'''returns the right-hand value of the first subelement of this block with the specified key, as a boolean'''
		return self.getValue(key,default=default,**kwargs) != 'no'
	
	def getValueBase( self, key:str|None, default:str="no", **kwargs ):
		value = self.getValue( key, default, **kwargs )
		while isinstance( value, CWList ):
			value = value.getValueBase( 'base', default='0', **kwargs )
		return value

	def hasKeyValue( self, key:str|None, value:str, **kwargs ):
		'''checks if the object has a subelement with the given key-value pair'''
		for element in self.getElements( key, **kwargs ):
			if match( element.value, value ):
				return True
		return False

	def getValues( self, key:str|None, **kwargs ):
		'''yields the right-hand value of each subelement of this block with the specified key'''
		for element in self.getElements( key, **kwargs ):
			yield element.value

	def getArrayContents( self, key:str|None, **kwargs ):
		'''yields each string within the specified array subelement'''
		for element in self.getElements( key, **kwargs ):
			yield from element.getValues( None, **kwargs )

	def getArrayContentsFirst( self, key:str, default:str="no", **kwargs ):
		'''returns the first string within the specified array subelement'''
		for element in self.getElements(key,**kwargs):
			for entry in element.value:
				return entry.value
		return default

	def getArrayContentsElements( self, key:str|None, **kwargs ) -> Generator[CWElement,None,None]:
		'''yeilds each element within the specified array subelement'''
		for element in self.getElements(key,**kwargs):
			yield from element.getElements(None,**kwargs)

	def navigateByDict(self,directions:dict) -> Generator[tuple[CWElement,object],None,None]:
		for element in self.contents():
			for key in [element.name,'*']:
				if key in directions:
					d = directions[element.name]
					if isinstance(d,dict):
						yield from element.navigateByDict(d)
					else:
						yield (element,d)

	def effectScopingRun( self, scopes:scopesContext, criteria:Callable[[CWElement],bool] ) -> Generator[tuple[CWElement,scopesContext],None,None]:
		scripted_effects = globalSettings['context_mod'].scripted_effects()
		effectNesting = globalSettings['effectNesting']
		eventTypes = globalSettings['eventTypes']
		for effect in self.contents(expand_inlines=True):
			effect.scopes = scopes
			if criteria(effect):
				yield (effect,scopes)
			if match( effect.name, 'save_event_target_as' ) or match( effect.name, 'save_global_event_target_as' ):
				eventTarget(effect.eval()).add(scopes.this)
			elif effect.name in scripted_effects:
				yield from effect.metaScriptExpansion(scripted_effects).effectScopingRun(scopes,criteria)
			elif effect.hasSubelements():
				if match( effect.name, 'fire_on_action' ):
					event_scopes = scopes.firedContext()
					scope_overwrites = effect.getElement('scopes')
					for i in range(4):
						key = 'from'*(i+1)
						if scope_overwrites.hasAttribute(key):
							event_scopes.froms[i] = scopes.link( scope_overwrites.getValue(key,evaluate=True) )
					globalData['onActionScopes'][effect.getValue('on_action',evaluate=True)].add(event_scopes)
				elif effect.name.lower in eventTypes:
					event_scopes = scopes.firedContext()
					scope_overwrites = effect.getElement('scopes')
					for i in range(4):
						key = 'from'*(i+1)
						if scope_overwrites.hasAttribute(key):
							event_scopes.froms[i] = scopes.link( scope_overwrites.getValue(key,evaluate=True) )
					globalData['eventScopes'][effect.getValue('id',evaluate=True)].add(event_scopes)
				# elif match( effect.name, 'set_next_astral_rift_event' )
				else:
					chain = decomposeChain(effect.name)
					if isScopeChain(chain) and effect.hasSubelements():
						yield from effect.value.effectScopingRun( scopes.link(chain), criteria )
					else:
						if effect.name.lower() in ['create_country','create_rebels']:
							event_scopes = scopes.step('country').firedContext()
							globalData['onActionScopes']['on_country_created'].add(event_scopes)
						for (effectBlock,scope) in effect.navigateByDict(effectNesting):
							if effectBlock.hasSubelements():
								if scope is None:
									yield from effectBlock.value.effectScopingRun( scopes, criteria )
								else:
									yield from effectBlock.value.effectScopingRun( scopes.step(scope), criteria )




class CWListValue(CWList):
	def __str__(self):
		contentstrings = map(str,self)
		if len(self) > 1 or ( len(self) == 1 and not isinstance( self[0].value, str ) ):
			return "{{{}\n}}".format(indent('\n'.join(contentstrings),initial_linebreak=True))
		else:
			return f"{{ {' '.join(contentstrings)} }}"

class ColorElement(CWListValue):
	def __init__(self,format:str,*args):
		super().__init__(*args)
		self.format = format

	def __str__(self):
		return f"{self.format} {super().__str__()}"
	

class metascriptSubstitution():
	def __init__(self,keys:list[str]=[],default:str|None=None):
		self.keys = keys
		self.default = default

	def parse(self,tokens:tokenizer) -> Self:
		params = []
		for token in tokens.metascriptSubstitutionTokens:
			if token == '|':
				pass
			elif token == '$':
				return self
			else:
				params.append(token)
		if len(params) > 1:
			self.default = params.pop()
		self.keys = params

	def inst(self,params:dict[str,str]) -> str:
		for key in self.keys:
			if key in params:
				return params[key]
		return self.default

class metascriptConditional():
	def __init__(self,key:str|None=None,valence:bool=True):
		self.key = key
		self.valence = valence
		self.rawContents = []

	def parse(self,tokens:tokenizer) -> Self:
		brackets = 0
		for token in tokens.metascriptConditionalTokens:
			if token == '[' and self.key is None:
				key = tokens.string_before(']')
				if key.startswith('!'):
					self.key = key[1:]
					self.valence = False
				else:
					self.key = key
					self.valence = True
			elif token == '$':
				self.rawContents.append( metascriptSubstitution().parse(tokens) )
			else:
				if token == '@[':
					brackets += 1
				elif token == ']':
					if brackets >= 0:
						return self
					else:
						self.brackets -= 1
				self.rawContents.append(token)

	def inst(self,params:dict[str,str]) -> str:
		if ( (self.key in params) and params[self.key] != 'no') == self.valence:
			inst = ''
			for section in self:
				if isinstance(section,str):
					inst += section
				else:
					inst += section.inst(params)
			return inst
		else:
			return ''

class metaScript(CWOverwritable):
	def __init__(
		self,
		name:str,
		filename:str|None=None,
		overwrite_type:str|None=None,
		mod:Mod|None=None,
		local_variables:dict[str,str]={}
	):
		super().__init__(filename,overwrite_type,mod)
		self.name = name
		self.rawContents = []
		self.memory_optimized = False
		self.default = CWListValue()
		self.local_variables = local_variables
		self.metadata = {}

	def parse(self,tokens:tokenizer) -> Self:
		brackets = 0
		for token in tokens.metascriptTokens:
			if isinstance(token,parserCommandObject):
				token = token.restoreString()
			if token == 'optimize_memory':
				self.memory_optimized = True
			elif token == '"':
				self.rawContents.append( '"{}"'.format( tokens.getQuotedString() ) )
			elif token == '$':
				self.rawContents.append( metascriptSubstitution().parse(tokens) )
			elif token == '[':
				self.rawContents.append( metascriptConditional().parse(tokens) )
			else:
				if token == '{':
					brackets += 1
				elif token == '}':
					if brackets <= 0:
						self.updateDefault()
						return self
					else:
						brackets -= 1
				self.rawContents.append(token)

	def inst(self,params:dict[str,str]={}):
		inst = ''
		for section in self.rawContents:
			if isinstance(section,str):
				inst += section
			else:
				inst += section.inst(params)
		return stringToCW(
			inst,
			filename=self.filename
		)

	def updateDefault(self):
		try:
			self.default = self.inst()
		except TypeError:
			self.default = None

def stringToCW( string:str, filename:str|None=None, parent:CWElement|None=None, replace_local_variables:bool|None=None, parser_commands:str|list[str]|None=None, overwrite_type:str|None=None, mod:Mod|None=None, metascript:bool=False, debug=False ) -> CWList[CWElement]:
	'''parses a string into a list of CWElement objects
	parameters:
	string: The string to convert.
	filename (optional): Marks CWElements as being from the specified file.
	parent (optional): Marks CWElements as being children of the specified CWElement.
	replace_local_variables (optional): if True, locally-defined scripted variables will be replaced with their values.
	parser_commands (optional): if this is set to a string or list of strings, the following tags will be enabled (where KEY stands for any of the entered strings):
	"#KEY:skip", "#KEY:/skip": ignore everything between these tags (or from the "#KEY:skip" to the end of the string if "#KEY:/skip" is not encountered)
	"#KEY:add_metadata:<metadata key>:<metadata value>": set the specified attribute in the "metadata" dictionary to the specified value for the next object
	"#KEY:add_block_metadata:<metadata key>:<metadata value>", "#KEY:/add_block_metadata:<metadata key>": set the specified attribute in the "metadata" dictionary to the specified value for each top-level object between these tags
	'''
	parser_commands = defaultToGlobal(parser_commands,'parser_commands')
	replace_local_variables = defaultToGlobal(replace_local_variables,'replace_local_variables')
	# print("building tokenizer")
	tokens = tokenizer( string, parser_commands, debug=debug )
	if parent is None:
		local_variables = {}
	else:
		local_variables = parent.local_variables
	if metascript:
		output_class = metascriptList
	else:
		output_class = CWList
	# print("parsing tokens")
	return output_class().parse(
		tokens,
		replace_local_variables,
		local_variables,
		element_params = {
			'filename':filename,
			'mod':mod,
			'overwrite_type':overwrite_type,
		},
		debug=debug,
	)

def fileToCW( path:str, filename:str|None=None, parent:CWElement|None=None, replace_local_variables:bool|None=None, parser_commands:str|list[str]|None=None, overwrite_type:str|None='LIOS', mod:Mod|None=None, metascript:bool=False, debug=False )->CWList[CWElement]:
	'''reads and parses a file into a list of CWElement objects
	parameters:
	path: The file path.
	parent (optional): Marks CWElements as being children of the specified CWElement (for use in the CWElement.replaceInlines method).
	replace_local_variables (optional): if True, locally-defined scripted variables will be replaced with their values.
	parser_commands (optional): if this is set to a string or list of strings, the following tags will be enabled (where KEY stands for any of the entered strings):
	"#KEY:skip", "#KEY:/skip": ignore everything between these tags (or from the "#KEY:skip" to the end of the string if "#KEY:/skip" is not encountered)
	"#KEY:add_metadata:<metadata key>:<metadata value>": set the specified attribute in the "metadata" dictionary to the specified value for the next object
	"#KEY:add_block_metadata:<metadata key>:<metadata value>", "#KEY:/add_block_metadata:<metadata key>": set the specified attribute in the "metadata" dictionary to the specified value for each top-level object between these tags
	'''
	# print(path)
	file = open(path,"r")
	try:
		fileContents = file.read()
	except:
		fileContents = ""
	if filename is None:
		filename = os.path.basename(path)
	cw = stringToCW( fileContents, filename=filename, parent=parent, replace_local_variables=replace_local_variables, parser_commands=parser_commands, overwrite_type=overwrite_type, mod=mod, metascript=metascript, debug=debug )
	file.close()
	return cw


class metascriptList(CWList):
	is_metascript = True

	def parse(
			self,
			tokens:tokenizer,
			replace_local_variables:bool = True,
			local_variables:dict[str,str] = {},
			element_params:dict[str,str] = {},
			debug:bool = False,
		) -> Self:
		block_metadata = {}
		unit_metadata = {}
		for token in tokens.cwtokens:
			if isinstance(token,parserCommandObject):
				if token.key == 'add_block_metadata':
					if len(token.parameters)==1:
						block_metadata[token.parameters[0]] = True
					else:
						block_metadata[token.parameters[0]] = token.parameters[1]
				elif token.key == 'add_metadata':
					if len(token.parameters)==1:
						unit_metadata[token.parameters[0]] = True
					else:
						unit_metadata[token.parameters[0]] = token.parameters[1]
				elif token.key == '/add_block_metadata':
					block_metadata.pop(token.parameters[0])
			elif token == 'inline_script' or token.startswith('@'):
				lastElement = CWElement(
					name=token,
					local_variables=local_variables.copy(),
					**element_params
				)
				lastElement.metadata = unit_metadata
				unit_metadata = {}
				for key in block_metadata:
					lastElement.metadata.setdefault(key,block_metadata[key])
				self.append( lastElement )
				next(tokens.cwtokens) # skip the '=' sign that will always be there
				if token.startswith('@'):
					lv_key = token[1:]
					local_variables[lv_key] = lastElement.value
					if replace_local_variables:
						self.pop()
			else:
				lastElement = metaScript(
					name=token,
					local_variables=local_variables.copy(),
					**element_params
				)
				lastElement.metadata = unit_metadata
				unit_metadata = {}
				for key in block_metadata:
					lastElement.metadata.setdefault(key,block_metadata[key])
				self.append(lastElement)
				next(tokens.cwtokens) # skip '='
				next(tokens.cwtokens) # skip '{'
				lastElement.parse(tokens)
		self.local_variables = local_variables
		return self

class scopeUnpackable(ABC):
	@abstractmethod
	def unpack(self,unpackTree:set|None=None) -> Iterator[str]:
		pass

vanilla_mod_object = Mod( mod_path = globalSettings['vanilla_path'], is_vanilla = True )

def set_vanilla_path(path):
	configure('vanilla_path',path)
	vanilla_mod_object.mod_path = path

class scopeSet(scopeUnpackable):
	def __init__(self,*args,locked=False) -> None:
		self.unpacked_scopes = set()
		self.pointers = []
		self.unpacked = True
		self.locked = False
		for item in args:
			self.add(item)
		self.locked = locked

	def add(self,item):
		if not self.locked:
			if isinstance(item,str):
				self.unpacked_scopes.add(item)
			if isinstance(item,scopeUnpackable) and not (item in self.pointers):
				self.pointers.append(item)
				self.unpacked = False

	def unpack(self,unpackTree:list[scopeUnpackable]|None=None) -> set[str]:
		if unpackTree is None:
			unpackTree = []
		unpackTree.append(self)
		for item in self.pointers:
			if not item in unpackTree:
				self.unpacked_scopes.update( item.unpack() )
		return self.unpacked_scopes

def toScopes(input) -> scopeSet:
	if isinstance(input,scopeSet):
		return input
	if isinstance(input,list):
		return scopeSet(*input)
	if isinstance(input,str):
		return scopeSet(input)

def eventTarget(key:str) -> scopeSet:
	event_targets = globalData['eventTargets']
	if '@' in key:
		key = key.split('@')[0]+'@'
	return event_targets.setdefault(key,scopeSet())

def decomposeChain(s:str) -> list[str]:
	return '.'.split(s.lower())

def isScopeChain(chain:list[str]) -> bool:
	for unit in chain:
		if ( not
		( unit in [ 'root','this','target', 'prev','prevprev','prevprevprev','prevprevprevprev','from','fromfrom','fromfromfrom','fromfromfromfrom', ] )
		or ( unit in globalSettings['scopeTransitions'] ) or ( unit.startswith('event_target:') )
		or ( unit.startswith('parameter:') ) ):
			return False
	return True

class scopesContext():
	def __init__(self,this=None,*args,froms=[],root=None,prev=None,lock=False) -> None:
		froms = list(args) + froms
		self.froms = [ toScopes(f) for f in froms ]
		while len(self.froms) < globalSettings['max_from_depth']:
			self.froms.append( scopeSet() )
		if root is None:
			self.root = self
		elif isinstance(root,scopesContext):
			self.root = root
		elif isinstance(root,str):
			self.root = scopesContext(root,froms=froms)
		if this is None:
			self.this = scopeSet()
		else:
			self.this = toScopes(this)
		if isinstance(prev,scopesContext):
			self.prev = prev
		elif isinstance(prev,list):
			if len(prev) > 0:
				self.prev = scopesContext(prev.pop(),root=self.root,froms=self.froms,prev=prev)
		if lock:
			self.this.locked = True

	def add(self,other:Self):
		self.this.add( other.this )
		for i in range(globalSettings['max_from_depth']):
			self.froms[i].add( other.froms[i] )

	def step(self,scope):
		return scopesContext(
			this=scope,
			root=self.root,
			froms=self.froms,
			prev=self,
		)

	def toFrom(self,count):
		froms = copy(self.froms)
		for i in range(count):
			if len(froms) < 1:
				maxFromDepth = globalSettings['max_from_depth']
				raise ShallowFromsException(f'Max from depth too low; set to {maxFromDepth}, tried to access from depth {maxFromDepth+count-i}')
			result = froms.pop(0)
		self.this = result
		self.froms = froms

	def link(self,commands:list[str]|str):
		if isinstance(commands,str):
			commands = decomposeChain(commands)
		context = copy(self)
		scopeTransitions = globalSettings['scopeTransitions']
		for command in commands:
			command = command.lower()
			if command == 'root':
				context = copy(context.root)
			elif command == 'prev':
				context = copy(context.prev)
			elif command == 'prevprev':
				context = copy(context.prev.prev)
			elif command == 'prevprevprev':
				context = copy(context.prev.prev.prev)
			elif command == 'prevprevprevprev':
				context = copy(context.prev.prev.prev.prev)
			elif command == 'from':
				context.toFrom(1)
			elif command == 'fromfrom':
				context.toFrom(2)
			elif command == 'fromfromfrom':
				context.toFrom(3)
			elif command == 'fromfromfromfrom':
				context.toFrom(4)
			elif command in scopeTransitions:
				context.this = scopeTransitions[command]
			elif command == 'target':
				context.this = '[TARGET]'
			elif command.startswith('event_target:'):
				key = command.split(':')[1]
				context.this = eventTarget(key)
			elif command.startswith('parameter:'):
				context.this = 'country'
		context.prev = self
		return context

	def firedContext(self):
		froms = [self.root.this] + copy(self.root.froms)
		froms.pop()
		return scopesContext(self.this,froms=froms)

	def unpackThis(self):
		return self.this.unpack()

def findEffectScopes(mods:list[Mod],criteria:Callable[[CWElement,scopesContext],bool]) -> list[tuple[CWElement,scopesContext]]:
	configure('expand_inlines',True)
	for mod in mods:
		configure('context_mod',mod)
		print(f'loading metascripts for mod {str(mod)}')
		mod.load_metascripts()
		print(f'loading events for mod {str(mod)}')
		mod.load_events()
		print(f'loading on_actions for mod {str(mod)}')
		mod.load_on_actions()

	print('applying hardcoded on_actions')
	hardcodedOnActions = globalSettings['hardcodedOnActions']
	for on_action in hardcodedOnActions:
		globalData['onActionScopes'][on_action].add(hardcodedOnActions[on_action])
	
	globalSettings['effectParseAdditionalSetup']()

	for mod in mods:
		configure('context_mod',mod)
		print(f'activating on_actions for mod {str(mod)}')
		mod.activate_on_actions()

	effectLocations = globalSettings['effectLocations']
	output_effects = []
	for mod in mods:
		configure('context_mod',mod)
		for folder in effectLocations:
			print(f'processing mod "{str(mod)}" folder "{folder}"')
			for (effectBlock,scopes) in mod.read_folder(folder).navigateByDict( effectLocations[folder] ):
				for effect in effectBlock.effectScopingRun(scopes,criteria):
					output_effects.append(effect)
		for event in mod.events():
			print(f'processing mod "{str(mod)}" events"')
			if event.hasSubelements():
				scopes = globalData['eventScopes'][event.getValue('id',evaluate=True)]
				for element in event.contents():
					if element.name in ['immediate','option','after','abort_effect']:
						for effect in effectBlock.effectScopingRun(scopes,criteria):
							output_effects.append(effect)
			else:
				print(f'namespace {event.value}')
		for (effectBlock,scopes) in globalSettings['additionalEffectBlocks'](mod):
			for effect in effectBlock.effectScopingRun(scopes,criteria):
				output_effects.append(effect)
	
	return output_effects