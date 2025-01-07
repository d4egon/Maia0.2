from datasets import load_dataset
from sentence_transformers import SentenceTransformer, InputExample, losses # type: ignore
from torch.utils.data import DataLoader
from rich.console import Console
from rich.progress import Progress, track
from rich.prompt import Prompt, Confirm
import os
import logging
import torch
from datetime import datetime
import random

# Initialize console for styled output
console = Console()

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
console.print(f"[bold blue]Using device: {device}[/bold blue]")

# Output folders
output_dir = "maia_fine_tuned_models"
os.makedirs(output_dir, exist_ok=True)

# Logging setup
def setup_logging():
    logs_dir = "logs/datasets"
    os.makedirs(logs_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"fineweb_log_{timestamp}.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info(f"Logging started at {timestamp}")

def test_on_subset():
    return Confirm.ask("Do you want to test on a tiny subset?")

def load_data(dataset_names, subset=False, subset_size=100):
    console.print("[bold blue]Loading datasets...[/bold blue]")
    datasets = []
    for dataset_name in track(dataset_names, description="[cyan]Processing datasets"):
        try:
            dataset = load_dataset(dataset_name)["train"]
            # Normalize dataset structure
            dataset = dataset.map(lambda x: {
                'text1': x.get('question', x.get('text', '')),
                'text2': x.get('context', x.get('choices', {}).get('text', [])[0]),
                'label': 1.0
            })
            if subset:
                indices = random.sample(range(len(dataset)), min(subset_size, len(dataset)))
                dataset = dataset.select(indices)
            datasets.append(dataset)
            console.print(f"[green]Loaded and processed {len(dataset)} rows from {dataset_name}.[/green]")
        except Exception as e:
            logging.warning(f"Failed to load dataset '{dataset_name}': {e}")
            console.print(f"[red]Failed to load dataset: {dataset_name}. Skipping.[/red]")
    if not datasets:
        raise ValueError("No valid datasets loaded.")
    return datasets

def prepare_data_for_training(datasets):
    console.print("[bold blue]Preparing data for training...[/bold blue]")
    examples = []
    for dataset in datasets:
        for row in track(dataset, description="[magenta]Preparing examples"):
            try:
                examples.append(InputExample(texts=[row['text1'], row['text2']], label=row['label']))
            except KeyError:
                logging.warning(f"Skipping row due to missing keys: {row}")
                continue
    if not examples:
        raise ValueError("No valid examples for training.")
    console.print(f"[bold green]Prepared {len(examples)} examples for training.[/bold green]")
    return DataLoader(examples, batch_size=16, shuffle=True)

def train_model(model, train_dataloader, device, epochs):
    model.to(device)
    loss = losses.CosineSimilarityLoss(model=model)
    with Progress(console=console) as progress:
        task = progress.add_task("[red]Training...", total=len(train_dataloader) * epochs)
        for epoch in range(epochs):
            model.train()
            epoch_loss = 0.0
            for batch in train_dataloader:
                try:
                    model.zero_grad()
                    loss_value = loss(batch)
                    loss_value.backward()
                    model.optimizer.step()
                    epoch_loss += loss_value.item()
                except Exception as e:
                    console.print(f"[red]Error during training: {e}[/red]")
                    logging.error(f"Error during training: {e}", exc_info=True)
                progress.advance(task)
            console.print(f"[green]Epoch {epoch + 1}/{epochs} completed. Loss: {epoch_loss / len(train_dataloader):.4f}[/green]")

def main():
    setup_logging()
    dataset_names = [
        "tau/commonsense_qa",
        "rajpurkar/squad",
        "allenai/openbookqa",
        "nvidia/OpenMathInstruct-2"
    ]
    datasets = load_data(dataset_names, subset=test_on_subset())
    train_dataloader = prepare_data_for_training(datasets)
    model_name = Prompt.ask("Choose model name or press Enter for default", default="all-MiniLM-L6-v2")
    model = SentenceTransformer(model_name)
    epochs = int(Prompt.ask("How many epochs?", default="3"))
    train_model(model, train_dataloader, device, epochs)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_save_path = os.path.join(output_dir, f"finetuned_model_{timestamp}")
    model.save(model_save_path)
    console.print(f"[bold green]Model saved to {model_save_path}[/bold green]")

if __name__ == "__main__":
    main()
