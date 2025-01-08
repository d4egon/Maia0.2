from datasets import load_dataset
from rich.console import Console

console = Console()

try:
    # Load the dataset
    dataset = load_dataset("nvidia/OpenMathInstruct-2", split="train")

    # Display dataset information
    console.print(f"[bold blue]Dataset Name: {dataset.builder_name}[/bold blue]")
    console.print(f"[green]Number of Rows: {len(dataset)}[/green]")

    # Display schema information
    console.print("[bold magenta]Dataset Features:[/bold magenta]")
    for feature_name, feature in dataset.features.items():
        console.print(f"- [cyan]{feature_name}[/cyan]: {feature}")

    # Print some sample data for a sanity check
    console.print("[bold magenta]Sample Data:[/bold magenta]")
    for row in dataset.select(range(3)):  # Print first 3 rows
        console.print(f"- {row}")

except Exception as e:
    console.print(f"[red]An error occurred while loading the dataset:[/red] {e}")