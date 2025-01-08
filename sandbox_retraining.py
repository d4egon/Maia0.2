# core/sandbox_retraining.py
import subprocess
import os
import shutil
import datetime
from sentence_transformers import SentenceTransformer # type: ignore
from typing import Any

def sandbox_retraining(model_loader: callable, data: Any, project_root: str = os.getcwd()):
    """
    Perform model retraining in a sandbox environment before deployment.

    :param model_loader: A function that loads the model on demand.
    :param data: The data object or path to the data for retraining the model.
    :param project_root: Path to the project root directory, defaults to current working directory.
    """
    try:
        # Define paths
        sandbox_dir = os.path.join(project_root, 'data', 'sandbox')
        data_path = os.path.join(project_root, 'data', 'processed')
        model_path = os.path.join(project_root, 'data', 'fine_tuned_models')
        checkpoint_path = os.path.join(project_root, 'data', 'checkpoints')

        # Ensure sandbox directory exists and is empty
        if os.path.exists(sandbox_dir):
            shutil.rmtree(sandbox_dir)
        os.makedirs(sandbox_dir)

        # Load the model on demand
        model = model_loader()

        # Prepare data for retraining
        prepared_data_path = prepare_data(data, os.path.join(sandbox_dir, 'retraining_data'))

        # Save model to a temporary directory for Docker to access
        model_dir = os.path.join(sandbox_dir, 'model')
        save_model_for_deploy(model, model_dir)

        # Create a Docker container for isolated environment
        docker_command = f"docker run -d --name retraining_sandbox -v {sandbox_dir}:/app python:3.8-slim"
        subprocess.run(docker_command, shell=True, check=True)
        
        # Copy retraining script into the container 
        retrain_script_path = os.path.join(project_root, 'model_training', 'retrain_script.py')
        copy_command = f"docker cp {retrain_script_path} retraining_sandbox:/app/"
        subprocess.run(copy_command, shell=True, check=True)
        
        # Run retraining script inside the container
        # Note: Adjust the command based on how your retrain_script.py expects to receive model and data paths
        retrain_command = f"docker exec retraining_sandbox python /app/retrain_script.py --model /app/model --data /app/retraining_data --output /app/retrained_model"
        subprocess.run(retrain_command, shell=True, check=True)
        
        # Check success factors
        if success_factors_met(model, data):
            # Load the retrained model
            # Assuming retrain_script.py saves the model in a way that can be loaded by SentenceTransformer
            retrained_model = load_model_from_docker(os.path.join(sandbox_dir, 'retrained_model'))
            deploy_model(retrained_model, model_path, checkpoint_path)
        else:
            print("Retraining failed in sandbox")
    
    except subprocess.CalledProcessError as e:
        print(f"Error in sandbox retraining: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Clean up the container and sandbox directory
        cleanup_command = "docker rm -f retraining_sandbox"
        subprocess.run(cleanup_command, shell=True)
        if os.path.exists(sandbox_dir):
            shutil.rmtree(sandbox_dir)

def prepare_data(data: Any, output_path: str) -> str:
    """
    Prepare data for retraining. This function should be implemented based on your data handling.

    :param data: The data to prepare.
    :param output_path: Path where prepared data should be saved.
    :return: Path to the prepared data.
    """
    # Placeholder for actual data preparation logic
    print(f"Preparing data at {output_path}")
    return output_path

def save_model_for_deploy(model: SentenceTransformer, path: str):
    """
    Save the SentenceTransformer model for deployment.

    :param model: The SentenceTransformer model object to be saved.
    :param path: The directory path where the model should be saved.
    """
    try:
        # Ensure the directory exists
        os.makedirs(path, exist_ok=True)

        # Save the model using SentenceTransformer's save method
        model.save(path)
        print(f"SentenceTransformer model saved to {path}")

    except Exception as e:
        print(f"Failed to save model: {e}")

def load_model_from_docker(path: str) -> SentenceTransformer:
    """
    Load the retrained model from the Docker environment. This function should be implemented
    to match how your model was saved in save_model_for_deploy.

    :param path: Path from where to load the model.
    :return: The loaded SentenceTransformer model object.
    """
    # Placeholder for model loading logic
    try:
        retrained_model = SentenceTransformer(path)
        print(f"Retrained SentenceTransformer model loaded from {path}")
        return retrained_model
    except Exception as e:
        print(f"Failed to load model: {e}")
        return None

def success_factors_met(model: SentenceTransformer, data: Any) -> bool:
    """
    Check if the success factors for model retraining are met.

    :param model: The model that was retrained.
    :param data: The data used for retraining.
    :return: True if success factors are met, False otherwise.
    """
    # Placeholder for actual success criteria check
    # This could involve model evaluation, data validation, etc.
    return True  # Example: Always return True for demonstration

def deploy_model(model: SentenceTransformer, model_path: str, checkpoint_path: str):
    """
    Deploy the retrained model if success factors are met.

    :param model: The model to deploy.
    :param model_path: Directory path to store the model.
    :param checkpoint_path: Directory path to store model checkpoints.
    """
    model_filename = f"model_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    checkpoint_filename = f"checkpoint_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Save the model
    save_model_for_deploy(model, os.path.join(model_path, model_filename))
    print(f"Model saved as {model_filename} in {model_path}")

    # Optionally save a checkpoint
    save_model_for_deploy(model, os.path.join(checkpoint_path, checkpoint_filename))
    print(f"Checkpoint saved as {checkpoint_filename} in {checkpoint_path}")

    print("Model deployment initiated.")

if __name__ == "__main__":
    # Example usage, assuming you have a model_loader function defined elsewhere
    def model_loader():
        return SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')

    # Example data, you would replace this with your actual data preparation
    data = "path_to_your_data_or_data_object"

    sandbox_retraining(model_loader, data)