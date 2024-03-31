import tensorflow.contrib.tensorrt as trt
import argparse

parser = argparse.ArgumentParser(description="Converts TF SavedModel to the TensorRT enabled graph.")

parser.add_argument("--input_model_dir", required=True)
parser.add_argument("--output_model_dir", required=True)
parser.add_argument("--batch_size", type=int, required=True)
parser.add_argument("--precision_mode", choices=["FP32", "FP16", "INT8"], required=True)

args = parser.parse_args()

trt.create_inference_graph(
    None, None, max_batch_size=args.batch_size,
    input_saved_model_dir=args.input_model_dir,
    output_saved_model_dir=args.output_model_dir,
    precision_mode=args.precision_mode)
