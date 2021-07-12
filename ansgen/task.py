class Task:
    name = None
    properties = None

    def write(self, file, base_indent):
        if self.properties is not None:
            file.write(" "*base_indent + f"- name: {self.name}\n")
            for key, value in self.properties.items():
                file.write(" "*(base_indent+2) + f"{key}:")
                self.write_property(value, file, base_indent+4)

    def write_property(self, property, file, indent):
        if isinstance(property, list):
            file.write("\n")
            for item in property:
                file.write(" "*indent + f"- {item}\n")
        elif isinstance(property, dict):
            file.write("\n")
            for key, value in property.items():
                file.write(" "*indent + f"{key}:")
                self.write_property(value, file, indent+2)
        else:
            file.write(f" {property}\n")

    def __init__(self, name, properties: dict) -> None:
        self.name = name
        self.properties = properties
