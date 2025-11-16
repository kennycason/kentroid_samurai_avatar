#!/usr/bin/env python3
"""
CHAOS VIEWER - Standalone Mathematical Visual Madness
Pure computational art and chaos theory visualization

Run this to experience the full glory of mathematical chaos!
"""

import pygame
import sys
from chaos_effect import ChaosEffect


class ChaosViewer:
    def __init__(self, width=1200, height=800, fullscreen=False):
        pygame.init()
        
        self.width = width
        self.height = height
        
        # Set up display
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.width = self.screen.get_width()
            self.height = self.screen.get_height()
        else:
            self.screen = pygame.display.set_mode((width, height))
        
        pygame.display.set_caption("CHAOS")
        
        # Initialize chaos effect
        self.chaos = ChaosEffect(self.width, self.height)
        
        # Clock for FPS
        self.clock = pygame.time.Clock()
        self.running = True
        
        # UI settings
        self.show_fps = False
        self.show_info = False
    
    def handle_events(self):
        """Handle keyboard and window events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # ESC or Q to quit
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.running = False
                
                # F to toggle FPS display
                elif event.key == pygame.K_f:
                    self.show_fps = not self.show_fps
                    print(f"FPS display: {'ON' if self.show_fps else 'OFF'}")
                
                # I to toggle info overlay
                elif event.key == pygame.K_i:
                    self.show_info = not self.show_info
                    print(f"Info display: {'ON' if self.show_info else 'OFF'}")
                
                # R to regenerate Voronoi points
                elif event.key == pygame.K_r:
                    self.chaos.regenerate_voronoi()
                    print("🔄 Voronoi points regenerated!")
                
                # SPACE to spawn extra particles
                elif event.key == pygame.K_SPACE:
                    self.chaos.spawn_particles(50)
                    print("✨ Spawned 50 particles!")
                
                # Numbers 1-9 to change kaleidoscope segments
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    segments = event.key - pygame.K_0
                    self.chaos.kaleidoscope_segments = segments
                    print(f"🎡 Kaleidoscope segments: {segments}")
    
    def draw_ui(self):
        """Draw UI overlay"""
        font = pygame.font.Font(None, 28)
        
        if self.show_fps:
            fps = self.clock.get_fps()
            fps_text = font.render(f"FPS: {fps:.1f}", True, (0, 255, 255))
            self.screen.blit(fps_text, (10, 10))
        
        if self.show_info:
            info_lines = [
                f"Particles: {len(self.chaos.particles)}",
                f"Attractor Points: {len(self.chaos.attractor_points)}",
                f"Kaleidoscope: {self.chaos.kaleidoscope_segments} segments",
                f"Fractal Depth: {self.chaos.fractal_depth}",
                "",
                "Controls:",
                "  ESC/Q: Quit",
                "  F: Toggle FPS",
                "  I: Toggle Info",
                "  R: Regenerate Voronoi",
                "  SPACE: Spawn Particles",
                "  1-9: Kaleidoscope Segments"
            ]
            
            y_offset = 40
            for line in info_lines:
                text = font.render(line, True, (0, 255, 255))
                self.screen.blit(text, (10, y_offset))
                y_offset += 25
    
    def run(self):
        """Main application loop"""
        print("\n" + "=" * 60)
        print("🌀✨💫 CHAOS EFFECT - MATHEMATICAL MADNESS 💫✨🌀")
        print("=" * 60)
        print("\nA celebration of computational beauty and chaos theory")
        print("\nFeaturing:")
        print("  • Voronoi Diagrams")
        print("  • Particle Systems with Physics")
        print("  • Lorenz Strange Attractor")
        print("  • Recursive Fractals")
        print("  • Lissajous Curves")
        print("  • Geometric Chaos")
        print("  • Kaleidoscope Effects")
        print("\nControls:")
        print("  ESC/Q: Quit")
        print("  F: Toggle FPS counter")
        print("  I: Toggle info overlay")
        print("  R: Regenerate Voronoi points")
        print("  SPACE: Spawn 50 particles")
        print("  1-9: Change kaleidoscope segments")
        print("\n" + "=" * 60 + "\n")
        
        while self.running:
            self.handle_events()
            
            # Update chaos effect
            self.chaos.update()
            
            # Clear screen with black
            self.screen.fill((0, 0, 0))
            
            # Draw chaos effect
            self.chaos.draw(self.screen)
            
            # Draw UI overlay
            self.draw_ui()
            
            # Update display
            pygame.display.flip()
            
            # Maintain 60 FPS
            self.clock.tick(60)
        
        pygame.quit()
        print("\n🌀 Chaos viewer closed. Reality restored. 🌀\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Chaos')
    parser.add_argument('--width', type=int, default=1200,
                       help='Window width (default: 1200)')
    parser.add_argument('--height', type=int, default=800,
                       help='Window height (default: 800)')
    parser.add_argument('--fullscreen', action='store_true',
                       help='Run in fullscreen mode')
    
    args = parser.parse_args()
    
    try:
        viewer = ChaosViewer(width=args.width, height=args.height, fullscreen=args.fullscreen)
        viewer.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

