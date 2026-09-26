"""Select saved design bodies from FreeCAD documents, excluding CAM tools."""
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET


def design_bodies(source):
    with zipfile.ZipFile(source) as archive:
        document = ET.fromstring(archive.read('Document.xml'))
        gui = ET.fromstring(archive.read('GuiDocument.xml'))
        types = {o.attrib['name']: o.attrib['type'] for o in document.findall('./Objects/Object')}
        data = {o.attrib['name']: o for o in document.findall('./ObjectData/Object')}
        visible = {v.attrib['name'] for v in gui.findall('.//ViewProvider')
                   if v.find(".//Property[@name='Visibility']/Bool[@value='true']") is not None}
        bodies = []
        for name, kind in types.items():
            if kind != 'PartDesign::Body':
                continue
            node = data[name]
            label = node.find("./Properties/Property[@name='Label']/String")
            label = label.attrib['value'] if label is not None else name
            if re.search(r'endmill|ballend|vbit|tool|stock', label, re.I):
                continue
            shape = node.find("./Properties/Property[@name='Shape']/Part")
            tip = node.find("./Properties/Property[@name='Tip']/Link")
            if shape is not None and shape.get('file') and tip is not None and tip.get('value'):
                bodies.append(name)
        # Bodies consumed by a design Boolean are already present in its result.
        consumed = set()
        for name, kind in types.items():
            if kind == 'PartDesign::Boolean':
                consumed.update(x.get('value') for x in data[name].findall("./Properties/Property[@name='Group']/LinkList/Link"))
        candidates = [name for name in bodies if name not in consumed]
        selected = [name for name in candidates if name in visible]
        if not selected and candidates:
            selected = candidates[:1]
        return selected
