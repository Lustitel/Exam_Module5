from utils.data_generator import DataGenerator
from random import randint

def generate_review():
    return {
      "rating": randint(0,5),
      "text": DataGenerator.generate_review()
    }