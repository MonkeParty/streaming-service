#!/bin/bash

# Input and output directories
INPUT_DIR="./full-videos"
OUTPUT_DIR="./hls-videos"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: FFmpeg is not installed. Please install FFmpeg and try again."
    exit 1
fi

# Loop through all .mp4 files in the input directory
for input_file in "$INPUT_DIR"/*.mp4; do
    if [ -f "$input_file" ]; then
        # Extract the base name of the file (without path and extension)
        filename=$(basename -- "$input_file")
        name="${filename%.*}"

        # Define output folder for this video
        video_output_dir="$OUTPUT_DIR/$name"
        mkdir -p "$video_output_dir"

        segment_filename_pattern="$video_output_dir/segment%d.ts"

        # Convert the video to HLS format
        echo "Converting '$filename' to HLS format..."
        ffmpeg -i "$input_file" \
               -codec: copy \
               -start_number 0 \
               -hls_time 10 \
               -hls_list_size 0 \
               -hls_segment_filename "$segment_filename_pattern" \
               -f hls "$video_output_dir/output.m3u8"

        # Check if FFmpeg succeeded
        if [ $? -eq 0 ]; then
            echo "Successfully converted '$filename' to HLS format in '$video_output_dir'."
        else
            echo "Error converting '$filename'. Check the FFmpeg logs for details."
        fi
    fi
done

echo "All videos have been processed."
