"""
Setup script for creating a macOS .app bundle of Samurai Samus Avatar
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
    'argv_emulation': False,  # Disabled - Carbon framework not available on modern macOS
    'packages': ['pygame', 'pyaudio', 'numpy', 'PIL'],
    'includes': ['chaos_effect', 'colorsys', 'pkg_resources'],  # Include our chaos_effect module
    'iconfile': 'AppIcon.icns',  # Samurai Samus app icon
    'excludes': ['matplotlib', 'scipy'],  # Exclude unused heavy packages
    'site_packages': True,  # Include all site-packages to catch namespace packages
    'plist': {
        'CFBundleName': 'Samurai Samus Avatar',
        'CFBundleDisplayName': 'Samurai Samus Avatar',
        'CFBundleIdentifier': 'com.kentroid.samurai.pngtuber',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSMicrophoneUsageDescription': 'This app needs access to your microphone for voice reactivity.',
        'NSHighResolutionCapable': True,
    }
}

setup(
    name='Samurai Samus',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

