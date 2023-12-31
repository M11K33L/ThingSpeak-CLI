from src.utils import Utils
from colorama import Fore

class ThingSpeak:
    def __init__(self, user_apy_key):
        self.user_apy_key = user_apy_key
        self.hayCanales = False
        self.get_account_info()


    # Method to print the overall information of a channel
    def print_channel_index(self, channels):
        Utils.clear()
        indexes = {}
        cont = 1
        print("Nº\t\t\tID\t\t\tCHANNEL NAME")
        print("- \t\t\t--\t\t\t------------")
        for c in channels:
            print(str(cont) + "\t\t\t" + str(c['id']) + "\t\t\t" + c['name'] + "\n")
            indexes[str(cont)] = c
            cont += 1
        return indexes


    # Method to obtain all the channels from the logged account
    def get_account_info(self):
        req = self.get_channels_list()

        channels = req.json()
        channel_number = len(req.json())

        if req.status_code == 200 and channel_number is not 0:
            self.hayCanales = True

            public_channels = []
            private_channels = []

            for c in req.json():
                if c['public_flag']:
                    public_channels.append(c)
                else:
                    private_channels.append(c)

            self.len_all_channels = channel_number
            self.channel_names = self.get_channel_names(channels)
            self.all_channels = channels
            self.len_public_channels = len(public_channels)
            self.public_channels = public_channels
            self.len_private_channels = len(private_channels)
            self.private_channels = private_channels
        else:
            self.hayCanales = False


    # Method get all the channel names
    def get_channel_names(self, channels_json):
        channel_names = []
        for i in channels_json:
            channel_names.append(str(i['name']))
        return channel_names


    # Method to get the channel name giving the index
    def get_channel_name(self, index):
        if index is not 0:
            index -= 1
        for i in range(len(self.channel_names)):
            if i == index:
                return self.channel_names[i]


    # Method to know how many private and public channels there are
    def get_channels_length(self):
        return len(self.get_channels_list().json())


    # Method to get the list of all existing channels
    def get_channels_list(self):
        req = Utils.make_request(method="GET",
                                url=f"https://api.thingspeak.com/channels.json?api_key={self.user_apy_key}")
        return req


    # Method to know how many public channels are there
    def get_public_channels_length(self):
        return len(self.get_public_channels().json())


    # Method to get the list of all public channels
    def get_public_channels(self):
        req = Utils.make_request(method="GET",
                                url="https://api.thingspeak.com/users/mwa0000031155118/channels.json")
        return req


    # Method to obtain all private channels
    def get_private_channels(self):
        pass


    # Metodo para obtener los objetos json de los canales a partir de la lista
    def get_channels_json(self, list):
        pass


    @staticmethod
    # Method to retrieve the settings of a channel giving the id
    def get_channel_settings(id, user_api_key):
        req = Utils.make_request(method="GET",
                                url=f"https://api.thingspeak.com/channels/{id}.json?api_key={user_api_key}")
        return req


    # Method to remove a channel
    @staticmethod
    def remove_channel(id, user_api_key):
        body = {"api_key": user_api_key}
        req = Utils.make_request(method="DELETE", url=f"https://api.thingspeak.com/channels/{id}.json", json=body)
        return req


    # Method to create a channel
    @staticmethod
    def create_channel(user_api_key):
        Utils.clear()
        name = str(input("Enter the new channel name: "))
        public_flag = str(input("Enter the public flag of the channel. [True] to make it public. [False] to make it private: "))
        
        # ADD SOME MORE PROMPTS INPUT TO CREATE THE CHENNELS WITH CUSTOM INFO

        if public_flag.__eq__('True') or public_flag.__eq__('False'):
        
            body = {"api_key": user_api_key, 'id': 2299146, 'name': f'{name}',
                    'description': 'Esta es la descripcion del canal 1',
                    'latitude': '0.0', 'longitude': '0.0', 'created_at': '2023-10-10T19:58:50Z', 'elevation': '',
                    'last_entry_id': None, 'public_flag': public_flag, 'url': None, 'ranking': 50, 'metadata': '',
                    'license_id': 0, 'github_url': None, 'tags': [], 'api_keys': [{'api_key': 'ZCRD02RYHN5Y8CXT',
                                                                                'write_flag': True},
                                                                                {'api_key': '97NQ78KHK1PK7RP7',
                                                                                'write_flag': False}]}

            r = Utils.make_request(method="POST", url="https://api.thingspeak.com/channels.json", json=body)
            Utils.give_response(message=f'New channel [{name}] created', clear=True, status=r.status_code)
        else:
            Utils.clear()
            print('Make sure to enter [True/False] in the public flag field.')
            Utils.wait(3)

    
    # Method to update information of the channel
    @staticmethod
    def update_channel_information(channel_id, updated_information):
        update_channel_information_url = f"https://api.thingspeak.com/channels/{channel_id}.json"
        return Utils.make_request(method="PUT", url=update_channel_information_url, json=updated_information)


    # Method to retrieve a channel fields
    @staticmethod
    def get_channel_fields(channel_id, api_key):
        return Utils.make_request(method="GET",
                                url=f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={api_key}")


    # Method to create only one field
    @staticmethod
    def create_one_field_for_channel(new_field_name, channel_id):
        return Utils.make_request(method="put", url=f"https://api.thingspeak.com/channels/{channel_id}.json",
                                json=new_field_name)


    # Method to clear all data from a given field
    @staticmethod
    def clear_data_from_all_fields(channel_id, api_key):
        url_clear_field = f'https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={api_key}'
        # params = {'api_key': write_api_key}
        return Utils.make_request(method="DELETE", url=url_clear_field)


    # Method to make de http request to get the feeds of giving channel
    @staticmethod
    def get_feeds_from_field(channel_id, field_index, read_api_key):
        url_read_data_field = f"https://api.thingspeak.com/channels/{channel_id}/fields/{field_index}.json?results=100&api_key={read_api_key}"
        return Utils.make_request(method="GET", url=url_read_data_field)


    # Method to make get http request to upload the data from a csv
    @staticmethod
    def upload_data_from_csv_file(channel_id, body):
        url_bulk_csv = f'https://api.thingspeak.com/channels/{channel_id}/bulk_update.csv'
        return Utils.make_request(method="POST", url=url_bulk_csv, data=body)