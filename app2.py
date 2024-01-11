import requests
import mysql.connector
from datetime import datetime, timedelta
import json

hotels = {
    "Loews Portofino Bay Hotel": 14841,
    "Hard Rock Hotel": 14842,
    "Loews Royal Pacific Resort": 14843,
    "Loews Sapphire Falls Resort": 14845,
    "Universal's Cabana Bay Beach Resort": 14844,
    "Universal's Aventura Hotel": 14856,
    "Universal's Endless Summer Resort - Surfside Inn and Suites": 15346,
    "Universal's Endless Summer Resort - Dockside Inn and Suites": 15783,
}

# Function to calculate dt1
def calculate_dt1(target_date):
    base_date = datetime(2024, 1, 11)
    base_dt1 = 8776
    delta = target_date - base_date
    return base_dt1 + delta.days

# Create or open a SQLite database
conn = mysql.connector.connect(
    host='your_host',  # Replace with your MySQL host
    user='your_username',  # Replace with your MySQL username
    password='your_password',  # Replace with your MySQL password
    database='your_database_name'  # Replace with your database name
)

# Create cursor
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS RateCodes (
                Date TEXT,
                RcID TEXT,
                PkgID TEXT,
                Amt TEXT,
                Name TEXT,
                Code TEXT,
                Desc TEXT,
                Img TEXT,
                Rest TEXT,
                Access TEXT,
                Corp TEXT,
                Voucher TEXT,
                Sold TEXT,
                IsMember TEXT,
                GutPolicy TEXT,
                CanPolicy TEXT,
                Phone TEXT,
                Link TEXT,
                IsStrike TEXT,
                IsOL TEXT,
                IsOLResVal TEXT,
                MaxCompNights TEXT,
                OfferMinLOS TEXT,
                IncentiveMinLOS TEXT,
                IsCompRate TEXT,
                LoyaltyOfferId TEXT,
                Restricted TEXT,
                IsPolicyRefundable TEXT,
                IsStrikeThrough TEXT,
                IsTurnDownSvc TEXT,
                VIPID TEXT,
                Attention TEXT,
                HotelNote TEXT,
                HotelNoteDisplayType TEXT,
                Images TEXT,
                IsAllowPayByPoints TEXT,
                IsHideRate TEXT,
                IsUpsellLOS TEXT,
                IsQualifiedRate TEXT,
                IsPublicPromo TEXT,
                IsIataRequired TEXT,
                HotelID INTEGER
            )''')

# Commit changes
conn.commit()

# Create a session
session = requests.Session()

# Base URL
url = "https://reservations.universalorlando.com/ibe/xml/getresultd.aspx"

for hotel_name, hotel_id in hotels.items():
    print(f"Processing data for {hotel_name}")
    # Loop over the next 180 days
    for day_offset in range(180):
        # Calculate the date
        date = datetime.now() + timedelta(days=day_offset)
        dt1_value = calculate_dt1(date)

        data = {
            'hotelID': str(hotel_id),
            'hgID': '641',
            'langID': '1',
            'currID': '1',
            'deviceWidth': '133',
            'wsmultiroom': '[]',
            'wscart': '{"CartID":"","LName":"","Dt1":' + str(dt1_value) + ',"Nights":1,"AvailabilityDt1":0,"AvailabilityDt2":0,"Rooms":1,"Adults":1,"Child1":0,"Child2":0,"Child3":0,"Child4":0,"ChildrenAges":"","Rate":"","RateCat":"","Promo":"APH","Voucher":"","Group":"","Iata":"","BedType":0,"Ns":0,"Ada":0,"Ix":-1,"Items":[],"Rsp":null,"IsChanged":false,"IsLoaded":false,"Sorting":0,"LoyaltyPoints":0,"ROOMTYPES":null,"ROOMSTAYS":null,"RoomIndex":0,"HidePromoCorpAccessCode":false,"IsAdClick":false,"CampaignID":"","Provider":"","Msg":""}'
        }

        # Make the request
        response = session.post(url, data=data)

        hotel_id = hotels[hotel_name]

        # Parse the response
        try:
            json_data = response.json()
            rate_codes = json_data.get("RateCodes", [])

            # Insert RateCodes data
            for item in rate_codes:
                c.execute('INSERT INTO RateCodes VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        (date.strftime('%Y-%m-%d'), item['RcID'], item['PkgID'], item['Amt'], item['Name'], item['Code'], item['Desc'], item['Img'], item['Rest'], item['Access'], item['Corp'], item['Voucher'], item['Sold'], item['IsMember'], item['GutPolicy'], item['CanPolicy'], item['Phone'], item['Link'], item['IsStrike'], item['IsOL'], item['IsOLResVal'], item['MaxCompNights'], item['OfferMinLOS'], item['IncentiveMinLOS'], item['IsCompRate'], item['LoyaltyOfferId'], str(item['Restricted']), item['IsPolicyRefundable'], item['IsStrikeThrough'], item['IsTurnDownSvc'], item['VIPID'], item['Attention'], item['HotelNote'], item['HotelNoteDisplayType'], json.dumps(item['Images']), item['IsAllowPayByPoints'], item['IsHideRate'], item['IsUpsellLOS'], item['IsQualifiedRate'], item['IsPublicPromo'], item['IsIataRequired'] , hotel_id))
                conn.commit()
                
        except json.JSONDecodeError:
            print(f"Failed to parse JSON for date {date.strftime('%Y-%m-%d')}")

        # Optional: Print a summary or log
        print(f"Data for {date.strftime('%Y-%m-%d')} processed.")

# Commit and close
conn.close()