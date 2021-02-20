import requests
from datetime import datetime
import os
import re
from pathlib import Path

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

class DeckBoxArtGenerator():
    def id_sorter(self, id):
        # This function has all possible color combinations
        # Can compare a set of ID to a set of these and just return the
        # proper order
        combos = {
            'azorius': ['W', 'U'],
            'dimir': ['U', 'B'],
            'rakdos': ['B', 'R'],
            'gruul': ['R', 'G'],
            'selesnya': ['G', 'W'],
            'orzhov': ['W', 'B'],
            'izzet': ['U', 'R'],
            'golgari': ['B', 'G'],
            'boros': ['R', 'W'],
            'simic': ['G', 'U'],
            'esper': ['W', 'U', 'B'],
            'grixis': ['U', 'B', 'R'],
            'jund': ['B', 'R', 'G'],
            'naya': ['R', 'G', 'W'],
            'bant': ['G', 'W', 'U'],
            'abzan': ['W', 'B', 'G'],
            'jeskai': ['U', 'R', 'W'],
            'sultai': ['B', 'G', 'U'],
            'mardu': ['R', 'W', 'B'],
            'temur': ['G', 'U', 'R'],
            'nogreen': ['W', 'U', 'B', 'R'],
            'nowhite': ['U', 'B', 'R', 'G'],
            'noblue': ['B', 'R', 'G', 'W'],
            'nored': ['G', 'W', 'U', 'B'],
            'noblack': ['R', 'G', 'W', 'U'],
            '5c': ['W', 'U', 'B', 'R', 'G']
        }

        if len(id) == 1:
            return id

        for key in combos.keys():
            if set(id) == set(combos[key]):
                return combos[key]


    def generate(self, card_name=None, title=None, colors=None):
        api = "https://api.scryfall.com/cards/named?fuzzy={}"

        # get name of card
        if not card_name:
            card_name = input("Card name: ")
        # request the card from scryfall's api
        try:
            card = requests.get(api.format(card_name)).json()
        
            # using scryfall's data, get their cropped version of the art and save it
            img = card['image_uris']['art_crop']
            img_name = os.path.join(str(Path.home()), "Desktop", card['name']+'.jpg')

            # Get Title, if blank, use card's name
            if not title:
                title = input('Deck title: ')
                if title == '':
                    title = card['name']

            # Write image to file
            with open(img_name, 'wb') as f:
                response = requests.get(img)
                f.write(response.content)

            # Open the image
            im = Image.open(img_name)
            H, W = im.height, im.width
            # Using the current image's aspect ratio, add white border to bottom of image
            #  at 10% of image height
            layer = Image.new('RGB', (W, int(H*1.10)), (255, 255, 255))
            layer.paste(im)
            draw = ImageDraw.Draw(layer)

            # Fill new empty bottom of image with colors of commander's identity
            # First, get the identity or use color override if provided
            r_colors = r"^([WUBRG]?)+$"
            if colors:
                if colors.lower() == 'colorless':
                    identity = ""
                elif re.match(r_colors, colors.upper()):
                    identity = colors.upper()
                else:
                    identity = card['color_identity']
                    error = "Color identity override was invalid."
            else:
                identity = card['color_identity']
            
            # Get width of each column based on number of colors
            if len(identity) == 0:
                identity = ['colorless',]
            col_width = W/len(identity)
            
            # Custom RGB values to match mtg colors from lands
            colors = {
                'W': (248, 231, 185),
                'U': (14, 104, 171),
                'B': (21, 11, 0),
                'R': (211, 32, 42),
                'G': (0, 115, 62),
                'colorless' : (238, 221, 204)
            }
            # Loop over ID and draw a rectangle in the matching color
            for i, v in enumerate(self.id_sorter(identity)):
                draw.rectangle([i*col_width, H, (i+1)*col_width-1, H+H*.1], fill=colors[v], width=H*.1)

            # Draw text over color ID bar with a white outline
            font = ImageFont.truetype("font.ttf", 42)
            w, h = draw.textsize(title, font=font)
            # text starts at: 
            # original image width-text width/2
            # original image Height + (10% org img height + text height)/2
            draw.text(((W-w)/2, (H+(H*.1-h)/2)), title, fill='white', font=font, stroke_fill='black', stroke_width=2)

            # Save image
            filename = os.path.join(str(Path.home()), "Desktop", f"{card['id']}-{datetime.now().timestamp()}.jpg")
            layer.save(filename)
            os.remove(img_name)
            return "Success"
        except Exception as e:
            return e