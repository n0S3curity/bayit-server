import json
import os
import random
import pathlib


def create_db_files():
    # Create directories if they do not exist
    os.makedirs('../databases', exist_ok=True)
    filenames = ['products.json', 'stats.json', 'cities.json', 'suggestions.json', 'categories.json',
                 'general_settings.json']
    for name in filenames:
        filepath = f'../databases/{name}'
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                if name == 'suggestions.json':
                    # Initialize suggestions.json with an empty list
                    json.dump({"items": []}, f, indent=4)
                elif name == 'cities.json':
                    # Initialize cities.json with an empty dictionary
                    json.dump({
                        "אילת": "Eilat",
                        "אשדוד": "Ashdod",
                        "אשקלון": "Ashkelon",
                        "באר שבע": "Be'er Sheva",
                        "בני ברק": "Bnei Brak",
                        "בת ים": "Bat Yam",
                        "גבעתיים": "Givatayim",
                        "הוד השרון": "Hod HaSharon",
                        "הרצליה": "Herzliya",
                        "חדרה": "Hadera",
                        "חולון": "Holon",
                        "חיפה": "Haifa",
                        "ירושלים": "Jerusalem",
                        "כפר סבא": "Kfar Saba",
                        "לוד": "Lod",
                        "מודיעין": "Modi'in",
                        "נהריה": "Nahariya",
                        "נס ציונה": "Ness Ziona",
                        "נתניה": "Netanya",
                        "פתח תקווה": "Petah Tikva",
                        "ראש העין": "Rosh Haayin",
                        "ראשון לציון": "Rishon LeZion",
                        "רחובות": "Rehovot",
                        "רמת גן": "Ramat Gan",
                        "רעננה": "Ra'anana",
                        "שדרות": "Sderot",
                        "רמלה": "Ramla",
                        "טבריה": "Tiberias",
                        "טירת כרמל": "Tirat Carmel",
                        "יקנעם": "Yokneam",
                        "קריית גת": "Kiryat Gat",
                        "קריית שמונה": "Kiryat Shmona",
                        "אופקים": "Ofakim",
                        "אור יהודה": "Or Yehuda",
                        "אור עקיבא": "Or Akiva",
                        "אריאל": "Ariel",
                        "בית שאן": "Beit She'an",
                        "בית שמש": "Beit Shemesh",
                        "דימונה": "Dimona",
                        "זכרון יעקב": "Zichron Yaakov",
                        "טייבה": "Tayibe",
                        "יבנה": "Yavne",
                        "כפר קאסם": "Kafr Qasim",
                        "כרמיאל": "Karmiel",
                        "מעלה אדומים": "Ma'ale Adumim",
                        "מגדל העמק": "Migdal HaEmek",
                        "מצפה רמון": "Mitzpe Ramon",
                        "נצרת": "Nazareth",
                        "נשר": "Nesher",
                        "עכו": "Akko",
                        "עפולה": "Afula",
                        "צפת": "Safed",
                        "קריית אונו": "Kiryat Ono",
                        "קריית ביאליק": "Kiryat Bialik",
                        "קריית ים": "Kiryat Yam",
                        "קריית מוצקין": "Kiryat Motzkin",
                        "קריית מלאכי": "Kiryat Malakhi",
                        "שפרעם": "Shfaram",
                        "אבן יהודה": "Even Yehuda",
                        "אזור": "Azor",
                        "אלעד": "Elad",
                        "אליכין": "Elyakhin",
                        "אעבלין": "I'billin",
                        "גבעת שמואל": "Givat Shmuel",
                        "ג'סר א זרקא": "Jisr az Zarqa",
                        "ג'לג'וליה": "Jaljulya",
                        "כפר יונה": "Kfar Yona",
                        "כפר כנא": "Kafr Kanna",
                        "כפר מנדא": "Kafr Manda",
                        "כפר תבור": "Kfar Tavor",
                        "מזכרת בתיה": "Mazkeret Batya",
                        "מכבים": "Maccabim",
                        "מטולה": "Metula",
                        "מעלות תרשיחא": "Ma'alot Tarshiha",
                        "נחף": "Nahf",
                        "ערד": "Arad",
                        "עין מאיר": "Ein Meir",
                        "עספיא": "Isfiya",
                        "פרדס חנה כרכור": "Pardes Hanna Karkur",
                        "קדימה צורן": "Kadima Zoran",
                        "רמת השרון": "Ramat HaSharon",
                        "שדות ים": "Sdot Yam",
                        "תל מונד": "Tel Mond",
                        "בנימינה גבעת עדה": "Binyamina Giv'at Ada",
                        "ג'ת": "Jatt",
                        "חריש": "Harish",
                        "ירוחם": "Yeruham",
                        "להבים": "Lehavim",
                        "מג'דל שמס": "Majdal Shams",
                        "עתלית": "Atlit",
                        "פרדס יהודה": "Pardes Yehuda",
                        "צורן": "Zoran",
                        "שוהם": "Shoham",
                        "אורנית": "Oranit",
                        "אלפי מנשה": "Alfei Menashe",
                        "בית אל": "Beit El",
                        "ביתר עילית": "Beitar Illit",
                        "גבעת זאב": "Geva Binyamin",
                        "היישוב היהודי": "Jewish Quarter",
                        "הכפר הירוק": "Kfar HaYarok",
                        "הר אדר": "Har Adar",
                        "כפר אדומים": "Kfar Adumim",
                        "כפר ורדים": "Kfar Vradim",
                        "מבשרת ציון": "Mevasseret Zion",
                        "קצרין": "Katzrin",
                        "קרני שומרון": "Karnei Shomron",
                        "שערי תקווה": "Sha'arei Tikva",
                        "גוש עציון": "Gush Etzion",
                        "קרית ארבע": "Kiryat Arba"
                    }
                        , f, indent=4)
                elif name == 'general_settings.json':
                    # Initialize general_settings.json with default settings
                    json.dump({
                        "supermarkets": {
                            "liked": {
                                "yohananof": [],
                                "osherad": [
                                ]
                            },
                            "available": {
                                "osherad": [
                                    {
                                        "StoreId": 1,
                                        "BikoretNo": 6,
                                        "StoreType": 1,
                                        "StoreName": "מגדל העמק",
                                        "Address": "האיצטדיון 11",
                                        "City": "מגדל העמק",
                                        "ZipCode": "2303401"
                                    },
                                    {
                                        "StoreId": 3,
                                        "BikoretNo": 4,
                                        "StoreType": 1,
                                        "StoreName": "גבעת שאול",
                                        "Address": "בית הדפוס 29",
                                        "City": "ירושלים",
                                        "ZipCode": "9548334"
                                    },
                                    {
                                        "StoreId": 5,
                                        "BikoretNo": 2,
                                        "StoreType": 1,
                                        "StoreName": "קרית ביאליק",
                                        "Address": "הנס מולר 6, צור שלום",
                                        "City": "קרית ביאליק",
                                        "ZipCode": "2751206"
                                    },
                                    {
                                        "StoreId": 6,
                                        "BikoretNo": 1,
                                        "StoreType": 1,
                                        "StoreName": "כנות",
                                        "Address": "אדום 24 פארק התעשיות כנות",
                                        "City": "כנות",
                                        "ZipCode": "7982500"
                                    },
                                    {
                                        "StoreId": 9,
                                        "BikoretNo": 8,
                                        "StoreType": 1,
                                        "StoreName": "אשדוד",
                                        "Address": "בעלי המלאכה 4",
                                        "City": "אשדוד",
                                        "ZipCode": "7761205"
                                    },
                                    {
                                        "StoreId": 10,
                                        "BikoretNo": 4,
                                        "StoreType": 1,
                                        "StoreName": "פתח תקווה - סגולה",
                                        "Address": "בן ציון גליס 30",
                                        "City": "פתח תקווה",
                                        "ZipCode": "4927930"
                                    },
                                    {
                                        "StoreId": 11,
                                        "BikoretNo": 3,
                                        "StoreType": 1,
                                        "StoreName": "בני ברק",
                                        "Address": "הקישון 11",
                                        "City": "בני ברק",
                                        "ZipCode": "5120314"
                                    },
                                    {
                                        "StoreId": 13,
                                        "BikoretNo": 1,
                                        "StoreType": 1,
                                        "StoreName": "באר שבע",
                                        "Address": "הקוצר 15 אזור תעשיה עמק שרה",
                                        "City": "באר שבע",
                                        "ZipCode": "8480904"
                                    },
                                    {
                                        "StoreId": 14,
                                        "BikoretNo": 0,
                                        "StoreType": 1,
                                        "StoreName": "חדרה",
                                        "Address": "המסגר 22 אזה\"ת הצפוני",
                                        "City": "חדרה",
                                        "ZipCode": "3850169"
                                    },
                                    {
                                        "StoreId": 16,
                                        "BikoretNo": 8,
                                        "StoreType": 1,
                                        "StoreName": "בית שמש - גליל",
                                        "Address": "מורדי הגיטאות 6",
                                        "City": "בית שמש",
                                        "ZipCode": "9958206"
                                    },
                                    {
                                        "StoreId": 20,
                                        "BikoretNo": 1,
                                        "StoreType": 1,
                                        "StoreName": "לוד",
                                        "Address": "בת שבע 1 מתחם טלרד",
                                        "City": "לוד",
                                        "ZipCode": "7120101"
                                    },
                                    {
                                        "StoreId": 22,
                                        "BikoretNo": 9,
                                        "StoreType": 1,
                                        "StoreName": "אשקלון בת הדר",
                                        "Address": "בת הדר",
                                        "City": "אשקלון בת הדר",
                                        "ZipCode": "7910300"
                                    },
                                    {
                                        "StoreId": 23,
                                        "BikoretNo": 8,
                                        "StoreType": 1,
                                        "StoreName": "נתניה",
                                        "Address": "שדרות תום לנטוס",
                                        "City": "נתניה",
                                        "ZipCode": "4276019"
                                    },
                                    {
                                        "StoreId": 24,
                                        "BikoretNo": 7,
                                        "StoreType": 1,
                                        "StoreName": "תל אביב",
                                        "Address": "קרמינצקי 3",
                                        "City": "תל אביב",
                                        "ZipCode": "6789903"
                                    },
                                    {
                                        "StoreId": 25,
                                        "BikoretNo": 6,
                                        "StoreType": 1,
                                        "StoreName": "ראשון לציון",
                                        "Address": "אצל 26",
                                        "City": "ראשון לציון",
                                        "ZipCode": "7570630"
                                    },
                                    {
                                        "StoreId": 26,
                                        "BikoretNo": 5,
                                        "StoreType": 1,
                                        "StoreName": "תלפיות",
                                        "Address": "פייר קניג 26 קניון הדר",
                                        "City": "ירושלים",
                                        "ZipCode": "9346934"
                                    },
                                    {
                                        "StoreId": 28,
                                        "BikoretNo": 3,
                                        "StoreType": 1,
                                        "StoreName": "שמגר",
                                        "Address": "שמגר 16",
                                        "City": "ירושלים",
                                        "ZipCode": "9446116"
                                    },
                                    {
                                        "StoreId": 29,
                                        "BikoretNo": 2,
                                        "StoreType": 1,
                                        "StoreName": "קרית ים",
                                        "Address": "גולדה מאיר 2",
                                        "City": "קריית ים",
                                        "ZipCode": "2905737"
                                    },
                                    {
                                        "StoreId": 30,
                                        "BikoretNo": 8,
                                        "StoreType": 1,
                                        "StoreName": "חיפה",
                                        "Address": "דרך בר יהודה 31",
                                        "City": "חיפה",
                                        "ZipCode": "3262724"
                                    },
                                    {
                                        "StoreId": 31,
                                        "BikoretNo": 7,
                                        "StoreType": 1,
                                        "StoreName": "כפר סבא",
                                        "Address": "דרך הים 9",
                                        "City": "כפר סבא",
                                        "ZipCode": "4418001"
                                    },
                                    {
                                        "StoreId": 32,
                                        "BikoretNo": 6,
                                        "StoreType": 1,
                                        "StoreName": "קרית אונו",
                                        "Address": "שמירה אימבר גדיש 9",
                                        "City": "קרית אונו",
                                        "ZipCode": "5510101"
                                    }
                                ],
                                "yohananof": [
                                    {
                                        "StoreId": "001",
                                        "BikoretNo": 6,
                                        "StoreType": 1,
                                        "StoreName": "יוחננוף מפוח",
                                        "Address": "רחוב המפוח 11, אזור התעשיה",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "002",
                                        "BikoretNo": 5,
                                        "StoreType": 1,
                                        "StoreName": "יוחננוף ישן",
                                        "Address": "unknown",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "004",
                                        "BikoretNo": 3,
                                        "StoreType": 1,
                                        "StoreName": "בילו",
                                        "Address": "צומת ביל\"ו",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "005",
                                        "BikoretNo": 2,
                                        "StoreType": 1,
                                        "StoreName": "אשדוד",
                                        "Address": "זבוטינסקי 27, סטאר סנטר",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "007",
                                        "BikoretNo": 0,
                                        "StoreType": 1,
                                        "StoreName": "עקרון",
                                        "Address": "המלך חסן 1",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "008",
                                        "BikoretNo": 9,
                                        "StoreType": 1,
                                        "StoreName": "אחד העם",
                                        "Address": "רחוב אחד העם 19",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "009",
                                        "BikoretNo": 8,
                                        "StoreType": 1,
                                        "StoreName": "נתיבות",
                                        "Address": "רחוב בעלי המלאכה 2, א.התעשיה",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "012",
                                        "BikoretNo": 4,
                                        "StoreType": 1,
                                        "StoreName": "רמלה",
                                        "Address": "שדרות ירושלים פינת נופי חמד",
                                        "City": "רמלה",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "013",
                                        "BikoretNo": 3,
                                        "StoreType": 1,
                                        "StoreName": "חוצות המפרץ",
                                        "Address": "החרושת 10 חוצות המפרץ",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "015",
                                        "BikoretNo": 1,
                                        "StoreType": 1,
                                        "StoreName": "אור יהודה",
                                        "Address": "רחוב הפלדה 1",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "016",
                                        "BikoretNo": 0,
                                        "StoreType": 1,
                                        "StoreName": "גן יבנה",
                                        "Address": "דרך מנחם בגין פינת המגנים 57",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "017",
                                        "BikoretNo": 9,
                                        "StoreType": 1,
                                        "StoreName": "מודיעין ישפרו",
                                        "Address": "unknown",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "018",
                                        "BikoretNo": 8,
                                        "StoreType": 1,
                                        "StoreName": "מודיעין כרמים",
                                        "Address": "unknown",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "019",
                                        "BikoretNo": 7,
                                        "StoreType": 1,
                                        "StoreName": "אור יהודה גדול",
                                        "Address": "אור יהודה",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "020",
                                        "BikoretNo": 3,
                                        "StoreType": 1,
                                        "StoreName": "ירושלים תלפיות",
                                        "Address": "האומן",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "021",
                                        "BikoretNo": 2,
                                        "StoreType": 1,
                                        "StoreName": "סגולה פתח תקווה",
                                        "Address": "סגולה",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "022",
                                        "BikoretNo": 1,
                                        "StoreType": 1,
                                        "StoreName": "חדרה",
                                        "Address": "unknown",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "023",
                                        "BikoretNo": 0,
                                        "StoreType": 1,
                                        "StoreName": "טבריה",
                                        "Address": "unknown",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "024",
                                        "BikoretNo": 9,
                                        "StoreType": 1,
                                        "StoreName": "כפר סבא",
                                        "Address": "unknown",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "025",
                                        "BikoretNo": 8,
                                        "StoreType": 1,
                                        "StoreName": "נס ציונה",
                                        "Address": "נס ציונה",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "026",
                                        "BikoretNo": 7,
                                        "StoreType": 1,
                                        "StoreName": "רמת השרון",
                                        "Address": "unknown",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "027",
                                        "BikoretNo": 6,
                                        "StoreType": 1,
                                        "StoreName": "יד אליהו",
                                        "Address": "יגאל אלון 57",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "028",
                                        "BikoretNo": 5,
                                        "StoreType": 1,
                                        "StoreName": "ראשלצ רמת אליהו",
                                        "Address": "משורר השואה 15",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "029",
                                        "BikoretNo": 4,
                                        "StoreType": 1,
                                        "StoreName": "בת ים",
                                        "Address": "בת ים",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "030",
                                        "BikoretNo": 0,
                                        "StoreType": 1,
                                        "StoreName": "נתניה",
                                        "Address": "נתניה",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "031",
                                        "BikoretNo": 9,
                                        "StoreType": 1,
                                        "StoreName": "מרכז סנטרו רחובות",
                                        "Address": "רחובות",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "032",
                                        "BikoretNo": 8,
                                        "StoreType": 1,
                                        "StoreName": "בן צבי תל אביב",
                                        "Address": "unknown",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "033",
                                        "BikoretNo": 7,
                                        "StoreType": 1,
                                        "StoreName": "איירפורט סיטי",
                                        "Address": "unknown",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "034",
                                        "BikoretNo": 6,
                                        "StoreType": 1,
                                        "StoreName": "מבקיעים אשקלון",
                                        "Address": "מתחם גלובוס סנטר, מבקיעים",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "035",
                                        "BikoretNo": 5,
                                        "StoreType": 1,
                                        "StoreName": "תל אביב נחלת יצחק",
                                        "Address": "unknown",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "036",
                                        "BikoretNo": 4,
                                        "StoreType": 1,
                                        "StoreName": "חדרה צפוני",
                                        "Address": "unknown",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "037",
                                        "BikoretNo": 3,
                                        "StoreType": 1,
                                        "StoreName": "עפולה",
                                        "Address": "קהילת ציון 30",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "038",
                                        "BikoretNo": 2,
                                        "StoreType": 1,
                                        "StoreName": "טבריה תחתית",
                                        "Address": "יהודה הלוי 113",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "039",
                                        "BikoretNo": 1,
                                        "StoreType": 1,
                                        "StoreName": "קרית שמונה",
                                        "Address": "שדרות תל חי 93",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    },
                                    {
                                        "StoreId": "040",
                                        "BikoretNo": 7,
                                        "StoreType": 1,
                                        "StoreName": "באר שבע",
                                        "Address": "unknown",
                                        "City": "0",
                                        "ZipCode": "0000000"
                                    }
                                ]
                            }
                        }
                    }, f, indent=4)
                else:
                    json.dump({}, f, indent=4)


def add_to_suggestions(param):
    # Load existing suggestions from file
    suggestions_path = '../databases/suggestions.json'
    with open(suggestions_path, 'r', encoding='utf-8') as f:
        suggestions = json.load(f)

    # Add the new suggestion to "items" list
    if "items" not in suggestions:
        suggestions["items"] = []

    if param not in suggestions["items"]:
        suggestions["items"].append(param)
    # Save the updated suggestions back to file
    with open(suggestions_path, 'w', encoding='utf-8') as f:
        json.dump(suggestions, f, ensure_ascii=False, indent=4)
    print("Suggestion added successfully.")


def get_hebrew_city_name(city_name):
    with open('../databases/cities.json', 'r', encoding='utf-8') as f:
        hebrew_cities = json.load(f)
    # hebrew cities are the values of the dictionary, so we need to find the key that matches the city_name
    for hebrew_city, english_city in hebrew_cities.items():
        if english_city.lower() == city_name.lower():
            return hebrew_city
    # if no match is found, return the original city name
    return city_name


def generate_receipt_filename():
    # generate a random ID like asDFsadf-asd-f-sadf-w-afds-fsdfdsaf
    random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
    return f"receipt_{random_id}"


def calculate_top_10_price_increase(products):
    price_increases = []
    for barcode, product in products.items():
        if barcode == "901046":
            continue

        # Need at least 3 history entries: two previous purchases + the last purchase
        history = product.get('history', [])
        if len(history) < 3:
            continue

        # Get last purchase and two purchases before it
        last_raw = history[-1].get('price')
        prev1_raw = history[-2].get('price')
        prev2_raw = history[-3].get('price')

        # Convert to floats, skip invalid
        try:
            last_price = float(last_raw)
            prev1_price = float(prev1_raw)
            prev2_price = float(prev2_raw)
        except (TypeError, ValueError):
            continue

        avg_prev = (prev1_price + prev2_price) / 2.0
        if avg_prev > 0:
            increase_percent = ((last_price - avg_prev) / avg_prev) * 100
            if increase_percent > 0:
                price_increases.append({
                    "name": product.get('name', 'Unknown'),
                    "barcode": barcode,
                    "price_increase": increase_percent,
                    "old_price": avg_prev,
                    "new_price": last_price
                })

    return sorted(price_increases, key=lambda x: x['price_increase'], reverse=True)[:10]


def calculate_top_10_price_drop(products):
    price_drops = []
    for barcode, product in products.items():
        if barcode == "901046":
            # Skip the product with barcode "901046"
            continue

        # Need at least 3 history entries: two previous purchases + the last purchase
        history = product.get('history', [])
        if len(history) < 3:
            continue

        # Get the last purchase price and the two purchases before it
        last_raw = history[-1].get('price')
        prev1_raw = history[-2].get('price')
        prev2_raw = history[-3].get('price')

        # Convert to floats, skip if values are missing or invalid
        try:
            last_price = float(last_raw)
            prev1_price = float(prev1_raw)
            prev2_price = float(prev2_raw)
        except (TypeError, ValueError):
            continue

        avg_prev = (prev1_price + prev2_price) / 2.0

        # Only calculate if average of previous prices is > 0
        if avg_prev > 0:
            price_drop_percent = ((avg_prev - last_price) / avg_prev) * 100
            # Only include actual drops
            if price_drop_percent > 0:
                price_drops.append({
                    "name": product.get('name', 'Unknown'),
                    "barcode": barcode,
                    "price_drop": price_drop_percent,
                    "old_price": avg_prev,
                    "new_price": last_price
                })

    return sorted(price_drops, key=lambda x: x['price_drop'], reverse=True)[:10]



def generate_item_id():
    # generate id from 1000 to 9999 as int
    return random.randint(1000, 999999)


# --- Main function to process a single receipt file ---


def process_receipt_file(file_path):
    print(f"Processing receipt file: {file_path}")

    # Load the receipt content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            receipt_content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading receipt file {file_path}: {e}")
        return

    # Initialize empty databases if they don't exist
    products_db_path = '../databases/products.json'
    stats_db_path = '../databases/stats.json'

    if not os.path.exists(os.path.dirname(products_db_path)):
        os.makedirs(os.path.dirname(products_db_path))

    # Define a default stats dictionary to ensure all keys are present
    default_stats = {
        "total_receipts": 0,
        "total_spent": 0.0,
        "total_items": 0,
        "average_spend_per_receipt": 0.0,
        "top_10_product_purchased": [],
        "top_10_price_increase": [],
        "receipts": {}
    }
    stats = default_stats.copy()

    # Load existing stats from file, if it exists
    try:
        with open(stats_db_path, 'r', encoding='utf-8') as f:
            existing_stats = json.load(f)
        stats.update(existing_stats)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Load existing products from file, if it exists
    try:
        with open(products_db_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        products = {}  # Initialize as an empty dictionary

    date_and_time = receipt_content.get('createdDate', 'Unknown Date and Time').replace("T", " ")

    receipt_items = receipt_content.get('items', [])
    # pop out of the list the item that has barcode "901046" or name "מיחזור אריזה"
    receipt_items = [item for item in receipt_items if
                     item.get('code') != "901046" and item.get('name') != "מיחזור אריזה"]
    # Process each item in the receipt
    for item in receipt_items:
        barcode = item.get('code')
        product_name = item.get('name')
        price = item.get('price')
        quantity = item.get('quantity', 1)
        total = item.get('total')

        # Robust check to ensure all critical fields exist before conversion
        if not all([barcode, product_name, price is not None, quantity is not None, total is not None]):
            print(f"Skipping malformed item: {item}")
            continue

        # Convert to appropriate types
        try:
            price = float(price)
            quantity = int(quantity)
            total = float(total)
        except (ValueError, TypeError) as e:
            print(f"Skipping item due to invalid number format: {item}, Error: {e}")
            continue

        # Check if product exists in the products database
        if barcode in products:
            if barcode == "901046":
                # Skip the product with barcode "901046"
                continue
            # Update existing product
            product_data = products[barcode]
            product_data['favorite'] = False
            product_data['total_quantity'] = int(product_data.get('total_quantity', 0)) + quantity
            product_data['total_price'] = float(product_data.get('total_price', 0.0)) + total

            # Update price history and min/max prices
            current_price = price
            cheapest_price = float(product_data.get('cheapest_price', current_price))
            highest_price = float(product_data.get('highest_price', current_price))
            last_price = float(product_data.get('last_price', current_price))

            # Update price increase before setting new last price
            if cheapest_price > 0:
                product_data['price_increase'] = ((last_price - cheapest_price) / cheapest_price) * 100
            else:
                product_data['price_increase'] = 0.0

            product_data['last_price'] = current_price
            product_data['cheapest_price'] = min(cheapest_price, current_price)
            product_data['highest_price'] = max(highest_price, current_price)

            # Add to purchase history
            history = product_data.get('history', [])
            history.append({
                "date": date_and_time,
                "quantity": quantity,
                "price": price
            })
            product_data['history'] = history

            # calculate the average price
            product_data['average_price'] = product_data['total_price'] / product_data['total_quantity']


        else:
            if barcode == "901046":
                # Skip the product with barcode "901046"
                continue
            # Add new product
            products[barcode] = {
                "barcode": barcode,
                "name": product_name,
                "price": price,
                "total_quantity": quantity,
                "total_price": total,
                "favorite": False,
                "history": [{
                    "date": date_and_time,
                    "quantity": quantity,
                    "price": price
                }],
                "cheapest_price": price,
                "highest_price": price,
                "price_increase": 0.0,
                "last_price": price,
                'settings': {"default_category": "", "alias": ""}

            }

    # Update stats.json
    total_receipt_price = receipt_content.get('total', 0.0)
    number_of_items = int(receipt_content.get('numberOfItems', 0))
    receipt_barcode = receipt_content.get('barcode', 'Unknown Barcode')

    stats['total_receipts'] = len(stats.get('receipts', {})) + 1
    stats['total_spent'] = sum(float(r.get('total_price', 0) or 0) for r in (stats.get('receipts') or {}).values()) + float(total_receipt_price or 0) 

    stats['total_items'] = calculate_total_items() + number_of_items
    stats['average_spend_per_receipt'] = stats['total_spent'] / stats['total_receipts'] if stats[
                                                                                               'total_receipts'] > 0 else 0.0

    # Sort products for top 10 purchased
    top_10_product_purchased = sorted(
        products.values(),
        key=lambda x: x.get('total_quantity', 0),
        reverse=True
    )[:10]
    stats['top_10_product_purchased'] = top_10_product_purchased

    # Calculate and update top 10 price increases and drops
    top_10_price_increase = calculate_top_10_price_increase(products)
    stats['top_10_price_increase'] = top_10_price_increase
    top_10_price_drop = calculate_top_10_price_drop(products)
    stats['top_10_price_drop'] = top_10_price_drop

    stats['receipts'][receipt_barcode] = {
        "total_price": total_receipt_price,
        "date_and_time": date_and_time
    }

    # Save the updated databases
    try:
        with open(products_db_path, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=4)
        print("Updated products.json successfully.")

        with open(stats_db_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)
        print("Updated stats.json successfully.")
    except IOError as e:
        print(f"Error saving database files: {e}")

def calculate_total_items():
    total_items = 0
    base_dir = pathlib.Path(__file__).resolve().parent.parent
    products_path = base_dir / "databases" / "products.json"
    with products_path.open('r', encoding='utf-8') as f:
        products = json.load(f)
    # iterate and sum all total_quantity fields from all products
    for product in products.values():
        total_items += product.get('total_quantity', 0)
    return total_items


def calculate_total_spent():
    base_dir = pathlib.Path(__file__).resolve().parent.parent
    stats_path = base_dir / "databases" / "stats.json"
    with stats_path.open('r', encoding='utf-8') as f:
        stats = json.load(f)
    average_spend_per_receipt = stats['total_spent'] / stats['total_receipts'] if stats['total_receipts'] > 0 else 0.0
    print(average_spend_per_receipt)
    return sum(float(r.get('total_price', 0) or 0) for r in (stats.get('receipts') or {}).values())  
    

if __name__ == "__main__":    # Example usage of process_receipt_file
    base_dir = pathlib.Path(__file__).resolve().parent.parent
    products_path = base_dir / "databases" / "products.json"
    with products_path.open('r', encoding='utf-8') as f:
        products = json.load(f)
    print(calculate_top_10_price_drop(products))
    print("""

---------------------------------------------------------


""")
    print(calculate_top_10_price_increase(products))


    print(calculate_total_items())
    print(calculate_total_spent())