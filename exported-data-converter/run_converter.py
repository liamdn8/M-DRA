#!/usr/bin/env python3
from converter import DRADataConverter

def main():
    # Configuration
    input_dir = "../data/real-data"
    output_dir = "../data/converted"
    
    # Create and run converter
    converter = DRADataConverter(input_dir, output_dir)
    converter.convert()

if __name__ == "__main__":
    main()