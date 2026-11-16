from faker import Faker
from datetime import timedelta, datetime, timezone
import random

fake = Faker()

class DataGenerator:

    @staticmethod
    def generate_film_name():
        return fake.sentence(10).rstrip('.')

    @staticmethod
    def generate_film_description():
        return fake.sentence(20).rstrip('.')

    @staticmethod
    def generate_price():
        return random.randint(1, 20000)

    @staticmethod
    def generate_genre_name():
        return fake.sentence(2).rstrip('.')

    @staticmethod
    def generate_creation_date():
        now = datetime.now(timezone.utc)
        return now.isoformat(timespec='milliseconds').replace("+00:00", "Z")

    @staticmethod
    def generate_review():
        return fake.sentence(5).rstrip('.')

    @staticmethod
    def generate_random_password():
        return fake.password(special_chars=False) + "1@"

    @staticmethod
    def generate_random_email():
        return f"{random.randint(10000, 99999)}_{fake.email()}"

    @staticmethod
    def generate_firstname():
        return fake.first_name()

    @staticmethod
    def generate_lastname():
        return fake.last_name()

    @staticmethod
    def generate_random_user_name():
        return f"{fake.first_name()} {fake.last_name()}"

    @staticmethod
    def generate_total_price():
        return random.randint(100, 5000)

    @staticmethod
    def generate_deposit_paid():
        return fake.boolean()

    @staticmethod
    def generate_checkin_date():
        checkin_date = fake.date_between(start_date='today', end_date='+30d')
        return checkin_date

    @staticmethod
    def generate_checkout_date(checkin_date):
        checkout_date = checkin_date + timedelta(days=random.randint(1, 14))
        return checkout_date

    @staticmethod
    def generate_additional_needs():
        options = ["Breakfast", "Lunch", "Dinner", "Late checkout", "Extra bed", ""]
        return random.choice(options)

    @staticmethod
    def generate_checkin_date_in_past():
        checkin_date = fake.date_between(start_date='-30d', end_date='today')
        return checkin_date

    @staticmethod
    def generate_unexisting_fields():
        genders = ['Male', 'Female', 'Combat-Helicopter']
        return {
            "gender": random.choice(genders),
            "age": random.randint(10, 50)
        }

    @staticmethod
    def generate_random_int(value):
        random_int = random.randint(10**value,10**(value+1)-1)
        return random_int