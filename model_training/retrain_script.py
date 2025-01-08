# model_training/retrain_script.py
import torch
from datasets import load_dataset # type: ignore
from sentence_transformers import SentenceTransformer, InputExample, losses # type: ignore
from sentence_transformers.losses import CosineSimilarityLoss # type: ignore
from torch.utils.data import DataLoader
from rich.console import Console
from rich.progress import Progress, track
import argparse
import os
import logging
from datetime import datetime
import random

# Initialize console for styled output
console = Console()

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
console.print(f"[bold blue]Using device: {device}[/bold blue]")

def setup_logging(log_dir):
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"fineweb_log_{timestamp}.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info(f"Logging started at {timestamp}")

def prepare_data_for_training(dataset_path, subset=False, subset_size=64):
    console.print("[bold blue]Preparing data for training...[/bold blue]")
    examples = []
    
    dataset = load_dataset(dataset_path, split="train")
    if subset:
        indices = random.sample(range(len(dataset)), min(subset_size, len(dataset)))
        dataset = dataset.select(indices)
    
    for row in track(dataset, description="[magenta]Processing data..."):
        try:
            text = row['text']
            sentences = text.split('. ')
            if len(sentences) > 1:
                for i in range(len(sentences) - 1):
                    examples.append(InputExample(texts=[sentences[i], sentences[i + 1]], label=0.8))
        except Exception as e:
            logging.warning(f"Skipping row due to error: {e}")
            continue

    if not examples:
        console.print("[bold red]No valid examples found in the dataset![/bold red]")
        raise ValueError("No valid examples for training.")
    console.print(f"[bold green]Prepared {len(examples)} examples for training.[/bold green]")

    return DataLoader(examples, batch_size=16, shuffle=True)

def train_model(model, train_dataloader, device, epochs):
    model.to(device)
    loss = CosineSimilarityLoss(model)

    with Progress(console=console) as progress:
        task = progress.add_task("[red]Training...", total=len(train_dataloader) * epochs)

        for epoch in range(epochs):
            total_loss = 0.0
            model.train()
            for batch in train_dataloader:
                try:
                    texts = batch.texts
                    labels = batch.label
                    
                    # Tokenize texts
                    tokenized1 = model.tokenize(texts[:, 0], padding=True, truncation=True, max_length=512)
                    tokenized2 = model.tokenize(texts[:, 1], padding=True, truncation=True, max_length=512)

                    input_ids1 = torch.tensor(tokenized1["input_ids"]).to(device)
                    input_ids2 = torch.tensor(tokenized2["input_ids"]).to(device)

                    # Compute outputs and loss
                    outputs1 = model(input_ids1)
                    outputs2 = model(input_ids2)
                    
                    labels = torch.tensor(labels).to(device)
                    loss_value = loss(outputs1, outputs2, labels)
                    
                    # Backward pass
                    loss_value.backward()
                    model.optimizer.step()
                    model.optimizer.zero_grad()

                    total_loss += loss_value.item()
                except Exception as e:
                    console.print(f"[red]Error during training: {e}[/red]")
                    logging.error(f"Error during training: {e}", exc_info=True)

                progress.advance(task)
            epoch_loss = total_loss / len(train_dataloader)
            console.print(f"[green]Epoch {epoch + 1} completed. Loss: {epoch_loss:.4f}[/green]")

def main():
    parser = argparse.ArgumentParser(description="Retrain SentenceTransformer model in Docker.")
    parser.add_argument("--model", type=str, required=True, help="Path to the model directory")
    parser.add_argument("--data", type=str, required=True, help="Path to the data directory")
    parser.add_argument("--output", type=str, required=True, help="Path to save the retrained model")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--subset", action="store_true", help="Use a subset of the data for testing")
    args = parser.parse_args()

    # Setup logging within the Docker environment
    setup_logging(args.output)

    # Load the model from the provided path
    model = SentenceTransformer(args.model, device=device)

    # Prepare data for training
    train_dataloader = prepare_data_for_training(args.data, subset=args.subset)

    # Train the model
    train_model(model, train_dataloader, device, args.epochs)

    # Save the retrained model
    model_save_path = os.path.join(args.output, f"finetuned_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    model.save(model_save_path)
    console.print(f"[bold green]Model saved to {model_save_path}[/bold green]")

if __name__ == "__main__":
    main()