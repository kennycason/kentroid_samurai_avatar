#!/usr/bin/env python3
"""
Kentroid Samurai PNG-Tuber
A simple VTuber-style avatar application with voice reactivity
"""

import pygame
import pyaudio
import numpy as np
import math
import sys
import random
import glob
import argparse
import json
from PIL import Image
from pathlib import Path
from chaos_effect import ChaosEffect

class SamuraiPNGTuber:
    def __init__(self, audio_device_index=None):
        pygame.init()
        
        # Config file path
        self.config_path = Path.home() / ".kentroid_samurai_avatar.json"
        
        # Load saved config
        config = self.load_config()
        
        # Audio device selection (CLI arg overrides config)
        if audio_device_index is not None:
            self.audio_device_index = audio_device_index
        else:
            self.audio_device_index = config.get('audio_device_index', None)
        
        # Window settings
        self.viewport_presets = [
            (800, 800),    # d+1: Square viewport
            (1200, 800),   # d+2: Wide viewport
            (1920, 1080)   # d+3: Full HD viewport (OBS-optimized with 100px lower position)
        ]
        self.current_viewport = config.get('viewport', 0)
        self.viewport_x_offset = config.get('viewport_x_offset', 0)  # Manual X offset for fine-tuning position (arrow keys)
        self.viewport_y_offset = config.get('viewport_y_offset', 0)  # Manual Y offset for fine-tuning position (arrow keys)
        self.width, self.height = self.viewport_presets[self.current_viewport]
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Kentroid Samurai PNG-Tuber")
        
        # Load samurai image
        self.image_path = Path(__file__).parent / "KentroidSamuraiTopVisorShade.PNG"
        self.load_image()
        
        # Load explosion sprite sheet
        self.load_explosion_sprites()
        
        # Load emoji images
        self.load_emoji_images()
        
        # Load background images
        self.load_background_images()
        
        # Background settings
        self.current_background = config.get('background', 1)  # 1=black, 2=rainbow, 3=ship01, 4=ship02, 5=crateria01, 6=brinstar01, 7=hellway01, 8=tourian01, 9=chaos
        self.rainbow_hue = 0.0  # For rainbow background animation
        self.chaos_effect = None  # For chaos background
        
        # Initialize chaos effect if background is chaos
        if self.current_background == 9:
            self.chaos_effect = ChaosEffect(self.width, self.height)
        
        # Effects system
        self.current_effect = None
        self.active_explosions = []
        self.active_emojis = []
        
        # Effect 3: Psychedelic color shift
        self.effect3_hue_offset = 0.0
        self.effect3_time = 0
        self.effect3_pattern_index = 0  # Current pattern
        self.effect3_pattern_timer = 0  # Time in current pattern
        self.effect3_pattern_duration = 300  # Frames per pattern (5 seconds at 60fps)
        
        # Zoom settings
        # Multiple zoom levels from full body to extreme close-up
        # Mask center at (1054, 514) in original 2048x2732 image
        self.mask_center_original = (1000, 500) # (1054, 514)
        self.image_center_original = (self.original_width // 2, self.original_height // 2)
        
        # Visor glow offset adjustment (relative to mask center)
        # Negative X = shift left, Positive X = shift right
        self.visor_glow_offset = (0, 0)  # Shift 80px left from mask center
        
        self.zoom_levels = [
            {
                'name': 'full_body',
                'scale': None,  # Will calculate to fit window
                'focus': 'center'  # Focus on image center
            },
            {
                'name': 'mid_body1',
                'scale': 0.4,
                'focus': 'mask'  # Intermediate zoom - focus on mask
            },
            {
                'name': 'mid_body2',
                'scale': 0.6,
                'focus': 'mask'  # Intermediate zoom
            },
            {
                'name': 'mid_body3',
                'scale': 0.8,
                'focus': 'mask'  # Intermediate zoom
            },
            {
                'name': 'face1',
                'scale': 1.0,
                'focus': 'mask'  # Focus on mask
            },
            {
                'name': 'face2',
                'scale': 1.1,
                'focus': 'mask'
            },
            {
                'name': 'face3',
                'scale': 1.2,
                'focus': 'mask'
            },
            {
                'name': 'face4',
                'scale': 1.3,
                'focus': 'mask'
            },
            {
                'name': 'face5',
                'scale': 1.4,
                'focus': 'mask'
            },
            {
                'name': 'face6',
                'scale': 1.5,
                'focus': 'mask'
            }
        ]
        self.current_zoom = config.get('zoom', 4)  # Default to Z+5 (face1, was Z+2)
        
        # Animation settings
        self.rock_angle = 0
        self.rock_speed = 0.5  # Faster rocking when talking
        self.max_rock_angle = 2  # degrees
        self.rock_intensity = 0.0  # Driven by audio like glow
        self.rock_decay = 0.08
        
        # Bobbing variability
        self.bob_pattern = 0  # Current bobbing pattern
        self.bob_patterns = [
            {'type': 'tilt', 'axis': 'z'},      # Normal head tilt
            {'type': 'vertical', 'axis': 'y'},   # Up-down bob
            {'type': 'tilt_left', 'axis': 'z'},  # Tilt more left
            {'type': 'tilt_right', 'axis': 'z'}, # Tilt more right
        ]
        self.pattern_change_counter = 0
        self.pattern_change_interval = 180  # Change pattern every 3 seconds at 60fps
        
        # Audio settings
        self.audio_chunk = 1024
        self.audio_format = pyaudio.paInt16
        self.audio_channels = 1
        self.audio_rate = 44100
        self.audio_threshold = 300  # Adjust for sensitivity
        
        # Visor glow settings (400x400 sphere on original image)
        self.glow_intensity = 0.0
        self.glow_decay = 0.05  # Slower decay so it's more visible
        self.max_glow = 1.0
        self.glow_base_size = 350  # 400x400 on original image scale
        self.glow_base_intensity = 0.3  # Always-on base glow
        
        # Audio debug
        self.last_volume = 0
        self.frame_count = 0
        
        # UI toggle
        self.show_ui = False
        
        # Initialize audio
        self.init_audio()
        
        # Clock for FPS
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Key states for combo detection
        self.keys_pressed = set()
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    print(f"Loaded config from {self.config_path}")
                    return config
        except Exception as e:
            print(f"Could not load config: {e}")
        
        # Return defaults if config doesn't exist or fails to load
        return {
            'viewport': 0,
            'zoom': 4,  # Z+5: face1 - good default zoom
            'background': 1,
            'viewport_x_offset': 0,
            'viewport_y_offset': 0,
            'audio_device_index': None
        }
    
    def save_config(self):
        """Save current configuration to JSON file"""
        try:
            config = {
                'viewport': self.current_viewport,
                'zoom': self.current_zoom,
                'background': self.current_background,
                'viewport_x_offset': self.viewport_x_offset,
                'viewport_y_offset': self.viewport_y_offset,
                'audio_device_index': self.audio_device_index
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Could not save config: {e}")
        
    def load_image(self):
        """Load and prepare the samurai image"""
        pil_image = Image.open(self.image_path)
        self.original_width, self.original_height = pil_image.size
        
        # Convert PIL image to pygame surface
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        
        self.original_image = pygame.image.fromstring(data, size, mode)
        self.original_image = self.original_image.convert_alpha()
        
        print(f"Loaded image: {self.original_width}x{self.original_height}")
    
    def load_explosion_sprites(self):
        """Load and split explosion sprite sheet into individual frames"""
        explosion_path = Path(__file__).parent / "explosion.png"
        explosion_sheet = pygame.image.load(str(explosion_path)).convert_alpha()
        
        # Get dimensions - 10 frames in a single row
        sheet_width = explosion_sheet.get_width()
        sheet_height = explosion_sheet.get_height()
        frame_width = sheet_width // 10
        frame_height = sheet_height
        
        # Split into individual frames
        self.explosion_frames = []
        for i in range(10):
            frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
            frame = explosion_sheet.subsurface(frame_rect).copy()
            self.explosion_frames.append(frame)
        
        print(f"Loaded {len(self.explosion_frames)} explosion frames ({frame_width}x{frame_height} each)")
    
    def load_emoji_images(self):
        """Load all emoji images from the emoji directory"""
        emoji_dir = Path(__file__).parent / "emoji"
        emoji_paths = glob.glob(str(emoji_dir / "*.png"))
        
        self.emoji_images = []
        for emoji_path in emoji_paths:
            try:
                emoji = pygame.image.load(emoji_path).convert_alpha()
                self.emoji_images.append(emoji)
                print(f"Loaded emoji: {Path(emoji_path).name}")
            except Exception as e:
                print(f"Warning: Could not load emoji {emoji_path}: {e}")
        
        print(f"Total emojis loaded: {len(self.emoji_images)}")
        
        # Emoji effect settings
        self.emoji_min_size = 50
        self.emoji_max_size = 150
    
    def load_background_images(self):
        """Load background images for different scenes"""
        bg_dir = Path(__file__).parent / "bg"
        
        self.bg_images = {}
        
        # Define background files to load
        bg_files = {
            'ship01': 'samus_ship01.png',
            'ship02': 'samus_ship02.png',
            'crateria01': 'crateria01.png',
            'brinstar01': 'brinstar01.png',
            'hellway01': 'hellway01.png',
            'tourian01': 'tourian01.png'
        }
        
        # Load each background
        for key, filename in bg_files.items():
            bg_path = bg_dir / filename
            try:
                if bg_path.exists():
                    self.bg_images[key] = pygame.image.load(str(bg_path)).convert()
                    print(f"Loaded background: {filename}")
                else:
                    print(f"Warning: {filename} not found")
            except Exception as e:
                print(f"Warning: Could not load {filename}: {e}")
        
        print(f"Total backgrounds loaded: {len(self.bg_images)}")
        
    def init_audio(self):
        """Initialize PyAudio for microphone input"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # If device index specified, get device info
            if self.audio_device_index is not None:
                device_info = self.audio.get_device_info_by_index(self.audio_device_index)
                print(f"Using audio device: {device_info['name']} (index {self.audio_device_index})")
            else:
                print("Using default audio input device")
            
            self.audio_stream = self.audio.open(
                format=self.audio_format,
                channels=self.audio_channels,
                rate=self.audio_rate,
                input=True,
                input_device_index=self.audio_device_index,
                frames_per_buffer=self.audio_chunk,
                stream_callback=self.audio_callback
            )
            self.audio_stream.start_stream()
            print("Audio initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize audio: {e}")
            self.audio = None
            self.audio_stream = None
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Process audio input to detect voice activity"""
        try:
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            volume = np.abs(audio_data).mean()
            self.last_volume = volume
            
            # Update glow intensity and rock intensity based on volume
            if volume > self.audio_threshold:
                intensity = min(self.max_glow, volume / 2000)
                self.glow_intensity = intensity
                self.rock_intensity = intensity  # Same intensity for rocking
                
                # Log when glow is triggered (every 30 frames to avoid spam)
                if self.frame_count % 30 == 0:
                    print(f"🎤 Audio detected! Volume: {volume:.0f}, Glow: {self.glow_intensity:.2f}")
            
        except Exception as e:
            print(f"Audio callback error: {e}")
        
        return (in_data, pyaudio.paContinue)
    
    def activate_effect(self, effect_number):
        """Activate or toggle an effect"""
        # If same effect is already active, deactivate it
        if self.current_effect == effect_number:
            print(f"Deactivating effect {effect_number}")
            self.current_effect = None
            self.active_explosions.clear()
            self.active_emojis.clear()
        else:
            # Deactivate current effect and activate new one
            if self.current_effect is not None:
                print(f"Stopping effect {self.current_effect}")
                self.active_explosions.clear()
                self.active_emojis.clear()
            
            print(f"Activating effect {effect_number}")
            self.current_effect = effect_number
            
            # Initialize effect-specific state
            if effect_number == 1:
                self.effect1_red_phase = 0.0  # Phase for oscillation
                self.effect1_explosion_timer = 0
            elif effect_number == 2:
                self.effect2_spawn_timer = 0
                # Spawn initial emojis
                for _ in range(10):
                    self.spawn_emoji()
            elif effect_number == 3:
                self.effect3_hue_offset = 0.0
                self.effect3_time = 0
                self.effect3_pattern_index = 0
                self.effect3_pattern_timer = 0
                print("🌈 PSYCHEDELIC MODE ACTIVATED - NEON DREAMS ENGAGED! 🌈")
    
    def update_effects(self):
        """Update active effects each frame"""
        if self.current_effect == 1:
            self.update_effect_1()
        elif self.current_effect == 2:
            self.update_effect_2()
        elif self.current_effect == 3:
            self.update_effect_3()
    
    def update_effect_1(self):
        """Update Effect 1: Rage mode with red tint and explosions"""
        # Oscillate red tint slowly (sine wave for smooth oscillation)
        self.effect1_red_phase += 0.015  # Slower oscillation speed
        # Use sine wave to oscillate between 0.3 (light red) and 1.0 (dark red)
        self.effect1_red_intensity = 0.65 + 0.35 * math.sin(self.effect1_red_phase)
        
        # Spawn explosions randomly - MORE EXPLOSIONS!
        self.effect1_explosion_timer += 1
        if self.effect1_explosion_timer >= 4:  # Spawn every 4 frames (twice as fast!)
            self.effect1_explosion_timer = 0
            
            # Spawn 1-2 explosions per spawn cycle
            num_explosions = random.randint(1, 2)
            for _ in range(num_explosions):
                # Random position on screen
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                
                # Random size (50% to 150% of original)
                scale = random.uniform(0.5, 1.5)
                
                explosion = {
                    'x': x,
                    'y': y,
                    'frame': 0,
                    'scale': scale
                }
                self.active_explosions.append(explosion)
        
        # Update all explosions
        for explosion in self.active_explosions[:]:
            explosion['frame'] += 0.5  # Animate through frames quickly
            if explosion['frame'] >= len(self.explosion_frames):
                self.active_explosions.remove(explosion)
    
    def spawn_emoji(self):
        """Spawn a new emoji with random properties"""
        if not self.emoji_images:
            return
        
        # Random emoji from loaded images
        emoji_image = random.choice(self.emoji_images)
        
        # Random size between min and max
        size = random.randint(self.emoji_min_size, self.emoji_max_size)
        
        # Random starting position (anywhere on screen)
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)
        
        # Random velocity (speed and direction)
        vx = random.uniform(-5, 5)
        vy = random.uniform(-5, 5)
        
        # Random rotation speed (degrees per frame)
        rotation_speed = random.uniform(-5, 5)
        
        # Random flip
        flip_x = random.choice([True, False])
        flip_y = random.choice([True, False])
        
        emoji = {
            'image': emoji_image,
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy,
            'size': size,
            'rotation': 0,
            'rotation_speed': rotation_speed,
            'flip_x': flip_x,
            'flip_y': flip_y
        }
        
        self.active_emojis.append(emoji)
    
    def update_effect_2(self):
        """Update Effect 2: Emoji Party with bouncing emojis"""
        # Spawn new emojis periodically
        self.effect2_spawn_timer += 1
        if self.effect2_spawn_timer >= 30 and len(self.active_emojis) < 20:  # Keep max 20 emojis
            self.effect2_spawn_timer = 0
            self.spawn_emoji()
        
        # Update all emojis
        for emoji in self.active_emojis[:]:
            # Update position
            emoji['x'] += emoji['vx']
            emoji['y'] += emoji['vy']
            
            # Bounce off edges
            if emoji['x'] - emoji['size'] // 2 < 0 or emoji['x'] + emoji['size'] // 2 > self.width:
                emoji['vx'] *= -1
                emoji['x'] = max(emoji['size'] // 2, min(self.width - emoji['size'] // 2, emoji['x']))
            
            if emoji['y'] - emoji['size'] // 2 < 0 or emoji['y'] + emoji['size'] // 2 > self.height:
                emoji['vy'] *= -1
                emoji['y'] = max(emoji['size'] // 2, min(self.height - emoji['size'] // 2, emoji['y']))
            
            # Update rotation
            emoji['rotation'] += emoji['rotation_speed']
            emoji['rotation'] %= 360
    
    def update_effect_3(self):
        """Update Effect 3: Psychedelic color transformation"""
        # Smoothly cycle through hue spectrum
        self.effect3_hue_offset += 2.0  # Degrees per frame
        self.effect3_hue_offset %= 360
        
        # Increment time for wave patterns
        self.effect3_time += 1
        
        # Cycle through patterns
        self.effect3_pattern_timer += 1
        if self.effect3_pattern_timer >= self.effect3_pattern_duration:
            self.effect3_pattern_timer = 0
            self.effect3_pattern_index = (self.effect3_pattern_index + 1) % 8  # 8 different patterns
            pattern_names = ["Horizontal Waves", "Vertical Waves", "Diagonal Scan", "Radial Burst", 
                           "Checkerboard", "Glitch Bars", "Spiral", "Plasma"]
            print(f"🌈 Pattern switched to: {pattern_names[self.effect3_pattern_index]}")
    
    def apply_red_tint(self, surface):
        """Apply red tint overlay to a surface"""
        if self.current_effect == 1 and self.effect1_red_intensity > 0:
            # Create a red overlay
            red_overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            alpha = int(self.effect1_red_intensity * 150)  # Max 150 alpha for red tint
            red_overlay.fill((255, 0, 0, alpha))
            surface.blit(red_overlay, (0, 0))
        return surface
    
    def apply_psychedelic_effect(self, surface):
        """Apply psychedelic color transformation to a surface (Effect 3)"""
        if self.current_effect != 3:
            return surface
        
        # Create a copy to avoid modifying original
        width, height = surface.get_size()
        effect_surface = surface.copy()
        
        # Base color layers (always applied)
        overlay1 = pygame.Surface((width, height), pygame.SRCALPHA)
        hue = self.effect3_hue_offset
        color1 = self.hsv_to_rgb(hue, 0.6, 1.0)
        overlay1.fill((*color1, 80))
        effect_surface.blit(overlay1, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        
        # Apply pattern-specific effects
        pattern_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if self.effect3_pattern_index == 0:
            # Horizontal Waves (original)
            for y in range(0, height, 4):
                wave_offset = math.sin((y * 0.02) + (self.effect3_time * 0.05))
                wave_hue = (self.effect3_hue_offset + wave_offset * 60) % 360
                wave_color = self.hsv_to_rgb(wave_hue, 0.8, 0.9)
                wave_alpha = int(abs(wave_offset) * 40)
                pygame.draw.line(pattern_surface, (*wave_color, wave_alpha), 
                               (0, y), (width, y), 4)
        
        elif self.effect3_pattern_index == 1:
            # Vertical Waves
            for x in range(0, width, 4):
                wave_offset = math.sin((x * 0.02) + (self.effect3_time * 0.05))
                wave_hue = (self.effect3_hue_offset + wave_offset * 60) % 360
                wave_color = self.hsv_to_rgb(wave_hue, 0.8, 0.9)
                wave_alpha = int(abs(wave_offset) * 40)
                pygame.draw.line(pattern_surface, (*wave_color, wave_alpha), 
                               (x, 0), (x, height), 4)
        
        elif self.effect3_pattern_index == 2:
            # Diagonal Scan Lines
            for i in range(-height, width, 8):
                offset = (i + self.effect3_time * 2) % (width + height)
                wave_hue = (self.effect3_hue_offset + (offset * 0.5)) % 360
                wave_color = self.hsv_to_rgb(wave_hue, 0.9, 1.0)
                pygame.draw.line(pattern_surface, (*wave_color, 60), 
                               (offset, 0), (offset - height, height), 3)
        
        elif self.effect3_pattern_index == 3:
            # Radial Burst
            center_x, center_y = width // 2, height // 2
            for angle in range(0, 360, 10):
                angle_rad = math.radians(angle + self.effect3_time * 2)
                radius = min(width, height)
                end_x = center_x + math.cos(angle_rad) * radius
                end_y = center_y + math.sin(angle_rad) * radius
                wave_hue = (self.effect3_hue_offset + angle) % 360
                wave_color = self.hsv_to_rgb(wave_hue, 0.8, 0.9)
                pygame.draw.line(pattern_surface, (*wave_color, 50), 
                               (center_x, center_y), (end_x, end_y), 2)
        
        elif self.effect3_pattern_index == 4:
            # Checkerboard
            checker_size = 20
            for y in range(0, height, checker_size):
                for x in range(0, width, checker_size):
                    if ((x // checker_size) + (y // checker_size) + (self.effect3_time // 10)) % 2:
                        checker_hue = (self.effect3_hue_offset + x + y) % 360
                        checker_color = self.hsv_to_rgb(checker_hue, 0.7, 0.8)
                        pygame.draw.rect(pattern_surface, (*checker_color, 70), 
                                       (x, y, checker_size, checker_size))
        
        elif self.effect3_pattern_index == 5:
            # Glitch Bars
            for i in range(10):
                bar_y = (i * height // 10 + self.effect3_time * (i % 3 + 1)) % height
                bar_height = random.randint(10, 40)
                bar_hue = (self.effect3_hue_offset + i * 36) % 360
                bar_color = self.hsv_to_rgb(bar_hue, 1.0, 1.0)
                pygame.draw.rect(pattern_surface, (*bar_color, 80), 
                               (0, bar_y, width, bar_height))
        
        elif self.effect3_pattern_index == 6:
            # Spiral
            center_x, center_y = width // 2, height // 2
            for i in range(0, 360, 5):
                angle = math.radians(i + self.effect3_time * 3)
                radius = (i / 360.0) * min(width, height) // 2
                x = center_x + math.cos(angle) * radius
                y = center_y + math.sin(angle) * radius
                spiral_hue = (self.effect3_hue_offset + i) % 360
                spiral_color = self.hsv_to_rgb(spiral_hue, 0.9, 1.0)
                if i > 0:
                    prev_angle = math.radians(i - 5 + self.effect3_time * 3)
                    prev_radius = ((i - 5) / 360.0) * min(width, height) // 2
                    prev_x = center_x + math.cos(prev_angle) * prev_radius
                    prev_y = center_y + math.sin(prev_angle) * prev_radius
                    pygame.draw.line(pattern_surface, (*spiral_color, 60), 
                                   (prev_x, prev_y), (x, y), 3)
        
        elif self.effect3_pattern_index == 7:
            # Plasma Effect
            for y in range(0, height, 6):
                for x in range(0, width, 6):
                    plasma_val = math.sin(x * 0.02 + self.effect3_time * 0.05)
                    plasma_val += math.sin(y * 0.02 + self.effect3_time * 0.05)
                    plasma_val += math.sin((x + y) * 0.01 + self.effect3_time * 0.05)
                    plasma_hue = (self.effect3_hue_offset + plasma_val * 50) % 360
                    plasma_color = self.hsv_to_rgb(plasma_hue, 0.8, 0.9)
                    plasma_alpha = int((plasma_val + 3) / 6 * 60)
                    pygame.draw.rect(pattern_surface, (*plasma_color, plasma_alpha), 
                                   (x, y, 6, 6))
        
        effect_surface.blit(pattern_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        
        return effect_surface
    
    def draw_explosions(self):
        """Draw all active explosions"""
        for explosion in self.active_explosions:
            frame_index = int(explosion['frame'])
            if 0 <= frame_index < len(self.explosion_frames):
                frame = self.explosion_frames[frame_index]
                
                # Scale the explosion
                if explosion['scale'] != 1.0:
                    new_width = int(frame.get_width() * explosion['scale'])
                    new_height = int(frame.get_height() * explosion['scale'])
                    frame = pygame.transform.smoothscale(frame, (new_width, new_height))
                
                # Center the explosion at its position
                rect = frame.get_rect(center=(explosion['x'], explosion['y']))
                self.screen.blit(frame, rect)
    
    def draw_emojis(self):
        """Draw all active emojis with rotation and flipping"""
        for emoji in self.active_emojis:
            # Scale emoji to desired size
            scaled_emoji = pygame.transform.smoothscale(emoji['image'], (emoji['size'], emoji['size']))
            
            # Apply flipping
            scaled_emoji = pygame.transform.flip(scaled_emoji, emoji['flip_x'], emoji['flip_y'])
            
            # Apply rotation
            rotated_emoji = pygame.transform.rotate(scaled_emoji, emoji['rotation'])
            
            # Center the emoji at its position
            rect = rotated_emoji.get_rect(center=(int(emoji['x']), int(emoji['y'])))
            self.screen.blit(rotated_emoji, rect)
    
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV color to RGB (values 0-1)"""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def draw_background(self):
        """Draw the current background"""
        if self.current_background == 1:
            # Black background (default)
            self.screen.fill((0, 0, 0))
        
        elif self.current_background == 2:
            # Rainbow background
            self.draw_rainbow_background()
        
        elif self.current_background == 3:
            # Ship 01 background
            if 'ship01' in self.bg_images:
                self.draw_cover_background(self.bg_images['ship01'])
            else:
                self.screen.fill((0, 0, 0))
        
        elif self.current_background == 4:
            # Ship 02 background
            if 'ship02' in self.bg_images:
                self.draw_cover_background(self.bg_images['ship02'])
            else:
                self.screen.fill((0, 0, 0))
        
        elif self.current_background == 5:
            # Crateria01 background
            if 'crateria01' in self.bg_images:
                self.draw_cover_background(self.bg_images['crateria01'])
            else:
                self.screen.fill((0, 0, 0))
        
        elif self.current_background == 6:
            # Brinstar01 background
            if 'brinstar01' in self.bg_images:
                self.draw_cover_background(self.bg_images['brinstar01'])
            else:
                self.screen.fill((0, 0, 0))
        
        elif self.current_background == 7:
            # Hellway01 background
            if 'hellway01' in self.bg_images:
                self.draw_cover_background(self.bg_images['hellway01'])
            else:
                self.screen.fill((0, 0, 0))
        
        elif self.current_background == 8:
            # Tourian01 background
            if 'tourian01' in self.bg_images:
                self.draw_cover_background(self.bg_images['tourian01'])
            else:
                self.screen.fill((0, 0, 0))
        
        elif self.current_background == 9:
            # Chaos background - mathematical madness!
            if self.chaos_effect:
                # Fill with black first, then draw chaos on top
                self.screen.fill((0, 0, 0))
                self.chaos_effect.update()
                self.chaos_effect.draw(self.screen)
            else:
                self.screen.fill((0, 0, 0))
    
    def draw_cover_background(self, bg_image):
        """Draw background image with cover fit (fills screen without distortion)"""
        # Get image dimensions
        img_width = bg_image.get_width()
        img_height = bg_image.get_height()
        
        # Calculate scale to cover the screen
        scale_w = self.width / img_width
        scale_h = self.height / img_height
        scale = max(scale_w, scale_h)  # Use max to cover (not contain)
        
        # Calculate new dimensions
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Scale the image
        scaled_bg = pygame.transform.smoothscale(bg_image, (new_width, new_height))
        
        # Center the image
        x = (self.width - new_width) // 2
        y = (self.height - new_height) // 2
        
        self.screen.blit(scaled_bg, (x, y))
    
    def draw_rainbow_background(self):
        """Draw a smooth rainbow gradient background"""
        # Update rainbow hue
        self.rainbow_hue += 0.003  # Slow smooth progression
        if self.rainbow_hue > 1.0:
            self.rainbow_hue = 0.0
        
        # Create a smooth gradient across the screen
        for y in range(self.height):
            # Calculate hue based on y position and time
            hue = (self.rainbow_hue + (y / self.height) * 0.3) % 1.0
            color = self.hsv_to_rgb(hue, 0.6, 0.8)  # Medium saturation and brightness
            
            pygame.draw.line(self.screen, color, (0, y), (self.width, y))
    
    def change_background(self, bg_number):
        """Change the background"""
        if 1 <= bg_number <= 9:
            self.current_background = bg_number
            
            # Initialize chaos effect if switching to chaos background
            if bg_number == 9:
                if not self.chaos_effect:
                    self.chaos_effect = ChaosEffect(self.width, self.height)
                    print("🌀 CHAOS BACKGROUND ACTIVATED - MATHEMATICAL MADNESS ENGAGED! 🌀")
            
            bg_names = {
                1: "Black",
                2: "Rainbow",
                3: "Samus Ship 01",
                4: "Samus Ship 02",
                5: "Crateria",
                6: "Brinstar",
                7: "Hellway",
                8: "Tourian",
                9: "Chaos (Mathematical Madness)"
            }
            print(f"Changed background to: {bg_names[bg_number]}")
            self.save_config()
    
    def get_scaled_image(self):
        """Get the samurai image scaled according to current zoom level"""
        zoom = self.zoom_levels[self.current_zoom]
        
        if zoom['name'] == 'full_body':
            # Scale to fit the window while maintaining aspect ratio
            scale_w = self.width / self.original_width
            scale_h = self.height / self.original_height
            scale = min(scale_w, scale_h) * 0.9  # 90% to leave some margin
        else:
            # Use specified scale for face zoom
            scale = zoom['scale']
        
        new_width = int(self.original_width * scale)
        new_height = int(self.original_height * scale)
        
        return pygame.transform.smoothscale(self.original_image, (new_width, new_height))
    
    def draw_visor_glow(self, surface, visor_pos, scale):
        """Draw the neon glowing sphere behind the visor - always visible, color changes with volume"""
        # Calculate total intensity (base + talking boost)
        total_intensity = self.glow_base_intensity + self.glow_intensity
        total_intensity = min(1.0, total_intensity)
        
        # Scale the 400x400 glow to current image scale (fixed size, no pulsing)
        glow_radius = int((self.glow_base_size / 2) * scale * 0.95)
        
        # First, draw a solid black circle directly on the screen to block the background
        pygame.draw.circle(surface, (0, 0, 0), visor_pos, glow_radius)
        
        # Determine color based on talking intensity
        # Idle: Blue -> Low volume: Cyan -> Medium: Green -> High: Pink/Magenta -> Very High: Purple
        talking_intensity = self.glow_intensity  # 0.0 to 1.0
        
        if talking_intensity < 0.1:
            # Idle/quiet: Deep blue
            r, g, b = 0, 150, 255
        elif talking_intensity < 0.3:
            # Low volume: Cyan
            r, g, b = 0, 255, 255
        elif talking_intensity < 0.5:
            # Medium volume: Green
            r, g, b = 0, 255, 150
        elif talking_intensity < 0.7:
            # High volume: Pink/Magenta
            r, g, b = 255, 100, 255
        else:
            # Very high volume: Purple
            r, g, b = 200, 0, 255
        
        # Create glow surface with transparency
        glow_size = glow_radius * 2
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        center = (glow_radius, glow_radius)
        
        # Draw the glowing circle with transparency
        alpha = int(total_intensity * 255)
        color = (r, g, b, alpha)
        pygame.draw.circle(glow_surface, color, center, glow_radius)
        
        # Blit glow surface on top of the black circle
        glow_rect = glow_surface.get_rect(center=visor_pos)
        surface.blit(glow_surface, glow_rect)
        
        # Decay talking boost only (base glow remains)
        self.glow_intensity = max(0, self.glow_intensity - self.glow_decay)
    
    def draw(self):
        """Main drawing function"""
        self.frame_count += 1
        
        # Update active effects
        self.update_effects()
        
        # Draw background (replaces screen.fill)
        self.draw_background()
        
        # Get scaled image
        scaled_image = self.get_scaled_image()
        zoom = self.zoom_levels[self.current_zoom]
        
        # Calculate scale factor for positioning
        if zoom['name'] == 'full_body':
            scale_w = self.width / self.original_width
            scale_h = self.height / self.original_height
            scale = min(scale_w, scale_h) * 0.9
        else:
            scale = zoom['scale']
        
        # Calculate where to position the image on screen
        if zoom['focus'] == 'center':
            # Full body: center the entire image
            image_x = self.width // 2 + self.viewport_x_offset
            image_y = self.height // 2 + self.viewport_y_offset
        else:
            # Zoomed views: position so mask center is at screen center
            mask_x_scaled = self.mask_center_original[0] * scale
            mask_y_scaled = self.mask_center_original[1] * scale
            image_x = self.width // 2 - mask_x_scaled + (scaled_image.get_width() // 2) + self.viewport_x_offset
            image_y = self.height // 2 - mask_y_scaled + (scaled_image.get_height() // 2) + self.viewport_y_offset
        
        image_rect = scaled_image.get_rect(center=(image_x, image_y))
        
        # Apply rock animation only when talking
        if self.rock_intensity > 0.02:
            self.rock_angle += self.rock_speed
            
            # Change bobbing pattern periodically
            self.pattern_change_counter += 1
            if self.pattern_change_counter >= self.pattern_change_interval:
                self.bob_pattern = (self.bob_pattern + 1) % len(self.bob_patterns)
                self.pattern_change_counter = 0
            
            # Calculate angle based on current pattern
            pattern = self.bob_patterns[self.bob_pattern]
            base_motion = math.sin(self.rock_angle)
            
            if pattern['type'] == 'tilt':
                # Normal head tilt (left-right)
                angle = base_motion * self.max_rock_angle * self.rock_intensity
                y_offset = 0
            elif pattern['type'] == 'vertical':
                # Up-down bobbing
                angle = base_motion * (self.max_rock_angle * 0.5) * self.rock_intensity
                y_offset = int(base_motion * 5 * self.rock_intensity)
            elif pattern['type'] == 'tilt_left':
                # Tilt with left bias
                angle = (base_motion - 0.3) * self.max_rock_angle * self.rock_intensity
                y_offset = 0
            elif pattern['type'] == 'tilt_right':
                # Tilt with right bias
                angle = (base_motion + 0.3) * self.max_rock_angle * self.rock_intensity
                y_offset = 0
            else:
                angle = base_motion * self.max_rock_angle * self.rock_intensity
                y_offset = 0
            
            # Apply y_offset if present
            if 'y_offset' not in locals():
                y_offset = 0
            
            # Decay rock intensity
            self.rock_intensity = max(0, self.rock_intensity - self.rock_decay)
        else:
            angle = 0
            y_offset = 0
            self.rock_intensity = 0
        
        # Rotate image for rocking effect and apply y_offset
        if angle != 0:
            rotated_image = pygame.transform.rotate(scaled_image, angle)
            center_with_offset = (image_rect.centerx, image_rect.centery + y_offset)
            rotated_rect = rotated_image.get_rect(center=center_with_offset)
        else:
            rotated_image = scaled_image
            rotated_rect = image_rect
        
        # Calculate visor/mask position on screen
        # The mask is at a known position in the original image
        mask_offset_x = (self.mask_center_original[0] - self.image_center_original[0]) * scale
        mask_offset_y = (self.mask_center_original[1] - self.image_center_original[1]) * scale
        
        # Apply visor glow offset for fine-tuning
        visor_offset_x_scaled = self.visor_glow_offset[0] * scale
        visor_offset_y_scaled = self.visor_glow_offset[1] * scale
        
        visor_x = rotated_rect.centerx + mask_offset_x + visor_offset_x_scaled
        visor_y = rotated_rect.centery + mask_offset_y + visor_offset_y_scaled
        
        # Draw glow behind the image (pass scale for proper sizing)
        self.draw_visor_glow(self.screen, (visor_x, visor_y), scale)
        
        # Apply psychedelic effect to the image (if active)
        if self.current_effect == 3:
            rotated_image = self.apply_psychedelic_effect(rotated_image)
        
        # Draw the samurai
        self.screen.blit(rotated_image, rotated_rect)
        
        # Apply red tint effect over the character (if active)
        if self.current_effect == 1:
            self.apply_red_tint(self.screen)
        
        # Draw explosions on top of everything
        self.draw_explosions()
        
        # Draw emojis on top of everything
        self.draw_emojis()
        
        # Draw UI info if enabled
        if self.show_ui:
            self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw UI information overlay"""
        font = pygame.font.Font(None, 30)
        
        # Current settings
        zoom_name = self.zoom_levels[self.current_zoom]['name']
        viewport = f"{self.width}x{self.height}"
        
        pattern_name = self.bob_patterns[self.bob_pattern]['type']
        total_glow = self.glow_base_intensity + self.glow_intensity
        
        effect_str = f"Effect {self.current_effect}" if self.current_effect else "None"
        if self.current_effect == 1:
            effect_str += f" (RAGE 🔥 Red: {self.effect1_red_intensity:.2f})"
        elif self.current_effect == 2:
            effect_str += f" (EMOJI PARTY 🎉 Count: {len(self.active_emojis)})"
        elif self.current_effect == 3:
            pattern_names = ["H-Wave", "V-Wave", "Diagonal", "Radial", "Checker", "Glitch", "Spiral", "Plasma"]
            pattern_name = pattern_names[self.effect3_pattern_index]
            effect_str += f" (PSYCHEDELIC 🌈 {pattern_name} | Hue: {self.effect3_hue_offset:.0f}°)"
        
        bg_names = {1: "Black", 2: "Rainbow", 3: "Ship 01", 4: "Ship 02", 5: "Crateria", 6: "Brinstar", 7: "Hellway", 8: "Tourian", 9: "Chaos"}
        bg_str = bg_names.get(self.current_background, "Unknown")
        
        # Add particle count for chaos background
        if self.current_background == 9 and self.chaos_effect:
            particles = len(self.chaos_effect.particles)
            bg_str += f" 🌀✨💫 ({particles} particles)"
        
        texts = [
            f"Zoom: {zoom_name} (Z+1 to Z+0, 0=zoom 10)",
            f"Viewport: {viewport} (D+1/D+2/D+3)",
            f"Position: X={self.viewport_x_offset:+d} Y={self.viewport_y_offset:+d} (Arrow keys ±5px, R to reset)",
            f"Background: {bg_str} (B+1 to B+9)",
            f"Effect: {effect_str} (E+1/E+2/E+3 to toggle)",
            f"Glow: {'🔵 TALKING' if self.glow_intensity > 0.02 else '🔵 IDLE'} ({total_glow:.2f})",
            f"Audio: Vol={self.last_volume:.0f}, Threshold={self.audio_threshold}",
            f"Bob: {self.rock_intensity:.2f} ({pattern_name})",
            "Press T to toggle UI | ESC to quit"
        ]
        
        y_offset = 10
        for text in texts:
            surface = font.render(text, True, (0, 255, 255))
            self.screen.blit(surface, (10, y_offset))
            y_offset += 30
    
    def change_viewport(self, preset_index):
        """Change viewport dimensions"""
        if 0 <= preset_index < len(self.viewport_presets):
            self.current_viewport = preset_index
            self.width, self.height = self.viewport_presets[preset_index]
            self.screen = pygame.display.set_mode((self.width, self.height))
            print(f"Changed viewport to {self.width}x{self.height}")
            self.save_config()
    
    def change_zoom(self, zoom_index):
        """Change zoom level"""
        if 0 <= zoom_index < len(self.zoom_levels):
            self.current_zoom = zoom_index
            zoom_name = self.zoom_levels[zoom_index]['name']
            print(f"Changed zoom to {zoom_name}")
            self.save_config()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                
                # ESC to quit
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                # T to toggle UI text
                elif event.key == pygame.K_t:
                    self.show_ui = not self.show_ui
                    print(f"UI text: {'ON' if self.show_ui else 'OFF'}")
                
                # Arrow keys to adjust viewport position (5px at a time)
                elif event.key == pygame.K_UP:
                    self.viewport_y_offset -= 5
                    print(f"Position offset: X={self.viewport_x_offset}, Y={self.viewport_y_offset}")
                    self.save_config()
                elif event.key == pygame.K_DOWN:
                    self.viewport_y_offset += 5
                    print(f"Position offset: X={self.viewport_x_offset}, Y={self.viewport_y_offset}")
                    self.save_config()
                elif event.key == pygame.K_LEFT:
                    self.viewport_x_offset -= 5
                    print(f"Position offset: X={self.viewport_x_offset}, Y={self.viewport_y_offset}")
                    self.save_config()
                elif event.key == pygame.K_RIGHT:
                    self.viewport_x_offset += 5
                    print(f"Position offset: X={self.viewport_x_offset}, Y={self.viewport_y_offset}")
                    self.save_config()
                
                # R to reset position offsets
                elif event.key == pygame.K_r:
                    self.viewport_x_offset = 0
                    self.viewport_y_offset = 0
                    print(f"Position offset reset to X=0, Y=0")
                    self.save_config()
                
                # Check for key combos
                # Z+1 through Z+0 for zoom levels (Z+0 = zoom 10)
                if pygame.K_z in self.keys_pressed and event.key == pygame.K_1:
                    self.change_zoom(0)
                elif pygame.K_z in self.keys_pressed and event.key == pygame.K_2:
                    self.change_zoom(1)
                elif pygame.K_z in self.keys_pressed and event.key == pygame.K_3:
                    self.change_zoom(2)
                elif pygame.K_z in self.keys_pressed and event.key == pygame.K_4:
                    self.change_zoom(3)
                elif pygame.K_z in self.keys_pressed and event.key == pygame.K_5:
                    self.change_zoom(4)
                elif pygame.K_z in self.keys_pressed and event.key == pygame.K_6:
                    self.change_zoom(5)
                elif pygame.K_z in self.keys_pressed and event.key == pygame.K_7:
                    self.change_zoom(6)
                elif pygame.K_z in self.keys_pressed and event.key == pygame.K_8:
                    self.change_zoom(7)
                elif pygame.K_z in self.keys_pressed and event.key == pygame.K_9:
                    self.change_zoom(8)
                elif pygame.K_z in self.keys_pressed and event.key == pygame.K_0:
                    self.change_zoom(9)
                
                # D+1 for viewport 1 (800x800)
                elif pygame.K_d in self.keys_pressed and event.key == pygame.K_1:
                    self.change_viewport(0)
                
                # D+2 for viewport 2 (1200x800)
                elif pygame.K_d in self.keys_pressed and event.key == pygame.K_2:
                    self.change_viewport(1)
                
                # D+3 for viewport 3 (1920x1080)
                elif pygame.K_d in self.keys_pressed and event.key == pygame.K_3:
                    self.change_viewport(2)
                
                # B+1 through B+9 for backgrounds
                elif pygame.K_b in self.keys_pressed and event.key == pygame.K_1:
                    self.change_background(1)
                elif pygame.K_b in self.keys_pressed and event.key == pygame.K_2:
                    self.change_background(2)
                elif pygame.K_b in self.keys_pressed and event.key == pygame.K_3:
                    self.change_background(3)
                elif pygame.K_b in self.keys_pressed and event.key == pygame.K_4:
                    self.change_background(4)
                elif pygame.K_b in self.keys_pressed and event.key == pygame.K_5:
                    self.change_background(5)
                elif pygame.K_b in self.keys_pressed and event.key == pygame.K_6:
                    self.change_background(6)
                elif pygame.K_b in self.keys_pressed and event.key == pygame.K_7:
                    self.change_background(7)
                elif pygame.K_b in self.keys_pressed and event.key == pygame.K_8:
                    self.change_background(8)
                elif pygame.K_b in self.keys_pressed and event.key == pygame.K_9:
                    self.change_background(9)
                
                # E+1, E+2, E+3 for effects
                elif pygame.K_e in self.keys_pressed and event.key == pygame.K_1:
                    self.activate_effect(1)
                elif pygame.K_e in self.keys_pressed and event.key == pygame.K_2:
                    self.activate_effect(2)
                elif pygame.K_e in self.keys_pressed and event.key == pygame.K_3:
                    self.activate_effect(3)
            
            elif event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    self.keys_pressed.remove(event.key)
    
    def run(self):
        """Main application loop"""
        print("\n=== Kentroid Samurai PNG-Tuber ===")
        print("Controls:")
        print("  Z+1: Full body (widest)")
        print("  Z+2-4: Mid-body zooms (progressive)")
        print("  Z+5-9: Face zooms (progressive, closer)")
        print("  Z+0: Maximum face zoom (closest)")
        print("  D+1: Square viewport (800x800)")
        print("  D+2: Wide viewport (1200x800)")
        print("  D+3: Full HD viewport (1920x1080, OBS-optimized)")
        print("  B+1: Black background")
        print("  B+2: Rainbow background")
        print("  B+3: Samus Ship 01 background")
        print("  B+4: Samus Ship 02 background")
        print("  B+5: Crateria background")
        print("  B+6: Brinstar background")
        print("  B+7: Hellway background")
        print("  B+8: Tourian background")
        print("  B+9: CHAOS background (MATHEMATICAL MADNESS 🌀✨💫)")
        print("  E+1: Toggle RAGE effect (red tint + explosions)")
        print("  E+2: Toggle EMOJI PARTY effect (bouncing emojis)")
        print("  E+3: Toggle PSYCHEDELIC effect (8 auto-cycling neon patterns)")
        print("  Arrow Keys: Fine-tune position (±5px)")
        print("  R: Reset position to center")
        print("  T: Toggle UI text overlay")
        print("  ESC: Quit")
        print("\nSpeak into your microphone to activate the visor glow and talking animation!")
        print("Bobbing pattern changes every 3 seconds for variety!")
        print("=" * 40 + "\n")
        
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if self.audio:
            self.audio.terminate()
        pygame.quit()
        print("PNG-Tuber closed.")

def list_audio_devices():
    """List all available audio input devices"""
    audio = pyaudio.PyAudio()
    print("\n" + "=" * 60)
    print("AVAILABLE AUDIO INPUT DEVICES:")
    print("=" * 60)
    
    device_count = audio.get_device_count()
    input_devices = []
    
    for i in range(device_count):
        try:
            device_info = audio.get_device_info_by_index(i)
            # Only show input devices
            if device_info['maxInputChannels'] > 0:
                input_devices.append((i, device_info))
                print(f"\nDevice Index: {i}")
                print(f"  Name: {device_info['name']}")
                print(f"  Channels: {device_info['maxInputChannels']}")
                print(f"  Sample Rate: {int(device_info['defaultSampleRate'])} Hz")
                print(f"  Host API: {audio.get_host_api_info_by_index(device_info['hostApi'])['name']}")
        except Exception as e:
            print(f"Error reading device {i}: {e}")
    
    print("\n" + "=" * 60)
    print(f"Total input devices found: {len(input_devices)}")
    print("=" * 60)
    print("\nTo use a specific device, run:")
    print("  python pngtuber.py --device <index>")
    print("\nExample:")
    print("  python pngtuber.py --device 3")
    print()
    
    audio.terminate()


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Kentroid Samurai PNG-Tuber')
    parser.add_argument('--list-devices', action='store_true',
                       help='List all available audio input devices and exit')
    parser.add_argument('--device', type=int, default=None,
                       help='Audio input device index to use (see --list-devices)')
    
    args = parser.parse_args()
    
    # If list devices flag is set, list and exit
    if args.list_devices:
        list_audio_devices()
        sys.exit(0)
    
    # Run the application
    try:
        app = SamuraiPNGTuber(audio_device_index=args.device)
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

