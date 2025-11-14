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
from PIL import Image
from pathlib import Path

class SamuraiPNGTuber:
    def __init__(self):
        pygame.init()
        
        # Window settings
        self.viewport_presets = [
            (800, 800),   # d+1: Square viewport
            (1200, 800)   # d+2: Wide viewport
        ]
        self.current_viewport = 0
        self.width, self.height = self.viewport_presets[self.current_viewport]
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Kentroid Samurai PNG-Tuber")
        
        # Load samurai image
        self.image_path = Path(__file__).parent / "KentroidSamuraiTopVisorShade.PNG"
        self.load_image()
        
        # Zoom settings
        # Multiple zoom levels from full body to extreme close-up
        # Mask center at (1054, 514) in original 2048x2732 image
        self.mask_center_original = (1054, 514)
        self.image_center_original = (self.original_width // 2, self.original_height // 2)
        
        # Visor glow offset adjustment (relative to mask center)
        # Negative X = shift left, Positive X = shift right
        self.visor_glow_offset = (-50, 0)  # Shift 80px left from mask center
        
        self.zoom_levels = [
            {
                'name': 'full_body',
                'scale': None,  # Will calculate to fit window
                'focus': 'center'  # Focus on image center
            },
            {
                'name': 'medium',
                'scale': 1.0,
                'focus': 'mask'  # Focus on mask
            },
            {
                'name': 'close',
                'scale': 1.1,
                'focus': 'mask'
            },
            {
                'name': 'closer',
                'scale': 1.2,
                'focus': 'mask'
            },
            {
                'name': 'extreme',
                'scale': 1.3,  # Most zoomed in
                'focus': 'mask'
            }
        ]
        self.current_zoom = 0
        
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
        self.show_ui = True
        
        # Initialize audio
        self.init_audio()
        
        # Clock for FPS
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Key states for combo detection
        self.keys_pressed = set()
        
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
        
    def init_audio(self):
        """Initialize PyAudio for microphone input"""
        try:
            self.audio = pyaudio.PyAudio()
            self.audio_stream = self.audio.open(
                format=self.audio_format,
                channels=self.audio_channels,
                rate=self.audio_rate,
                input=True,
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
        glow_radius = int((self.glow_base_size / 2) * scale)
        
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
        
        # Create glow surface
        glow_size = glow_radius * 2
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        
        # Draw single solid circle with transparency based on intensity
        alpha = int(total_intensity * 255)
        color = (r, g, b, alpha)
        center = (glow_radius, glow_radius)
        pygame.draw.circle(glow_surface, color, center, glow_radius)
        
        # Blit glow surface
        glow_rect = glow_surface.get_rect(center=visor_pos)
        surface.blit(glow_surface, glow_rect)
        
        # Decay talking boost only (base glow remains)
        self.glow_intensity = max(0, self.glow_intensity - self.glow_decay)
    
    def draw(self):
        """Main drawing function"""
        self.frame_count += 1
        
        # Clear screen with black background
        self.screen.fill((0, 0, 0))
        
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
            image_x = self.width // 2
            image_y = self.height // 2
        else:
            # Zoomed views: position so mask center is at screen center
            mask_x_scaled = self.mask_center_original[0] * scale
            mask_y_scaled = self.mask_center_original[1] * scale
            image_x = self.width // 2 - mask_x_scaled + (scaled_image.get_width() // 2)
            image_y = self.height // 2 - mask_y_scaled + (scaled_image.get_height() // 2)
        
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
        
        # Draw the samurai
        self.screen.blit(rotated_image, rotated_rect)
        
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
        
        texts = [
            f"Zoom: {zoom_name} (Z+1 to Z+5)",
            f"Viewport: {viewport} (D+1/D+2)",
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
    
    def change_zoom(self, zoom_index):
        """Change zoom level"""
        if 0 <= zoom_index < len(self.zoom_levels):
            self.current_zoom = zoom_index
            zoom_name = self.zoom_levels[zoom_index]['name']
            print(f"Changed zoom to {zoom_name}")
    
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
                
                # Check for key combos
                # Z+1 through Z+5 for zoom levels
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
                
                # D+1 for viewport 1 (800x800)
                elif pygame.K_d in self.keys_pressed and event.key == pygame.K_1:
                    self.change_viewport(0)
                
                # D+2 for viewport 2 (1200x800)
                elif pygame.K_d in self.keys_pressed and event.key == pygame.K_2:
                    self.change_viewport(1)
            
            elif event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    self.keys_pressed.remove(event.key)
    
    def run(self):
        """Main application loop"""
        print("\n=== Kentroid Samurai PNG-Tuber ===")
        print("Controls:")
        print("  Z+1: Full body zoom")
        print("  Z+2: Medium zoom")
        print("  Z+3: Close zoom")
        print("  Z+4: Closer zoom")
        print("  Z+5: Extreme zoom (most zoomed)")
        print("  D+1: Square viewport (800x800)")
        print("  D+2: Wide viewport (1200x800)")
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

if __name__ == "__main__":
    try:
        app = SamuraiPNGTuber()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

