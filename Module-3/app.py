from flask import Flask, request, render_template
from PIL import Image, ImageFilter
from pprint import PrettyPrinter
from dotenv import load_dotenv
import json
import os
import random
import requests

load_dotenv()

app = Flask(__name__)

@app.route('/')
def homepage():
    """A homepage with handy links for your convenience."""
    return render_template('home.html')

################################################################################
# COMPLIMENTS ROUTES
################################################################################

list_of_compliments = [
    'awesome',
    'beatific',
    'blithesome',
    'conscientious',
    'coruscant',
    'erudite',
    'exquisite',
    'fabulous',
    'fantastic',
    'gorgeous',
    'indubitable',
    'ineffable',
    'magnificent',
    'outstanding',
    'propitioius',
    'remarkable',
    'spectacular',
    'splendiferous',
    'stupendous',
    'super',
    'upbeat',
    'wondrous',
    'zoetic'
]

@app.route('/compliments')
def compliments():
    """Shows the user a form to get compliments."""
    return render_template('compliments_form.html')


@app.route('/compliments_results')
def compliments_results():
    """Show the user some compliments."""
    name = request.args.get('users_name', 'Friend')
    wants_compliments = request.args.get('wants_compliments') == 'yes'
    num_compliments = int(request.args.get('num_compliments', 1))
    compliment = random.sample(list_of_compliments, num_compliments) if wants_compliments else []
    context = {
        'name': name,
        'wants_compliments': wants_compliments,
        'compliment': compliment,
    }
    return render_template('compliments_results.html', **context)


################################################################################
# ANIMAL FACTS ROUTE
################################################################################

animal_to_fact = {
    'koala': 'Koala fingerprints are so close to humans\' that they could taint crime scenes. 🐨',
    'parrot': 'Parrots will selflessly help each other out. 🦜',
    'mantis shrimp': 'The mantis shrimp has the world\'s fastest punch. 🦐',
    'lion': 'Female lions do 90 percent of the hunting. 🦁',
    'narwhal': 'Narwhal tusks are really an "inside out" tooth. 🦄'
}


@app.route('/animal_facts')
def animal_facts():
    """Show a form to choose an animal and receive facts."""
    chosen_animal = request.args.get('animal')
    fact = animal_to_fact.get(chosen_animal)
    
    # Pass data to the template
    context = {
        'animals': list(animal_to_fact.keys()),  
        'chosen_animal': chosen_animal,        
        'fact': fact                            
    }
    return render_template('animal_facts.html', **context)


################################################################################
# IMAGE FILTER ROUTE
################################################################################

filter_types_dict = {
    'blur': ImageFilter.BLUR,
    'contour': ImageFilter.CONTOUR,
    'detail': ImageFilter.DETAIL,
    'edge enhance': ImageFilter.EDGE_ENHANCE,
    'emboss': ImageFilter.EMBOSS,
    'sharpen': ImageFilter.SHARPEN,
    'smooth': ImageFilter.SMOOTH
}

def save_image(image, filter_type):
    """Save the image, then return the full file path of the saved image."""
    new_file_name = f"{filter_type}-{image.filename}"
    image.filename = new_file_name
    file_path = os.path.join(app.root_path, 'static/images', new_file_name)
    image.save(file_path)
    return file_path, new_file_name


def apply_filter(file_path, filter_name):
    """Apply a Pillow filter to a saved image."""
    i = Image.open(file_path)
    i.thumbnail((500, 500))
    i = i.filter(filter_types_dict.get(filter_name))
    i.save(file_path)


@app.route('/image_filter', methods=['GET', 'POST'])
def image_filter():
    """Filter an image uploaded by the user, using the Pillow library."""
    filter_types = filter_types_dict.keys()

    if request.method == 'POST':
        filter_type = request.form.get('filter_type')  # Get the filter type
        image = request.files.get('users_image')  # Get the uploaded image

        if not image or not filter_type:
            context = {'filter_types': filter_types, 'error': 'Please upload an image and select a filter.'}
            return render_template('image_filter.html', **context)

        # Save the image and apply the filter
        file_path, file_name = save_image(image, filter_type)
        apply_filter(file_path, filter_type)

        # Build the image URL
        image_url = f'/static/images/{file_name}'

        context = {
            'filter_types': filter_types,
            'image_url': image_url,
         }

        return render_template('image_filter.html', **context)

    else:  # If it's a GET request
        context = {
            'filter_types': filter_types,  # List of filter types for the form
        }
        return render_template('image_filter.html', **context)


################################################################################
# GIF SEARCH ROUTE
################################################################################

API_KEY = os.getenv('API_KEY')
print(API_KEY)

TENOR_URL = 'https://tenor.googleapis.com/v2/search'
pp = PrettyPrinter(indent=4)

@app.route('/gif_search', methods=['GET', 'POST'])
def gif_search():
    """Show a form to search for GIFs and show resulting GIFs from Tenor API."""
    if request.method == 'POST':
        search_query = request.form.get('search_query')  # Get the search query
        quantity = int(request.form.get('quantity', 5))  # Get the quantity of GIFs requested

        response = requests.get(
            TENOR_URL,
            params={
                'q': search_query,
                'key': API_KEY,
                'client_key': 'Module-3',
                'limit': quantity,
            })

        if response.status_code != 200:
            return "Error: Unable to connect to the Tenor API."

        # Parse JSON
        data = json.loads(response.content)
        gifs = data.get('results', [])

        # Check if any GIFs were found
        if not gifs:
            return render_template('gif_search.html', message="No GIFs found. Please try a different search.")

        context = {
            'gifs': gifs  # Pass the GIFs to the template
        }

        return render_template('gif_search.html', **context)

    # GET request renders the form
    return render_template('gif_search.html')


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
