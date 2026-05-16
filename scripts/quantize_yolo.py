import os
from ultralytics import YOLO
from roboflow import Roboflow

def drone_optimized_quantization():
    # --- 1. SET YOUR ACTUAL CREDENTIALS HERE ---
    API_KEY = "YOUR_ROBOFLOW_API_KEY"
    WORKSPACE = "goyalpreeti"  # Found in your Roboflow URL
    PROJECT = "drone-detection-lzvig-sa0py"      # Found in your Roboflow URL
    VERSION = 1                        # Usually 1 if it's your first version
    
    try:
        # Initialize Roboflow
        rf = Roboflow(api_key=API_KEY) 
        project = rf.workspace(WORKSPACE).project(PROJECT)
        version = project.version(VERSION)
        
        print(f"📡 Downloading '{PROJECT}' version {VERSION} from Roboflow...")
        dataset = version.download("yolov8")
        
        # Path to the data.yaml created by Roboflow
        drone_data_yaml = os.path.join(dataset.location, "data.yaml")
        
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        print("Check your API Key, Workspace Name, and Project Name!")
        return

    # 2. Load the baseline model
    model = YOLO("yolov8n.pt")

    print(f"\n--- Starting Drone-Specific Calibration ---")
    print(f"Using dataset at: {drone_data_yaml}")
    
    # 3. Export with INT8 Quantization + 320px Optimization
    try:
        # Note: 'data' is crucial here for the accuracy calibration (Step 2 of your approach)
        path = model.export(
            format="openvino", 
            int8=True, 
            data=drone_data_yaml, 
            imgsz=320
        )
        
        # Determine the final export folder name
        export_folder = "yolov8n_int8_openvino_model"
        print(f"\n✅ SUCCESS: Drone-Optimized model saved to: {os.path.abspath(export_folder)}")
        
    except Exception as e:
        print(f"❌ Error during quantization: {e}")

if __name__ == "__main__":
    drone_optimized_quantization()