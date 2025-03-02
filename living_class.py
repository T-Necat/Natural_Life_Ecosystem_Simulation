import pandas as pd
import random
import os

file_path = os.path.join(os.path.dirname(__file__), 'creatures_list.csv')

distances = {
    'sheep': [2, 0, []],
    'wolf': [3, 4, ['sheep']],
    'cow': [1, 0, []],
    'chicken': [1, 0, []],
    'rooster': [1, 0, []],
    'lion': [4, 5, ['sheep', 'cow']],
    'hunter': [3, 6, ['wolf', 'lion']]
}

class Living:
    def __init__(self, species, gender):
        self.id = random.randint(1000, 9999)
        self.species = species
        self.gender = gender
        self.location = [random.randint(0, 499), random.randint(0, 499)]
        self.movement_distance = distances[species][0]
        self.hunting_distance = distances[species][1]
        self.huntable_creatures = distances[species][2]
        self._save()

    def _save(self):
        try:
            if not os.path.exists(file_path):
                pd.DataFrame(columns=['id', 'species', 'gender', 'location', 'movement_distance', 
                                   'hunting_distance', 'huntable_creatures']).to_csv(file_path, index=False)
            
            df = pd.read_csv(file_path)
            new_creature = pd.DataFrame([{
                'id': self.id,
                'species': self.species,
                'gender': self.gender,
                'location': str(self.location),
                'movement_distance': self.movement_distance,
                'hunting_distance': self.hunting_distance,
                'huntable_creatures': str(self.huntable_creatures)
            }])
            
            df = pd.concat([df, new_creature], ignore_index=True)
            df.to_csv(file_path, index=False)
            
        except Exception as e:
            print(f"Error saving creature: {e}")

    def __repr__(self):
        return f"{self.species} {self.gender} (ID: {self.id}, Location: {self.location})"

    def __str__(self):
        return f"{self.species} ({self.gender})"
