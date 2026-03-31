import datetime
import json
import os
import time
import glob
import traceback
import xmltodict
from il_supermarket_scarper.scrapper_runner import MainScrapperRunner


class Scrapper:
    def __init__(self):
        self.osherad_folder = '../databases/osherad_data'
        self.yohananof_folder = '../databases/yohananof_data'
        self.osherad_scan_count = 0
        self.yohananof_scan_count = 0

    def run_scraper_for_osher_ad(self):
        while True:
            try:
                start_time = datetime.datetime.now()
                print(f"Starting Osher Ad scraper, date and time: {datetime.datetime.now()}")
                scraper = MainScrapperRunner(enabled_scrapers=["OSHER_AD"], dump_folder_name=self.osherad_folder,
                                             lookup_in_db=True)
                scraper.run(limit=None, files_types=None, when_date="latest", suppress_exception=False)
                self.osherad_scan_count += 1
                print(
                    f"Osher Ad scraper scan {self.osherad_scan_count} completed successfully. "
                    f"sleeping for 2 hours.")

                liked_supermarkets = self.extract_liked_supermarkets("osherad")
                if not liked_supermarkets:
                    print("No liked supermarkets found for osherad in general_settings.json, skipping extraction.")
                    continue

                for supermarket in liked_supermarkets:
                    print(f"extracting data for Liked supermarket: {supermarket}")
                    full_prices_path = self.extract_full_prices(supermarket, self.osherad_folder,
                                                                supermarket_name="osherad")
                    if full_prices_path != "failed":
                        print(f"Full prices extracted for {supermarket}: {full_prices_path}")
                        self.parse_full_prices(full_prices_path=full_prices_path, branch=supermarket['StoreId'],
                                               name="osherad")
                        print(f"Full prices parsed for {supermarket['StoreId']}, branch: {supermarket['StoreName']}")

                        full_promos_path = self.extract_full_promos(supermarket, self.osherad_folder,
                                                                    supermarket_name="osherad")
                        if full_promos_path != "failed":
                            self.parse_full_promos(full_promos_path=full_promos_path, branch=supermarket['StoreId'],
                                                   name="osherad")
                        else:
                            print(f"Failed to extract full promos for {supermarket}, skipping.")
                            pass
                    else:
                        print(f"Failed to extract full prices for {supermarket}, skipping.")
                        pass

                end_time = datetime.datetime.now()
                print(f"Osher Ad scraper completed at {end_time}, total duration: {end_time - start_time}")
                time.sleep(7200)  # Sleep for 2 hours before the next run

            except Exception as e:
                print(f"Error in Osher Ad scraper: {e}\n {traceback.print_exc()}")
                end_time = datetime.datetime.now()
                print(f"Osher Ad scraper failed at {end_time}, total duration: {end_time - start_time}")
                time.sleep(600)  # Sleep for 10 minutes on error before retrying

    def run_scraper_for_yohananof(self):
        while True:
            try:
                start_time = datetime.datetime.now()
                print(f"Starting yohananof scraper, date and time: {datetime.datetime.now()}")
                scraper = MainScrapperRunner(enabled_scrapers=["YOHANANOF"], dump_folder_name=self.yohananof_folder,
                                             lookup_in_db=True)
                scraper.run(limit=None, files_types=None, when_date="latest", suppress_exception=False)
                self.yohananof_scan_count += 1
                print(
                    f"yohananof scraper scan {self.yohananof_scan_count} completed successfully. "
                    f"sleeping for 2 hours.")

                liked_supermarkets = self.extract_liked_supermarkets("yohananof")
                if not liked_supermarkets:
                    print("No liked supermarkets found for yohananof in general_settings.json, skipping extraction.")
                    continue

                for supermarket in liked_supermarkets:
                    print(f"extracting data for Liked supermarket: {supermarket}")
                    full_prices_path = self.extract_full_prices(supermarket, self.yohananof_folder,
                                                                supermarket_name="yohananof")
                    if full_prices_path != "failed":
                        print(f"Full prices extracted for {supermarket}: {full_prices_path}")
                        self.parse_full_prices(full_prices_path=full_prices_path, branch=supermarket['StoreId'],
                                               name="yohananof")
                        print(f"Full prices parsed for {supermarket['StoreId']}, branch: {supermarket['StoreName']}")

                        full_promos_path = self.extract_full_promos(supermarket, self.yohananof_folder,
                                                                    supermarket_name="yohananof")
                        if full_promos_path != "failed":
                            self.parse_full_promos(full_promos_path=full_promos_path, branch=supermarket['StoreId'],
                                                   name="yohananof")
                        else:
                            print(f"Failed to extract full promos for {supermarket}, skipping.")
                            pass
                    else:
                        print(f"Failed to extract full prices for {supermarket}, skipping.")
                        pass

                end_time = datetime.datetime.now()
                print(f"yohananof scraper completed at {end_time}, total duration: {end_time - start_time}")
                time.sleep(7200)  # Sleep for 2 hours before the next run

            except Exception as e:
                print(f"Error in yohananof scraper: {e}\n {traceback.print_exc()}")
                end_time = datetime.datetime.now()
                print(f"yohananof scraper failed at {end_time}, total duration: {end_time - start_time}")
                time.sleep(600)  # Sleep for 10 minutes on error before retrying

    def extract_liked_supermarkets(self, supermarket_name_in_liked):
        """ extracts liked supermarkets from the ../databases/general_settingsjson database """
        try:
            with open('../databases/general_settings.json', 'r', encoding='utf-8') as file:
                general_settings = json.load(file)
            liked_supermarkets = general_settings['supermarkets']["liked"]
            if not liked_supermarkets:
                print("No liked supermarkets found in general_settings.json")
                return []
            # Filter liked supermarkets based on the provided name
            if supermarket_name_in_liked in liked_supermarkets.keys():
                liked_supermarkets = liked_supermarkets[supermarket_name_in_liked]
                return liked_supermarkets
            else:
                print(f"No liked supermarkets found for {supermarket_name_in_liked} in general_settings.json")
                return "failed"
        except Exception as e:
            print(f"Error reading general_settings.json: {e}\n{traceback.print_exc()}")
            return "failed"

    def extract_full_prices(self, supermarket, data_folder, supermarket_name):
        print(f"Extracting prices and promotions for supermarket:{supermarket_name}, StoreId: {supermarket['StoreId']}")
        try:
            folder_name = f"{data_folder}/{supermarket_name.capitalize()}"
            if not os.path.exists(folder_name):
                print(f"Folder {folder_name} does not exist. Skipping extraction for {supermarket_name}.")
                return "failed"

            files = [f for f in os.listdir(folder_name) if
                     f.lower().startswith("pricefull") and str(supermarket['StoreId']) in f and f.endswith(".xml")]

            if not files:
                print(f"No pricefull files found for StoreId {supermarket['StoreId']} in {folder_name}.")
                return "failed"

            if len(files) > 1:
                most_updated_file_path = max(files, key=lambda f: int(f.split('-')[-1].split('.')[0]))
            else:
                most_updated_file_path = files[0]

            most_updated_file_path = os.path.join(folder_name, most_updated_file_path)
            print(f"Most updated price file found: {most_updated_file_path}")

            return most_updated_file_path
        except Exception as e:
            print(f"Error extracting prices: {e}\n{traceback.print_exc()}")
            return "failed"

    def extract_full_promos(self, supermarket, data_folder, supermarket_name):
        """ Extracts the most recent PromoFull XML file for a given supermarket and branch. """
        try:
            folder_name = f"{data_folder}/{supermarket_name.capitalize()}"
            if not os.path.exists(folder_name):
                print(f"Folder {folder_name} does not exist. Skipping extraction for {supermarket_name}.")
                return "failed"

            files = [f for f in os.listdir(folder_name) if
                     f.lower().startswith("promofull") and str(supermarket['StoreId']) in f and f.endswith(".xml")]

            if not files:
                print(f"No promofull files found for StoreId {supermarket['StoreId']} in {folder_name}.")
                return "failed"

            if len(files) > 1:
                most_updated_file_path = max(files, key=lambda f: int(f.split('-')[-1].split('.')[0]))
            else:
                most_updated_file_path = files[0]

            most_updated_file_path = os.path.join(folder_name, most_updated_file_path)
            print(f"Most updated promo file found: {most_updated_file_path}")
            return most_updated_file_path

        except Exception as e:
            print(f"Error extracting promos: {e}\n{traceback.print_exc()}")
            return "failed"

    def parse_full_prices(self, full_prices_path, branch, name):
        """ Parses the full prices XML file and extracts relevant data """
        try:
            time.sleep(1)
            print(f"Parsing full prices from {full_prices_path}")
            with open(full_prices_path, 'r', encoding='utf-8') as file:
                xml_content = file.read()

            special_branch_file = full_prices_path.split('/')[-1]
            special_branch_file = special_branch_file.split("-")[0] + "-" + special_branch_file.split("-")[1]
            special_branch_file = special_branch_file.replace("Full", "")
            print(f"searching for special branch file: {special_branch_file}")

            list_of_files = os.listdir(os.path.dirname(full_prices_path))
            full_special_paths = []
            for f in list_of_files:
                if special_branch_file in f and f.endswith(".xml") and "null" not in f.lower():
                    full_special_path = os.path.join(os.path.dirname(full_prices_path), f)
                    print(f"Found special branch file: {full_special_path}")
                    full_special_paths.append(full_special_path)

            data = xmltodict.parse(xml_content)
            json_data = json.dumps(data, indent=4, ensure_ascii=False)
            json_data = json.loads(json_data)

            if full_special_paths:
                print(f"Using special branch files: {full_special_paths}")
                codes = [item['ItemCode'] for item in json_data['Root']['Items']['Item']]
                counter = 0
                for full_special_path in full_special_paths:
                    with open(full_special_path, 'r', encoding='utf-8') as file:
                        special_data = file.read()
                        special_xml_content = xmltodict.parse(special_data)

                        if 'Root' in special_xml_content and 'Items' in special_xml_content['Root'] and 'Item' in \
                                special_xml_content['Root']['Items']:
                            items_to_add = special_xml_content['Root']['Items']['Item']
                            if not isinstance(items_to_add, list):
                                items_to_add = [items_to_add]

                            for item in items_to_add:
                                if item['ItemCode'] not in codes:
                                    json_data['Root']['Items']['Item'].append(item)
                                    codes.append(item['ItemCode'])
                                    counter += 1
                                else:
                                    print(f"Item {item['ItemCode']} already exists in full prices data, skipping.")
                print(f"Added {counter} special items to the full prices data.")

            json_data['supermarket_name'] = name
            json_data['total_items'] = len(json_data['Root']['Items']['Item'])
            print(f"Total items found: {json_data['total_items']}")

            output_folder = "../databases/liked_supermarkets_parsed_prices"
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            json_file_path = os.path.join(output_folder, f"{name}_{branch}_full_prices.json")
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, indent=4, ensure_ascii=False)
            print(f"Successfully parsed full prices from {full_prices_path}")
        except Exception as e:
            print(f"Error parsing full prices: {e}\n {traceback.print_exc()}")

    def parse_full_promos(self, full_promos_path, branch, name):
        """
        Parses the full promos XML file and updates the full_price file with promo objects.
        """
        try:
            time.sleep(1)

            if not os.path.exists(full_promos_path):
                print(f"Promo file not found at {full_promos_path}. Cannot link promos.")
                return

            print(f"Parsing full promos from: {full_promos_path}")

            with open(full_promos_path, 'r', encoding='utf-8') as file:
                xml_content = file.read()

            data = xmltodict.parse(xml_content)
            json_data = json.dumps(data, indent=4, ensure_ascii=False)
            promos_dict = json.loads(json_data)

            promos_by_item_code = {}
            if 'Root' in promos_dict and 'Promotions' in promos_dict['Root'] and 'Promotion' in \
                    promos_dict['Root']['Promotions']:
                promo_list = promos_dict['Root']['Promotions']['Promotion']
                if not isinstance(promo_list, list):
                    promo_list = [promo_list]

                for promo in promo_list:
                    promo_data = {
                        'PromotionId': promo.get('PromotionId'),
                        'PromotionDescription': promo.get('PromotionDescription'),
                        'PromotionUpdateDate': promo.get('PromotionUpdateDate'),
                        'PromotionEndDate': promo.get('PromotionEndDate'),
                        'MinQty': promo.get('MinQty'),
                        'DiscountedPrice': promo.get('DiscountedPrice'),
                        'DiscountedPricePerMida': promo.get('DiscountedPricePerMida'),
                    }

                    promo_items = promo.get('PromotionItems')
                    if promo_items and 'Item' in promo_items:
                        promo_item_list = promo_items.get('Item')
                        if not isinstance(promo_item_list, list):
                            promo_item_list = [promo_item_list]

                        for item in promo_item_list:
                            item_code = item.get('ItemCode')
                            if item_code:
                                promos_by_item_code[item_code] = promo_data

            parsed_prices_folder = "../databases/liked_supermarkets_parsed_prices"
            prices_json_path = os.path.join(parsed_prices_folder, f"{name}_{branch}_full_prices.json")

            if not os.path.exists(prices_json_path):
                print(f"Prices JSON file not found at {prices_json_path}. Cannot link promos.")
                return

            with open(prices_json_path, 'r', encoding='utf-8') as json_file:
                prices_data = json.load(json_file)

            promo_counter = 0
            if 'Root' in prices_data and 'Items' in prices_data['Root'] and 'Item' in prices_data['Root']['Items']:
                items_list = prices_data['Root']['Items']['Item']
                if not isinstance(items_list, list):
                    items_list = [items_list]

                for item in items_list:
                    item_code = item.get('ItemCode')
                    if item_code and item_code in promos_by_item_code:
                        item['promo'] = promos_by_item_code[item_code]
                        promo_counter += 1

                prices_data['total_items_with_promos'] = promo_counter

            with open(prices_json_path, 'w', encoding='utf-8') as json_file:
                json.dump(prices_data, json_file, indent=4, ensure_ascii=False)

            print(
                f"Successfully parsed promos from {full_promos_path} and updated {promo_counter} items in {prices_json_path}.")

        except Exception as e:
            print(f"Error parsing full promos: {e}\n{traceback.print_exc()}")


if __name__ == '__main__':
    try:
        scrap = Scrapper()
        scrap.run_scraper_for_osher_ad()
        scrap.run_scraper_for_yohananof()
        # You can test the individual functions with the correct file paths
        # scrap.parse_full_prices("../databases/yohananof_data/Yohananof/PriceFull7290803800003-007-202509190010.xml",
        #                         "007", "yohananof")
        # scrap.parse_full_promos("../databases/yohananof_data/Yohananof/PromoFull7290803800003-007-202509190010.xml",
        #                         "007", "yohananof")
    except Exception as e:
        print(f"scraper failed: {e}\n{traceback.print_exc()}")