from src.utils import Utils
from src.thingspeak import ThingSpeak

import time
import psutil
from tabulate import tabulate
import re


class Field:

    def __init__(self, field_index, field_name, channel_id, write_key, read_key):
        self.field_index = field_index
        self.field_name = field_name
        self.channel_id = channel_id
        self.write_key = write_key
        self.read_key = read_key


    def update_date(self, index, name, data):
        self.index = index

    
    # Method to get the feeds from a field
    def get_data_from_field(self):
        res = ThingSpeak.get_feeds_from_field(self.channel_id, self.field_index, self.read_key)
        if res.status_code == 200:
            return res.json()['feeds']


    # Method to read data from a especific field
    def read_data_from_field(self):

        field_values = self.get_data_from_field()

        field_entries = []
        cont = 1
        for entri in field_values:
            value = entri[f'field{self.field_index}']
            if value is not None:
                e = []
                e.append(cont)
                datetime = Utils.format_date(entri['created_at'])
                date, time = datetime.split(" ")
                e.append(date)
                e.append(time)
                e.append(value)
                field_entries.append(e)
                cont += 1

        self.field_data_table = tabulate(field_entries, tablefmt="rounded_grid")


    def subir_datos(self):
        i = 0
        # print("Press q to stop de upload.")
        while i < 500:
            # if keyboard.is_pressed('q'):
            #     break
            cpu = psutil.cpu_percent()  # USO DE LA CPU
            vm = psutil.virtual_memory()
            ram = vm.percent  # USO DE LA RAM

            self.mostrar_recursos_hardware(cpu, ram, size=30)
            i += 1
            time.sleep(0.5)
            Utils.make_request(method="post", url="https://api.thingspeak.com/update.json", json={
                "api_key": self.write_key,
                "field" + self.field_index: cpu
            })


    def upload_csv(self):
        
        message = 'Upload csv file'
        path_file = str(input('Enter the csv file path: '))

        with open(path_file, 'r') as file:
            
            pattern = r"(\d+)[\s\,\|\-]+(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})[\s\,\|\-]+(\d+(\.\d+)?)"

            # striped_data = [word.strip().split('\t')[2] for word in file.readlines()]

            # Crear la cadena de actualización para ThingSpeak
            string_template = '0,,,,,,,,,,,,ok|'

            bulk_data = ""
            for index, row_data in enumerate(file):
                # print(row_data)
                # input(re.match(pattern, row_data))
                if re.match(pattern, row_data):
                    lista = string_template.split(',')
                    lista[0] = str(index)
                    lista[int(self.field_index)] = row_data.split('\t')[2].strip()
                    temp_template = ','.join(lista)

                    bulk_data += temp_template

            # Datos para enviar en la solicitud POST
            data_to_send = {
                'write_api_key': self.write_key,
                'time_format': 'absolute',
                'updates': bulk_data .rstrip('|')  # Eliminar el último carácter '|' para evitar problemas
            }

            r = ThingSpeak.upload_data_from_csv_file(self.channel_id, data_to_send)

            if r.status_code == 202:
                Utils.give_response(message=message, clear=True, status=202)
                return 'actualizar'
            else:
                Utils.give_response(message=message, clear=True, status=201)


    # GRAFICO TIMIDO para que se vea algo al subir los datos
    # Se podria implementar con un thread y meterle la actualizacion cada 2 segundos para que se vea mas real
    def mostrar_recursos_hardware(self, cpu, ram, size=50):
        cpu_p = (cpu / 100.0)
        cpu_carga = ">" * int(cpu_p * size) + "-" * (size - int(cpu_p * size))

        ram_p = (ram / 100.0)
        ram_carga = ">" * int(ram_p * size) + "-" * (size - int(ram_p * size))

        print(f"\rUSO DE LA CPU: |{cpu_carga}| {cpu:.2f}%", end="")
        print(f"\tUSO DE LA RAM: |{ram_carga}| {ram:.2f}%", end="\r")


    # Method to download the data of a given field
    # download filw formats
    #   .xlsx
    #   .cvs
    #   .txt
    def download_data(self):
        Utils.clear()
        file_name = str(input("Enter the file name: "))

        date_format = str(input('Select the date format: \n'\
            '1 -> 2018-06-14T12:12:22\n' \
            '2 -> 2018-06-14 12:12:22\n'
        ))

        format_options = {
            "1": Utils.create_xlsx,
            "2": Utils.create_csv,
            "3": Utils.create_txt
        }

        str_banner_choose_format = "Choose file format for downloading the data:\n\n" \
                    "1 -> xlsx\n" \
                    "2 -> csv\n" \
                    "3 -> txt\n"
        selected_option = Utils.endless_terminal(str_banner_choose_format, *list(format_options.keys()), clear=True)

        pattern = r"│\s*(\d+)\s*│\s*(\d{4}-\d{2}-\d{2})\s*│\s*(\d{2}:\d{2}:\d{2})\s*│\s*(\d+\.\d+)\s*│"
        coincidencias = re.findall(pattern, self.field_data_table)

        data = []
        for index, date, time, value in coincidencias:
            row = []
            row.append(index)
            if date_format == '1':
                row.append(date + 'T' + time)
            else:
                row.append(date)
                row.append(time)
            row.append(value)
            data.append(row)

        format_options[selected_option](data, file_name, self.field_index, date_format)


    # Method to clear all the data of the field
    def clear_field_data():
        pass


    # Method to delete the current field
    def delete_field():
        pass