from pathlib import Path
import yaml

class Identity:
    """
    A class representing a netrunner identity

    Attributes:
        name (str): Full proper name of the identity
        faction (str): Faction of the identity
        short_name (str): Short name of the identity
    """
    def __init__(self, reference: str = "no reference"):
        """
        Initializes a netrunner identity object (using identities.yml)

        Parameters:
            reference (str): can be the full name, short name, or common alternative spelling of the identity
        """
        self.name = "unknown"
        self.id_data = {}

        p = Path(__file__).with_name('identities.yml')
        with p.open('r') as identities_file:
            identities = yaml.safe_load(identities_file)

        if reference in identities.keys():
            self.name = reference
            self.id_data = identities[reference]
        else:
            for id_name,id_data in identities.items():
                if 'alt_names' in id_data and reference in id_data['alt_names']:
                    self.name = id_name
                    self.id_data = identities[id_name]
                    break
                if 'short_name' in id_data and reference == id_data['short_name']:
                    self.name = id_name
                    self.id_data = identities[id_name]
                    break

        self.faction = self.id_data.get('faction','unknown')
        self.short_name = self.id_data.get('short_name','unknown')

        if self.name == "unknown":
            print("could not find identity: "+str(reference))