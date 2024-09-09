import os.path
import sys
import xml.etree.ElementTree as ET
import re
from xml.dom import minidom

target_root = ""

# a key in a mappings is an entry in VS style,
# values assigned to it are entries in a Qt Creator style description
mappings = {
    "Comment": ["Comment", "Doxygen.Comment"],
    "Plain Text": ["Text", "Parameter", "Local", "Field", "Label"],
    "Selected Text": "Selection",
    "Brace Matching (Rectangle)": "Parentheses",
    "class name": "Type",
    "Number": ["Number", "Function"],
    "Operator": "Operator",
    "String": "String",
    "String(C# @ Verbatim)": "",
    "urlformat": "",
    "User Types": ["PrimitiveType", "Overloaded Operator"],
    "enum name": ["Static"],
    "interface name": [],
    "delegate name": "",
    "struct name": "",
    "Indicator Margin": "",
    "Line Numbers": "LineNumber",
    "Preprocessor Keyword": "Preprocessor",
    "Keyword": "Keyword",
    "XML Doc Comment": "",
    "XML Doc Tag": "",
    "CSS Comment": "",
    "CSS Keyword": "",
    "CSS Property Name": "",
    "CSS Property Value": "",
    "CSS Selector": "",
    "CSS String Value": "",
    "HTML Attribute": "",
    "HTML Attribute Value": "Link",
    "HTML Comment": "",
    "HTML Element Name": "",
    "HTML Entity": "",
    "HTML Operator": "",
    "HTML Server-Side Script": "",
    "HTML Tag Delimiter": "",
    "Razor Code": "",
    "Script Comment": "",
    "Script Identifier": ["JsScopeVar", "JsImportVar", "JsGlobalVar"],
    "Script Keyword": "",
    "Script Number": "",
    "Script Operator": "",
    "Script String": "",
    "XML Attribute": ["QmlLocalId", "QmlExternalId", "QmlTypeId"],
    "XML Attribute Quotes": "",
    "XML Attribute Value": "",
    "XML CData Section": "",
    "XML Comment": "",
    "XML Delimiter": "",
    "XML Name": ["QmlRootObjectProperty", "QmlScopeObjectProperty", "QmlExternalObjectProperty"],
    "XML Text": "",
    "XAML Attribute": "",
    "XAML Attribute Quotes": "",
    "XAML Attribute Value": "",
    "XAML CData Section": "",
    "XAML Comment": "",
    "XAML Delimiter": "",
    "XAML Markup Extension Class": "",
    "XAML Markup Extension Parameter Name": "",
    "XAML Markup Extension Parameter Value": "",
    "XAML Name": "",
    "XAML Text": "",
    "Inactive Selected Text": "",
    "outlining.square": "",
    "outlining.verticalrule": "",
    "Syntax Error": "Error",
    "Warning": "Warning",
    "outlining.collapsehintadornment": "",
    "Collapsible Text": "",
    "Excluded Code": "DisabledCode",
    "MarkerFormatDefinition/HighlightedReference": "",
    "CurrentLineActiveFormat": "CurrentLine",
    "CurrentLineInactiveFormat": "",
}


def map_element(child_element: ET.Element, mapping: str, output_element: ET.Element):
    """
    Converts an XML element of VS theme into a QtCreator color syntax entry
    :param child_element: source element, looks like <Item Name="Plain Text" Foreground="0x02000000" Background="0x00F8F8F8" BoldFont="No"/>
    :param mapping: an internal element of a jagged array, describing name relations
    :param output_element: QtCreator's theme root element, <style-scheme>
    :return: None
    """
    foreground = child_element.attrib.get("Foreground")
    background = child_element.attrib.get("Background")
    target_name = mapping
    sub_element = ET.SubElement(output_element, "style", {
        "name": target_name,
        "foreground": map_color(foreground)
    })
    if background != "0x02000000":
        sub_element.attrib["background"] = map_color(background)


def parse_color(source: str) -> [int]:
    """
    Converts string color representation into a byte array
    :param source: string like "0xAABBCCDD" or "AABBCCDD"
    :return: array of integers
    """
    result = []
    if source.startswith("0x"):
        i = 2
    else:
        i = 0
    while i + 2 <= len(source):
        segment = source[i: i + 2]
        result.append(int(segment, 16))
        i = i + 2
    return result


def convert_color(source: [int]) -> str:
    """
    Converts a byte array in a hexadecimal string
    """
    ints = map(lambda f: "{:02X}".format(f), source)
    return "".join(ints)


def map_color(input_color: str) -> str:
    """
    Transforms color string from Visual Studio's ABGR to
    QtCreator's ARGB. Example:
    0x0033FF9E -> #009EFF33
    """
    arr = parse_color(input_color)
    r0 = arr[3]
    g0 = arr[2]
    b0 = arr[1]
    return "#" + convert_color([r0, g0, b0])


def usage():
    print("Usage: main.py [file|directory]")


def process_file(input_file: str):
    print(f"Processing: {input_file}")
    tree = ET.parse(input_file)
    root = tree.getroot()

    output = ET.fromstring("<style-scheme version=\"1.0\"></style-scheme>")

    output_file_name = os.path.basename(input_file)
    output_file_name, _ = os.path.splitext(output_file_name)
    output.attrib["name"] = output_file_name
    output_file_name = os.path.join(target_root, output_file_name + ".xml")

    # iterate via Item elements
    for child in root.findall(".//Item"):
        source_name = child.attrib.get("Name")
        if source_name not in mappings.keys():
            continue
        if type(mappings[source_name]).__name__ == "list":
            for element in mappings[source_name]:
                map_element(child, element, output)
            continue
        if len(mappings[source_name]) != 0:
            map_element(child, mappings[source_name], output)

    binary_buf = ET.tostring(output) # binary
    string_buf = binary_buf.decode("utf-8")
    string_buf = re.sub('\s+(?=<)', '', string_buf)
    pretty_binary = minidom.parseString(string_buf).toprettyxml(indent="\t", encoding = "utf-8")
    with open(output_file_name, "wb") as f:
        f.write(pretty_binary)
        f.flush()
        f.close()


def main():
    global target_root

    if len(sys.argv) <= 1:
        usage()
        exit(0)

    # TODO: Linux support
    app_data = os.environ.get("APPDATA")
    target_root = os.path.join(app_data, "QtProject/qtcreator/styles")
    print(f"Saving to: {target_root}")
    os.makedirs(target_root, exist_ok=True)

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        i = i + 1
        if os.path.isfile(arg):
            process_file(arg)
        else:
            files = [f for f in os.listdir(arg)]
            for file in files:
                if file.endswith(".vssettings"):
                    process_file(os.path.join(arg, file))


if __name__ == "__main__":
    main()
