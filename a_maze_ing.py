"""Entry point for the Maze Generator CLI application."""

import sys
from MazeGenerator.parser import Parser
from MazeGenerator.maze_engine import MazeEngine


def print_menu() -> None:
    """Print the user command menu."""
    print("\n--- Maze Generator Menu ---")
    print("g - Generate new maze (with current seed)")
    print("s - Show/Hide solution path")
    print("t - Next theme")
    print("w - Write/Save to file")
    print("q - Quit")
    print("---------------------------")


def main() -> None:
    """Run the main interactive CLI loop."""
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <path_to_config>")
        return

    config_path = sys.argv[1]
    parser = Parser(config_path)

    try:
        args = parser.get_args()
        engine = MazeEngine(*args)

        engine.generate()
        engine.solve()

        show_path = True

        while True:
            print("\033[H\033[J", end="")
            theme_name = engine.renderer.get_current_theme_name()
            print(f"\nCurrent Theme: {theme_name}")

            engine.show(with_path=show_path)
            print_menu()

            choice = input("Select action: ").lower().strip()

            if choice == 'g':
                engine.seed += 1
                engine.generate()
                engine.solve()
            elif choice == 's':
                show_path = not show_path
            elif choice == 't':
                engine.renderer.next_theme()
            elif choice == 'w':
                engine.save()
                print(f"Maze saved to {engine.output_file}")
                input("Press Enter to continue...")
            elif choice == 'q':
                print("Goodbye!")
                break
            else:
                print("Invalid command. Try again.")

    except FileNotFoundError:
        print(f"Error: File '{config_path}' not found.")
    except ValueError as e:
        print(f"Error in config file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
