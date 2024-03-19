from wonderwords import RandomWord
from random import randint, choice
from faker import Faker

class EmailGen:
    def __init__(self):
        self.gen_methods = [
            self.gen_email,
            self.gen_email_2,
            self.gen_email_3,
            self.gen_email_4,
            self.gen_email_5,
            self.gen_email_6,
            self.gen_email_7,
            self.gen_email_8,
            self.gen_email_9,
            self.gen_email_10,
            self.gen_email_11,
            self.gen_email_12,
            self.gen_email_13,
            self.gen_email_14,
            self.gen_email_15
        ]
        
        # add weights
        self.weight_method(self.gen_email_10, 4)
        self.weight_method(self.gen_email_15, 2)
        

    def gen(self, first_name, last_name, fake_domain):
        email_method = choice(self.gen_methods)
        dirty_email = email_method(first_name, last_name, fake_domain)
        clean_email = self.cleanup(dirty_email)
        
        return clean_email
    
    def cleanup(self, email):
        # ensure emails look clean
        clean_email = email.lower()
        clean_email = clean_email.replace("-", "")
        clean_email = clean_email.replace(" ", "")
        
        return clean_email
    
    def weight_method(self, method, weight):
        # Allows us to preferentially use methods more than others
        for _ in range(0, weight):
            self.gen_methods.append(method)

    def gen_email(self, first_name, last_name, fake_domain):
        fake = Faker()
        faker_email = fake.email()

        base_email_prefix = faker_email.split("@")[0]
        email = f"{first_name}{base_email_prefix}{randint(10, 999)}@{fake_domain}"

        return email


    def gen_email_2(self, first_name, last_name, fake_domain):
        return f"{first_name}.{last_name}{randint(10, 999)}@{fake_domain}"


    def gen_email_3(self, first_name, last_name, fake_domain):
        fake = Faker()
        faker_email = fake.email()

        base_email_prefix = faker_email.split("@")[0]
        email = f"{last_name}{base_email_prefix}{randint(1, 99)}@{fake_domain}"

        return email


    def gen_email_4(self, first_name, last_name, fake_domain):
        return f"{first_name}{RandomWord().word()}{randint(1, 999)}@{fake_domain}".lower()


    def gen_email_5(self, first_name, last_name, fake_domain):
        first_initial = first_name[:1]
        return f"{first_initial}{last_name}{randint(10, 999)}@{fake_domain}".lower()


    def gen_email_6(self, first_name, last_name, fake_domain):
        last_initial = last_name[:1]
        return f"{first_name}{last_initial}{randint(10, 999)}@{fake_domain}".lower()


    def gen_email_7(self, first_name, last_name, fake_domain):
        return self.gen_email_8(first_name, last_name, fake_domain)


    def gen_email_8(self, first_name, last_name, fake_domain):
        return f"{RandomWord().word()}{last_name}{randint(1, 999)}@{fake_domain}".lower()


    def gen_email_11(self, first_name, last_name, fake_domain):
        return f"{first_name}{RandomWord().word()}{randint(1, 999)}@{fake_domain}".lower()


    def gen_email_12(self, first_name, last_name, fake_domain):
        return f"{first_name}.{RandomWord().word()[:1].lower()}.{last_name}{randint(1, 99)}@{fake_domain}".lower()


    def gen_email_13(self, first_name, last_name, fake_domain):
        return f"{first_name}{RandomWord().word()[:1].lower()}{last_name}{randint(1, 99)}@{fake_domain}".lower()


    def gen_email_9(self, first_name, last_name, fake_domain):
        return f"{RandomWord().word()}{RandomWord().word()}{first_name[:1].upper()}{last_name[:1].upper()}{randint(1, 99)}@{fake_domain}"


    def gen_email_14(self, first_name, last_name, fake_domain):
        return f"{RandomWord().word()}{RandomWord().word()}{first_name[:1].upper()}{last_name[:1].upper()}{randint(1, 99)}@{fake_domain}"


    def gen_email_15(self, first_name, last_name, fake_domain):
        fake = Faker()
        base_string = f"{fake.profile()['username']}"
        return f"{base_string.lower()}{first_name}{randint(1, 99)}@{fake_domain}"


    def gen_email_10(self,first_name, last_name, fake_domain):
        fake = Faker()
        base_string = f"{fake.profile()['username']}"

        cases = [1, 2, 4, 5, 6]
        chosen_case = choice(cases)

        if chosen_case == 1:
            return f"{base_string}{randint(1, 999)}@{fake_domain}".lower()
        elif chosen_case == 2:
            return f"{base_string}{randint(1, 999)}@{fake_domain}".lower()
        elif chosen_case == 4:
            return f"{first_name[:1].upper()}{base_string.lower()}{randint(10, 99)}@{fake_domain.lower()}"
        elif chosen_case == 5:
            return f"{first_name[:1]}{last_name}{base_string.lower()}@{fake_domain.lower()}"
        elif chosen_case == 6:
            return f"{first_name[:1]}{last_name}{base_string.lower()}{randint(1, 999)}@{fake_domain.lower()}"
