from calendar import c
from utils.exceptions import DuplicatedAttribute, MissedMandatoryAttributes, \
    UnknownProperties, ErrorFileFormat, MissedMandatoryProperties
from data.structures import CompilerConfig, LanguageConfig, BuildConfig

from utils.constants import *
from utils.regex_patterns import RE_ATTRIBUTES, RE_VALID_LINE_FORMAT

import re


def get_project_config(root_path: str) -> dict:
    """Parses the file looking for a kind of AST token tokens"""

    # Open the configuration file in 'read-only' mode
    config_file = read_config_file_lines(root_path)

    # Check if the config file format it's valid
    check_valid_config_file(config_file)

    # If the config file it's OK, the we can retrieve all the config sections
    return get_sections(config_file)



def read_config_file_lines(root_path: str) -> list:
    """ Get all the lines written in the conf file """
    with open(root_path + '/' + CONFIGURATION_FILE_NAME, 'r') as config_file:
        return config_file.readlines()


def check_valid_config_file(config_file: list):
    """ # TODO """
    # Parses the file to check if it's valid
    for idx, line in enumerate(config_file):
        line = line.strip()

        if line and not re.match(RE_VALID_LINE_FORMAT, line):
            raise ErrorFileFormat(idx + 1, line)


def clean_file(file: str) -> list:
    """Clean the file and retrieve only lines with attribute or property format"""
    # Pattern to retrieve all lines who are attributes [[#attr]] or properties
    valid_lines_pattern = r"^\[\[#\w+]]$|^\w+: ?.+"
    return re.findall(
            valid_lines_pattern, file, re.MULTILINE
        )


def parse_attr_properties_block(file: str) -> dict:
    block_pattern = r"^\[\[#\w+]]\n(?:^\w+: ?.+\n?)+"
    blocks = re.findall(block_pattern, file, re.MULTILINE)

    retrieved_data = {}

    for block in blocks:
        attr_pattern = r"^\[\[#(\w+)]]"
        property_pattern = r"^(.+): (.+)$"

        attribute_identifier = re.search(attr_pattern, block).group(0)
        extracted_properties = re.findall(property_pattern, block, re.MULTILINE)

        properties: list = []
        for property_name, property_value in extracted_properties:
            properties.append(
                {"property_name": property_name,
                 "property_value": property_value
                }
            )

        retrieved_data[attribute_identifier] = properties

    return retrieved_data


def get_sections(config_file: str) -> dict:
    """ Recovers the sections described in the config file, returning a dict with 
        the instances of the dataclasses designed for carry the final data 
        to the compiler """

    # Initializes the map with the config values and provide default values
    config: dict = {
        'compiler' : CompilerConfig('clang'),
        'language' : LanguageConfig(20, 'libstdc++'),
        'build' : BuildConfig('./build')
    }

    cleaned_config_file: list = clean_file("".join(config_file))
    attr_ppt_collection = parse_attr_properties_block('\n'.join(cleaned_config_file))

    """ 
        Once we have parsed and cleaned the sections founded on the config file, we can 
        start match them against the valid ones (the ones allowed by Zork).
        Until here, we only validated that the code written on the conf file it's
        syntanctically correct acording the rules provided by the program. 
        Now we must discover if the retrived data it's also available and exists
        inside Zork.
    """

    # # For every attribute and property founded in the config file, now stored as a 
    # # dict with the attribute name as a key and the properties as an inner dict
    # for attribute, ppt_list in attr_ppt_collection.items():
    #     for section in PROGRAM_SECTIONS: # For every section available on the program
    #         if section.identifier == attribute:
    #             # Then we found a valid whole section to serialize into the dataclasses.
    #             # Remove the '[[#' and ']' from the name, to match it against the dict
    #             # that holds the instances of the configuration classes
    #             print('\nSection: ' +  attribute)
    #             attr_identifier = attribute[3:-2]
    #             # Now matches the available properties of the current attribute on the loop
    #             # against the retrieved ones in the current 'attribute' instace
    #             for property in ppt_list: # For every property discovered on the conf file
    #                 # For every property available in the program for the current section
    #                 for designed_ppt in section.properties: # Properties instance
    #                     designed_ppt_identifier = designed_ppt.as_dict()['identifier']

    #                     if designed_ppt_identifier == property["property_name"]:
    #                         print(f'PROPERTIES in config file: {property}')
    #                         print(f'MATCH. Value: {property["property_value"]}')
    #                         # Kind of templating metaprogramming, taking advantage of
    #                         # the Python's duck typing system, due to the lack of real 
    #                         # generic programming tools
    #                         config[attr_identifier].set_property(property["property_name"], property["property_value"])


    # Tracks the mandatory attributes not written in the config file
    missed_mandatory_attributes: list = []

    print('\n')
    for section in PROGRAM_SECTIONS:
        print(f'Program section: {section}')
        # Try to get the same property (if exists in the config file)
        # In this way, we can also check if all the mandatory attributes are
        # configured, and are valid ones

        # TODO Check for duplicates

        config_file_section_properties = attr_ppt_collection.get(section.identifier)

        # The logic for a valid founded property goes here
        if not config_file_section_properties == None:
            print(f'\tFinded properties: {config_file_section_properties}')

            missed_mandatory_properties: list = []
            invalid_properties_found: list = []

            # List with the program defined property identifiers for the current attribute
            program_defined_property_identifiers_for_current_attribute = [
                property.identifier for property in section.properties
            ]

            detected_properties_for_current_attribute = [
                ppt_identifier['property_name'] for ppt_identifier in config_file_section_properties
            ]

            # Check for mandatory properties for the current attribute
            for program_property in section.properties:
                if program_property.mandatory == True:
                    if not program_property.identifier in detected_properties_for_current_attribute:
                        missed_mandatory_properties.append(program_property.identifier)

            # If we have all the mandatory ones, unpack the founded properties to validate them
            for ppt_identifier in detected_properties_for_current_attribute:
                if not ppt_identifier in program_defined_property_identifiers_for_current_attribute:
                    invalid_properties_found.append(ppt_identifier)
            
            if len(missed_mandatory_properties) > 0:
                raise MissedMandatoryProperties(missed_mandatory_properties, section.identifier)
            if len(invalid_properties_found) > 0:
                raise UnknownProperties(invalid_properties_found, section.identifier)

            # If everything it's valid, we can fill our config dict with the data
            for validated_property in config_file_section_properties:
                config[section.identifier[3:-2]].set_property(
                    validated_property['property_name'], validated_property['property_value'] 
                )

                        
        else: 
            if section.mandatory == True:
                missed_mandatory_attributes.append(section.identifier)

    if len(missed_mandatory_attributes) > 0:
        raise MissedMandatoryAttributes(missed_mandatory_attributes)

    return config
