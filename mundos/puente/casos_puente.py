# casos_puente.py  ---  los niveles del puente de noche (datos, no programa)
# 'gente': (nombre, minutos que tarda en cruzar). 'linterna': minutos de bateria.
# 'miedosos': no se quedan SOLOS en el monte sin linterna. 'peleados': no se quedan JUNTOS
# en el monte sin linterna. La bateria alcanza justo para el mejor plan, y ese plan es unico.
# Fabricados y verificados con herramientas/generar_casos_puente.py.
CASOS = {1: {'titulo': 'El puente de noche · nivel 1',
     'gente': [('Pixie', 4), ('Rosa', 8), ('Toño', 9)],
     'miedosos': ['Rosa'],
     'peleados': [('Rosa', 'Toño')],
     'linterna': 21},
 2: {'titulo': 'El puente de noche · nivel 2',
     'gente': [('Pixie', 8), ('Rosa', 10), ('Toño', 11), ('Inés', 12)],
     'miedosos': ['Inés'],
     'peleados': [('Rosa', 'Inés'), ('Rosa', 'Toño')],
     'linterna': 49},
 3: {'titulo': 'El puente de noche · nivel 3',
     'gente': [('Pixie', 1), ('Rosa', 2), ('Toño', 8), ('Inés', 10), ('Lucho', 14)],
     'miedosos': ['Rosa'],
     'peleados': [('Inés', 'Lucho'), ('Rosa', 'Lucho')],
     'linterna': 32},
 4: {'titulo': 'El puente de noche · nivel 4',
     'gente': [('Pixie', 5), ('Rosa', 9), ('Toño', 10), ('Inés', 12), ('Lucho', 14), ('Chela', 15)],
     'miedosos': ['Rosa', 'Inés'],
     'peleados': [('Toño', 'Chela'), ('Rosa', 'Lucho')],
     'linterna': 83}}
