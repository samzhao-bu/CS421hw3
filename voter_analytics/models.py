from django.db import models
from django.utils.dateparse import parse_date
from django.db import transaction
import csv

class Voter(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    street_number = models.CharField(max_length=20)
    street_name = models.CharField(max_length=100)
    apartment_number = models.CharField(max_length=20, blank=True)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    party_affiliation = models.CharField(max_length=50)
    precinct_number = models.CharField(max_length=10)
    v20state = models.BooleanField(default=False)
    v21town = models.BooleanField(default=False)
    v21primary = models.BooleanField(default=False)
    v22general = models.BooleanField(default=False)
    v23town = models.BooleanField(default=False)
    voter_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.party_affiliation}"

def load_data():

    Voter.objects.all().delete()
    
    filename = '/Users/samzhao/Desktop/Django/data/newton_voters.csv'
    with open(filename, 'r') as file:
        
        reader = csv.reader(file)
        headers = next(reader)  
        
        
        for row in reader:
            try:
               
                voter = Voter(
                    last_name=row[1].strip(),
                    first_name=row[2].strip(),
                    street_number=row[3].strip(),
                    street_name=row[4].strip(),
                    apartment_number=row[5].strip(),
                    zip_code=row[6].strip(),
                    date_of_birth=parse_date(row[7]),
                    date_of_registration=parse_date(row[8]),
                    party_affiliation=row[9].strip(),
                    precinct_number=row[10].strip(),
                    v20state=row[11].strip().upper() == 'TRUE',
                    v21town=row[12].strip().upper() == 'TRUE',
                    v21primary=row[13].strip().upper() == 'TRUE',
                    v22general=row[14].strip().upper() == 'TRUE',
                    v23town=row[15].strip().upper() == 'TRUE',
                    voter_score=int(row[16])
                )
                voter.save()
                print(f'Created voter: {voter}')
            except Exception as e:
                
                print(f"Exception occurred: {e}, data: {row}")

        # After the loop
        print("Done loading all voters.")