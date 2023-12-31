from src.thingspeak import ThingSpeak
from src.utils import Utils
from src.canal import Channel
from src.field import Field

from colorama import Fore, init
import signal
import sys
import re

title = """
  ..... ..     ....              ...                     .                        .... .      ....  
    :   .. .    ..   ...   .... .:.    ....  ....  ...   :  ..                   :.    ..      :.   
    :   .. ..   ..  .: .: .. .:  ....  .  .. ^.... ...:  :..:        ....        ::    :.      :    
    .   .. .:  ..:. .. .: .:..:  . .: .:..:. :... .:..:. :...                    :.... :....  .:..   
                           ....       .:                                                            
                           ...
                                     by M11K33L         
"""

# u = Utils()
init()
help_tail = "\nEnter help to see available commands.\nEnter \"b\" to go backwards."


# Method to handle the exit of the program when ctrl + c is pressed
def signal_handler(signum=None, frame=None):
    # ctrl + c
    if signum == signal.SIGINT:
        Utils.clear()
        sys.exit(0)
    # ctrl + l
    # elif signum == signal.SIGINFO:
    #     Utils.clear()
    else:
        sys.exit(0)


# MORE SIGNALS
signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGINFO, signal_handler)


# Method to check the user-api-token
def checkUserApyKey(user_api_key):
    Utils.clear()
    init()
    req = Utils.make_request(method="GET",
                            url=f"https://api.thingspeak.com/channels.json?api_key={user_api_key}")

    if req.status_code == 200:
        return True
    elif req.status_code == 401:
        return False


# Method to login
def login():
    
    str_banner = "Enter your api key: "

    while True:
        user_api_key = Utils.endless_terminal(title + '\n\n\n' + str_banner, tty=False, clear=True)

        if checkUserApyKey(user_api_key):
            print(Fore.GREEN + "Successfull " + Fore.WHITE + "APY KEY provided.")
            Utils.wait_animation(1)
            main_menu(user_api_key)
        else:
            print(Fore.RED + "Wrong " + Fore.WHITE + "APY KEY provided.")
            Utils.wait_animation(1)


# Method to control de flow of a selected field
def field_menu(ts, channel, index, field_name):
    field = Field(index, field_name, channel.id, channel.write_api_key, channel.read_api_key)
    field.read_data_from_field()

    options_dict = {
        "upload": [field.subir_datos, "Upload data to the current field."],
        "upload csv": [field.upload_csv, "Upload the data of a csv file to the field."],
        "download data": [field.download_data, "Download the data from the current field to a file.(xlsx, txt, csv)"]
        # "clear field": field.clear_field_data, # LA API DE THINGSPEAK NO PROPORCIONA UNA RUTA PARA ESTO
        # "delete field": field.delete_field # LA API DE THINGSPEAK NO PROPORCIONA UNA RUTA PARA ESTO
    }
    
    while True:
        option = Utils.endless_terminal("FIELD DATA\n----------\n" + field.field_data_table + "\n" + help_tail, *list(options_dict.keys()), help_message=Utils.get_help_str_template(options_dict), menu=channel.channel_name, menu1=field_name, clear=True)
    
        if option == 'b':
            break

        field_operation = options_dict[option][0]()
        if field_operation == 'actualizar':
            field.read_data_from_field()


def fields_selector(ts, channel):
    pattern = re.compile(r"^[1-8]$")

    options_dict = {
        "create field": [channel.create_one_field, "Create a new field, up to 8 maximum."], # OK
        "rename field": [channel.rename_field_name, "Rename a field and give it a new name."], # OK
        "clear fields": [channel.clear_data_from_all_fields, "Clear all the data from all the fields."] # OK
        # "delete field": [channel.delete_one_field, # LA API DE THINGSPEAK NO PROPORCIONA UNA FORMA DE BORRA UN SOLO CANAL
        # "delete all fields": channel.delete_all_fields # LA API DE THINGSPEAK NO PROPORCIONA UNA FORMA DE BORRA UN SOLO CANAL
    }

    str_field_header = "CHANNEL FIELDS\n--------------"
    
    while True:
        o = channel.print_channel_fields()

        if o == 'b':
            break
        
        if o == 'refresh':
            continue

        valid_options = list(options_dict.keys()) + channel.valid_field_indexes

        field_menu_option = Utils.endless_terminal(channel.table_of_fields + "\n\nSelect a field by entering his index." + help_tail, *valid_options, help_message=Utils.get_help_str_template(options_dict, banner=str_field_header), menu=channel.channel_name)

        if field_menu_option == 'b':
            break

        # field has been selected
        if pattern.match(field_menu_option):
            field_menu(ts, channel, field_menu_option, channel.get_field_name(int(field_menu_option)))
            continue
        
        options_dict[field_menu_option][0]()


# Method to control the flow of a selected channel
# + Selecet a field
# + Remove the channel
def channel_menu(ts, user_api_key, i, indexes, channel_name):
    channel = Channel(user_api_key, i, indexes[i], channel_name)

    str_header = "CHANNEL PREVIEW\n---------------\n"

    str_channel_help = "\n\nCHANNEL OPTIONS\n" \
                            "---------------\n\n" \
                            "1 -- Channel information and settings\n\n" \
                            "2 -- Channel fields.\n\n" \
                            "3 -- Clear all channel data.\n\n" \
                            "4 -- Delete the channel.\n\n" \
                            "Select a option by entering his index.\n" \
                            "Enter \"b\" to go backwards"

    options_dict = {
        "1": channel.doNothing,
        "2": channel.get_channel_fields,
        "3": channel.clear_data_from_all_fields,
        "4": channel.delete_channel
    }

    update_menu_options_dict = {
        "more info": [channel.display_more_channel_info, "Keys of the channel"],
        "update info": [channel.update_channels_information, "Update a the channel information. Name, tags, etc..."]
    }

    str_info_header = "CHANNEL METADATA\n----------------"

    while True:

        option = Utils.endless_terminal(str_header + channel.create_channel_resume_table() + str_channel_help, *list(options_dict.keys()), menu=channel.channel_name, clear=True)

        if option == '1':
            
            more_info_table = ''
            this_help_tail = help_tail

            while True:

                if more_info_table:
                    this_help_tail = '\n'

                update_option = Utils.endless_terminal(channel.generate_channel_information_table() + "\n" + this_help_tail + more_info_table, 
                                                       *list(update_menu_options_dict.keys()),
                                                        help_message=Utils.get_help_str_template(update_menu_options_dict, banner=str_info_header), 
                                                        menu=channel.channel_name, clear=False)

                if update_option == 'b':
                    break

                more_info_table = update_menu_options_dict[update_option][0]()

        if option == 'b':
            break
        elif option == '2':
            fields_selector(ts, channel)
        
        channel_option = options_dict[option]()

        # Refresh
        if channel_option != 'n' and option == '3' or option == '4' and channel_option == 'reset':
            ts.get_account_info()
            break


# ThingSpeak menu Method
def main_menu(user_api_key):
    ts = ThingSpeak(user_api_key)

    str_banner = "1 -- PUBLIC CHANNELS.\n\n" \
                        "2 -- PRIVATE CHANNELS.\n\n" \
                        "3 -- ALL CHANNELS.\n\n" \
                        "4 -- Create a new channel.\n" \

    while True:
        if ts.hayCanales:

            option = Utils.endless_terminal(str_banner, "1", "2", "3", "4", clear="yes")

            if option.__eq__("b"):
                break

            if option == "1":
                indexes = ts.print_channel_index(ts.public_channels)
            elif option == "2":
                indexes = ts.print_channel_index(ts.private_channels)
            elif option == "3":
                indexes = ts.print_channel_index(ts.all_channels)
            elif option == "4":
                ts.create_channel(user_api_key)
                ts.get_account_info()
                continue

            i = Utils.endless_terminal("\nSelect a channel by entering his index.\nEnter \"b\" to go backwards.", *indexes.keys())

            if i.__eq__('b'):
                continue

            channel_menu(ts, user_api_key, i, indexes, ts.get_channel_name(int(i)))
        else:
            i = Utils.endless_terminal("You dont have any channels in this account.\nDo you want to create one? [y/n] ",
                                tty=False, clear=True)
            if i.__eq__("y"):
                ts.create_channel(user_api_key)
                ts.get_account_info()


if __name__ == '__main__':
    login()