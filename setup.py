"""
Setup script for creating a macOS .app bundle of Kentroid Samurai PNG-Tuber
"""

from setuptools import setup

APP = ['pngtuber.py']
DATA_FILES = [
    ('', ['KentroidSamuraiTopVisorShade.PNG']),
    ('', ['explosion.png']),
    ('bg', [
        'bg/samus_ship01.png',
        'bg/samus_ship02.png',
        'bg/crateria01.png',
        'bg/brinstar01.png',
        'bg/hellway01.png',
        'bg/tourian01.png'
    ]),
    ('emoji', [
        'emoji/chloe_kraid500x500.png',
        'emoji/chloe_rainbowmetroid500x500.png',
        'emoji/samus_rover500x500.png',
        'emoji/scarlett_unicorn500x500.png'
    ])
]

OPTIONS = {
    'argv_emulation': True,  # Allows drag-and-drop on the app icon
    'packages': ['pygame', 'pyaudio', 'numpy', 'PIL'],
    'includes': ['chaos_effect'],  # Include our chaos_effect module
    'iconfile': None,  # You can add an .icns file here if you have one
    'plist': {
        'CFBundleName': 'Kentroid Samurai PNG-Tuber',
        'CFBundleDisplayName': 'Kentroid Samurai PNG-Tuber',
        'CFBundleIdentifier': 'com.kentroid.samurai.pngtuber',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSMicrophoneUsageDescription': 'This app needs access to your microphone for voice reactivity.',
        'NSHighResolutionCapable': True,
    }
}

setup(
    name='Kentroid Samurai PNG-Tuber',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

