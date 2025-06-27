#!/usr/bin/env python3
"""
OT-BICME Robot Simulation Entry Point
Simulates robot behavior in virtual environment using pygame and pymunk
"""

import pygame
import pymunk
import pymunk.pygame_util
import sys
import time
import math
from typing import Tuple, List


class RobotSimulation:
    """Main simulation class for OT-BICME robot"""

    def __init__(self, width: int = 1200, height: int = 800):
        """Initialize simulation environment"""
        self.width = width
        self.height = height
        self.running = True

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("OT-BICME Robot Simulation")
        self.clock = pygame.time.Clock()

        # Initialize physics space
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)  # 2D simulation, no gravity

        # Drawing options
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        # Robot properties
        self.robot_body = None
        self.robot_shape = None
        self.robot_position = (width // 2, height // 2)
        self.robot_angle = 0

        self.setup_environment()
        self.create_robot()

    def setup_environment(self):
        """Setup simulation environment with boundaries"""
        # Create boundary walls
        static_body = self.space.static_body

        # Bottom wall
        bottom = pymunk.Segment(
            static_body, (0, self.height), (self.width, self.height), 5
        )
        # Top wall
        top = pymunk.Segment(static_body, (0, 0), (self.width, 0), 5)
        # Left wall
        left = pymunk.Segment(static_body, (0, 0), (0, self.height), 5)
        # Right wall
        right = pymunk.Segment(
            static_body, (self.width, 0), (self.width, self.height), 5
        )

        for wall in [bottom, top, left, right]:
            wall.friction = 0.7
            wall.color = (255, 0, 0, 255)  # Red walls (RGBA)
            self.space.add(wall)

    def create_robot(self):
        """Create robot body in simulation"""
        # Robot is a box (rectangular shape)
        robot_mass = 10
        robot_size = (60, 40)  # width, height

        # Create robot body
        moment = pymunk.moment_for_box(robot_mass, robot_size)
        self.robot_body = pymunk.Body(robot_mass, moment)
        self.robot_body.position = self.robot_position

        # Create robot shape
        self.robot_shape = pymunk.Poly.create_box(self.robot_body, robot_size)
        self.robot_shape.friction = 0.7
        self.robot_shape.color = (0, 255, 0, 255)  # Green robot (RGBA)

        # Add to space
        self.space.add(self.robot_body, self.robot_shape)

    def handle_input(self):
        """Handle keyboard input for robot control"""
        keys = pygame.key.get_pressed()
        force_magnitude = 500

        # WASD movement
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            # Forward
            force = (0, -force_magnitude)
            self.robot_body.apply_force_at_local_point(force, (0, 0))

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            # Backward
            force = (0, force_magnitude)
            self.robot_body.apply_force_at_local_point(force, (0, 0))

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            # Turn left
            self.robot_body.angular_velocity = -2

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            # Turn right
            self.robot_body.angular_velocity = 2

        # Damping to stop robot gradually
        if not any(
            [keys[pygame.K_w], keys[pygame.K_s], keys[pygame.K_UP], keys[pygame.K_DOWN]]
        ):
            self.robot_body.velocity = self.robot_body.velocity * 0.95

        if not any(
            [
                keys[pygame.K_a],
                keys[pygame.K_d],
                keys[pygame.K_LEFT],
                keys[pygame.K_RIGHT],
            ]
        ):
            self.robot_body.angular_velocity *= 0.95

    def update_simulation(self, dt: float):
        """Update physics simulation"""
        # Step physics
        self.space.step(dt)

        # Keep robot in bounds
        x, y = self.robot_body.position
        if x < 30:
            self.robot_body.position = (30, y)
        if x > self.width - 30:
            self.robot_body.position = (self.width - 30, y)
        if y < 20:
            self.robot_body.position = (x, 20)
        if y > self.height - 20:
            self.robot_body.position = (x, self.height - 20)

    def draw(self):
        """Render simulation"""
        # Clear screen
        self.screen.fill((50, 50, 50))  # Dark gray background

        # Draw physics objects
        self.space.debug_draw(self.draw_options)

        # Draw robot info
        self.draw_robot_info()

        # Update display
        pygame.display.flip()

    def draw_robot_info(self):
        """Draw robot telemetry on screen"""
        font = pygame.font.Font(None, 36)

        # Robot position
        x, y = self.robot_body.position
        pos_text = font.render(f"Position: ({x:.1f}, {y:.1f})", True, (255, 255, 255))
        self.screen.blit(pos_text, (10, 10))

        # Robot velocity
        vx, vy = self.robot_body.velocity
        vel_text = font.render(f"Velocity: ({vx:.1f}, {vy:.1f})", True, (255, 255, 255))
        self.screen.blit(vel_text, (10, 50))

        # Robot angle
        angle = math.degrees(self.robot_body.angle)
        angle_text = font.render(f"Angle: {angle:.1f}°", True, (255, 255, 255))
        self.screen.blit(angle_text, (10, 90))

        # Instructions
        instr_text = font.render("WASD/Arrow Keys: Move Robot", True, (200, 200, 200))
        self.screen.blit(instr_text, (10, self.height - 60))

        quit_text = font.render("ESC: Quit Simulation", True, (200, 200, 200))
        self.screen.blit(quit_text, (10, self.height - 30))

    def run(self):
        """Main simulation loop"""
        print("🤖 OT-BICME Robot Simulation Started!")
        print("📋 Controls:")
        print("   WASD or Arrow Keys: Move robot")
        print("   ESC: Quit simulation")
        print("=" * 50)

        dt = 1.0 / 60.0  # 60 FPS

        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            # Handle input
            self.handle_input()

            # Update simulation
            self.update_simulation(dt)

            # Draw everything
            self.draw()

            # Control frame rate
            self.clock.tick(60)

        print("🏁 Simulation stopped!")
        pygame.quit()


def main():
    """Main entry point"""
    try:
        simulation = RobotSimulation()
        simulation.run()
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install simulation dependencies with:")
        print("   pip install pygame pymunk")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Simulation interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
