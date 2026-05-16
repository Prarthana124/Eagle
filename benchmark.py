import time
import torch
from ultralytics import YOLO

def run_benchmark(model_path, name, iterations=100, img_size=320):
    print(f"\n--- Benchmarking {name} (imgsz={img_size}) ---")
    
    # Explicitly setting the task to 'detect'
    model = YOLO(model_path, task='detect')
    
    fake_frame = torch.rand(1, 3, img_size, img_size)
    
    # Warmup
    for _ in range(10):
        model.predict(fake_frame, verbose=False, device='cpu', imgsz=img_size)

    # Main Timing Loop
    start_time = time.time()
    for _ in range(iterations):
        model.predict(fake_frame, verbose=False, device='cpu', imgsz=img_size)
    end_time = time.time()

    total_time = end_time - start_time
    avg_fps = iterations / total_time
    print(f"Average FPS: {avg_fps:.2f}")
    
    return avg_fps

if __name__ == "__main__":
    fp32_path = "yolov8n.pt"
    int8_path = "yolov8n_int8_openvino_model" 

    fps_baseline = run_benchmark(fp32_path, "Baseline FP32")
    fps_optimized = run_benchmark(int8_path, "Optimized INT8")

    speed_up = fps_optimized / fps_baseline
    print(f"\n🚀 FINAL SPEED-UP FACTOR: {speed_up:.2f}x")