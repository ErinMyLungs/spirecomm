import PySimpleGUI as sg
import os
import pandas as pd
import numpy as np

spire_cards = os.path.abspath('/home/erin/.steam/steam/steamapps/common/SlayTheSpire/cards')
layout = [
     [sg.Image(spire_cards+'/Strike_R.png', key='CARD0', size=(200, 155)), sg.Text('NaN___', key='CARD0_SCORE', font=('Ariel',20))],
     [sg.Image(spire_cards+'/Defend_R.png', key="CARD1", size=(200, 155)), sg.Text('NaN___', key='CARD1_SCORE', font=('Ariel',20))],
     [sg.Image(spire_cards+'/PommelStrike.png', key="CARD2", size=(200, 155)), sg.Text('NaN___', key='CARD2_SCORE', font=('Ariel',20))]
]
sg.change_look_and_feel('Grey')
window = sg.Window('Draft Bot Card Scores', layout)

while True:
    event, values = window.read(timeout=2)
    if event in (None, 'Quit'):
        break
    temp = pd.read_csv('/home/erin/.steam/steam/steamapps/common/SlayTheSpire/gui.csv')
    image_paths = list(temp.name.map(lambda x: '/'+x.replace(' ', '_')+'.png'))
    scores = list(temp.weight.map(lambda x: str(x)[:str(x).find('.')+2] if x else 'NaN'))
    max_score = scores[np.argmax([float(x) for x in scores])]

    for idx in range(3):
        window[f'CARD{idx}'].update(spire_cards+image_paths[idx])

        if scores[idx] == max_score:
            window[f'CARD{idx}_SCORE'].update(scores[idx], text_color='red', background_color='gold')
        else:
            window[f'CARD{idx}_SCORE'].update(scores[idx], text_color='white', background_color='grey')
